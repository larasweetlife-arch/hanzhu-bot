"""
Сообщения от 茶茶 (версия 24): ненавязчивые напоминания о занятиях.

  · Не больше 2 раз в день по умолчанию; 3-й раз только по выбору человека. Настройка 0–3 (команда /chacha).
  · Ночью (22:00–09:00) не пишет. Время каждому чуть сдвинуто (до 40 минут), чтобы не слать всем разом.
  · Если человек молчит 3 дня подряд (не открывал ни слов, ни практики, ни кнопки 茶茶), 茶茶 сама пишет реже:
    на один шаг меньше, а после ещё 3 дней молчания — перестаёт и один раз об этом сообщает.
  · Первое сообщение любому человеку — вопрос с кнопками «как часто писать». Не ответил — действует 2 раза в день.
  · Новым пользователям первое сообщение приходит не раньше следующего дня после регистрации.
  · Режим: «pilot» (по умолчанию) — сообщения приходят только Лазизе; /chacha_on — всем, /chacha_off — снова только ей.
  · Лазиза: /chacha_test — показать все тексты и пример сообщения с кнопками.
Тексты — texts_v15.py (4 языка).
"""
import html
import logging
import threading
import time
from datetime import datetime, timedelta

import booking
import db
import tutors
from texts_v15 import BANK, CC

esc = lambda s: html.escape(str(s), quote=False)
ctx = {}
_BUSY = threading.Lock()

QUIET_FROM, QUIET_TO = 22, 9                    # ночью не пишем
SLOTS = {"morning": (9, 30), "day": (14, 0), "evening": (19, 30)}
KINDS = {1: ["day"], 2: ["morning", "evening"], 3: ["morning", "day", "evening"]}
JITTER = 40                                     # минут сдвига на человека
WINDOW = timedelta(minutes=150)                 # опоздавшее (после простоя бота) сообщение больше не шлём
DEFAULT_FREQ = 2
IGNORE_DAYS = 3
LANGS = ("ru", "uz", "en", "zh")


def C(lang, key, **kw):
    s = CC.get(lang, CC["ru"]).get(key)
    if s is None:
        s = CC["ru"][key]
    return s.format(**kw) if kw else s


