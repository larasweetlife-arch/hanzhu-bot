"""
汉助 HanZhu — Chinese Learning Assistant
Создан Лазизой Ропижоновой · @qing_laoshi

Запуск:  python bot.py
"""
import os


def _read_env():
    """Читает .env без внешних библиотек. На хостинге переменные задаются в панели."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

_read_env()

import html
import random
import logging
import threading
from datetime import datetime, timedelta

import telebot
from telebot import types

import db
import scheduler
import content as C
from texts import t, T, LANG_PROMPT, WEEKDAYS

TOKEN = os.environ.get("BOT_TOKEN", "").strip()
OWNER_ID = int(os.environ.get("OWNER_ID", "0") or 0)

if not TOKEN or TOKEN.startswith("ВСТАВЬ"):
    raise SystemExit(
        "\n❌ Не найден токен бота.\n"
        "   Дома: открой файл .env и вставь токен в строку BOT_TOKEN=\n"
        "   На хостинге: добавь переменную BOT_TOKEN в настройках.\n")

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
db.init()

esc = html.escape                      # всё, что вводит человек, экранируем перед отправкой
STATE = {}                             # диалоги: {user_id: {"step": ..., "data": {...}}}
ONBOARD_STEPS = {"name", "source", "level"}


def lang_of(uid):
    return (db.get_user(uid) or {}).get("lang") or "ru"

def is_owner(uid):
    return bool(OWNER_ID) and uid == OWNER_ID

def notify_owner(text, **kw):
    if not OWNER_ID:
        return None
    try:
        return bot.send_message(OWNER_ID, text, **kw)
    except Exception as e:
        logging.warning("owner notify failed: %s", e)
        return None


# ─── КЛАВИАТУРЫ ───────────────────────────────────────────────────────────────

def kb_main(uid):
    lang = lang_of(uid)
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.row(t(lang, "b_word"), t(lang, "b_chengyu"))
    k.row(t(lang, "b_fact"), t(lang, "b_tr"))
    k.row(t(lang, "b_progress"), t(lang, "b_lang"))
    k.row(t(lang, "b_channel"), t(lang, "b_help"))
    return k

def kb_langs():
    k = types.InlineKeyboardMarkup(row_width=2)
    k.add(types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang:ru"),
          types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang:uz"),
          types.InlineKeyboardButton("🇬🇧 English", callback_data="lang:en"),
          types.InlineKeyboardButton("🇨🇳 中文", callback_data="lang:zh"))
    return k

def kb_list(prefix, items):
    k = types.InlineKeyboardMarkup(row_width=1)
    for i, s in enumerate(items):
        k.add(types.InlineKeyboardButton(s, callback_data=f"{prefix}:{i}"))
    return k


# ─── ЗНАКОМСТВО: язык → имя → откуда узнал → уровень ─────────────────────────

@bot.message_handler(commands=["start"])
def cmd_start(m):
    uid = m.from_user.id
    STATE.pop(uid, None)
    u = db.get_user(uid)
    if u and u.get("level"):
        return bot.send_message(uid, t(u["lang"], "menu"), reply_markup=kb_main(uid))
    STATE[uid] = {"step": "lang", "data": {}}
    bot.send_message(uid, LANG_PROMPT, reply_markup=kb_langs())


@bot.callback_query_handler(func=lambda c: c.data.startswith("lang:"))
def cb_lang(c):
    uid = c.from_user.id
    lang = c.data.split(":")[1]
    bot.answer_callback_query(c.id)
    if lang not in T:
        return
    st = STATE.get(uid)
    if st and st["step"] == "lang":                 # первый запуск
        st["data"]["lang"] = lang
        st["step"] = "name"
        bot.edit_message_text(t(lang, "ask_name"), uid, c.message.message_id)
    elif st and st["step"] in ONBOARD_STEPS:        # старая кнопка посреди знакомства
        return
    else:                                           # смена языка у уже знакомого
        db.save_user(uid, lang=lang)
        bot.edit_message_text(t(lang, "lang_changed"), uid, c.message.message_id)
        bot.send_message(uid, t(lang, "menu"), reply_markup=kb_main(uid))


@bot.callback_query_handler(func=lambda c: c.data.startswith("src:"))
def cb_source(c):
    uid = c.from_user.id
    st = STATE.get(uid)
    bot.answer_callback_query(c.id)
    if not st or st["step"] != "source":
        return
    try:
        st["data"]["source"] = T["ru"]["sources"][int(c.data.split(":")[1])]
    except (ValueError, IndexError):
        return
    st["step"] = "level"
    lang = st["data"]["lang"]
    bot.edit_message_text(t(lang, "ask_level"), uid, c.message.message_id,
                          reply_markup=kb_list("lvl", T[lang]["levels"]))


@bot.callback_query_handler(func=lambda c: c.data.startswith("lvl:"))
def cb_level(c):
    uid = c.from_user.id
    st = STATE.get(uid)
    bot.answer_callback_query(c.id)
    if not st or st["step"] != "level":
        return
    try:
        level = T["ru"]["levels"][int(c.data.split(":")[1])]
    except (ValueError, IndexError):
        return
    STATE.pop(uid, None)
    d = st["data"]
    lang = d["lang"]
    db.save_user(uid, name=d.get("name", ""), username=c.from_user.username or "",
                 lang=lang, level=level, source=d.get("source", ""))
    bot.edit_message_text(t(lang, "done", name=esc(d.get("name", ""))), uid, c.message.message_id)
    bot.send_message(uid, t(lang, "menu"), reply_markup=kb_main(uid))
    notify_owner(
        f"🆕 <b>Новый пользователь</b>\n{esc(d.get('name',''))} (@{esc(c.from_user.username or '—')})\n"
        f"Язык: {lang} · Уровень: {level}\nИсточник: {esc(d.get('source',''))}\n"
        f"ID: <code>{uid}</code>")


# ─── ПРОГРЕСС УЧЕНИКА ─────────────────────────────────────────────────────────

def bar(pct, width=10):
    filled = max(0, min(width, round(pct / 100 * width)))
    return "█" * filled + "░" * (width - filled)


def progress_text(uid, lang):
    done, paid, left = db.balance(uid)
    ts = db.tests(uid)
    sched = db.get_schedule(uid)
    if done == 0 and paid == 0 and not ts:
        return t(lang, "no_progress")

    out = [f"<b>{t(lang,'p_title')}</b>", "",
           f"{t(lang,'p_lessons')}: <b>{done}</b>",
           f"{t(lang,'p_paid')}: <b>{paid}</b>"]
    if left >= 0:
        out.append(f"{t(lang,'p_left')}: <b>{left}</b>")
    else:   # ученику долг не показываем цифрой — мягкая просьба, детали обсуждаешь ты
        out.append(f"💬 {t(lang,'p_renew')}")

    if sched:
        days = ", ".join(f"{WEEKDAYS[lang][s['weekday']]} {s['time']}" for s in sched)
        out.append(f"{t(lang,'p_sched')}: {days}")

    if ts:
        out += ["", f"<b>{t(lang,'p_tests')}</b>", ""]
        for r in ts[-6:]:
            pct = r["score"] / r["max_score"] * 100
            out.append(f"<code>{bar(pct)}</code> {pct:.0f}%  ·  {esc(r['title'] or '—')}")
            out.append(f"<i>{r['date']}: {r['score']:g}/{r['max_score']:g}</i>")
        p = db.progress(uid)
        if p and p["count"] > 1:
            arrow = "📈" if p["delta"] > 0 else ("📉" if p["delta"] < 0 else "➖")
            out += ["", f"{t(lang,'p_first')}: {p['first']:.0f}%   {t(lang,'p_last')}: {p['last']:.0f}%",
                    f"{arrow} {t(lang,'p_growth')}: <b>{p['delta']:+.0f}</b> {t(lang,'p_pp')}"]
    else:
        out += ["", t(lang, "p_no_tests")]

    last = db.last_lessons(uid, 3)
    if last:
        out += ["", f"<b>{t(lang,'p_recent')}</b>"]
        for l in last:
            out.append(f"· {l['date']}" + (f" · {esc(l['topic'])}" if l["topic"] else ""))
    return "\n".join(out)


# ─── КОНТЕНТ ──────────────────────────────────────────────────────────────────

def send_word(uid):
    db.log_event(uid, "word"); lang = lang_of(uid)
    w = random.choice(C.WORDS)
    bot.send_message(uid, f"{t(lang,'word')}\n\n<b>{w['zh']}</b>\n🔊 <code>{w['py']}</code>\n"
                          f"📖 {esc(w.get(lang, w['ru']))}")

def send_chengyu(uid):
    db.log_event(uid, "chengyu"); lang = lang_of(uid)
    c = random.choice(C.CHENGYU)
    bot.send_message(uid, f"{t(lang,'chengyu')}\n\n<b>{c['zh']}</b>\n🔊 <code>{c['py']}</code>\n\n"
                          f"{esc(c.get(lang, c['ru']))}\n\n<i>{c['ex']}</i>")

def send_fact(uid):
    db.log_event(uid, "fact"); lang = lang_of(uid)
    f = random.choice(C.FACTS)
    bot.send_message(uid, f"{t(lang,'fact')}\n\n{esc(f.get(lang, f['ru']))}")

def ask_translate(uid):
    STATE[uid] = {"step": "translate", "data": {}}
    bot.send_message(uid, t(lang_of(uid), "tr_ask"))

def ask_language(uid):
    STATE.pop(uid, None)
    bot.send_message(uid, LANG_PROMPT, reply_markup=kb_langs())

def send_progress(uid):
    db.log_event(uid, "progress")
    bot.send_message(uid, progress_text(uid, lang_of(uid)))


@bot.message_handler(commands=["menu"])
def cmd_menu(m):
    bot.send_message(m.chat.id, t(lang_of(m.from_user.id), "menu"), reply_markup=kb_main(m.from_user.id))

@bot.message_handler(commands=["word"])
def cmd_word(m): send_word(m.from_user.id)

@bot.message_handler(commands=["chengyu"])
def cmd_chengyu(m): send_chengyu(m.from_user.id)

@bot.message_handler(commands=["fact"])
def cmd_fact(m): send_fact(m.from_user.id)

@bot.message_handler(commands=["translate"])
def cmd_translate(m): ask_translate(m.from_user.id)

@bot.message_handler(commands=["progress"])
def cmd_progress(m): send_progress(m.from_user.id)

@bot.message_handler(commands=["lang"])
def cmd_lang(m): ask_language(m.from_user.id)

@bot.message_handler(commands=["help"])
def cmd_help(m):
    bot.send_message(m.chat.id, t(lang_of(m.from_user.id), "help"))


# ─── НАПОМИНАНИЯ И ПОДТВЕРЖДЕНИЕ ЗАНЯТИЙ ──────────────────────────────────────

def send_reminder(kind, slot, lesson):
    uid, lang = slot["user_id"], slot["lang"] or "ru"
    time_s = lesson.strftime("%H:%M")
    iso = lesson.strftime("%Y-%m-%dT%H:%M")
    if kind == "24h":
        today = datetime.now(db.TZ).date()
        day = t(lang, "day_today") if lesson.date() == today else t(lang, "day_tomorrow")
        k = types.InlineKeyboardMarkup(row_width=2)
        k.add(types.InlineKeyboardButton(t(lang, "btn_yes"), callback_data=f"att:yes:{iso}"),
              types.InlineKeyboardButton(t(lang, "btn_no"), callback_data=f"att:no:{iso}"))
        bot.send_message(uid, t(lang, "remind24", day=day, time=time_s), reply_markup=k)
    else:
        txt = t(lang, "remind1", time=time_s)
        if slot.get("zoom_link"):
            txt += t(lang, "remind1_link", link=esc(slot["zoom_link"]))
        bot.send_message(uid, txt)


@bot.callback_query_handler(func=lambda c: c.data.startswith("att:"))
def cb_attendance(c):
    uid = c.from_user.id
    lang = lang_of(uid)
    bot.answer_callback_query(c.id)
    try:
        _, answer, iso = c.data.split(":", 2)
        lesson = datetime.strptime(iso, "%Y-%m-%dT%H:%M").replace(tzinfo=db.TZ)
    except ValueError:
        return
    try:
        bot.edit_message_reply_markup(uid, c.message.message_id, reply_markup=None)
    except Exception:
        pass
    now = datetime.now(db.TZ)
    if lesson <= now:
        return bot.send_message(uid, t(lang, "att_past"))

    u = db.get_user(uid) or {}
    name = esc(u.get("name") or "?")
    when = lesson.strftime("%d.%m %H:%M")
    if answer == "yes":
        db.save_attendance(uid, iso, "yes")
        bot.send_message(uid, t(lang, "att_yes"))
        notify_owner(f"✅ {name} подтвердил(а) занятие {when}")
    else:
        STATE[uid] = {"step": "absent_reason",
                      "data": {"iso": iso, "late": (lesson - now) < timedelta(hours=3)}}
        bot.send_message(uid, t(lang, "att_ask"))


def send_backup(chat_id, caption="🗄 Копия базы. Сохрани файл в надёжное место."):
    dest = db.DATA_DIR / f"hanzhu_backup_{db.today()}.db"
    try:
        db.make_backup(dest)
        with open(dest, "rb") as f:
            bot.send_document(chat_id, f, caption=caption)
    finally:
        if dest.exists():
            dest.unlink()


def send_weekly(now):
    since = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    lessons = db.lessons_count_since(since)
    new = db.users_since(since)
    absent = db.absences_since(since)
    top = db.top_events_since(since)
    labels = {"word": "Слово дня", "chengyu": "Чэнъюй", "fact": "Факт", "progress": "Прогресс",
              "translate": "Перевод"}
    low = []
    for s in db.students():
        _, _, left = db.balance(s["user_id"])
        if left <= 0:
            low.append(f"· {esc(s['name'])}: " + (f"остаток 0" if left == 0 else f"долг {abs(left)}"))
    txt = [f"📊 <b>Итоги недели</b>", "",
           f"Уроков проведено: <b>{lessons}</b>", f"Новых в боте: <b>{new}</b>",
           f"Отмен от учеников: <b>{absent}</b>"]
    if top:
        txt += ["", "<b>Чем пользуются чаще всего</b>"]
        txt += [f"· {labels.get(e['kind'], e['kind'])}: {e['n']}" for e in top]
    if low:
        txt += ["", "<b>Пора напомнить об оплате</b>"] + low
    notify_owner("\n".join(txt))
    if OWNER_ID:
        try:
            send_backup(OWNER_ID, "🗄 Копия базы за неделю. Старые можно удалять.")
        except Exception as e:
            logging.warning("не удалось отправить копию базы: %s", e)


# ─── АДМИНКА ──────────────────────────────────────────────────────────────────

@bot.message_handler(commands=["admin"])
def cmd_admin(m):
    if not is_owner(m.from_user.id):
        return
    STATE.pop(m.from_user.id, None)
    k = types.InlineKeyboardMarkup(row_width=1)
    k.add(types.InlineKeyboardButton("👥 Мои ученики", callback_data="a:students"),
          types.InlineKeyboardButton("➕ Сделать учеником", callback_data="a:make"),
          types.InlineKeyboardButton("📊 Статистика бота", callback_data="a:stats"))
    bot.send_message(m.chat.id, f"<b>Панель преподавателя</b>\n\nВсего в боте: {len(db.all_users())}\n"
                                f"Учеников: {len(db.students())}", reply_markup=k)


@bot.message_handler(commands=["backup"])
def cmd_backup(m):
    if is_owner(m.from_user.id):
        send_backup(m.chat.id)


def owner_only(handler):
    def wrapper(c):
        if not is_owner(c.from_user.id):
            return bot.answer_callback_query(c.id)
        return handler(c)
    return wrapper


@bot.callback_query_handler(func=lambda c: c.data == "a:stats")
@owner_only
def cb_stats(c):
    users = db.all_users()
    by_lang, by_src = {}, {}
    for u in users:
        by_lang[u["lang"]] = by_lang.get(u["lang"], 0) + 1
        s = u["source"] or "—"
        by_src[s] = by_src.get(s, 0) + 1
    txt = [f"<b>Статистика</b>\n", f"Пользователей: {len(users)}", "", "<b>Языки</b>"]
    txt += [f"· {k}: {v}" for k, v in sorted(by_lang.items(), key=lambda x: -x[1])]
    txt.append("\n<b>Откуда узнали</b>")
    txt += [f"· {esc(k)}: {v}" for k, v in sorted(by_src.items(), key=lambda x: -x[1])]
    bot.send_message(c.message.chat.id, "\n".join(txt))
    bot.answer_callback_query(c.id)


@bot.callback_query_handler(func=lambda c: c.data == "a:make")
@owner_only
def cb_make(c):
    users = [u for u in db.all_users() if not u["is_student"]]
    bot.answer_callback_query(c.id)
    if not users:
        return bot.send_message(c.message.chat.id, "Все пользователи уже отмечены учениками.")
    k = types.InlineKeyboardMarkup(row_width=1)
    for u in users[:40]:
        k.add(types.InlineKeyboardButton(f"{u['name'] or '—'} (@{u['username'] or u['user_id']})",
                                         callback_data=f"mk:{u['user_id']}"))
    bot.send_message(c.message.chat.id, "Кого отметить учеником?", reply_markup=k)


@bot.callback_query_handler(func=lambda c: c.data.startswith("mk:"))
@owner_only
def cb_make_do(c):
    uid = int(c.data.split(":")[1])
    db.save_user(uid, is_student=1)
    bot.edit_message_text(f"✅ {esc((db.get_user(uid) or {}).get('name',''))} теперь ученик.",
                          c.message.chat.id, c.message.message_id)
    bot.answer_callback_query(c.id, "Готово")


@bot.callback_query_handler(func=lambda c: c.data == "a:students")
@owner_only
def cb_students(c):
    st = db.students()
    bot.answer_callback_query(c.id)
    if not st:
        return bot.send_message(c.message.chat.id,
                                "Учеников пока нет. Отметь кого-нибудь через «➕ Сделать учеником».")
    k = types.InlineKeyboardMarkup(row_width=1)
    for u in st:
        done, paid, left = db.balance(u["user_id"])
        k.add(types.InlineKeyboardButton(
            f"{'⚠️' if left <= 0 else '✅'} {u['name']} · {done} ур. · остаток {left}",
            callback_data=f"st:{u['user_id']}"))
    bot.send_message(c.message.chat.id, "<b>Ученики</b>", reply_markup=k)


def student_card(uid):
    u = db.get_user(uid)
    done, paid, left = db.balance(uid)
    p = db.progress(uid)
    sched = db.get_schedule(uid)
    days = ", ".join(f"{WEEKDAYS['ru'][s['weekday']]} {s['time']}" for s in sched) or "не задано"
    lines = [f"<b>{esc(u['name'] or '—')}</b>  @{esc(u['username'] or '—')}",
             f"Уровень: {esc(u['level'] or '—')}", "",
             f"Проведено: <b>{done}</b>", f"Оплачено: <b>{paid}</b>",
             f"Остаток: <b>{left}</b>" if left >= 0 else f"⚠️ Долг: <b>{abs(left)}</b>", "",
             f"Расписание: {days}", f"Zoom: {'есть' if u.get('zoom_link') else 'не задан'}"]
    if p:
        lines += ["", f"Тестов: {p['count']}",
                  f"Было {p['first']:.0f}% → стало {p['last']:.0f}% ({p['delta']:+.0f} п.п.)"]
    return "\n".join(lines)


@bot.callback_query_handler(func=lambda c: c.data.startswith("st:"))
@owner_only
def cb_student(c):
    uid = int(c.data.split(":")[1])
    k = types.InlineKeyboardMarkup(row_width=2)
    k.add(types.InlineKeyboardButton("✅ Урок проведён", callback_data=f"les:{uid}"),
          types.InlineKeyboardButton("💰 Записать оплату", callback_data=f"pay:{uid}"),
          types.InlineKeyboardButton("📝 Результат теста", callback_data=f"tst:{uid}"),
          types.InlineKeyboardButton("↩️ Отменить урок", callback_data=f"undo:{uid}"),
          types.InlineKeyboardButton("🗓 Расписание", callback_data=f"sch:{uid}"),
          types.InlineKeyboardButton("🔗 Ссылка Zoom", callback_data=f"zm:{uid}"))
    k.add(types.InlineKeyboardButton("💬 Напомнить об оплате", callback_data=f"nd:{uid}"))
    bot.send_message(c.message.chat.id, student_card(uid), reply_markup=k)
    bot.answer_callback_query(c.id)


def _ask(c, step, prompt):
    uid = int(c.data.split(":")[1])
    STATE[c.from_user.id] = {"step": step, "data": {"uid": uid}}
    bot.send_message(c.message.chat.id, prompt)
    bot.answer_callback_query(c.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("les:"))
@owner_only
def cb_lesson(c):
    _ask(c, "lesson_topic", "Тема урока? Напиши коротко, или отправь «-», чтобы без темы.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("pay:"))
@owner_only
def cb_pay(c):
    _ask(c, "pay_count", "За сколько уроков оплата? Просто число.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("tst:"))
@owner_only
def cb_test(c):
    _ask(c, "test_input", "Запиши результат так:\n<code>Название | набрано | максимум</code>\n\n"
                          "Например:\n<code>Лексика HSK2 | 17 | 20</code>")

@bot.callback_query_handler(func=lambda c: c.data.startswith("sch:"))
@owner_only
def cb_sched(c):
    _ask(c, "sched_input", "Когда занятия? Например:\n<code>пн 18:00, ср 18:00</code>\n\n"
                           "Время по Ташкенту. Чтобы убрать расписание, отправь «-».")

@bot.callback_query_handler(func=lambda c: c.data.startswith("zm:"))
@owner_only
def cb_zoom(c):
    _ask(c, "zoom_input", "Пришли ссылку на Zoom (или «-», чтобы убрать).")

@bot.callback_query_handler(func=lambda c: c.data.startswith("undo:"))
@owner_only
def cb_undo(c):
    uid = int(c.data.split(":")[1])
    ok = db.undo_last_lesson(uid)
    bot.answer_callback_query(c.id, "Последний урок удалён" if ok else "Уроков нет")
    if ok:
        bot.send_message(c.message.chat.id, student_card(uid))

@bot.callback_query_handler(func=lambda c: c.data.startswith("nd:"))
@owner_only
def cb_nudge(c):
    uid = int(c.data.split(":")[1])
    try:
        bot.send_message(uid, t(lang_of(uid), "pay_nudge"))
        bot.answer_callback_query(c.id, "Отправила")
    except Exception:
        bot.answer_callback_query(c.id, "Не получилось: ученик мог закрыть бота")


def lesson_balance_alert(sid):
    _, _, left = db.balance(sid)
    if left < 0:
        notify_owner(f"⚠️ У ученика долг: {abs(left)} ур.")
    elif left == 0:
        notify_owner("🟡 Оплаченные уроки закончились. Пора напомнить об оплате.")
    elif left == 1:
        notify_owner("ℹ️ Остался 1 оплаченный урок.")


# ─── ТЕКСТОВЫЕ СООБЩЕНИЯ ──────────────────────────────────────────────────────

@bot.message_handler(func=lambda m: True, content_types=["text"])
def on_text(m):
    uid = m.from_user.id
    txt = (m.text or "").strip()

    # ответ преподавателя на пересланный вопрос → уходит ученику
    if is_owner(uid) and m.reply_to_message:
        target = db.inbox_user(m.reply_to_message.message_id)
        if target:
            try:
                bot.send_message(target, f"💬 Laziza:\n{esc(txt)}")
                return bot.send_message(uid, "✅ Отправила")
            except Exception:
                return bot.send_message(uid, "Не получилось отправить: человек мог закрыть бота.")

    st = STATE.get(uid)
    if st:
        step, d = st["step"], st["data"]
        lang = lang_of(uid)

        if step == "lang":
            return bot.send_message(uid, LANG_PROMPT, reply_markup=kb_langs())

        if step == "name":
            d["name"] = txt[:60]
            st["step"] = "source"
            return bot.send_message(uid, t(d["lang"], "ask_source", name=esc(d["name"])),
                                    reply_markup=kb_list("src", T[d["lang"]]["sources"]))

        if step == "translate":
            STATE.pop(uid, None)
            db.log_event(uid, "translate")
            r = C.DICT.get(txt.lower())
            if not r:
                return bot.send_message(uid, t(lang, "tr_none"), reply_markup=kb_main(uid))
            if "zh" in r:
                out = f"🔤 {esc(txt)} → <b>{r['zh']}</b>\n🔊 <code>{r['py']}</code>"
            else:
                out = f"🔤 <b>{esc(txt)}</b>\n🔊 <code>{r['py']}</code>\n📖 {esc(r.get(lang, r.get('ru', '')))}"
            return bot.send_message(uid, out, reply_markup=kb_main(uid))

        if step == "absent_reason":
            STATE.pop(uid, None)
            reason = txt[:300]
            db.save_attendance(uid, d["iso"], "no", reason)
            bot.send_message(uid, t(lang, "att_late" if d["late"] else "att_ok"))
            u = db.get_user(uid) or {}
            when = datetime.strptime(d["iso"], "%Y-%m-%dT%H:%M").strftime("%d.%m %H:%M")
            msg = f"❌ {esc(u.get('name') or '?')} не сможет прийти {when}\nПричина: {esc(reason)}"
            if d["late"]:
                msg += "\n⚠️ Меньше чем за 3 часа до урока: по условиям урок оплачивается."
            return notify_owner(msg)

        if is_owner(uid):
            sid = d.get("uid")
            if step == "lesson_topic":
                STATE.pop(uid, None)
                db.add_lesson(sid, None if txt == "-" else txt[:120])
                bot.send_message(uid, f"✅ Урок записан.\n\n{student_card(sid)}")
                return lesson_balance_alert(sid)

            if step == "pay_count":
                if not txt.lstrip("+-").isdigit():
                    return bot.send_message(uid, "Нужно число. Попробуй ещё раз.")
                STATE.pop(uid, None)
                db.add_payment(sid, int(txt))
                bot.send_message(uid, f"💰 Оплата записана.\n\n{student_card(sid)}")
                try:
                    bot.send_message(sid, "💰 Оплата получена, спасибо!\n\n" + progress_text(sid, lang_of(sid)))
                except Exception:
                    pass
                return

            if step == "test_input":
                parts = [p.strip() for p in txt.split("|")]
                if len(parts) != 3:
                    return bot.send_message(uid, "Нужен формат: <code>Название | набрано | максимум</code>")
                try:
                    sc, mx = (float(x.replace(",", ".")) for x in parts[1:])
                    if mx <= 0:
                        raise ValueError
                except ValueError:
                    return bot.send_message(uid, "Баллы должны быть числами, максимум больше нуля.")
                STATE.pop(uid, None)
                db.add_test(sid, parts[0][:80], sc, mx)
                bot.send_message(uid, f"📝 Результат записан.\n\n{student_card(sid)}")
                try:
                    bot.send_message(sid, "📝 Появился новый результат теста!\n\n" + progress_text(sid, lang_of(sid)))
                except Exception:
                    pass
                return

            if step == "sched_input":
                if txt == "-":
                    slots = []
                else:
                    try:
                        slots = scheduler.parse_schedule(txt)
                    except ValueError:
                        return bot.send_message(uid, "Не поняла формат. Пример: <code>пн 18:00, ср 18:00</code>")
                STATE.pop(uid, None)
                db.set_schedule(sid, slots)
                return bot.send_message(uid, f"🗓 Расписание сохранено. Напоминания пойдут сами: "
                                             f"за сутки с кнопками и за час со ссылкой.\n\n{student_card(sid)}")

            if step == "zoom_input":
                if txt != "-" and not txt.lower().startswith("http"):
                    return bot.send_message(uid, "Это не похоже на ссылку. Она должна начинаться с http.")
                STATE.pop(uid, None)
                db.save_user(sid, zoom_link=None if txt == "-" else txt)
                return bot.send_message(uid, f"🔗 Ссылка сохранена.\n\n{student_card(sid)}")

    # ── кнопки меню ──
    lang = lang_of(uid)
    actions = {t(lang, "b_word"): send_word, t(lang, "b_chengyu"): send_chengyu,
               t(lang, "b_fact"): send_fact, t(lang, "b_tr"): ask_translate,
               t(lang, "b_progress"): send_progress, t(lang, "b_lang"): ask_language}
    if txt in actions:
        return actions[txt](uid)
    if txt == t(lang, "b_channel"):
        return bot.send_message(uid, t(lang, "channel"))
    if txt == t(lang, "b_help"):
        return bot.send_message(uid, t(lang, "help"))

    # ── незнакомый человек → знакомство; знакомый → вопрос уходит преподавателю ──
    u = db.get_user(uid)
    if not u or not u.get("level"):
        return cmd_start(m)
    if is_owner(uid):
        return bot.send_message(uid, t(lang, "menu"), reply_markup=kb_main(uid))
    sent = notify_owner(f"💬 <b>{esc(u['name'] or '?')}</b> (@{esc(u['username'] or '—')}):\n{esc(txt)}\n\n"
                        f"<i>Ответь на это сообщение, и я перешлю ответ.</i>")
    if sent:
        db.save_inbox(sent.message_id, uid)
    bot.send_message(uid, t(lang, "q_sent"), reply_markup=kb_main(uid))


# ─── ЗАПУСК ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        bot.set_my_commands([
            types.BotCommand("menu", "меню"), types.BotCommand("word", "слово дня"),
            types.BotCommand("chengyu", "чэнъюй"), types.BotCommand("fact", "факт о Китае"),
            types.BotCommand("progress", "мой прогресс"), types.BotCommand("lang", "язык")])
    except Exception as e:
        logging.warning("не удалось задать команды: %s", e)
    threading.Thread(target=scheduler.loop, args=(send_reminder, send_weekly), daemon=True).start()
    print("🐉 汉助 HanZhu запущен. Останови сочетанием Ctrl+C.")
    bot.infinity_polling(skip_pending=True, timeout=30)
