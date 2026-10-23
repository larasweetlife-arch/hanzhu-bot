"""
Репетиторы, часть 2 (версия 23): перенос записи, отзывы об уроках, пробный урок, связь с Лазизой.

  · Перенос: ученик в «Мои записи» жмёт «Перенести», выбирает свободное время, репетитор подтверждает или отказывает.
  · Отзывы: после урока ученик ставит оценку и по желанию пишет текст; репетитор видит отзывы, рейтинг
    (по отзывам, которые разрешено показывать) виден в профиле, когда таких отзывов не меньше трёх.
  · Пробный урок: кнопка в профиле репетитора, заявка приходит ему в бот, он отвечает свайпом на сообщение.
  · Связь с Лазизой: кнопка «Написать Лазизе» (OWNER_CONTACT, по умолчанию nutlrz) и команда /tutor с объяснением.

Тексты для учеников — texts_v14.py (4 языка), для репетиторов и Лазизы — здесь, по-русски.
"""
import html
import logging
import os
from datetime import datetime, timedelta

from telebot import types

import booking
import db
import tutors
from texts import t

esc = lambda s: html.escape(str(s), quote=False)
ctx = {}
TX = {}                                    # диалоги: {uid: {"step": ..., ...}}

OWNER_CONTACT = (os.getenv("OWNER_CONTACT", "nutlrz") or "nutlrz").lstrip("@")
CONTACT_URL = f"https://t.me/{OWNER_CONTACT}"
CONTACT_LABEL = "💬 Написать Лазизе"
MOVE_LIMIT = timedelta(hours=3)            # ближе к уроку перенос только по договорённости
MOVE_SLOTS = 8
RATING_MIN_N = 3                           # столько отзывов с разрешением показать нужно, чтобы показать рейтинг

INFO_TEXT = """ℹ️ <b>Бот 汉助 для репетиторов</b>

Это Telegram-бот для изучения китайского (@hanzhu_chinesebot). Репетитор получает в нём инструменты для работы с учениками и появляется в списке «Записаться на занятия».

<b>Что умеет</b>
· Профиль: фото, о себе, цены, ссылка на занятие. Ученики видят его в боте.
· Запись на свободные часы и напоминание за 3 часа вам и ученику, со ссылкой на урок.
· Перенос урока: ученик просит, вы подтверждаете одной кнопкой.
· Домашние задания: текстом, а с уровня «Стандарт» ещё фото, видео, аудио и файлами.
· Записи уроков, которые ученик не может сохранить или переслать (с уровня «Стандарт»).
· Отзывы учеников после уроков и заявки на пробный урок.
· Список ваших учеников. Вы видите только своих.
· Реклама ваших занятий всем пользователям бота: команда /ad (платно звёздами, на уровне «Про» скидка 30%). Лазиза проверяет объявление перед отправкой.

<b>Как это устроено</b>
1. Лазиза добавляет вас в бот.
2. Вы открываете /myteacher и принимаете соглашение.
3. Заполняете профиль: имя, описание, цены, ссылку на урок, свободные часы.
4. Лазиза включает подписку на 30 или 90 дней, и профиль можно публиковать.
5. Ученики записываются, вы проводите занятия. Оплата за занятия идёт напрямую между вами и учеником: бот деньги не принимает.

<b>Уровни подписки</b>
{tiers}

Стоимость уровней и способ оплаты Лазиза называет лично. Если что-то непонятно или хочется обсудить подписку, нажмите кнопку ниже."""


# ─── ВСПОМОГАТЕЛЬНОЕ ──────────────────────────────────────────────────────────

def _one(sql, args=()):
    return tutors._one(sql, args)


def _all(sql, args=()):
    return tutors._all(sql, args)


def _run(sql, args=()):
    return tutors._run(sql, args)


def contact_row():
    return [(CONTACT_LABEL, "url:" + CONTACT_URL)]