def init_db():
    with db._conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS chacha (
            user_id INTEGER PRIMARY KEY, freq INTEGER, asked INTEGER NOT NULL DEFAULT 0,
            blocked INTEGER NOT NULL DEFAULT 0, last_cut TEXT
        );
        CREATE TABLE IF NOT EXISTS chacha_cfg (k TEXT PRIMARY KEY, v TEXT);
        """)


def _one(sql, args=()):
    return tutors._one(sql, args)


def _run(sql, args=()):
    return tutors._run(sql, args)


def is_owner(uid):
    return bool(ctx.get("owner_id")) and uid == ctx["owner_id"]


def mode():
    r = _one("SELECT v FROM chacha_cfg WHERE k='mode'")
    return r["v"] if r else "pilot"


def set_mode(v):
    _run("INSERT OR REPLACE INTO chacha_cfg (k, v) VALUES ('mode', ?)", (v,))


def row(uid):
    return _one("SELECT * FROM chacha WHERE user_id=?", (uid,)) or {"user_id": uid, "freq": None, "asked": 0, "blocked": 0, "last_cut": None}


def freq_of(uid):
    f = row(uid)["freq"]
    return DEFAULT_FREQ if f is None else int(f)


def set_row(uid, **kw):
    if not _one("SELECT 1 AS x FROM chacha WHERE user_id=?", (uid,)):
        _run("INSERT INTO chacha (user_id) VALUES (?)", (uid,))
    for k, v in kw.items():
        _run(f"UPDATE chacha SET {k}=? WHERE user_id=?", (v, uid))


def freq_label(lang, n):
    return C(lang, f"f{n}")


# ─── ТЕКСТЫ ───────────────────────────────────────────────────────────────────

def first_name(u, lang):
    w = ((u or {}).get("name") or "").split()
    return esc(w[0]) if w else C(lang, "friend")


def pick_text(uid, kind, day, lang, u):
    bank = BANK.get(lang, BANK["ru"])[kind]
    i = (uid + day.toordinal() + list(SLOTS).index(kind)) % len(bank)
    return bank[i].format(name=first_name(u, lang))


def ask_kb(lang):
    return booking.ikb([[(C(lang, f"f{n}"), f"cc:f:{n}")] for n in (1, 2, 3, 0)])


def msg_kb(lang):
    return booking.ikb([[(C(lang, "go"), "cc:go")], [(C(lang, "cfg"), "cc:cfg")]])


# ─── ПЛАНИРОВЩИК ──────────────────────────────────────────────────────────────

def audience(today):
    """Кому сейчас можно писать: в режиме pilot только владелице."""
    if mode() != "all":
        o = ctx.get("owner_id")
        return [db.get_user(o) or {"user_id": o, "lang": "ru", "name": "Лазиза"}] if o else []
    out = []
    for u in db.all_users():
        if not u.get("level") or is_owner(u["user_id"]):
            continue
        if (u.get("created_at") or "")[:10] >= today.isoformat():       # зарегистрировались сегодня: пусть сперва освоятся
            continue
        out.append(u)
    if ctx.get("owner_id"):
        out.append(db.get_user(ctx["owner_id"]) or {"user_id": ctx["owner_id"], "lang": "ru", "name": "Лазиза"})
    return out


def active_since(uid, day):
    """Был ли человек активен с этого дня (слова, практика, чай-тренировка, кнопка 茶茶)."""
    d = day.isoformat()
    with db._conn() as c:
        if c.execute("SELECT 1 FROM events WHERE user_id=? AND date>=? LIMIT 1", (uid, d)).fetchone():
            return True
        if c.execute("SELECT 1 FROM tea_score WHERE user_id=? AND day>=? AND points>0 LIMIT 1", (uid, d)).fetchone():
            return True
        return c.execute("SELECT 1 FROM sent WHERE user_id=? AND key LIKE 'cc_tap:%' AND substr(key,8)>=? LIMIT 1", (uid, d)).fetchone() is not None


def got_message_each_day(uid, days):
    return all(any(db.was_sent(uid, f"cc:{d.isoformat()}:{k}") for k in SLOTS) for d in days)


def ignored_tasks(now):
    """Раз в день после 9:00: кто молчит три дня подряд, тому пишем реже."""
    key = f"cc_eval:{now.date().isoformat()}"
    if db.was_sent(0, key):
        return []
    db.mark_sent(0, key)
    today = now.date()
    days = [today - timedelta(days=i) for i in range(1, IGNORE_DAYS + 1)]       # вчера, позавчера, ...
    out = []
    for u in audience(today):
        uid = u["user_id"]
        r = row(uid)
        f = freq_of(uid)
        if f < 1 or r["blocked"] or is_owner(uid):
            continue
        if r["last_cut"] and r["last_cut"] >= days[-1].isoformat():
            continue
        if not got_message_each_day(uid, days) or active_since(uid, days[-1]):
            continue
        set_row(uid, freq=f - 1, last_cut=days[0].isoformat())
        out.append((uid, "stop" if f - 1 == 0 else "cut", u))
    return out


def due_tasks(now):
    today = now.date()
    out = []
    for u in audience(today):
        uid = u["user_id"]
        r = row(uid)
        f = freq_of(uid)
        if f < 1 or r["blocked"]:
            continue
        for kind in KINDS[min(f, 3)]:
            h, mi = SLOTS[kind]
            at = datetime(today.year, today.month, today.day, h, mi, tzinfo=db.TZ) + timedelta(minutes=uid % JITTER)
            if not (at <= now < at + WINDOW):
                continue
            key = f"cc:{today.isoformat()}:{kind}"
            if db.was_sent(uid, key):
                continue
            if not r["asked"]:                                  # первое сообщение — вопрос; остальные в этот день не шлём
                for k in KINDS[3]:
                    db.mark_sent(uid, f"cc:{today.isoformat()}:{k}")
                out.append((uid, "ask", u))
                break
            db.mark_sent(uid, key)
            out.append((uid, kind, u))
    return out


def hook(now):
    """Из планировщика раз в минуту. Сообщения уходят из отдельного потока, чтобы не задерживать напоминания об уроках."""
    if not (QUIET_TO <= now.hour < QUIET_FROM):
        return
    if _BUSY.locked():
        return
    tasks = ignored_tasks(now) + due_tasks(now)
    if tasks:
        threading.Thread(target=run_tasks, args=(tasks, now.date()), daemon=True).start()


def run_tasks(tasks, today):
    with _BUSY:
        for uid, kind, u in tasks:
            send_one(uid, kind, u, today)
            time.sleep(0.06)


def send_one(uid, kind, u, today):
    bot = ctx["bot"]
    lang = (u or {}).get("lang") if (u or {}).get("lang") in LANGS else "ru"
    try:
        if kind == "ask":
            set_row(uid, asked=1)
            bot.send_message(uid, C(lang, "ask"), reply_markup=ask_kb(lang))
        elif kind in ("cut", "stop"):
            bot.send_message(uid, C(lang, kind))
        else:
            bot.send_message(uid, pick_text(uid, kind, today, lang, u), reply_markup=msg_kb(lang))
    except Exception as e:
        if "403" in str(e) or "blocked" in str(e).lower() or "deactivated" in str(e).lower():
            set_row(uid, blocked=1)
        else:
            logging.warning("сообщение 茶茶 не ушло (%s): %s", uid, e)


# ─── КНОПКИ И КОМАНДЫ ─────────────────────────────────────────────────────────

def settings_screen(uid):
    lang = ctx["lang_of"](uid)
    ctx["bot"].send_message(uid, C(lang, "cfg_title", cur=freq_label(lang, freq_of(uid))), reply_markup=ask_kb(lang))


def cb(c):
    p = c.data.split(":")
    uid = c.from_user.id
    bot = ctx["bot"]
    try:
        bot.answer_callback_query(c.id)
    except Exception:
        pass
    lang = ctx["lang_of"](uid)
    try:
        if p[1] == "f":
            n = max(0, min(3, int(p[2])))
            set_row(uid, freq=n, asked=1, blocked=0, last_cut=None)
            try:
                bot.edit_message_reply_markup(uid, c.message.message_id, reply_markup=None)
            except Exception:
                pass
            return bot.send_message(uid, C(lang, "saved", cur=freq_label(lang, n)))
        if p[1] == "cfg":
            return settings_screen(uid)
        if p[1] == "go":
            db.mark_sent(uid, f"cc_tap:{db.today()}")
            db.log_event(uid, "chacha")
            return ctx["open_practice"](uid)
    except Exception:
        logging.exception("茶茶: ошибка в кнопке %s", c.data)


def owner_on(m):
    if not is_owner(m.from_user.id):
        return
    set_mode("all")
    n = len(audience(datetime.now(db.TZ).date()))
    ctx["bot"].send_message(m.chat.id, f"🍵 Сообщения 茶茶 включены для всех (сейчас получателей: {n}). Первым людям придёт вопрос «как часто писать», потом по расписанию. Выключить: /chacha_off")


def owner_off(m):
    if not is_owner(m.from_user.id):
        return
    set_mode("pilot")
    ctx["bot"].send_message(m.chat.id, "🍵 Теперь 茶茶 пишет только тебе (проверочный режим). Включить всем: /chacha_on")


def owner_test(m):
    """Показать все тексты (по языкам) и настоящий пример с кнопками."""
    if not is_owner(m.from_user.id):
        return
    uid = m.from_user.id
    bot = ctx["bot"]
    names = {"morning": "Утро", "day": "День", "evening": "Вечер"}
    for lang in LANGS:
        parts = [f"<b>{lang.upper()}</b>"]
        for kind in ("morning", "day", "evening"):
            parts.append(f"\n<b>{names[kind]}</b>")
            for s in BANK[lang][kind]:
                parts.append("· " + s.format(name="Лазиза"))
        bot.send_message(uid, "\n".join(parts))
    u = db.get_user(uid) or {"lang": "ru", "name": "Лазиза"}
    lang = u.get("lang") if u.get("lang") in LANGS else "ru"
    bot.send_message(uid, "Так выглядит вопрос новому человеку и обычное сообщение:")
    bot.send_message(uid, C(lang, "ask"), reply_markup=ask_kb(lang))
    bot.send_message(uid, pick_text(uid, "morning", datetime.now(db.TZ).date(), lang, u), reply_markup=msg_kb(lang))
    bot.send_message(uid, f"Режим сейчас: <b>{'всем' if mode() == 'all' else 'проверочный (только тебе)'}</b>. Расписание: утро ~09:30, день ~14:00, вечер ~19:30 (у каждого сдвиг до 40 минут), ночью 22:00–09:00 тишина.")


def register(bot, owner_id, lang_of, open_practice):
    ctx.update(bot=bot, owner_id=owner_id, lang_of=lang_of, open_practice=open_practice)
    init_db()
    bot.message_handler(commands=["chacha"])(lambda m: settings_screen(m.from_user.id))
    bot.message_handler(commands=["chacha_on"])(owner_on)
    bot.message_handler(commands=["chacha_off"])(owner_off)
    bot.message_handler(commands=["chacha_test"])(owner_test)
    bot.callback_query_handler(func=lambda c: c.data.startswith("cc:"))(cb)
