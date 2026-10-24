"""
Запись на занятия к преподавателям (версия 12).

Ученик: меню «Записаться на занятия» → выбор преподавателя → пост преподавателя (фото, о себе, цены)
→ свободные часы → подтверждение → сообщение со ссылкой на занятие → напоминание со ссылкой за 3 часа.

Преподаватель (и владелица бота): /myteacher — свой профиль, часы, ссылка, записи.
Владелица: /teachers — список преподавателей, добавление и удаление.

Всё время — по Ташкенту (db.TZ). Тексты для учеников — в texts_v12.py, для преподавателей — здесь, по-русски.
"""
import html
import logging
import re
from datetime import datetime, timedelta, time as dtime

from telebot import types

import db
import scheduler
from texts import t, WEEKDAYS

FMT = "%Y-%m-%dT%H:%M"
LEAD_MIN = 120                      # ближе чем за 2 часа до начала записаться нельзя
DAYS_AHEAD = 14
MAX_ACTIVE = 3                      # активных записей у одного ученика
REMIND_BEFORE = timedelta(hours=3)

esc = lambda s: html.escape(str(s), quote=False)
ctx = {}                            # bot, owner_id, lang_of, notify_owner, ask_trial, labels
hooks = {}                          # подключает tutors.py: on_book, editor_rows, editor_lines, can_publish, gate
S = {}                              # диалоги редактирования: {user_id: {"tid": .., "field": ..}}

FIELDS = {
    "name":     ("Имя", 50, "Как тебя будут видеть ученики. Например: Анна Ли."),
    "tagline":  ("Кратко", 70, "Одна короткая строка под именем. Например: «Китайский для детей и взрослых». Чтобы убрать, пришли «-»."),
    "bio":      ("Описание", 550, "Расскажи о себе и занятиях: образование и опыт, кого и чему учишь, как проходят уроки. До 550 символов."),
    "prices":   ("Цены", 1000, "Цены и условия. Например: «Урок 60 минут: 150 000 сум. Пробный: 50 000 сум. Абонемент на 8 уроков: −10%». До 1000 символов."),
    "photo":    ("Фото", 0, "Пришли фото (как обычное фото, не файлом). Оно будет в посте."),
    "contact":  ("Связь", 40, "Твой username в Telegram, например @teacher. Ученики увидят кнопку «Написать в Telegram». Чтобы скрыть связь, пришли «-»."),
    "link":     ("Ссылка", 300, "Ссылка на занятие (Zoom, Google Meet, Telegram-звонок и т. п.). Она придёт ученику в подтверждении и в напоминании за 3 часа. Чтобы убрать, пришли «-»."),
    "hours":    ("Часы", 500, "Пришли свои свободные часы на неделю по времени Ташкента (UTC+5). Каждое время — начало урока.\n"
                              "Пример: пн 18:00, ср 18:00, сб 11:00\nЧтобы очистить, пришли «-»."),
    "duration": ("Длительность", 3, "Сколько минут идёт один урок? Пришли число от 20 до 180, например 60."),
}


# ─── БАЗА ─────────────────────────────────────────────────────────────────────