def init_db():
    with db._conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS bk_moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT, booking_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
            new_start TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', created TEXT
        );
        CREATE TABLE IF NOT EXISTS bk_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT, teacher_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
            booking_id INTEGER, rating INTEGER NOT NULL, text TEXT, public INTEGER DEFAULT 0, created TEXT
        );
        CREATE INDEX IF NOT EXISTS ix_bkrv_t ON bk_reviews(teacher_id, public);
        """)


def who_of(uid):
    u = db.get_user(uid) or {}
    return esc(u.get("name") or "?") + (f" (@{esc(u['username'])})" if u.get("username") else "")


def targets(tc):
    """Кому сообщать о событии у этого репетитора: ему самому и Лазизе, как и о записях."""
    out = []
    for to in (tc.get("user_id"), ctx.get("owner_id")):
        if to and to not in out:
            out.append(to)
    return out


def info_text():
    return INFO_TEXT.format(tiers="\n".join(f"<b>{tutors.TIERS[n]}.</b> {tutors.TIER_INFO[n]}" for n in (1, 2, 3)))


def send_info(uid):
    return tutors.say(uid, info_text(), booking.ikb([contact_row()]))


def no_profile(uid):
    """/myteacher у человека без профиля."""
    return tutors.say(uid, "Профиль преподавателя пока не создан. Лазиза добавит тебя, и он появится здесь. "
                           "Как всё устроено: /tutor",
                      booking.ikb([contact_row()]))


# ─── ПЕРЕНОС ЗАПИСИ ───────────────────────────────────────────────────────────

def _my_booking(bid, uid):
    return _one("SELECT * FROM bookings WHERE id=? AND user_id=? AND status='active'", (bid, uid))


def move_start(c, bid):
    uid = c.from_user.id
    lang = ctx["lang_of"](uid)
    b = _my_booking(bid, uid)
    if not b:
        return booking.my_bookings(uid, c)
    tc = booking.teacher(b["teacher_id"])
    if not tc:
        return booking.my_bookings(uid, c)
    now = datetime.now(db.TZ)
    old = booking._parse(b["start"])
    back = [(t(lang, "bk_btn_back"), "bk:my")]
    write = _write_row(lang, tc)
    if old - now < MOVE_LIMIT:
        return booking.show(c, t(lang, "mv2_late"), booking.ikb([write, back] if write else [back]))
    if _one("SELECT 1 FROM bk_moves WHERE booking_id=? AND status='pending'", (bid,)):
        return booking.show(c, t(lang, "mv2_wait"), booking.ikb([back]))
    slots = [s for s in booking.free_slots(b["teacher_id"]) if s != old][:MOVE_SLOTS]
    if not slots:
        return booking.show(c, t(lang, "mv2_none"), booking.ikb([write, back] if write else [back]))
    rows, row = [], []
    for s in slots:
        row.append((f"{booking.day_label(s, lang)} {s:%H:%M}", f"tq:mc:{bid}:{s:%Y%m%d%H%M}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append(back)
    booking.show(c, t(lang, "mv2_pick", name=esc(tc["name"]), now=f"{booking.day_label(old, lang)}, {old:%H:%M}"), booking.ikb(rows))


def _write_row(lang, tc):
    """Кнопка «Написать репетитору», если у него открыта связь."""
    un = booking.contact_username(tc)
    return [(t(lang, "mv2_write"), f"url:https://t.me/{un}")] if un else None


def move_request(c, bid, stamp):
    uid = c.from_user.id
    lang = ctx["lang_of"](uid)
    b = _my_booking(bid, uid)
    if not b:
        return booking.my_bookings(uid, c)
    tc = booking.teacher(b["teacher_id"])
    new = booking._dt(stamp)
    now = datetime.now(db.TZ)
    old = booking._parse(b["start"])
    if not tc or old - now < MOVE_LIMIT or _one("SELECT 1 FROM bk_moves WHERE booking_id=? AND status='pending'", (bid,)):
        return move_start(c, bid)
    if new not in booking.free_slots(b["teacher_id"]):
        booking.bot_answer(c, t(lang, "mv2_gone"), True)
        return move_start(c, bid)
    mid = _run("INSERT INTO bk_moves (booking_id, user_id, new_start, created) VALUES (?,?,?,?)",
               (bid, uid, new.strftime(booking.FMT), tutors.now_s()))
    booking.show(c, t(lang, "mv2_sent"), booking.ikb([[(t(lang, "bk_btn_back"), "bk:my")]]))
    text = (f"🔁 <b>Просьба перенести урок</b>\n\n{who_of(uid)}\n"
            f"Сейчас: {booking.day_label(old, 'ru')}, {old:%H:%M}\n"
            f"Хочет: <b>{booking.day_label(new, 'ru')}, {new:%H:%M}</b> (Ташкент)")
    kb = booking.ikb([[("✅ Подтвердить", f"tq:my:{mid}"), ("✖️ Отказать", f"tq:mn:{mid}")]])
    for to in targets(tc):
        try:
            ctx["bot"].send_message(to, text, reply_markup=kb)
        except Exception as e:
            logging.warning("просьба о переносе %s не ушла: %s", to, e)


def move_answer(c, mid, ok):
    uid = c.from_user.id
    bot = ctx["bot"]
    m = _one("SELECT * FROM bk_moves WHERE id=?", (mid,))
    b = _one("SELECT * FROM bookings WHERE id=?", (m["booking_id"],)) if m else None
    tc = booking.teacher(b["teacher_id"]) if b else None
    if not m or not tc or uid not in targets(tc):
        return
    if m["status"] != "pending":
        return booking.bot_answer(c, "Уже обработано")
    student = m["user_id"]
    lang = ctx["lang_of"](student)
    new = booking._dt(datetime.strptime(m["new_start"], booking.FMT).strftime("%Y%m%d%H%M"))
    old = booking._parse(b["start"])
    verdict = None
    if ok and b["status"] != "active":
        ok, verdict = False, "Эта запись уже отменена, переносить нечего."
    elif ok and new not in booking.free_slots(b["teacher_id"]):
        ok, verdict = False, "Это время уже занято, ученику отправлен отказ."
    _run("UPDATE bk_moves SET status=? WHERE id=?", ("ok" if ok else "no", mid))
    booking.bot_answer(c, "Готово")
    if ok:
        now = datetime.now(db.TZ)
        with db._conn() as cc:
            cc.execute("UPDATE bookings SET start=?, reminded=? WHERE id=?",
                       (m["new_start"], 1 if new - now < booking.REMIND_BEFORE else 0, b["id"]))
        verdict = f"✅ Перенесено: {who_of(student)}, {booking.day_label(new, 'ru')} {new:%H:%M}"
        text = t(lang, "mv2_ok", name=esc(tc["name"]), day=booking.day_label(new, lang), time=f"{new:%H:%M}") + "\n\n" \
            + booking.link_block(lang, tc, "bk_link", "bk_nolink")
    else:
        verdict = verdict or f"✖️ Отказано: {who_of(student)}"
        text = t(lang, "mv2_no", name=esc(tc["name"]), day=booking.day_label(old, lang), time=f"{old:%H:%M}")
    try:
        bot.edit_message_text(verdict, c.message.chat.id, c.message.message_id)
    except Exception:
        pass
    try:
        bot.send_message(student, text, disable_web_page_preview=True)
    except Exception:
        pass


# ─── ОТЗЫВЫ ───────────────────────────────────────────────────────────────────

def review_hook(now):
    """Раз в минуту: после прошедшего урока один раз в месяц на репетитора просим оценку."""
    lo = (now - timedelta(days=3)).strftime(booking.FMT)
    for b in _all("SELECT * FROM bookings WHERE status='active' AND start<? AND start>?", (now.strftime(booking.FMT), lo)):
        end = booking._parse(b["start"]) + timedelta(minutes=b["duration"])
        if now < end + timedelta(minutes=10):
            continue
        tc = booking.teacher(b["teacher_id"])
        uid = b["user_id"]
        if not tc or tutors.is_owner_tc(tc) or tc.get("user_id") == uid:
            continue
        key = f"bkrv:{tc['id']}:{now:%Y%m}"
        if db.was_sent(uid, key) or db.was_sent(uid, f"bkrvb:{b['id']}"):
            continue
        db.mark_sent(uid, key)
        db.mark_sent(uid, f"bkrvb:{b['id']}")
        lang = ctx["lang_of"](uid)
        kb = booking.ikb([[("⭐" * n, f"tq:r:{b['id']}:{n}") for n in (1, 2, 3, 4, 5)]])
        try:
            ctx["bot"].send_message(uid, t(lang, "rvt_ask", name=esc(tc["name"])), reply_markup=kb)
        except Exception as e:
            logging.warning("просьба об отзыве %s не ушла: %s", uid, e)


def rating_of(tid):
    r = _one("SELECT AVG(rating) a, COUNT(*) n FROM bk_reviews WHERE teacher_id=? AND public=1", (tid,))
    return (round(r["a"], 1), r["n"]) if r and r["n"] else (None, 0)


def post_line(lang, tc):
    if tutors.is_owner_tc(tc):
        return ""
    avg, n = rating_of(tc["id"])
    return t(lang, "tc_rating", avg=avg, n=n) if n >= RATING_MIN_N else ""


def post_rows(lang, tc):
    if tutors.is_owner_tc(tc):
        return [(t(lang, "trl_btn"), "bk:trial")]            # у самой Лазизы уже есть свой пробный урок
    return [(t(lang, "trl_btn"), f"tq:tr:{tc['id']}")]


def rating_chosen(c, bid, n):
    uid = c.from_user.id
    lang = ctx["lang_of"](uid)
    b = _my_booking(bid, uid) or _one("SELECT * FROM bookings WHERE id=? AND user_id=?", (bid, uid))
    if not b or not 1 <= n <= 5:
        return
    if _one("SELECT 1 FROM bk_reviews WHERE booking_id=? AND user_id=?", (bid, uid)):
        return booking.bot_answer(c)
    TX[uid] = {"step": "rv_text", "bid": bid, "tid": b["teacher_id"], "rating": n}
    booking.bot_answer(c)
    _edit(c, t(lang, "rvt_text"))


def _edit(c, text, kb=None):
    try:
        ctx["bot"].edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=kb)
    except Exception:
        ctx["bot"].send_message(c.message.chat.id, text, reply_markup=kb)


def review_public(c, flag):
    uid = c.from_user.id
    lang = ctx["lang_of"](uid)
    d = TX.get(uid)
    booking.bot_answer(c)
    if not d or d.get("step") != "rv_public":
        return
    TX.pop(uid, None)
    tc = booking.teacher(d["tid"])
    _run("INSERT INTO bk_reviews (teacher_id, user_id, booking_id, rating, text, public, created) VALUES (?,?,?,?,?,?,?)",
         (d["tid"], uid, d["bid"], d["rating"], d["text"], 1 if flag else 0, tutors.now_s()))
    _edit(c, t(lang, "rvt_thanks"))
    if tc and tc.get("user_id"):
        try:
            ctx["bot"].send_message(tc["user_id"], f"⭐ <b>Новый отзыв</b>: {d['rating']}/5\n{who_of(uid)}\n"
                                    f"{esc(d['text']) or '—'}\nМожно показывать в профиле: {'да' if flag else 'нет'}")
        except Exception:
            pass


def reviews_screen(uid, tid, mid=None):
    tc = booking.teacher(tid)
    if not tc or not (tc["user_id"] == uid or tutors.is_owner(uid)):
        return
    rows = _all("SELECT * FROM bk_reviews WHERE teacher_id=? ORDER BY id DESC LIMIT 10", (tid,))
    avg_all = _one("SELECT AVG(rating) a, COUNT(*) n FROM bk_reviews WHERE teacher_id=?", (tid,))
    lines = [f"⭐ <b>Отзывы: {esc(tc['name'])}</b>", ""]
    if not rows:
        lines.append("Пока отзывов нет. Просьба об отзыве уходит ученику после урока, не чаще раза в месяц.")
    else:
        lines.append(f"Средняя оценка: {round(avg_all['a'], 1)} (всего {avg_all['n']}). Последние 10:")
        lines.append("")
        for r in rows:
            lines.append(f"{'⭐' * r['rating']} {who_of(r['user_id'])}" + ("" if r["public"] else " · 🔒 только вам"))
            if r["text"]:
                lines.append(esc(r["text"]))
            lines.append("")
        lines.append(f"Рейтинг в профиле появится, когда будет {RATING_MIN_N} отзыва с разрешением показывать.")
    booking.put(uid, mid, "\n".join(lines).strip(), booking.ikb([[("⬅️ К профилю", f"bt:e:{tid}")]]))


# ─── ПРОБНЫЙ УРОК ─────────────────────────────────────────────────────────────

def trial_start(c, tid):
    uid = c.from_user.id
    lang = ctx["lang_of"](uid)
    tc = booking.teacher(tid)
    booking.bot_answer(c)
    if not tc or not tc["active"]:
        return booking.start(uid, c)
    if db.was_sent(uid, f"trial:{tid}:{db.today()}"):
        return ctx["bot"].send_message(uid, t(lang, "trl_again"))
    TX[uid] = {"step": "trial", "tid": tid}
    ctx["bot"].send_message(uid, t(lang, "trl_ask"))


def trial_finish(uid, txt):
    d = TX.pop(uid, None)
    lang = ctx["lang_of"](uid)
    tc = booking.teacher(d["tid"]) if d else None
    if not tc:
        return
    db.mark_sent(uid, f"trial:{d['tid']}:{db.today()}")
    u = db.get_user(uid) or {}
    text = (f"📝 <b>Заявка на пробный урок</b>\n\n{who_of(uid)}\nЯзык бота: {esc(u.get('lang') or '—')} · Уровень: {esc(u.get('level') or '—')}\n\n"
            f"{esc(txt[:600])}\n\n↩️ Ответь на это сообщение (свайпом), и ответ придёт ученику.")
    to = tc.get("user_id") or ctx.get("owner_id")
    try:
        sent = ctx["bot"].send_message(to, text)
        _run("INSERT OR REPLACE INTO t_inbox (chat_id, msg_id, user_id) VALUES (?,?,?)", (to, sent.message_id, uid))
        if to == ctx.get("owner_id"):
            db.save_inbox(sent.message_id, uid)
    except Exception as e:
        logging.warning("заявка на пробный урок не ушла: %s", e)
    ctx["bot"].send_message(uid, t(lang, "trl_sent", name=esc(tc["name"])), reply_markup=ctx["kb_main"](uid) if ctx.get("kb_main") else None)


# ─── ТЕКСТ И КНОПКИ ───────────────────────────────────────────────────────────

def on_text(m, txt):
    """Вызывается из tutors._on_text. True — сообщение обработано здесь."""
    uid = m.from_user.id
    d = TX.get(uid)
    if not d:
        return False
    if tutors._is_menu(txt, uid):
        TX.pop(uid, None)
        return False
    lang = ctx["lang_of"](uid)
    if d["step"] == "trial":
        trial_finish(uid, txt)
        return True
    if d["step"] == "rv_text":
        d["text"] = "" if txt == "-" else txt[:500]
        d["step"] = "rv_public"
        ctx["bot"].send_message(uid, t(lang, "rvt_public"),
                                reply_markup=booking.ikb([[(t(lang, "rvt_yes"), "tq:rp:1"), (t(lang, "rvt_no"), "tq:rp:0")]]))
        return True
    return False


def cb_tx(c):
    p = c.data.split(":")
    act = p[1]
    uid = c.from_user.id
    try:
        if act == "mv":
            booking.bot_answer(c); return move_start(c, int(p[2]))
        if act == "mc":
            booking.bot_answer(c); return move_request(c, int(p[2]), p[3])
        if act in ("my", "mn"):
            return move_answer(c, int(p[2]), act == "my")
        if act == "r":
            return rating_chosen(c, int(p[2]), int(p[3]))
        if act == "rp":
            return review_public(c, p[2] == "1")
        if act == "tr":
            return trial_start(c, int(p[2]))
        if act == "rl":
            booking.bot_answer(c); return reviews_screen(uid, int(p[2]), c.message.message_id)
        if act == "info":
            booking.bot_answer(c); return send_info(uid)
        booking.bot_answer(c)
    except Exception:
        logging.exception("репетиторы (часть 2): ошибка в кнопке %s", c.data)
        booking.bot_answer(c)


def hook(now):
    try:
        review_hook(now)
    except Exception:
        logging.exception("просьбы об отзывах: ошибка")


def register(bot, owner_id, lang_of, kb_main=None):
    ctx.update(bot=bot, owner_id=owner_id, lang_of=lang_of, kb_main=kb_main)
    init_db()
    booking.hooks.update(post_line=post_line, post_rows=post_rows, no_profile=no_profile, x_text=on_text)

    @bot.message_handler(commands=["tutor"])
    def _tutor(m):
        send_info(m.from_user.id)

    bot.callback_query_handler(func=lambda c: c.data.startswith("tq:"))(cb_tx)
