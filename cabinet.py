"""
Кабинеты репетитора и ученика (версия 34): отмены, переносы, оплаченные уроки.

Здесь вся логика «что произошло с занятием»; Telegram и сайт Mini App только вызывают эти функции.
Данные берутся из уже существующих таблиц: schedule (недельное расписание), moves (переносы), lessons (проведённые уроки),
payments (оплаты), attendance (ответы «не смогу»), а новая таблица lesson_log хранит, кто и почему отменил или перенёс занятие.

Правила (Лазиза):
· отмена за 6 часов и раньше: урок не списывается;
· отмена позже: урок списывается, если Лазиза не отметила «форс-мажор»;
· форс-мажор подтверждает только Лазиза: урок не списывается, ученик видит слова поддержки;
· если урок отменила Лазиза, он не списывается никогда;
· перенос от Лазизы вступает в силу сразу, ученику приходит уведомление;
· ученик только просит перенос, решает Лазиза.
"""
import html
import logging
from datetime import datetime, timedelta

import db
import scheduler
from texts import t, WEEKDAYS

FMT = "%Y-%m-%dT%H:%M"
LATE_HOURS = 6                       # отмена позже чем за столько часов считается поздней
REASONS = ("sick", "family", "work", "tech", "force", "other")
REASON_RU = {"sick": "болезнь", "family": "семейные обстоятельства", "work": "работа или учёба", "tech": "техника или связь",
             "force": "форс-мажор", "other": "другое"}
MAX_DAYS_AHEAD = 90

esc = lambda s: html.escape(str(s), quote=False)
ctx = {}                             # notify_owner, send, ikb, lang_of, balance_alert, after_held


# ─── мелочи ──────────────────────────────────────────────────────────────────

def now():
    return datetime.now(db.TZ)


def parse(iso):
    return datetime.strptime(iso, FMT).replace(tzinfo=db.TZ)


def iso_of(dt):
    return dt.strftime(FMT)


def when_label(dt, lang):
    return f"{WEEKDAYS[lang][dt.weekday()]}, {dt.strftime('%d.%m %H:%M')}"


def _lang(uid):
    f = ctx.get("lang_of")
    return f(uid) if f else ((db.get_user(uid) or {}).get("lang") or "ru")


def _name(uid):
    u = db.get_user(uid) or {}
    return esc(u.get("name") or "?")


def _tell(uid, key, **kw):
    """Сообщение ученику на его языке."""
    send = ctx.get("send")
    if send:
        try:
            send(uid, t(_lang(uid), key, **kw))
        except Exception:
            logging.exception("кабинет: не отправилось ученику %s", uid)


def _owner(text, **kw):
    f = ctx.get("notify_owner")
    return f(text, **kw) if f else None


def _btns(rows):
    return ctx["ikb"](rows) if ctx.get("ikb") else None


def is_late(iso, at=None):
    return (parse(iso) - (at or now())) < timedelta(hours=LATE_HOURS)


# ─── занятия ученика ─────────────────────────────────────────────────────────

def occurrences(uid, start_offset=0, days=21):
    """[(datetime, slot)] занятий ученика с учётом подтверждённых переносов."""
    slots = [dict(x, user_id=uid) for x in db.get_schedule(uid)]
    moves = [m for m in db.moves_ok() if m["user_id"] == uid]
    return scheduler.occurrences(now(), slots, moves, days=days, start_offset=start_offset)


def _has_lesson(uid, iso):
    return any(iso_of(dt) == iso for dt, _ in occurrences(uid, start_offset=-2, days=95))


def _held_dates(uid):
    return {r["date"] for r in db.lessons_all(uid, 400)}


def _status(uid, iso, dt, at, held_dates):
    """planned / held / cancelled / past (прошло, но не отмечено) и запись журнала."""
    c = db.log_find(uid, iso, "cancel")
    if c:
        return "cancelled", c
    h = db.log_find(uid, iso, "held")
    if h:
        return "held", h
    if dt <= at:
        return ("held", None) if iso[:10] in held_dates else ("past", None)
    return "planned", None


