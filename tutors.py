"""
Репетиторы в боте (версия 22).

Что здесь:
  · три уровня подписки (Старт / Стандарт / Про), которые выдаёт и продлевает Лазиза;
  · соглашение репетитора: принимается кнопкой, версия и дата сохраняются;
  · домашние задания репетитора для его учеников (ученик сдаёт их репетитору, а не Лазизе);
  · записи уроков: репетитор отправляет запись ученику или группе, Telegram не даёт её сохранить и переслать;
  · обсуждения о Китае для всех пользователей, темы не по теме не публикуются.

Тексты для репетиторов и Лазизы — по-русски (здесь), для учеников — в texts_v13.py на четырёх языках.
"""
import html
import json
import logging
import os
import re
import time
from datetime import datetime, timedelta

from telebot import types

import booking
import db
from agreement import AGREEMENT_TEXT, AGREEMENT_VERSION
from texts import t

esc = lambda s: html.escape(str(s), quote=False)
ctx = {}                              # bot, owner_id, lang_of, deliver_hw, hw_media_of, hw_default_text, parse_due, HW_MEDIA_MAX, labels
TS = {}                               # диалоги репетитора и Лазизы: {uid: {...}}
TD = {}                               # диалоги обсуждений: {uid: {...}}
LAST = {"topic": {}, "post": {}}      # защита от потока сообщений

TOPICS_ON = os.getenv("TOPICS_ON", "1") != "0"
TOPIC_TITLE_MAX, TOPIC_BODY_MAX, POST_MAX = 80, 600, 600
TOPIC_PAUSE, POST_PAUSE = 15 * 60, 10          # секунд между новыми темами / ответами одного человека
PAGE = 8

TIERS = {0: "Без подписки", 1: "Старт", 2: "Стандарт", 3: "Про"}
TIER_INFO = {
    1: "Профиль в разделе «Записаться на занятия», запись учеников и напоминания за 3 часа, домашние задания текстом.",
    2: "Всё из «Старта», плюс домашние задания с фото, видео, аудио и файлами и записи уроков, которые ученик не может сохранить или переслать.",
    3: "Всё из «Стандарта», плюс профиль всегда закреплён в начале списка «Записаться на занятия» со звёздочкой ⭐.",
}
FEAT = {"hw_text": 1, "hw_media": 2, "records": 2}
REC_KINDS = ("video", "video_note", "audio", "voice", "document", "animation")


# ─── БАЗА ─────────────────────────────────────────────────────────────────────