def init_db():
    with db._conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE,
            name TEXT, tagline TEXT, bio TEXT, prices TEXT, photo TEXT,
            contact TEXT, link TEXT, hours TEXT, duration INTEGER DEFAULT 60,
            active INTEGER DEFAULT 0, created TEXT
        );
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT, teacher_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
            start TEXT NOT NULL, duration INTEGER NOT NULL, status TEXT DEFAULT 'active',
            reminded INTEGER DEFAULT 0, created TEXT
        );
        CREATE INDEX IF NOT EXISTS ix_bk_start ON bookings(status, start);
        """)
        cols = {r["name"] for r in c.execute("PRAGMA table_info(teachers)")}
        if "tier" not in cols:
            # версия 22: подписки репетиторов. Те, кто уже в списке, получают 30 дней высшего уровня, чтобы ничего не пропало внезапно
            for col, typ in (("tier", "INTEGER"), ("tier_until", "TEXT"), ("agreed_ver", "INTEGER"), ("agreed_at", "TEXT")):
                c.execute(f"ALTER TABLE teachers ADD COLUMN {col} {typ}")
            owner = ctx.get("owner_id")
            grace = (datetime.now(db.TZ).date() + timedelta(days=30)).isoformat()
            c.execute("UPDATE teachers SET tier=3, tier_until=? WHERE user_id IS NOT ?", (grace, owner))
            c.execute("UPDATE teachers SET tier=3 WHERE user_id IS ?", (owner,))


def _one(sql, args=()):
    with db._conn() as c:
        r = c.execute(sql, args).fetchone()
        return dict(r) if r else None


def _all(sql, args=()):
    with db._conn() as c:
        return [dict(r) for r in c.execute(sql, args).fetchall()]


def teacher(tid):
    return _one("SELECT * FROM teachers WHERE id=?", (tid,))


def teacher_of_user(uid):
    return _one("SELECT * FROM teachers WHERE user_id=?", (uid,))


def teachers(active_only=True):
    # в списке для учеников сначала репетиторы с высшим уровнем подписки, дальше по порядку добавления
    return _all("SELECT * FROM teachers" + (" WHERE active=1" if active_only else "")
                + " ORDER BY CASE WHEN COALESCE(tier,0)>=3 THEN 0 ELSE 1 END, id")


_COLS = {"name", "tagline", "bio", "prices", "photo", "contact", "link", "hours", "duration", "active",
         "tier", "tier_until", "agreed_ver", "agreed_at"}


def update(tid, **kw):
    kw = {k: v for k, v in kw.items() if k in _COLS}
    if not kw:
        return
    with db._conn() as c:
        c.execute(f"UPDATE teachers SET {', '.join(k + '=?' for k in kw)} WHERE id=?", (*kw.values(), tid))


def add_teacher(uid, name, username=None):
    with db._conn() as c:
        c.execute("INSERT OR IGNORE INTO teachers (user_id, name, contact, created) VALUES (?,?,?,?)",
                  (uid, name, username or "", db.today()))
    return teacher_of_user(uid)


def delete_teacher(tid):
    with db._conn() as c:
        c.execute("DELETE FROM teachers WHERE id=?", (tid,))


def seed_owner():
    """Владелица бота — первый преподаватель. Профиль создаётся скрытым: ученики его не видят, пока она его не заполнит и не опубликует."""
    oid = ctx.get("owner_id")
    if not oid or teacher_of_user(oid):
        return
    tc = add_teacher(oid, "Лазиза")
    update(tc["id"], tier=3, tagline="Китайский язык",
           bio="Преподаватель китайского языка. Автор бота 汉助 и игры «Путешествие по Китаю с 茶茶».")


def _parse(s):
    return datetime.strptime(s, FMT).replace(tzinfo=db.TZ)


def active_bookings(tid=None, uid=None, future_only=True):
    sql, args = "SELECT * FROM bookings WHERE status='active'", []
    if tid is not None:
        sql += " AND teacher_id=?"; args.append(tid)
    if uid is not None:
        sql += " AND user_id=?"; args.append(uid)
    rows = _all(sql + " ORDER BY start", args)
    if future_only:
        now = datetime.now(db.TZ)
        rows = [b for b in rows if _parse(b["start"]) + timedelta(minutes=b["duration"]) > now]
    return rows


# ─── СВОБОДНЫЕ ЧАСЫ ───────────────────────────────────────────────────────────

def free_slots(tid, now=None):
    """Свободные начала уроков на ближайшие две недели: недельное расписание преподавателя
    минус уже сделанные записи и (для владелицы) её постоянные ученики."""
    now = now or datetime.now(db.TZ)
    tc = teacher(tid)
    if not tc or not (tc["hours"] or "").strip():
        return []
    try:
        tpl = scheduler.parse_schedule(tc["hours"])
    except ValueError:
        return []
    dur = tc["duration"] or 60
    taken = [(_parse(b["start"]), b["duration"]) for b in active_bookings(tid=tid, future_only=False)]
    regular = []
    if ctx.get("owner_id") and tc["user_id"] == ctx["owner_id"]:
        try:
            regular = [lesson for lesson, _ in scheduler.occurrences(now, db.all_schedules(), db.moves_ok(), days=DAYS_AHEAD + 1)]
        except Exception:
            logging.exception("не удалось учесть постоянные уроки")
    out = []
    for off in range(DAYS_AHEAD + 1):
        day = now.date() + timedelta(days=off)
        for wd, tm in tpl:
            if day.weekday() != wd:
                continue
            h, mi = map(int, tm.split(":"))
            dt = datetime.combine(day, dtime(h, mi), tzinfo=db.TZ)
            if dt < now + timedelta(minutes=LEAD_MIN):
                continue
            if any(abs((dt - s).total_seconds()) / 60 < max(dur, d) for s, d in taken):
                continue
            if any(abs((dt - r).total_seconds()) / 60 < max(dur, 60) for r in regular):
                continue
            out.append(dt)
    return sorted(set(out))


def book(tid, uid, dt):
    """('ok', id) | ('taken', None) | ('limit', None) | ('gone', None)."""
    tc = teacher(tid)
    if not tc or not tc["active"]:
        return "gone", None
    with db._conn() as c:
        c.execute("BEGIN IMMEDIATE")
        if dt not in free_slots(tid):
            return "taken", None
        n = c.execute("SELECT COUNT(*) FROM bookings WHERE user_id=? AND status='active' AND start>=?",
                      (uid, (datetime.now(db.TZ) - timedelta(hours=3)).strftime(FMT))).fetchone()[0]
        if n >= MAX_ACTIVE:
            return "limit", None
        now = datetime.now(db.TZ)
        cur = c.execute("INSERT INTO bookings (teacher_id, user_id, start, duration, reminded, created) VALUES (?,?,?,?,?,?)",
                        (tid, uid, dt.strftime(FMT), tc["duration"] or 60,
                         1 if dt - now < REMIND_BEFORE else 0, now.strftime(FMT)))
        return "ok", cur.lastrowid


def cancel(bid):
    with db._conn() as c:
        c.execute("UPDATE bookings SET status='cancelled' WHERE id=?", (bid,))


# ─── ОБЩЕЕ ────────────────────────────────────────────────────────────────────

def ikb(rows):
    k = types.InlineKeyboardMarkup()
    for row in rows:
        k.row(*[types.InlineKeyboardButton(a, url=b[4:]) if b.startswith("url:") else types.InlineKeyboardButton(a, callback_data=b)
                for a, b in row])
    return k


def day_label(dt, lang):
    return f"{WEEKDAYS[lang][dt.weekday()]} {dt:%d.%m}"


def lang_of(uid):
    return ctx["lang_of"](uid)


def put(uid, mid, text, kb=None, photo=None):
    """Новое сообщение вместо старого (фото нельзя превратить в текст редактированием)."""
    bot = ctx["bot"]
    if mid:
        try:
            bot.delete_message(uid, mid)
        except Exception:
            pass
    if photo:
        try:
            if len(text) <= 1024:
                return bot.send_photo(uid, photo, caption=text, reply_markup=kb)
            bot.send_photo(uid, photo)
        except Exception as e:
            logging.warning("фото преподавателя не отправилось: %s", e)
    return bot.send_message(uid, text, reply_markup=kb, disable_web_page_preview=True)


def show(c, text, kb=None, photo=None):
    uid, mid = c.from_user.id, c.message.message_id
    if not photo and getattr(c.message, "content_type", "text") == "text":
        try:
            return ctx["bot"].edit_message_text(text, uid, mid, reply_markup=kb, disable_web_page_preview=True)
        except Exception:
            pass
    return put(uid, mid, text, kb, photo)


def contact_username(tc):
    m = re.search(r"([A-Za-z][A-Za-z0-9_]{4,31})\s*$", (tc.get("contact") or "").strip())
    return m.group(1) if m else ""


# ─── УЧЕНИК ───────────────────────────────────────────────────────────────────

def start(uid, c=None):
    """Кнопка меню «Записаться на занятия»."""
    lang = lang_of(uid)
    ts = teachers()
    if not ts:
        text, kb = t(lang, "bk_none"), ikb([[(t(lang, "bk_trial_btn"), "bk:trial")]])
        return show(c, text, kb) if c else ctx["bot"].send_message(uid, text, reply_markup=kb)
    if len(ts) == 1 and not active_bookings(uid=uid):
        return post(uid, ts[0]["id"], c, single=True)
    rows = []
    for x in ts:
        label = ("⭐ " if (x.get("tier") or 0) >= 3 and x.get("user_id") != ctx.get("owner_id") else "") \
            + x["name"] + (f" · {x['tagline']}" if x.get("tagline") else "")
        rows.append([(label[:60], f"bk:t:{x['id']}")])
    my = active_bookings(uid=uid)
    if my:
        rows.append([(t(lang, "bk_my_btn", n=len(my)), "bk:my")])
    text = t(lang, "bk_list")
    if c:
        return show(c, text, ikb(rows))
    ctx["bot"].send_message(uid, text, reply_markup=ikb(rows))


def post(uid, tid, c=None, single=False):
    lang = lang_of(uid)
    tc = teacher(tid)
    if not tc or not tc["active"]:
        return start(uid, c)
    parts = [f"<b>{esc(tc['name'])}</b>"]
    if tc.get("tagline"):
        parts.append(f"<i>{esc(tc['tagline'])}</i>")
    if tc.get("bio"):
        parts += ["", esc(tc["bio"])]
    if tc.get("prices"):
        parts += ["", f"💰 <b>{t(lang, 'bk_prices_h')}</b>", esc(tc["prices"])]
    parts += ["", f"⏱ {tc['duration'] or 60} {t(lang, 'bk_min')}"]
    if hooks.get("post_line"):
        try:
            line = hooks["post_line"](lang, tc)
            if line:
                parts.append(line)
        except Exception:
            logging.exception("строка с рейтингом не собралась")
    k = types.InlineKeyboardMarkup()
    k.row(types.InlineKeyboardButton(t(lang, "bk_b_hours"), callback_data=f"bk:d:{tid}"))
    if hooks.get("post_rows"):
        for label, cb in hooks["post_rows"](lang, tc):
            k.row(types.InlineKeyboardButton(label, callback_data=cb))
    un = contact_username(tc)
    if un:
        k.row(types.InlineKeyboardButton(t(lang, "bk_b_contact"), url=f"https://t.me/{un}"))
    if not single:
        k.row(types.InlineKeyboardButton(t(lang, "bk_b_back"), callback_data="bk:l"))
    text = "\n".join(parts)
    if c:
        return show(c, text, k, tc.get("photo"))
    return put(uid, None, text, k, tc.get("photo"))


def pick_day(c, tid):
    uid = c.from_user.id
    lang = lang_of(uid)
    tc = teacher(tid)
    if not tc or not tc["active"]:
        return start(uid, c)
    days = {}
    for dt in free_slots(tid):
        days.setdefault(dt.date(), []).append(dt)
    k = types.InlineKeyboardMarkup(row_width=3)
    if not days:
        text = t(lang, "bk_no_free", name=esc(tc["name"]))
    else:
        text = t(lang, "bk_pick_day", name=esc(tc["name"]))
        k.add(*[types.InlineKeyboardButton(day_label(v[0], lang), callback_data=f"bk:s:{tid}:{d:%Y%m%d}")
                for d, v in days.items()])
    un = contact_username(tc)
    if un and not days:
        k.row(types.InlineKeyboardButton(t(lang, "bk_b_contact"), url=f"https://t.me/{un}"))
    k.row(types.InlineKeyboardButton(t(lang, "bk_btn_back"), callback_data=f"bk:t:{tid}"))
    show(c, text, k)


def pick_time(c, tid, ymd):
    uid = c.from_user.id
    lang = lang_of(uid)
    tc = teacher(tid)
    if not tc:
        return start(uid, c)
    times = [dt for dt in free_slots(tid) if dt.strftime("%Y%m%d") == ymd]
    if not times:
        return pick_day(c, tid)
    k = types.InlineKeyboardMarkup(row_width=4)
    k.add(*[types.InlineKeyboardButton(dt.strftime("%H:%M"), callback_data=f"bk:c:{tid}:{dt:%Y%m%d%H%M}") for dt in times])
    k.row(types.InlineKeyboardButton(t(lang, "bk_btn_back"), callback_data=f"bk:d:{tid}"))
    show(c, t(lang, "bk_pick_time", day=day_label(times[0], lang)), k)


def _dt(s):
    return datetime.strptime(s, "%Y%m%d%H%M").replace(tzinfo=db.TZ)


def confirm(c, tid, stamp):
    uid = c.from_user.id
    lang = lang_of(uid)
    tc = teacher(tid)
    dt = _dt(stamp)
    if not tc or dt not in free_slots(tid):
        bot_answer(c, t(lang, "bk_taken"))
        return pick_day(c, tid)
    k = ikb([[(t(lang, "bk_btn_yes"), f"bk:ok:{tid}:{stamp}")], [(t(lang, "bk_btn_back"), f"bk:s:{tid}:{stamp[:8]}")]])
    show(c, t(lang, "bk_confirm", name=esc(tc["name"]), day=day_label(dt, lang), time=dt.strftime("%H:%M"),
              dur=tc["duration"] or 60, min=t(lang, "bk_min")), k)


def bot_answer(c, text=None, alert=False):
    try:
        ctx["bot"].answer_callback_query(c.id, text, show_alert=alert)
    except Exception:
        pass


def link_block(lang, tc, key_with, key_without):
    link = (tc.get("link") or "").strip()
    return t(lang, key_with, link=esc(link)) if link else t(lang, key_without)


def do_book(c, tid, stamp):
    uid = c.from_user.id
    lang = lang_of(uid)
    dt = _dt(stamp)
    status, bid = book(tid, uid, dt)
    if status == "limit":
        bot_answer(c, t(lang, "bk_limit"), True)
        return start(uid, c)
    if status != "ok":
        bot_answer(c, t(lang, "bk_taken"), True)
        return pick_day(c, tid)
    bot_answer(c)
    tc = teacher(tid)
    text = t(lang, "bk_done", name=esc(tc["name"]), day=day_label(dt, lang), time=dt.strftime("%H:%M"),
             dur=tc["duration"] or 60, min=t(lang, "bk_min"),
             link=link_block(lang, tc, "bk_link", "bk_nolink"))
    put(uid, c.message.message_id, text, ikb([[(t(lang, "bk_cancel_btn"), f"bk:x:{bid}")]]))
    u = db.get_user(uid) or {}
    who = f"{esc(u.get('name') or '?')}" + (f" (@{esc(u['username'])})" if u.get("username") else "")
    note = f"📅 <b>Новая запись</b>\n\n{who} → {esc(tc['name'])}\n🕒 {day_label(dt, 'ru')}, {dt:%H:%M} (Ташкент) · {tc['duration'] or 60} мин"
    if not (tc.get("link") or "").strip():
        note += "\n\n⚠️ У преподавателя не задана ссылка на занятие: пришли её ученику сама. Задать ссылку можно в /myteacher."
    notify_teacher(tc, note)
    if hooks.get("on_book"):
        try:
            hooks["on_book"](tid, uid)
        except Exception:
            logging.exception("не удалось связать ученика с репетитором")


def notify_teacher(tc, text):
    bot = ctx["bot"]
    seen = set()
    for to in (tc.get("user_id"), ctx.get("owner_id")):
        if to and to not in seen:
            seen.add(to)
            try:
                bot.send_message(to, text)
            except Exception as e:
                logging.warning("уведомление преподавателю %s не ушло: %s", to, e)


def my_bookings(uid, c=None):
    lang = lang_of(uid)
    rows = active_bookings(uid=uid)
    k = types.InlineKeyboardMarkup()
    if not rows:
        text = t(lang, "bk_my_none")
    else:
        lines = [t(lang, "bk_my_head"), ""]
        for b in rows:
            tc = teacher(b["teacher_id"]) or {"name": "?"}
            dt = _parse(b["start"])
            lines.append(f"📅 {day_label(dt, lang)}, {dt:%H:%M} · {esc(tc['name'])}")
            k.row(types.InlineKeyboardButton(f"❌ {day_label(dt, lang)} {dt:%H:%M}", callback_data=f"bk:x:{b['id']}"),
                  types.InlineKeyboardButton(t(lang, "mv2_btn"), callback_data=f"tq:mv:{b['id']}"))
        text = "\n".join(lines)
    k.row(types.InlineKeyboardButton(t(lang, "bk_b_back"), callback_data="bk:l"))
    show(c, text, k) if c else ctx["bot"].send_message(uid, text, reply_markup=k)


def cancel_ask(c, bid):
    uid = c.from_user.id
    lang = lang_of(uid)
    b = _one("SELECT * FROM bookings WHERE id=? AND user_id=? AND status='active'", (bid, uid))
    if not b:
        return my_bookings(uid, c)
    tc = teacher(b["teacher_id"]) or {"name": "?"}
    dt = _parse(b["start"])
    show(c, t(lang, "bk_cancel_ask", name=esc(tc["name"]), day=day_label(dt, lang), time=dt.strftime("%H:%M")),
         ikb([[(t(lang, "bk_cancel_yes"), f"bk:xx:{bid}")], [(t(lang, "bk_btn_back"), "bk:my")]]))


def cancel_do(c, bid):
    uid = c.from_user.id
    lang = lang_of(uid)
    b = _one("SELECT * FROM bookings WHERE id=? AND user_id=? AND status='active'", (bid, uid))
    if b:
        cancel(bid)
        tc = teacher(b["teacher_id"]) or {}
        dt = _parse(b["start"])
        u = db.get_user(uid) or {}
        who = f"{esc(u.get('name') or '?')}" + (f" (@{esc(u['username'])})" if u.get("username") else "")
        if tc:
            notify_teacher(tc, f"❌ <b>Запись отменена учеником</b>\n\n{who}\n🕒 {day_label(dt, 'ru')}, {dt:%H:%M} (Ташкент)\nЭто время снова свободно.")
    bot_answer(c)
    show(c, t(lang, "bk_cancelled"), ikb([[(t(lang, "bk_b_again"), "bk:l")]]))


# ─── НАПОМИНАНИЕ ЗА 3 ЧАСА ────────────────────────────────────────────────────

def hook(now):
    """Вызывается планировщиком раз в минуту."""
    for b in _all("SELECT * FROM bookings WHERE status='active' AND reminded=0"):
        st = _parse(b["start"])
        if now >= st - REMIND_BEFORE:
            with db._conn() as c:
                c.execute("UPDATE bookings SET reminded=1 WHERE id=?", (b["id"],))   # сперва отмечаем: не слать дважды
            if now >= st:
                continue
            tc = teacher(b["teacher_id"])
            if not tc:
                continue
            lang = lang_of(b["user_id"])
            try:
                ctx["bot"].send_message(
                    b["user_id"],
                    t(lang, "bk_remind", name=esc(tc["name"]), day=day_label(st, lang), time=st.strftime("%H:%M"),
                      link=link_block(lang, tc, "bk_link", "bk_nolink")),
                    disable_web_page_preview=True)
            except Exception as e:
                logging.warning("напоминание о записи %s не ушло: %s", b["id"], e)
            u = db.get_user(b["user_id"]) or {}
            try:
                if tc.get("user_id"):
                    ctx["bot"].send_message(tc["user_id"], f"⏰ Через 3 часа занятие: {esc(u.get('name') or '?')}"
                                            + (f" (@{esc(u['username'])})" if u.get("username") else "")
                                            + f", {st:%H:%M} (Ташкент).")
            except Exception:
                pass


# ─── ПРЕПОДАВАТЕЛЬ: ПРОФИЛЬ ───────────────────────────────────────────────────

def can_edit(uid, tc):
    return bool(tc) and (uid == ctx.get("owner_id") or tc.get("user_id") == uid)


def _ok(v):
    return "✅" if v else "▫️"


def editor(uid, tid, mid=None):
    tc = teacher(tid)
    if not can_edit(uid, tc):
        return
    nb = len(active_bookings(tid=tid))
    lines = [f"👩‍🏫 <b>Профиль преподавателя</b>", "",
             f"Статус: {'🟢 виден ученикам' if tc['active'] else '⚪️ скрыт, ученики его не видят'}", "",
             f"{_ok(tc['name'])} Имя: {esc(tc['name'] or '—')}",
             f"{_ok(tc['tagline'])} Кратко: {esc(tc['tagline'] or '—')}",
             f"{_ok(tc['bio'])} Описание: {len(tc['bio'] or '')} симв.",
             f"{_ok(tc['prices'])} Цены: {esc(tc['prices'] or '—')}",
             f"{_ok(tc['photo'])} Фото: {'есть' if tc['photo'] else 'нет'}",
             f"{_ok(contact_username(tc))} Связь: {('@' + contact_username(tc) + ' (кнопка «Написать в Telegram» видна ученикам)') if contact_username(tc) else 'скрыта: ученики не видят твой Telegram'}",
             f"{_ok(tc['link'])} Ссылка на занятие: {'есть' if tc['link'] else 'нет'}",
             f"{_ok(tc['hours'])} Свободные часы: {esc(tc['hours'] or 'не заданы')}",
             f"⏱ Урок: {tc['duration'] or 60} мин", "",
             f"📋 Записей впереди: {nb}"]
    if hooks.get("editor_lines"):
        lines += hooks["editor_lines"](uid, tc)
    rows = [[("Имя", f"bt:f:{tid}:name"), ("Кратко", f"bt:f:{tid}:tagline")],
            [("Описание", f"bt:f:{tid}:bio"), ("Цены", f"bt:f:{tid}:prices")],
            [("Фото", f"bt:f:{tid}:photo"), ("Связь", f"bt:f:{tid}:contact")],
            [("Ссылка на занятие", f"bt:f:{tid}:link")],
            [("Свободные часы", f"bt:f:{tid}:hours"), ("Длительность", f"bt:f:{tid}:duration")],
            [("👁 Как видят ученики", f"bt:pv:{tid}"), (f"📋 Записи ({nb})", f"bt:bk:{tid}")],
            [("⚪️ Скрыть от учеников" if tc["active"] else "🟢 Опубликовать", f"bt:pub:{tid}")]]
    if hooks.get("editor_rows"):
        rows += hooks["editor_rows"](uid, tc)
    if uid == ctx.get("owner_id"):
        rows.append([("⬅️ К списку", "bt:list")] + ([("🗑 Удалить", f"bt:del:{tid}")] if tc["user_id"] != uid else []))
    put(uid, mid, "\n".join(lines), ikb(rows))


def teachers_list(uid, mid=None):
    ts = teachers(active_only=False)
    rows = [[(("🟢 " if x["active"] else "⚪️ ") + (x["name"] or "?"), f"bt:e:{x['id']}")] for x in ts]
    rows.append([("➕ Добавить преподавателя", "bt:add")])
    put(uid, mid, "👩‍🏫 <b>Преподаватели</b>\n\n🟢 виден ученикам · ⚪️ скрыт\n\nНажми на преподавателя, чтобы открыть его профиль.", ikb(rows))


def bookings_view(uid, tid, mid=None):
    tc = teacher(tid)
    if not can_edit(uid, tc):
        return
    rows, lines = [], [f"📋 <b>Записи: {esc(tc['name'])}</b>", ""]
    bs = active_bookings(tid=tid)
    if not bs:
        lines.append("Пока записей нет.")
    for b in bs:
        dt = _parse(b["start"])
        u = db.get_user(b["user_id"]) or {}
        lines.append(f"📅 {day_label(dt, 'ru')}, {dt:%H:%M} · {esc(u.get('name') or '?')}" + (f" (@{esc(u['username'])})" if u.get("username") else ""))
        rows.append([(f"❌ Отменить {day_label(dt, 'ru')} {dt:%H:%M}", f"bt:xc:{b['id']}")])
    rows.append([("⬅️ К профилю", f"bt:e:{tid}")])
    put(uid, mid, "\n".join(lines), ikb(rows))


def ask_field(uid, tid, field, mid=None):
    label, _, hint = FIELDS[field]
    S[uid] = {"tid": tid, "field": field}
    put(uid, mid, f"✏️ <b>{label}</b>\n\n{hint}", ikb([[("Отмена", f"bt:e:{tid}")]]))


def _saved(uid, tid, what="Сохранено"):
    S.pop(uid, None)
    ctx["bot"].send_message(uid, f"✅ {what}")
    editor(uid, tid)


def on_text(m):
    """Ответ в диалоге редактирования профиля. True — сообщение обработано здесь."""
    uid = m.from_user.id
    st = S.get(uid)
    if not st:
        return False
    txt = (m.text or "").strip()
    if txt.startswith("/") or txt in ctx["labels"](lang_of(uid)):
        S.pop(uid, None)
        return False
    bot = ctx["bot"]
    field, tid = st["field"], st.get("tid")

    if field == "add":
        if uid != ctx.get("owner_id"):
            S.pop(uid, None)
            return True
        un = txt.lstrip("@").strip().lower()
        u = _one("SELECT user_id, name, username FROM users WHERE lower(username)=?", (un,)) if un else None
        if not u:
            bot.send_message(uid, "Не нашла такого человека в боте. Пусть он сначала откроет бота и нажмёт /start, "
                                  "а потом пришли его @username ещё раз.")
            return True
        if teacher_of_user(u["user_id"]):
            S.pop(uid, None)
            bot.send_message(uid, "Этот человек уже в списке преподавателей.")
            teachers_list(uid)
            return True
        tc = add_teacher(u["user_id"], u["name"] or u["username"])
        S.pop(uid, None)
        bot.send_message(uid, f"✅ {esc(tc['name'])} добавлен(а). Профиль пока скрыт: пусть заполнит его в /myteacher, "
                              f"или заполни сама через список. Опубликовать можно кнопкой в профиле.")
        try:
            bot.send_message(u["user_id"], "👩‍🏫 Тебя добавили преподавателем в боте 汉助. Открой /myteacher: "
                                           "там имя, описание, фото, цены, свободные часы и ссылка на занятие. "
                                           "Когда всё заполнишь, нажми «Опубликовать».")
            bot.set_my_commands([types.BotCommand("myteacher", "мой профиль преподавателя"), types.BotCommand("menu", "меню")],
                                scope=types.BotCommandScopeChat(u["user_id"]))
        except Exception as e:
            logging.warning("не удалось написать новому преподавателю: %s", e)
        editor(uid, tc["id"])
        return True

    tc = teacher(tid)
    if not can_edit(uid, tc):
        S.pop(uid, None)
        return True
    if field == "photo":
        bot.send_message(uid, "Пришли, пожалуйста, именно фото (не файлом) или нажми «Отмена».")
        return True
    label, limit, _ = FIELDS[field]
    if field in ("name", "bio") and txt == "-":
        bot.send_message(uid, "Это поле нельзя оставить пустым.")
        return True
    if field in ("tagline", "prices", "contact", "link", "hours") and txt == "-":
        update(tid, **{field: ""})
        return _saved(uid, tid, "Убрано") or True
    if field == "duration":
        if not txt.isdigit() or not 20 <= int(txt) <= 180:
            bot.send_message(uid, "Нужно число минут от 20 до 180, например 60.")
            return True
        update(tid, duration=int(txt))
        return _saved(uid, tid) or True
    if len(txt) > limit:
        bot.send_message(uid, f"Слишком длинно: {len(txt)} символов, можно до {limit}. Сократи и пришли ещё раз.")
        return True
    if field == "contact":
        mm = re.fullmatch(r"(?:https?://)?(?:t\.me/|@)?([A-Za-z][A-Za-z0-9_]{4,31})", txt)
        if not mm:
            bot.send_message(uid, "Не похоже на username. Пришли в виде @name или «-», чтобы скрыть связь.")
            return True
        txt = "@" + mm.group(1)
    if field == "link" and not txt.lower().startswith("http"):
        bot.send_message(uid, "Ссылка должна начинаться с http. Или пришли «-», чтобы убрать.")
        return True
    if field == "hours":
        try:
            slots = scheduler.parse_schedule(txt)
        except ValueError:
            bot.send_message(uid, "Не поняла формат. Пример: пн 18:00, ср 18:00, сб 11:00 (день недели и время начала).")
            return True
        txt = ", ".join(f"{WEEKDAYS['ru'][wd]} {tm}" for wd, tm in slots)
    update(tid, **{field: txt})
    _saved(uid, tid)
    return True


def on_photo(m):
    """Фото в диалоге «Фото преподавателя». True — обработано."""
    uid = m.from_user.id
    st = S.get(uid)
    if not st or st.get("field") != "photo":
        return False
    tc = teacher(st.get("tid"))
    if not can_edit(uid, tc):
        S.pop(uid, None)
        return True
    if m.content_type != "photo":
        ctx["bot"].send_message(uid, "Пришли, пожалуйста, именно фото (не файлом) или нажми «Отмена».")
        return True
    update(tc["id"], photo=m.photo[-1].file_id)
    _saved(uid, tc["id"])
    return True


def admin_callback(c):
    uid = c.from_user.id
    bot = ctx["bot"]
    parts = c.data.split(":")
    act = parts[1]
    mid = c.message.message_id
    bot_answer(c)
    S.pop(uid, None)
    is_owner = uid == ctx.get("owner_id")

    if act == "list":
        return teachers_list(uid, mid) if is_owner else None
    if act == "add":
        if not is_owner:
            return
        S[uid] = {"field": "add"}
        return put(uid, mid, "➕ Пришли @username преподавателя в Telegram. Он должен уже открыть бота и нажать /start.",
                   ikb([[("Отмена", "bt:list")]]))
    if act == "xc":                                     # отмена записи преподавателем
        b = _one("SELECT * FROM bookings WHERE id=? AND status='active'", (int(parts[2]),))
        tc = teacher(b["teacher_id"]) if b else None
        if not (b and can_edit(uid, tc)):
            return
        cancel(b["id"])
        dt = _parse(b["start"])
        lang = lang_of(b["user_id"])
        try:
            bot.send_message(b["user_id"], t(lang, "bk_cancelled_by_teacher", name=esc(tc["name"]), day=day_label(dt, lang),
                                             time=dt.strftime("%H:%M")))
        except Exception:
            pass
        return bookings_view(uid, tc["id"], mid)

    tid = int(parts[2])
    tc = teacher(tid)
    if not can_edit(uid, tc):
        return
    if act == "e":
        return editor(uid, tid, mid)
    if act == "f":
        return ask_field(uid, tid, parts[3], mid)
    if act == "bk":
        return bookings_view(uid, tid, mid)
    if act == "pv":
        saved = tc["active"]
        update(tid, active=1)                       # предпросмотр показывает именно то, что увидят ученики
        try:
            post(uid, tid, None, single=True)
        finally:
            update(tid, active=saved)
        return bot.send_message(uid, "👆 Так видят пост ученики.", reply_markup=ikb([[("⬅️ К профилю", f"bt:e:{tid}")]]))
    if act == "pub":
        if not tc["active"]:
            missing = [n for n, v in (("описание", tc["bio"]), ("свободные часы", tc["hours"])) if not v]
            if missing:
                return bot.send_message(uid, "Чтобы опубликовать, заполни: " + ", ".join(missing) + ".")
            if hooks.get("can_publish"):
                ok_, why = hooks["can_publish"](tc)
                if not ok_:
                    return bot.send_message(uid, why, reply_markup=ikb(hooks["publish_rows"](tc)) if hooks.get("publish_rows") else None)
            update(tid, active=1)
            extra = "" if tc["link"] else "\n⚠️ Ссылка на занятие не задана: ученики получат запись без ссылки."
            bot.send_message(uid, "🟢 Профиль опубликован: ученики видят его в «Записаться на занятия»." + extra)
        else:
            update(tid, active=0)
            bot.send_message(uid, "⚪️ Профиль скрыт. Уже сделанные записи сохраняются.")
        return editor(uid, tid)
    if act == "del" and is_owner and tc["user_id"] != uid:
        if len(parts) > 3 and parts[3] == "yes":
            delete_teacher(tid)
            with db._conn() as cc:
                cc.execute("UPDATE bookings SET status='cancelled' WHERE teacher_id=? AND status='active'", (tid,))
            bot.send_message(uid, "🗑 Удалила. Будущие записи к этому преподавателю отменены.")
            return teachers_list(uid)
        return put(uid, mid, f"Удалить преподавателя {esc(tc['name'])}? Будущие записи к нему отменятся.",
                   ikb([[("Да, удалить", f"bt:del:{tid}:yes")], [("Отмена", f"bt:e:{tid}")]]))


def cb_bk(c):
    p = c.data.split(":")
    uid = c.from_user.id
    try:
        a = p[1]
        if a == "l":
            bot_answer(c); return start(uid, c)
        if a == "t":
            bot_answer(c); return post(uid, int(p[2]), c)
        if a == "d":
            bot_answer(c); return pick_day(c, int(p[2]))
        if a == "s":
            bot_answer(c); return pick_time(c, int(p[2]), p[3])
        if a == "c":
            bot_answer(c); return confirm(c, int(p[2]), p[3])
        if a == "ok":
            return do_book(c, int(p[2]), p[3])
        if a == "my":
            bot_answer(c); return my_bookings(uid, c)
        if a == "x":
            bot_answer(c); return cancel_ask(c, int(p[2]))
        if a == "xx":
            return cancel_do(c, int(p[2]))
        if a == "trial":
            bot_answer(c); return ctx["ask_trial"](uid)
        bot_answer(c)
    except Exception:
        logging.exception("запись на занятия: ошибка")
        bot_answer(c)


def cb_bt(c):
    try:
        admin_callback(c)
    except Exception:
        logging.exception("профиль преподавателя: ошибка")
        bot_answer(c)


# ─── ПОДКЛЮЧЕНИЕ К БОТУ ───────────────────────────────────────────────────────

def register(bot, owner_id, lang_of, notify_owner, ask_trial, labels):
    ctx.update(bot=bot, owner_id=owner_id, lang_of=lang_of, notify_owner=notify_owner, ask_trial=ask_trial, labels=labels)
    init_db()
    seed_owner()

    @bot.message_handler(commands=["book"])
    def _book(m):
        start(m.from_user.id)

    @bot.message_handler(commands=["myteacher"])
    def _my(m):
        uid = m.from_user.id
        tc = teacher_of_user(uid)
        if not tc:
            if hooks.get("no_profile"):
                return hooks["no_profile"](uid)
            return bot.send_message(uid, "Профиль преподавателя пока не создан. Попроси Лазизу добавить тебя.")
        if hooks.get("gate") and hooks["gate"](uid, tc):      # соглашение репетитора ещё не принято: сначала оно
            return
        editor(uid, tc["id"])

    @bot.message_handler(commands=["teachers"])
    def _ts(m):
        if m.from_user.id == owner_id:
            teachers_list(m.from_user.id)

    bot.callback_query_handler(func=lambda c: c.data.startswith("bk:"))(cb_bk)
    bot.callback_query_handler(func=lambda c: c.data.startswith("bt:"))(cb_bt)