def _moved_info(uid, iso):
    """(откуда перенесено, кто попросил) для занятия, которое появилось в результате переноса."""
    for m in db.moves_for_user(uid):
        if m["status"] == "ok" and m["new"] == iso:
            lg = db.log_by_ref("move", m["id"])
            return m["orig"], (lg or {}).get("who")
    return None, None


def _row(uid, name, dt, slot, at, held_dates):
    iso = iso_of(dt)
    st, lg = _status(uid, iso, dt, at, held_dates)
    out = {"uid": uid, "name": name, "iso": iso, "date": iso[:10], "time": iso[11:], "wd": dt.weekday(), "status": st,
           "late": bool(dt > at and is_late(iso, at)), "past": dt <= at, "soon": dt <= at + timedelta(hours=1)}
    if slot.get("moved"):
        orig, who = _moved_info(uid, iso)
        out["moved_from"], out["moved_by"] = orig, who
    if lg and st == "cancelled":
        out["cancel"] = {"id": lg["id"], "code": lg["code"], "text": lg["text"], "who": lg["who"], "late": bool(lg["late"]),
                         "state": lg["status"], "charged": bool(lg["charged"])}
    return out


def student_lessons(uid, start_offset=0, days=28):
    at = now()
    held = _held_dates(uid)
    name = (db.get_user(uid) or {}).get("name")
    return [_row(uid, name, dt, slot, at, held) for dt, slot in occurrences(uid, start_offset, days)]


def balance_view(uid):
    """Счётчик оплаченных уроков: всего и «пачка» (последняя оплата) для ряда галочек."""
    done, paid, left = db.balance(uid)
    pays = db.payments_all(uid, 1)
    pkg = pays[0]["lessons"] if pays and pays[0]["lessons"] > 0 else max(paid, 0)
    pkg = max(0, min(pkg, 24))
    held_in_pkg = max(0, min(pkg, pkg - left)) if pkg else 0
    return {"done": done, "paid": paid, "left": left, "pkg": pkg, "pkg_done": held_in_pkg}


def _log_item(r):
    out = {"id": r["id"], "kind": r["kind"], "lesson": r["lesson"], "who": r["who"], "status": r["status"], "code": r["code"],
           "text": r["text"], "late": bool(r["late"]), "charged": bool(r["charged"]), "created": r["created"]}
    if r["kind"] == "move" and r["ref"]:
        m = db.move_get(r["ref"])
        out["new"] = m["new"] if m else None
    return out


def student_view(uid):
    at = now()
    items = student_lessons(uid, 0, 28)
    upcoming = [x for x in items if x["status"] in ("planned", "cancelled") and parse(x["iso"]) > at]
    logs = [_log_item(r) for r in db.log_for_user(uid, 14) if r["kind"] in ("cancel", "move")]
    lessons = [{"date": r["date"], "topic": r["topic"]} for r in db.lessons_all(uid, 12)]
    pend = [x for x in logs if x["kind"] == "move" and x["status"] == "pending"]
    return {"balance": balance_view(uid), "upcoming": upcoming, "log": logs, "lessons": lessons, "pending": pend,
            "late_hours": LATE_HOURS}


# ─── кабинет преподавателя ───────────────────────────────────────────────────

def owner_week(offset_days=0, days=7):
    at = now()
    out = []
    held_cache = {}
    for dt, slot in scheduler.occurrences(at, db.all_schedules(), db.moves_ok(), days=days, start_offset=offset_days):
        uid = slot["user_id"]
        if uid not in held_cache:
            held_cache[uid] = _held_dates(uid)
        out.append(_row(uid, slot.get("name"), dt, slot, at, held_cache[uid]))
    return out


def owner_students():
    at = now()
    res = []
    for u in db.students():
        uid = u["user_id"]
        nxt = next((iso_of(dt) for dt, _ in occurrences(uid, 0, 15) if dt > at and not db.lesson_cancelled(uid, iso_of(dt))), None)
        b = balance_view(uid)
        res.append({"uid": uid, "name": u.get("name") or "?", "username": u.get("username"), "left": b["left"], "paid": b["paid"],
                    "done": b["done"], "next": nxt})
    return res