def init_db():
    with db._conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS tutor_students (
            teacher_id INTEGER NOT NULL, user_id INTEGER NOT NULL, created TEXT,
            PRIMARY KEY (teacher_id, user_id)
        );
        CREATE TABLE IF NOT EXISTS t_inbox (
            chat_id INTEGER NOT NULL, msg_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
            PRIMARY KEY (chat_id, msg_id)
        );
        CREATE TABLE IF NOT EXISTS recordings (
            id INTEGER PRIMARY KEY AUTOINCREMENT, teacher_id INTEGER NOT NULL, kind TEXT NOT NULL,
            file_id TEXT NOT NULL, title TEXT, created TEXT
        );
        CREATE TABLE IF NOT EXISTS rec_access (
            rec_id INTEGER NOT NULL, user_id INTEGER NOT NULL, msg_id INTEGER, created TEXT,
            PRIMARY KEY (rec_id, user_id)
        );
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, title TEXT NOT NULL, body TEXT NOT NULL,
            created TEXT NOT NULL, updated TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open'
        );
        CREATE TABLE IF NOT EXISTS topic_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, topic_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
            text TEXT NOT NULL, created TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open'
        );
        CREATE INDEX IF NOT EXISTS ix_topics_upd ON topics(status, updated);
        CREATE INDEX IF NOT EXISTS ix_posts_topic ON topic_posts(topic_id, status);
        """)


def _one(sql, args=()):
    with db._conn() as c:
        r = c.execute(sql, args).fetchone()
        return dict(r) if r else None


def _all(sql, args=()):
    with db._conn() as c:
        return [dict(r) for r in c.execute(sql, args).fetchall()]


def _run(sql, args=()):
    with db._conn() as c:
        return c.execute(sql, args).lastrowid


def now_s():
    return datetime.now(db.TZ).strftime("%Y-%m-%d %H:%M")


def owner_id():
    return ctx.get("owner_id")


def is_owner(uid):
    return bool(owner_id()) and uid == owner_id()


def ikb(rows):
    return booking.ikb(rows)


def say(uid, text, kb=None):
    return ctx["bot"].send_message(uid, text, reply_markup=kb, disable_web_page_preview=True)


def send_long(uid, text, limit=3600):
    """Длинный текст несколькими сообщениями, разрезая по пустым строкам."""
    part = ""
    for para in text.split("\n\n"):
        if part and len(part) + len(para) + 2 > limit:
            say(uid, part)
            part = ""
        part = (part + "\n\n" + para) if part else para
    if part:
        say(uid, part)


# ─── УРОВНИ ПОДПИСКИ ──────────────────────────────────────────────────────────

def is_owner_tc(tc):
    return bool(tc) and tc.get("user_id") == owner_id()


def eff_tier(tc):
    """Действующий уровень: у Лазизы всегда высший, у остальных 0, если срок вышел."""
    if is_owner_tc(tc):
        return 3
    until = tc.get("tier_until")
    if until and until < db.today():
        return 0
    return int(tc.get("tier") or 0)


def days_left(tc):
    until = tc.get("tier_until")
    if not until:
        return None
    return (datetime.strptime(until, "%Y-%m-%d").date() - datetime.strptime(db.today(), "%Y-%m-%d").date()).days


def agreed(tc):
    return is_owner_tc(tc) or tc.get("agreed_ver") == AGREEMENT_VERSION


def check(tc, feat):
    """(можно ли, почему нельзя). Лазиза может всё."""
    if is_owner_tc(tc):
        return True, ""
    if not agreed(tc):
        return False, "Сначала нужно принять соглашение репетитора. Открой /myteacher."
    need, have = FEAT[feat], eff_tier(tc)
    if have >= need:
        return True, ""
    if have == 0:
        return False, ("Подписка не активна, поэтому эта функция сейчас недоступна. "
                       "Напиши Лазизе, она включит или продлит подписку. Посмотреть уровни: кнопка «Подписка» в /myteacher.")
    return False, f"Эта функция доступна на уровне «{TIERS[need]}» и выше, а сейчас у тебя «{TIERS[have]}». Лазиза может перевести тебя на другой уровень."


def tier_text(tc):
    have = eff_tier(tc)
    if is_owner_tc(tc):
        return "Про (без срока: у тебя всё включено)"
    s = TIERS[have]
    d = days_left(tc)
    if have and d is not None:
        s += f" до {datetime.strptime(tc['tier_until'], '%Y-%m-%d'):%d.%m.%Y} (осталось {d} дн.)"
    elif tc.get("tier") and d is not None and d < 0:
        s = f"{TIERS[int(tc['tier'])]} закончилась {datetime.strptime(tc['tier_until'], '%Y-%m-%d'):%d.%m.%Y}"
    return s


def tiers_screen():
    lines = ["💳 <b>Уровни подписки</b>", ""]
    for n in (1, 2, 3):
        lines += [f"<b>{TIERS[n]}</b>", TIER_INFO[n], ""]
    return "\n".join(lines).strip()


# ─── ПОДКЛЮЧЕНИЕ К booking.py ─────────────────────────────────────────────────

def can_publish(tc):
    if is_owner_tc(tc):
        return True, ""
    if not agreed(tc):
        return False, "Чтобы опубликовать профиль, сначала прими соглашение репетитора: открой /myteacher."
    if eff_tier(tc) < 1:
        return False, "Чтобы профиль был виден ученикам, нужна активная подписка. Напиши Лазизе, она её включит."
    return True, ""


def publish_rows(tc):
    return [[("💳 Подписка", f"tt:my:{tc['id']}")]]


def editor_lines(uid, tc):
    if is_owner_tc(tc):
        return []
    ag = "принято" if agreed(tc) else "не принято"
    return ["", f"💳 Подписка: {tier_text(tc)}", f"📜 Соглашение: {ag}"]


def editor_rows(uid, tc):
    tid = tc["id"]
    rows = []
    if is_owner_tc(tc):
        if uid == tc["user_id"]:
            rows.append([("🎞 Записи уроков", f"tt:rec:{tid}"), ("👥 Мои ученики", f"tt:st:{tid}")])
        return rows
    if uid == tc["user_id"]:
        rows.append([("📚 Домашка", f"tt:hw:{tid}"), ("🎞 Записи уроков", f"tt:rec:{tid}")])
        rows.append([("👥 Мои ученики", f"tt:st:{tid}"), ("💳 Подписка", f"tt:my:{tid}")])
        rows.append([("📜 Соглашение", f"tt:ag:{tid}")])
    if is_owner(uid):
        rows.append([("💳 Выдать/продлить подписку", f"tt:sub:{tid}")])
    return rows


def gate(uid, tc):
    """/myteacher: пока соглашение не принято, показываем его. True, если показали."""
    if agreed(tc) or is_owner_tc(tc):
        return False
    show_agreement(uid, tc["id"])
    return True


def show_agreement(uid, tid):
    send_long(uid, AGREEMENT_TEXT)
    say(uid, "Если согласен(на) с условиями, нажми «Принимаю».", ikb([[("✅ Принимаю", f"tt:agy:{tid}")]]))


def on_book(tid, uid):
    """Ученик записался к репетитору: он теперь «его» ученик."""
    tc = booking.teacher(tid)
    if tc and tc.get("user_id") != uid and not is_owner_tc(tc):
        link(tid, uid)


# ─── УЧЕНИКИ РЕПЕТИТОРА ───────────────────────────────────────────────────────

def link(tid, uid):
    _run("INSERT OR IGNORE INTO tutor_students (teacher_id, user_id, created) VALUES (?,?,?)", (tid, uid, db.today()))


def unlink(tid, uid):
    _run("DELETE FROM tutor_students WHERE teacher_id=? AND user_id=?", (tid, uid))


def students_of(tc):
    """Ученики репетитора. У Лазизы — все отмеченные ученики."""
    if is_owner_tc(tc):
        return [{"user_id": s["user_id"], "name": s["name"]} for s in db.students()]
    return _all("SELECT u.user_id, u.name FROM tutor_students s JOIN users u ON u.user_id=s.user_id "
                "WHERE s.teacher_id=? ORDER BY u.name", (tc["id"],))


def name_of(uid):
    return esc((db.get_user(uid) or {}).get("name") or "—")


def students_screen(uid, tid, mid=None):
    tc = booking.teacher(tid)
    sts = students_of(tc)
    lines = ["👥 <b>Мои ученики</b>", ""]
    rows = []
    if not sts:
        lines.append("Пока никого. Ученики появляются здесь сами, когда записываются к тебе на занятие. "
                     "Можно добавить вручную по @username, если человек уже открывал бота.")
    for s in sts[:40]:
        lines.append(f"· {esc(s['name'] or '—')}")
        if not is_owner_tc(tc):
            rows.append([(f"✖️ Убрать: {(s['name'] or '—')[:30]}", f"tt:sd:{tid}:{s['user_id']}")])
    if is_owner_tc(tc):
        lines.append("\nУ Лазизы это все, кого она отметила учениками («➕ Сделать учеником» в админ-меню).")
    else:
        rows.append([("➕ Добавить по @username", f"tt:sa:{tid}")])
    rows.append([("⬅️ К профилю", f"bt:e:{tid}")])
    booking.put(uid, mid, "\n".join(lines), ikb(rows))


# ─── ВЫБОР УЧЕНИКОВ ───────────────────────────────────────────────────────────

def picker_markup(uid):
    d = TS[uid]
    tc = booking.teacher(d["tid"])
    rows = []
    if is_owner_tc(tc):
        for g in db.group_list():
            if g["n"]:
                rows.append([(f"👥 {g['name']} ({g['n']})", f"tt:pg:{g['id']}")])
    for s in students_of(tc)[:60]:
        rows.append([(("☑️ " if s["user_id"] in d["sel"] else "⬜ ") + (s["name"] or "—")[:40], f"tt:pt:{s['user_id']}")])
    rows.append([(f"✅ Готово ({len(d['sel'])})", "tt:pok"), ("✖️ Отмена", "tt:px")])
    return ikb(rows)


def start_picker(uid, tid, mode, prompt, **extra):
    tc = booking.teacher(tid)
    if not students_of(tc):
        return say(uid, "Пока нет учеников. Они появятся, когда запишутся к тебе на занятие, "
                        "или добавь их вручную: «👥 Мои ученики» → «Добавить по @username».")
    TS[uid] = {"mode": mode, "tid": tid, "sel": set(), "step": "pick", **extra}
    booking.S.pop(uid, None)
    say(uid, prompt, picker_markup(uid))


# ─── ДОМАШКИ РЕПЕТИТОРА ───────────────────────────────────────────────────────

def hw_start(uid, tid):
    tc = booking.teacher(tid)
    if not tc or tc["user_id"] != uid or is_owner_tc(tc):
        return
    ok, why = check(tc, "hw_text")
    if not ok:
        return say(uid, why)
    start_picker(uid, tid, "hw", "📚 <b>Кому задать домашку?</b>\nОтметь учеников и нажми «Готово».")


def hw_ask_text(uid):
    d = TS[uid]
    d["step"] = "hw_text"
    d["media"] = []
    tc = booking.teacher(d["tid"])
    media_ok = check(tc, "hw_media")[0]
    extra = (f" Можно приложить фото, видео, аудио, голосовое или файл (до {ctx['HW_MEDIA_MAX']})." if media_ok else
             " Вложения (фото, видео, аудио, файлы) доступны на уровне «Стандарт» и выше.")
    say(uid, "Что задать? Напиши текст задания." + extra)


def hw_ask_due(uid):
    TS[uid]["step"] = "hw_due"
    say(uid, "К какому сроку? Напиши «сегодня», «завтра», «послезавтра», дату вроде <code>15.10</code> или «-», если без срока.")


def hw_finish(uid, due):
    d = TS.pop(uid)
    media = d.get("media") or None
    text = d.get("text") or ctx["hw_default_text"](media)
    ok, fail = ctx["deliver_hw"](sorted(d["sel"]), text, due, media, teacher_id=d["tid"])
    msg = f"📚 Домашка отправлена: {len(ok)} чел."
    if fail:
        msg += "\n⚠️ Не дошла (человек мог закрыть бота): " + ", ".join(name_of(u) for u in fail)
    say(uid, msg)


# ─── ЗАПИСИ УРОКОВ ────────────────────────────────────────────────────────────

def rec_menu(uid, tid, mid=None):
    tc = booking.teacher(tid)
    if not tc or tc["user_id"] != uid:
        return
    rs = _all("SELECT r.*, (SELECT COUNT(*) FROM rec_access a WHERE a.rec_id=r.id) AS n FROM recordings r "
              "WHERE teacher_id=? ORDER BY id DESC LIMIT 15", (tid,))
    lines = ["🎞 <b>Записи уроков</b>", "",
             "Отправляешь запись ученику или группе: Telegram не даёт им сохранить и переслать её. "
             "Но снять экран на камеру он запретить не может, поэтому ученики получают запись только для личного просмотра."]
    rows = [[("➕ Новая запись", f"tt:rn:{tid}")]]
    if rs:
        lines += ["", "Твои записи:"]
    for r in rs:
        rows.append([(f"🎞 {r['title'][:35]} · {r['n']} чел.", f"tt:rv:{r['id']}")])
    rows.append([("⬅️ К профилю", f"bt:e:{tid}")])
    booking.put(uid, mid, "\n".join(lines), ikb(rows))


def rec_view(uid, rid, mid=None):
    r = _one("SELECT * FROM recordings WHERE id=?", (rid,))
    tc = booking.teacher(r["teacher_id"]) if r else None
    if not tc or tc["user_id"] != uid:
        return
    who = _all("SELECT u.name FROM rec_access a JOIN users u ON u.user_id=a.user_id WHERE a.rec_id=? ORDER BY u.name", (rid,))
    lines = [f"🎞 <b>{esc(r['title'])}</b>", f"Загружена: {r['created']}", "", f"Доступна ({len(who)}):"]
    lines += [f"· {esc(x['name'] or '—')}" for x in who[:40]] or ["пока никому"]
    booking.put(uid, mid, "\n".join(lines),
                ikb([[("➕ Открыть ещё кому-то", f"tt:rg:{rid}")], [("🗑 Удалить запись", f"tt:rd:{rid}")],
                     [("⬅️ К записям", f"tt:rec:{tc['id']}")]]))


def protected_send(u, kind, fid, cap):
    """Отправка с запретом сохранять и пересылать (protect_content)."""
    bot = ctx["bot"]
    if kind == "video_note":
        bot.send_message(u, cap, protect_content=True)
        return bot.send_video_note(u, fid, protect_content=True)
    return getattr(bot, "send_" + kind)(u, fid, caption=cap[:1024], protect_content=True)


def grant(rid, uids, announce=True):
    r = _one("SELECT * FROM recordings WHERE id=?", (rid,))
    tc = booking.teacher(r["teacher_id"]) if r else None
    if not r or not tc:
        return [], list(uids)
    ok, fail = [], []
    for u in uids:
        lang = ctx["lang_of"](u)
        try:
            if announce:
                ctx["bot"].send_message(u, t(lang, "rec_new", name=esc(tc["name"]), title=esc(r["title"])))
            sent = protected_send(u, r["kind"], r["file_id"], t(lang, "rec_cap", title=esc(r["title"]), name=esc(tc["name"])))
            _run("INSERT OR REPLACE INTO rec_access (rec_id, user_id, msg_id, created) VALUES (?,?,?,?)",
                 (rid, u, getattr(sent, "message_id", None), now_s()))
            ok.append(u)
        except Exception as e:
            logging.warning("запись урока %s не дошла до %s: %s", rid, u, e)
            fail.append(u)
    return ok, fail


def rec_delete(rid):
    for a in _all("SELECT user_id, msg_id FROM rec_access WHERE rec_id=?", (rid,)):
        if a.get("msg_id"):
            try:
                ctx["bot"].delete_message(a["user_id"], a["msg_id"])
            except Exception:
                pass
    _run("DELETE FROM rec_access WHERE rec_id=?", (rid,))
    _run("DELETE FROM recordings WHERE id=?", (rid,))


def has_records(uid):
    return _one("SELECT 1 AS x FROM rec_access WHERE user_id=?", (uid,)) is not None


def send_records(uid, c=None):
    """Кнопка меню «Записи уроков» у ученика."""
    lang = ctx["lang_of"](uid)
    rs = _all("SELECT r.id, r.title, r.created, tc.name AS tname FROM rec_access a JOIN recordings r ON r.id=a.rec_id "
              "JOIN teachers tc ON tc.id=r.teacher_id WHERE a.user_id=? ORDER BY r.id DESC LIMIT 20", (uid,))
    if not rs:
        return say(uid, t(lang, "rec_none"))
    rows = [[(f"🎞 {r['title'][:32]} · {r['tname'][:16]}", f"tr:v:{r['id']}")] for r in rs]
    say(uid, t(lang, "rec_head"), ikb(rows))


def cb_tr(c):
    uid = c.from_user.id
    ctx["bot"].answer_callback_query(c.id)
    p = c.data.split(":")
    if len(p) < 3 or p[1] != "v":
        return
    lang = ctx["lang_of"](uid)
    r = _one("SELECT r.*, tc.name AS tname FROM recordings r JOIN rec_access a ON a.rec_id=r.id AND a.user_id=? "
             "JOIN teachers tc ON tc.id=r.teacher_id WHERE r.id=?", (uid, int(p[2])))
    if not r:
        return say(uid, t(lang, "rec_gone"))
    try:
        protected_send(uid, r["kind"], r["file_id"], t(lang, "rec_cap", title=esc(r["title"]), name=esc(r["tname"])))
    except Exception as e:
        logging.warning("запись %s не открылась у %s: %s", r["id"], uid, e)
        say(uid, t(lang, "rec_gone"))


# ─── ОБСУЖДЕНИЯ ───────────────────────────────────────────────────────────────

_ON_TOPIC = re.compile(
    r"китай|китаец|китайц|кнр\b|пекин|шанха|гонконг|гуанч|шэньч|ханч|сиань|чэнд|тайван|макао|мандарин|пиньин|иероглиф|"
    r"путунхуа|синолог|сычуан|юньнан|тибет|конфуци|чэнъюй|чэнюй|\bhsk\b|\bхск\b|china|chinese|beijing|shanghai|"
    r"hong\s?kong|mandarin|pinyin|hanzi|chengyu|xitoy|хитой|сун ?цзы|[一-鿿]", re.I)
_LINKS = re.compile(r"https?://|www\.|t\.me/|@\w{4,}", re.I)


def on_topic(*texts):
    return bool(_ON_TOPIC.search(" ".join(texts)))


def first_name(uid):
    name = ((db.get_user(uid) or {}).get("name") or "").strip().split(" ")[0] or "—"
    mark = "👩‍🏫 " if booking.teacher_of_user(uid) else ""
    return mark + esc(name[:20])


def send_topics(uid, c=None, page=0):
    if not TOPICS_ON:
        return
    lang = ctx["lang_of"](uid)
    rows_all = _all("SELECT t.id, t.title, (SELECT COUNT(*) FROM topic_posts p WHERE p.topic_id=t.id AND p.status='open') AS n "
                    "FROM topics t WHERE t.status='open' ORDER BY t.updated DESC LIMIT ? OFFSET ?", (PAGE + 1, page * PAGE))
    more = len(rows_all) > PAGE
    rows = [[(f"{r['title'][:44]} · {r['n']}", f"tp:o:{r['id']}")] for r in rows_all[:PAGE]]
    nav = []
    if page > 0:
        nav.append(("◀️", f"tp:l:{page - 1}"))
    if more:
        nav.append(("▶️", f"tp:l:{page + 1}"))
    if nav:
        rows.append(nav)
    rows.append([(t(lang, "tp_new_btn"), "tp:new")])
    text = t(lang, "tp_head") + ("" if rows_all else "\n\n" + t(lang, "tp_none"))
    if c:
        try:
            return ctx["bot"].edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=ikb(rows))
        except Exception:
            pass
    say(uid, text, ikb(rows))


def topic_view(uid, tid, c=None):
    lang = ctx["lang_of"](uid)
    tp = _one("SELECT * FROM topics WHERE id=? AND status='open'", (tid,))
    if not tp:
        return say(uid, t(lang, "tp_gone"))
    posts = _all("SELECT * FROM topic_posts WHERE topic_id=? AND status='open' ORDER BY id DESC LIMIT 10", (tid,))[::-1]
    total = _one("SELECT COUNT(*) AS n FROM topic_posts WHERE topic_id=? AND status='open'", (tid,))["n"]
    head = [f"💬 <b>{esc(tp['title'])}</b>", f"<i>{first_name(tp['user_id'])} · {tp['created'][:10]}</i>", "", esc(tp["body"]), "",
            t(lang, "tp_count", n=total)]
    body = []
    for p in posts:
        body.append(f"\n<b>{first_name(p['user_id'])}</b>: {esc(p['text'])}")
    if not posts:
        body.append("\n" + t(lang, "tp_empty_posts"))
    text = "\n".join(head) + "\n" + "".join(body)
    if len(text) > 3900:
        text = text[:3890] + "…"
    rows = [[(t(lang, "tp_reply_btn"), f"tp:re:{tid}"), (t(lang, "tp_report_btn"), f"tp:r:{tid}")]]
    if is_owner(uid) or uid == tp["user_id"]:
        rows.append([(f"🗑 #{tid}", f"tp:dt:{tid}")])
    if is_owner(uid):
        rows.append([(f"🗑 ответ {p['id']}", f"tp:dp:{p['id']}") for p in posts[-5:]])
    rows.append([(t(lang, "tp_back"), "tp:l:0")])
    if c:
        try:
            return ctx["bot"].edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=ikb(rows))
        except Exception:
            pass
    say(uid, text, ikb(rows))


def _pause_ok(kind, uid, secs):
    now = time.time()
    if now - LAST[kind].get(uid, 0) < secs:
        return False
    LAST[kind][uid] = now
    return True


def topic_text(uid, m, txt):
    """Шаги создания темы и ответа. True — сообщение обработано."""
    d = TD[uid]
    lang = ctx["lang_of"](uid)
    bot = ctx["bot"]
    step = d["step"]
    if _LINKS.search(txt):
        say(uid, t(lang, "tp_links"))
        return True
    if step == "title":
        d["title"] = txt[:TOPIC_TITLE_MAX]
        d["step"] = "body"
        say(uid, t(lang, "tp_ask_body"))
        return True
    if step == "body":
        if not on_topic(d["title"], txt):
            TD.pop(uid, None)
            say(uid, t(lang, "tp_off"))
            return True
        if not _pause_ok("topic", uid, TOPIC_PAUSE):
            TD.pop(uid, None)
            say(uid, t(lang, "tp_flood"))
            return True
        TD.pop(uid, None)
        tid = _run("INSERT INTO topics (user_id, title, body, created, updated) VALUES (?,?,?,?,?)",
                   (uid, d["title"], txt[:TOPIC_BODY_MAX], now_s(), now_s()))
        say(uid, t(lang, "tp_created"))
        return topic_view(uid, tid) or True
    if step == "reply":
        if not _pause_ok("post", uid, POST_PAUSE):
            say(uid, t(lang, "tp_flood"))
            return True
        TD.pop(uid, None)
        tid = d["tid"]
        tp = _one("SELECT * FROM topics WHERE id=? AND status='open'", (tid,))
        if not tp:
            say(uid, t(lang, "tp_gone"))
            return True
        _run("INSERT INTO topic_posts (topic_id, user_id, text, created) VALUES (?,?,?,?)", (tid, uid, txt[:POST_MAX], now_s()))
        _run("UPDATE topics SET updated=? WHERE id=?", (now_s(), tid))
        say(uid, t(lang, "tp_replied"))
        if tp["user_id"] != uid:
            try:
                bot.send_message(tp["user_id"], t(ctx["lang_of"](tp["user_id"]), "tp_notify", title=esc(tp["title"])),
                                 reply_markup=ikb([[(t(ctx["lang_of"](tp["user_id"]), "tp_open"), f"tp:o:{tid}")]]))
            except Exception:
                pass
        return topic_view(uid, tid) or True
    return False


def cb_tp(c):
    uid = c.from_user.id
    bot = ctx["bot"]
    lang = ctx["lang_of"](uid)
    p = c.data.split(":")
    act = p[1]
    bot.answer_callback_query(c.id)
    if not TOPICS_ON:
        return
    if act == "l":
        TD.pop(uid, None)
        return send_topics(uid, c, int(p[2]) if len(p) > 2 else 0)
    if act == "new":
        TD[uid] = {"step": "title"}
        booking.S.pop(uid, None)
        return say(uid, t(lang, "tp_ask_title"), ikb([[(t(lang, "tp_cancel"), "tp:x")]]))
    if act == "x":
        TD.pop(uid, None)
        return say(uid, t(lang, "tp_cancelled"))
    tid = int(p[2])
    if act == "o":
        return topic_view(uid, tid, c)
    if act == "re":
        TD[uid] = {"step": "reply", "tid": tid}
        booking.S.pop(uid, None)
        return say(uid, t(lang, "tp_ask_reply"), ikb([[(t(lang, "tp_cancel"), "tp:x")]]))
    if act == "r":
        tp = _one("SELECT * FROM topics WHERE id=?", (tid,))
        if tp and owner_id():
            try:
                bot.send_message(owner_id(), f"🚩 Жалоба на тему #{tid} «{esc(tp['title'])}» от {first_name(uid)}:\n\n{esc(tp['body'])}",
                                 reply_markup=ikb([[("🗑 Удалить тему", f"tp:dt:{tid}"), ("Оставить", "tp:keep")]]))
            except Exception:
                pass
        return say(uid, t(lang, "tp_reported"))
    if act == "dt":
        tp = _one("SELECT * FROM topics WHERE id=?", (tid,))
        if tp and (is_owner(uid) or uid == tp["user_id"]):
            _run("UPDATE topics SET status='removed' WHERE id=?", (tid,))
            if is_owner(uid) and tp["user_id"] != uid:
                try:
                    bot.send_message(tp["user_id"], "Твоя тема в обсуждениях удалена: она не соответствует правилам раздела.")
                except Exception:
                    pass
            say(uid, "🗑 Тема удалена.")
            return send_topics(uid)
        return
    if act == "dp" and is_owner(uid):
        _run("UPDATE topic_posts SET status='removed' WHERE id=?", (tid,))
        return say(uid, "🗑 Ответ удалён.")


def cb_tp_keep(c):
    ctx["bot"].answer_callback_query(c.id)


# ─── ДИАЛОГИ: ТЕКСТ И ВЛОЖЕНИЯ ────────────────────────────────────────────────

def _is_menu(txt, uid):
    return txt.startswith("/") or txt in ctx["labels"](ctx["lang_of"](uid))


def _on_text(m):
    """Первое звено обработки текста в bot.on_text. True — сообщение обработано здесь."""
    uid = m.from_user.id
    txt = (m.text or "").strip()
    bot = ctx["bot"]

    if m.reply_to_message and not is_owner(uid):                 # ответ репетитора на сдачу ученика
        target = _one("SELECT user_id FROM t_inbox WHERE chat_id=? AND msg_id=?", (m.chat.id, m.reply_to_message.message_id))
        if target:
            tc = booking.teacher_of_user(uid)
            who = esc(tc["name"]) if tc else "Преподаватель"
            try:
                bot.send_message(target["user_id"], f"💬 {who}:\n{esc(txt)}")
                bot.send_message(uid, "✅ Отправлено")
            except Exception:
                bot.send_message(uid, "Не получилось отправить: человек мог закрыть бота.")
            return True

    if uid in TD:
        if _is_menu(txt, uid):
            TD.pop(uid, None)
        else:
            return topic_text(uid, m, txt)

    d = TS.get(uid)
    if not d:
        return False
    if _is_menu(txt, uid):
        TS.pop(uid, None)
        return False
    step = d["step"]
    if step == "hw_text":
        d["text"] = txt[:500]
        hw_ask_due(uid)
        return True
    if step == "hw_due":
        due = ctx["parse_due"](txt, db.today())
        if due is None:
            say(uid, "Не поняла срок. Примеры: завтра, 15.10, «-».")
            return True
        hw_finish(uid, due)
        return True
    if step == "rec_title":
        title = (txt[:60] if txt != "-" else "") or f"Запись урока {datetime.now(db.TZ):%d.%m}"
        d["title"] = title
        rid = _run("INSERT INTO recordings (teacher_id, kind, file_id, title, created) VALUES (?,?,?,?,?)",
                   (d["tid"], d["kind"], d["file_id"], title, now_s()))
        TS[uid] = {"mode": "rec", "tid": d["tid"], "sel": set(), "step": "pick", "rid": rid}
        say(uid, f"✅ Запись «{esc(title)}» сохранена. Кому её открыть?", picker_markup(uid))
        return True
    if step == "add_student":
        un = txt.lstrip("@").strip().lower()
        u = _one("SELECT user_id, name FROM users WHERE lower(username)=?", (un,)) if un else None
        if not u:
            say(uid, "Не нашла такого человека в боте. Пусть он сначала откроет бота и нажмёт /start, потом пришли @username ещё раз.")
            return True
        TS.pop(uid, None)
        link(d["tid"], u["user_id"])
        say(uid, f"✅ {esc(u['name'] or un)} добавлен(а) в твои ученики.")
        return students_screen(uid, d["tid"]) or True
    return False


def _on_media(m):
    """Вложения в диалогах репетитора и ответ вложением на сдачу. True — обработано."""
    uid = m.from_user.id
    bot = ctx["bot"]
    if m.reply_to_message and not is_owner(uid):
        target = _one("SELECT user_id FROM t_inbox WHERE chat_id=? AND msg_id=?", (m.chat.id, m.reply_to_message.message_id))
        if target:
            tc = booking.teacher_of_user(uid)
            try:
                gid = getattr(m, "media_group_id", None)
                if not (gid and LAST.setdefault("rg", {}).get(gid)):
                    bot.send_message(target["user_id"], f"💬 {esc(tc['name']) if tc else 'Преподаватель'}:")
                    bot.send_message(uid, "✅ Отправлено")
                bot.copy_message(target["user_id"], m.chat.id, m.message_id)
                if gid:
                    LAST["rg"][gid] = True
            except Exception:
                bot.send_message(uid, "Не получилось отправить: человек мог закрыть бота.")
            return True
    d = TS.get(uid)
    if not d:
        return False
    if d["step"] == "rec_file":
        if m.content_type not in REC_KINDS:
            say(uid, "Пришли запись видео, аудио или файлом (не фото) либо нажми «Отмена».")
            return True
        obj = getattr(m, m.content_type)
        d["kind"], d["file_id"] = m.content_type, obj.file_id
        d["step"] = "rec_title"
        say(uid, "Как назвать запись? Например: «Урок 12: числа». Или «-», чтобы подписать датой.")
        return True
    if d["step"] == "hw_text":
        tc = booking.teacher(d["tid"])
        ok, why = check(tc, "hw_media")
        if not ok:
            say(uid, why)
            return True
        md = ctx["hw_media_of"](m)
        if not md:
            return False
        lst = d.setdefault("media", [])
        if len(lst) >= ctx["HW_MEDIA_MAX"]:
            say(uid, f"Больше {ctx['HW_MEDIA_MAX']} вложений не приложить. Нажми «Дальше».", ikb([[("➡️ Дальше", "tt:hwn")]]))
            return True
        lst.append(md)
        cap = (getattr(m, "caption", None) or "").strip()
        if cap and not d.get("text"):
            d["text"] = cap[:500]
        gid = getattr(m, "media_group_id", None)
        if gid and d.get("last_group") == gid:
            return True
        d["last_group"] = gid
        say(uid, f"📎 Приложено: {len(lst)}. Можно прислать ещё, написать текст задания или нажать «Дальше».",
            ikb([[("➡️ Дальше", "tt:hwn")]]))
        return True
    return False


def on_text(m):
    """Сбой здесь не должен ломать остальной бот: пишем в журнал и отдаём сообщение дальше."""
    try:
        return _on_text(m)
    except Exception:
        logging.exception("репетиторы: ошибка в обработке текста")
        return False


def on_media(m):
    try:
        return _on_media(m)
    except Exception:
        logging.exception("репетиторы: ошибка в обработке вложения")
        return False


# ─── КНОПКИ РЕПЕТИТОРА И ЛАЗИЗЫ ───────────────────────────────────────────────

def _teacher_of(uid, tid, owner_ok=False):
    tc = booking.teacher(tid)
    if not tc:
        return None
    if tc["user_id"] == uid or (owner_ok and is_owner(uid)):
        return tc
    return None


def sub_screen(uid, tid, mid=None):
    tc = booking.teacher(tid)
    if not tc or not is_owner(uid):
        return
    rows = []
    for n in (1, 2, 3):
        rows.append([(f"{TIERS[n]} · 30 дн.", f"tt:set:{tid}:{n}:30"), (f"{TIERS[n]} · 90 дн.", f"tt:set:{tid}:{n}:90")])
    rows.append([("⛔ Снять подписку", f"tt:set:{tid}:0:0")])
    rows.append([("⬅️ К профилю", f"bt:e:{tid}")])
    booking.put(uid, mid, f"💳 <b>Подписка: {esc(tc['name'])}</b>\n\nСейчас: {tier_text(tc)}\n\n"
                          "Выбери уровень и срок. Если у репетитора такой же уровень ещё действует, срок продлится от даты окончания.", ikb(rows))


def set_tier(uid, tid, tier, days):
    tc = booking.teacher(tid)
    if not tc or not is_owner(uid) or is_owner_tc(tc):
        return
    if tier == 0:
        booking.update(tid, tier=0, tier_until=None, active=0)
        note = "Подписка снята, профиль скрыт от учеников. Уже сделанные записи сохраняются."
    else:
        base = datetime.strptime(db.today(), "%Y-%m-%d").date()
        cur = tc.get("tier_until")
        if int(tc.get("tier") or 0) == tier and cur and cur >= db.today():
            base = datetime.strptime(cur, "%Y-%m-%d").date()
        until = (base + timedelta(days=days)).isoformat()
        booking.update(tid, tier=tier, tier_until=until)
        note = f"Подписка «{TIERS[tier]}» до {datetime.strptime(until, '%Y-%m-%d'):%d.%m.%Y}."
    say(uid, f"✅ {esc(tc['name'])}: {note}")
    if tc.get("user_id"):
        try:
            ctx["bot"].send_message(tc["user_id"], f"💳 {note}")
        except Exception:
            pass
    sub_screen(uid, tid)


def cb_tt(c):
    uid = c.from_user.id
    bot = ctx["bot"]
    p = c.data.split(":")
    act = p[1]
    mid = c.message.message_id
    bot.answer_callback_query(c.id)
    # кнопки выбора учеников и вложений: диалог лежит у самого человека
    if act == "px":
        TS.pop(uid, None)
        return say(uid, "Отменено.")
    if act in ("pt", "pg", "pok", "hwn"):
        d = TS.get(uid)
        if not d:
            return say(uid, "Выбор устарел, начни заново.")
        if act == "pt":
            d["sel"].symmetric_difference_update({int(p[2])})
        elif act == "pg":
            tc = booking.teacher(d["tid"])
            if is_owner_tc(tc):
                ids = {x["user_id"] for x in db.group_members(int(p[2]))}
                d["sel"] = d["sel"] - ids if ids <= d["sel"] else d["sel"] | ids
        elif act == "hwn":
            if d.get("step") == "hw_text":
                try:
                    bot.edit_message_reply_markup(c.message.chat.id, mid, reply_markup=None)
                except Exception:
                    pass
                return hw_ask_due(uid)
            return
        elif act == "pok":
            if not d["sel"]:
                return bot.answer_callback_query(c.id, "Никто не выбран")
            mode = d["mode"]
            try:
                bot.edit_message_reply_markup(c.message.chat.id, mid, reply_markup=None)
            except Exception:
                pass
            if mode == "hw":
                return hw_ask_text(uid)
            ok, fail = grant(d["rid"], sorted(d["sel"]))
            TS.pop(uid, None)
            msg = f"🎞 Запись открыта: {len(ok)} чел."
            if fail:
                msg += "\n⚠️ Не дошла (человек мог закрыть бота): " + ", ".join(name_of(u) for u in fail)
            return say(uid, msg)
        try:
            bot.edit_message_reply_markup(c.message.chat.id, mid, reply_markup=picker_markup(uid))
        except Exception:
            pass
        return

    if act in ("rv", "rg", "rd", "rdy"):
        r = _one("SELECT * FROM recordings WHERE id=?", (int(p[2]),))
        tc = booking.teacher(r["teacher_id"]) if r else None
        if not tc or tc["user_id"] != uid:
            return
        rid = r["id"]
        if act == "rv":
            return rec_view(uid, rid, mid)
        if act == "rg":
            return start_picker(uid, tc["id"], "recgive", f"🎞 <b>Кому открыть «{esc(r['title'])}»?</b>", rid=rid)
        if act == "rd":
            return booking.put(uid, mid, f"Удалить запись «{esc(r['title'])}»? Она исчезнет у всех учеников.",
                               ikb([[("Да, удалить", f"tt:rdy:{rid}")], [("Отмена", f"tt:rv:{rid}")]]))
        rec_delete(rid)
        say(uid, "🗑 Запись удалена.")
        return rec_menu(uid, tc["id"])

    tid = int(p[2])
    if act == "sub":
        return sub_screen(uid, tid, mid)
    if act == "set":
        return set_tier(uid, tid, int(p[3]), int(p[4]))
    tc = booking.teacher(tid)
    if not tc:
        return
    if act == "my":                                    # репетитор смотрит свою подписку (или Лазиза смотрит чужую)
        if tc["user_id"] != uid and not is_owner(uid):
            return
        txt = f"💳 <b>Подписка</b>\n\nСейчас: {tier_text(tc)}\n\n{tiers_screen()}\n\nПродлить или сменить уровень можно через Лазизу."
        return booking.put(uid, mid, txt, ikb([[("⬅️ К профилю", f"bt:e:{tid}")]]))
    if act == "ag":
        if tc["user_id"] != uid:
            return
        if agreed(tc):
            send_long(uid, AGREEMENT_TEXT)
            return say(uid, f"✅ Ты приняла/принял соглашение версии {tc.get('agreed_ver')} ({tc.get('agreed_at') or '—'}).",
                       ikb([[("⬅️ К профилю", f"bt:e:{tid}")]]))
        return show_agreement(uid, tid)
    if act == "agy":
        if tc["user_id"] != uid:
            return
        booking.update(tid, agreed_ver=AGREEMENT_VERSION, agreed_at=now_s())
        try:
            bot.edit_message_reply_markup(c.message.chat.id, mid, reply_markup=None)
        except Exception:
            pass
        if owner_id() and not is_owner(uid):
            try:
                bot.send_message(owner_id(), f"📜 {esc(tc['name'])} принял(а) соглашение репетитора (версия {AGREEMENT_VERSION}).")
            except Exception:
                pass
        say(uid, "✅ Соглашение принято, спасибо!")
        return booking.editor(uid, tid)
    if tc["user_id"] != uid:
        return
    if act == "st":
        return students_screen(uid, tid, mid)
    if act == "sa":
        TS[uid] = {"step": "add_student", "tid": tid}
        booking.S.pop(uid, None)
        return say(uid, "Пришли @username ученика. Он должен уже открыть бота и нажать /start.")
    if act == "sd":
        unlink(tid, int(p[3]))
        return students_screen(uid, tid, mid)
    if act == "hw":
        return hw_start(uid, tid)
    if act == "rec":
        return rec_menu(uid, tid, mid)
    if act == "rn":
        ok, why = check(tc, "records")
        if not ok:
            return say(uid, why)
        TS[uid] = {"step": "rec_file", "tid": tid}
        booking.S.pop(uid, None)
        return say(uid, "Пришли запись урока: видео, кружок, аудио или файл. Можно переслать из другого чата.",
                   ikb([[("Отмена", "tt:px")]]))


# ─── НАПОМИНАНИЯ О ПОДПИСКЕ ───────────────────────────────────────────────────

def hook(now):
    """Раз в минуту: предупреждает о конце подписки за 3 дня и скрывает профиль, когда срок вышел."""
    for tc in _all("SELECT * FROM teachers WHERE tier_until IS NOT NULL AND COALESCE(tier,0)>0"):
        if is_owner_tc(tc) or not tc.get("user_id"):
            continue
        d = days_left(tc)
        uid, until = tc["user_id"], tc["tier_until"]
        try:
            if d is not None and d < 0:
                if not db.was_sent(uid, f"subx:{until}"):
                    db.mark_sent(uid, f"subx:{until}")
                    booking.update(tc["id"], active=0)
                    ctx["bot"].send_message(uid, f"💳 Подписка «{TIERS[int(tc['tier'])]}» закончилась, профиль скрыт от учеников. "
                                                 "Уже сделанные записи сохраняются. Чтобы вернуться в список, напиши Лазизе.")
                    if owner_id():
                        ctx["bot"].send_message(owner_id(), f"💳 У {esc(tc['name'])} закончилась подписка, профиль скрыт.")
            elif d is not None and d <= 3 and not db.was_sent(uid, f"sub3:{until}"):
                db.mark_sent(uid, f"sub3:{until}")
                ctx["bot"].send_message(uid, f"💳 Подписка «{TIERS[int(tc['tier'])]}» заканчивается через {d} дн. "
                                             "Чтобы профиль остался в списке, напиши Лазизе.")
                if owner_id():
                    ctx["bot"].send_message(owner_id(), f"💳 Через {d} дн. заканчивается подписка у {esc(tc['name'])}.")
        except Exception as e:
            logging.warning("напоминание о подписке %s: %s", uid, e)


# ─── ПОДКЛЮЧЕНИЕ К БОТУ ───────────────────────────────────────────────────────

def register(bot, owner_id_, lang_of, funcs):
    ctx.update(bot=bot, owner_id=owner_id_, lang_of=lang_of, **funcs)
    init_db()
    booking.hooks.update(on_book=on_book, editor_rows=editor_rows, editor_lines=editor_lines,
                         can_publish=can_publish, publish_rows=publish_rows, gate=gate)

    @bot.message_handler(commands=["topics"])
    def _topics(m):
        send_topics(m.from_user.id)

    @bot.message_handler(commands=["records"])
    def _records(m):
        send_records(m.from_user.id)

    bot.callback_query_handler(func=lambda c: c.data.startswith("tt:"))(_safe(cb_tt))
    bot.callback_query_handler(func=lambda c: c.data.startswith("tr:"))(_safe(cb_tr))
    bot.callback_query_handler(func=lambda c: c.data == "tp:keep")(cb_tp_keep)
    bot.callback_query_handler(func=lambda c: c.data.startswith("tp:"))(_safe(cb_tp))


def _safe(fn):
    def wrapper(c):
        try:
            return fn(c)
        except Exception:
            logging.exception("репетиторы: ошибка в кнопке %s", getattr(c, "data", "?"))
            try:
                ctx["bot"].answer_callback_query(c.id)
            except Exception:
                pass
    return wrapper