def owner_student(uid):
    u = db.get_user(uid)
    if not u:
        return None
    at = now()
    return {"uid": uid, "name": u.get("name") or "?", "username": u.get("username"), "balance": balance_view(uid),
            "schedule": db.get_schedule(uid),
            "upcoming": [x for x in student_lessons(uid, 0, 28) if parse(x["iso"]) > at],
            "past": [x for x in student_lessons(uid, -14, 14) if parse(x["iso"]) <= at][-8:],
            "log": [_log_item(r) for r in db.log_for_user(uid, 25) if r["kind"] in ("cancel", "move")],
            "lessons": [{"id": r["id"], "date": r["date"], "topic": r["topic"]} for r in db.lessons_all(uid, 15)],
            "payments": [{"date": r["date"], "lessons": r["lessons"], "note": r["note"]} for r in db.payments_all(uid, 10)]}


def owner_pending():
    """Что ждёт решения: запросы на перенос и форс-мажоры."""
    moves = []
    for m in db.moves_pending():
        lg = db.log_by_ref("move", m["id"])
        moves.append({"id": m["id"], "uid": m["user_id"], "name": (db.get_user(m["user_id"]) or {}).get("name") or "?",
                      "orig": m["orig"], "new": m["new"], "late": bool(lg and lg["late"]),
                      "clash": clash_name(m["user_id"], parse(m["new"]))})
    force = []
    for r in db.log_pending("cancel", ("force_pending",)):
        force.append({"id": r["id"], "uid": r["user_id"], "name": (db.get_user(r["user_id"]) or {}).get("name") or "?",
                      "lesson": r["lesson"], "text": r["text"]})
    return {"moves": moves, "force": force}


# ─── отмена занятия ──────────────────────────────────────────────────────────

def _charge(uid, iso):
    """Списываем урок за позднюю отмену: запись в «проведённые» с пометкой."""
    return db.lesson_row_add(uid, "⏱ поздняя отмена", iso[:10])


def student_cancel(uid, iso, code, text=""):
    """Ученик отменяет своё участие. -> {"ok": True, ...} или {"err": ...}."""
    code = code if code in REASONS else "other"
    text = (text or "").strip()[:300]
    at = now()
    try:
        dt = parse(iso)
    except ValueError:
        return {"err": "bad"}
    if dt <= at:
        return {"err": "past"}
    if not _has_lesson(uid, iso):
        return {"err": "nolesson"}
    if db.log_find(uid, iso, "cancel"):
        return {"err": "dup"}
    late = is_late(iso, at)
    reason = REASON_RU[code] + (f": {text}" if text else "")
    db.save_attendance(uid, iso, "no", reason)                 # чтобы утренняя сводка и итоги недели видели отмену
    state, charged, lid = "ok", 0, None
    if late and code == "force":
        state = "force_pending"                                # пока Лазиза не решит, не списываем
    elif late:
        charged, lid = 1, _charge(uid, iso)
    log_id = db.log_add(uid, iso, "cancel", code, text, "student", late, state, charged, lid)
    when = dt.strftime("%d.%m %H:%M")
    head = f"❌ <b>{_name(uid)}</b> не сможет прийти {when}\nПричина: {esc(reason)}"
    if state == "force_pending":
        _owner(head + f"\n\n⚠️ Меньше чем за {LATE_HOURS} ч до урока. Это форс-мажор? Пока урок не списан.",
               reply_markup=_btns([[("🆘 Форс-мажор: не списывать", f"cf:ok:{log_id}")], [("✖️ Не форс-мажор: списать", f"cf:no:{log_id}")]]))
    elif charged:
        _owner(head + f"\n\n⚠️ Меньше чем за {LATE_HOURS} ч до урока: урок списан.",
               reply_markup=_btns([[("🆘 Это форс-мажор: вернуть урок", f"cf:ok:{log_id}")]]))
        _alert(uid)
    else:
        _owner(head + "\n\nУрок не списывается.")
    return {"ok": True, "late": late, "charged": bool(charged), "force_pending": state == "force_pending", "id": log_id,
            "code": code}


def owner_cancel(uid, iso, code, text=""):
    """Лазиза отменяет занятие: урок никогда не списывается, ученик получает уведомление с причиной."""
    code = code if code in REASONS else "other"
    text = (text or "").strip()[:300]
    try:
        dt = parse(iso)
    except ValueError:
        return {"err": "bad"}
    if not _has_lesson(uid, iso):
        return {"err": "nolesson"}
    if db.log_find(uid, iso, "cancel"):
        return {"err": "dup"}
    if db.log_find(uid, iso, "held"):
        return {"err": "held"}
    log_id = db.log_add(uid, iso, "cancel", code, text, "teacher", 0, "ok", 0, None)
    lang = _lang(uid)
    reason = t(lang, "cr_" + code) + (f": {text}" if text else "")
    _tell(uid, "tc_notice", when=when_label(dt, lang), reason=reason)
    return {"ok": True, "id": log_id}


def force_decide(log_id, ok):
    """Лазиза решает, был ли форс-мажор. -> {"ok": True, "state": ...} или {"err": ...}."""
    r = db.log_get(log_id)
    if not r or r["kind"] != "cancel" or r["who"] != "student":
        return {"err": "none"}
    uid, iso = r["user_id"], r["lesson"]
    when = when_label(parse(iso), _lang(uid))
    if ok:
        if r["status"] not in ("force_pending", "ok") or (r["status"] == "ok" and not r["charged"]):
            return {"err": "done"}
        if r["charged"] and r["lesson_id"]:
            db.lesson_row_del(r["lesson_id"])
        db.log_set(log_id, status="force_ok", charged=0, lesson_id=None)
        _tell(uid, "cf_ok_student", when=when, support=t(_lang(uid), "cr_support"))
        return {"ok": True, "state": "force_ok"}
    if r["status"] != "force_pending":
        return {"err": "done"}
    lid = _charge(uid, iso)
    db.log_set(log_id, status="force_no", charged=1, lesson_id=lid)
    _tell(uid, "cf_no_student", when=when)
    _alert(uid)
    return {"ok": True, "state": "force_no"}


# ─── переносы ────────────────────────────────────────────────────────────────

def clash_name(uid, new_dt):
    """Имя другого ученика, у которого в это время уже урок, или None."""
    off = (new_dt.date() - now().date()).days
    if off < 0 or off > 120:
        return None
    for dt, x in scheduler.occurrences(now(), db.all_schedules(), db.moves_ok(), days=1, start_offset=off):
        if dt == new_dt and x["user_id"] != uid and not db.lesson_cancelled(x["user_id"], iso_of(dt)):
            return x.get("name") or "?"
    return None


def _check_new(new_iso, at):
    try:
        new = parse(new_iso)
    except ValueError:
        return None, "bad"
    if new <= at:
        return None, "past"
    if new > at + timedelta(days=MAX_DAYS_AHEAD):
        return None, "far"
    return new, None


def request_move(uid, orig_iso, new_iso):
    """Ученик просит перенести урок. Решает Лазиза; пока она не ответила, урок остаётся на прежнем месте."""
    at = now()
    new, err = _check_new(new_iso, at)
    if err:
        return {"err": err}
    try:
        orig = parse(orig_iso)
    except ValueError:
        return {"err": "bad"}
    if orig <= at:
        return {"err": "past"}
    if new_iso == orig_iso:
        return {"err": "same"}
    if not _has_lesson(uid, orig_iso) or db.lesson_cancelled(uid, orig_iso):
        return {"err": "nolesson"}
    if any(m["orig"] == orig_iso for m in db.moves_pending(uid)):
        return {"err": "dup"}
    late = is_late(orig_iso, at)
    mid = db.move_add(uid, orig_iso, new_iso)
    db.log_add(uid, orig_iso, "move", None, None, "student", late, "pending", 0, None, mid)
    clash = clash_name(uid, new)
    text = (f"🔄 <b>{_name(uid)}</b> просит перенести урок (по просьбе ученика)\n{orig.strftime('%d.%m %H:%M')} → "
            f"<b>{new.strftime('%d.%m %H:%M')}</b> ({WEEKDAYS['ru'][new.weekday()]})")
    if late:
        text += f"\n⚠️ Запрос пришёл меньше чем за {LATE_HOURS} ч до урока: решаешь ты."
    if clash:
        text += f"\n⚠️ В это время уже урок с {esc(clash)}"
    _owner(text, reply_markup=_btns([[("✅ Подтвердить", f"mvy:{mid}"), ("✖️ Отказать", f"mvn:{mid}")],
                                     [("🕐 Другое время", f"mvo:{mid}")]]))
    return {"ok": True, "id": mid, "late": late}


def move_decide(mid, ok):
    """Лазиза принимает или отклоняет запрос ученика. -> запись переноса или None, если уже обработан."""
    m = db.move_get(mid)
    if not m or m["status"] != "pending":
        return None
    db.move_set(mid, "ok" if ok else "no")
    lg = db.log_by_ref("move", mid)
    if lg:
        db.log_set(lg["id"], status="ok" if ok else "no")
    uid = m["user_id"]
    lang = _lang(uid)
    new = parse(m["new"])
    _tell(uid, "mv_ok" if ok else "mv_no", when=when_label(new, lang))
    return m


def teacher_move(uid, orig_iso, new_iso, who="teacher", replace_mid=None, allow_clash=False):
    """Лазиза переносит урок: действует сразу, ученику уведомление. who: 'student' (по просьбе ученика) или 'teacher' (по её инициативе)."""
    who = "student" if who == "student" else "teacher"
    at = now()
    new, err = _check_new(new_iso, at)
    if err:
        return {"err": err}
    try:
        orig = parse(orig_iso)
    except ValueError:
        return {"err": "bad"}
    if new_iso == orig_iso:
        return {"err": "same"}
    if not _has_lesson(uid, orig_iso) or db.lesson_cancelled(uid, orig_iso):
        return {"err": "nolesson"}
    if db.log_find(uid, orig_iso, "held"):
        return {"err": "held"}
    clash = clash_name(uid, new)
    if clash and not allow_clash:
        return {"err": "clash", "clash": clash}
    if replace_mid:                                             # вместо запроса ученика предложено другое время
        old = db.move_get(replace_mid)
        if old and old["status"] == "pending":
            db.move_set(replace_mid, "no")
            lg = db.log_by_ref("move", replace_mid)
            if lg:
                db.log_set(lg["id"], status="replaced")
    for p in db.moves_pending(uid):                             # прежние запросы на это же занятие закрываем
        if p["orig"] == orig_iso:
            db.move_set(p["id"], "no")
            lg = db.log_by_ref("move", p["id"])
            if lg:
                db.log_set(lg["id"], status="replaced")
    mid = db.move_add(uid, orig_iso, new_iso)
    db.move_set(mid, "ok")
    db.log_add(uid, orig_iso, "move", None, None, who, is_late(orig_iso, at), "ok", 0, None, mid)
    lang = _lang(uid)
    _tell(uid, "mvt_notice", old=when_label(orig, lang), new=when_label(new, lang),
          by=t(lang, "mvby_student" if who == "student" else "mvby_teacher"))
    return {"ok": True, "id": mid, "clash": clash}


# ─── проведённые уроки и оплаты ──────────────────────────────────────────────

def mark_held(uid, iso, topic=""):
    """Лазиза отмечает урок проведённым (галочка)."""
    try:
        dt = parse(iso)
    except ValueError:
        return {"err": "bad"}
    if dt > now() + timedelta(hours=1):
        return {"err": "future"}
    if db.log_find(uid, iso, "cancel"):
        return {"err": "cancelled"}
    if db.log_find(uid, iso, "held"):
        return {"err": "dup"}
    if not _has_lesson(uid, iso):
        return {"err": "nolesson"}
    topic = (topic or "").strip()[:120] or None
    lid = db.lesson_row_add(uid, topic, iso[:10])
    db.log_add(uid, iso, "held", None, topic, "teacher", 0, "ok", 0, lid)
    _alert(uid)
    if ctx.get("after_held"):
        try:
            ctx["after_held"](uid)
        except Exception:
            logging.exception("после урока")
    return {"ok": True}


def add_payment(uid, n):
    try:
        n = int(n)
    except (TypeError, ValueError):
        return {"err": "bad"}
    if n == 0 or abs(n) > 200:
        return {"err": "bad"}
    db.add_payment(uid, n)
    return {"ok": True}


def _alert(uid):
    f = ctx.get("balance_alert")
    if f:
        try:
            f(uid)
        except Exception:
            logging.exception("напоминание про остаток уроков")
