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
import csv
import io
import json
import hashlib
import random
import re
from urllib.parse import quote
import logging
import threading
import time
from datetime import datetime, timedelta

import telebot
from telebot import types

import db
import scheduler
import dictionary
import practice
import quest
import content as C
from texts import t, T, LANG_PROMPT, WEEKDAYS, PROFILE
from texts_v8 import WISHES

TOKEN = os.environ.get("BOT_TOKEN", "").strip()
OWNER_ID = int(os.environ.get("OWNER_ID", "0") or 0)
# Оплата продления практики не через Telegram Stars. Эти три строки задаёшь ты в переменных хостинга:
PAY_INFO = os.environ.get("PAY_INFO", "").strip()      # как оплатить: название получателя/магазина, номер карты или реквизиты без личных данных
PAY_PRICE = os.environ.get("PAY_PRICE", "").strip()    # например «39 000 сум»
PAY_URL = os.environ.get("PAY_URL", "").strip()        # ссылка на оплату (Payme, Click, Uzum или эквайринг с Visa/UnionPay), по желанию
PRO_DAYS = int(os.environ.get("PRO_DAYS", "30") or 30)
WEBAPP_URL = os.environ.get("WEBAPP_URL", "").strip().strip("\"'").rstrip("/")   # адрес Mini App (https://...)
if WEBAPP_URL and not WEBAPP_URL.lower().startswith(("http://", "https://")):
    WEBAPP_URL = "https://" + WEBAPP_URL      # если https:// забыли, добавим сами
if WEBAPP_URL.lower().startswith("http://"):
    WEBAPP_URL = "https://" + WEBAPP_URL[7:]  # Telegram принимает Mini App только по https
# Версия 11: поддержка проекта и покупки в игре за Telegram Stars
DONATE_INFO = os.environ.get("DONATE_INFO", "").strip()   # реквизиты карты для поддержки (текст как есть). В код не вписываем: только в переменную на Railway
DONATE_URL = os.environ.get("DONATE_URL", "").strip()     # или ссылка на сбор (Boosty, Tribute, Ko-fi, CloudTips), по желанию
STARS_ON = os.environ.get("STARS_ON", "1").strip().lower() not in ("0", "off", "no", "false")

if not TOKEN or TOKEN.startswith("ВСТАВЬ"):
    raise SystemExit(
        "\n❌ Не найден токен бота.\n"
        "   Дома: открой файл .env и вставь токен в строку BOT_TOKEN=\n"
        "   На хостинге: добавь переменную BOT_TOKEN в настройках.\n")

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
db.init()
quest.init_db()

esc = lambda s: html.escape(str(s), quote=False)   # только < > &: апострофы узбекского (o', g') не трогаем                      # всё, что вводит человек, экранируем перед отправкой
STATE = {}                             # диалоги: {user_id: {"step": ..., "data": {...}}}
ONBOARD_STEPS = {"name", "source", "level"}


def lang_of(uid):
    st = STATE.get(uid)                       # посреди знакомства язык ещё живёт только в диалоге
    if st and st.get("data", {}).get("lang"):
        return st["data"]["lang"]
    return (db.get_user(uid) or {}).get("lang") or "ru"

def is_owner(uid):
    return bool(OWNER_ID) and uid == OWNER_ID

STICKER_ROLES = {
    "hello":     "👋 Приветствие (после знакомства и при каждом /start)",
    "thanks":    "🙏 Спасибо (оплата получена)",
    "celebrate": "🎉 Радость (результат теста вырос)",
    "thinking":  "🤔 Думает (слова нет в словаре)",
    "study":     "📖 Урок скоро (напоминание за час)",
    "sleepy":    "😴 Про запас (пока нигде не используется)",
}


def send_sticker(uid, name):
    """Отправляет стикер, если он задан. Если нет или не вышло, тихо пропускает."""
    file_id = db.get_sticker(name)
    if not file_id:
        return
    try:
        bot.send_sticker(uid, file_id)
    except Exception as e:
        logging.warning("стикер %s не отправился: %s", name, e)


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
    k.row(t(lang, "b_grammar"), t(lang, "b_texts"))
    k.row(t(lang, "b_progress"), t(lang, "b_adult"))
    k.row(t(lang, "b_lang"), t(lang, "b_channel"))
    k.row(t(lang, "b_practice"), t(lang, "b_rules"))
    if not is_owner(uid):
        if (db.get_user(uid) or {}).get("is_student"):
            k.row(t(lang, "b_friend"))
        else:
            k.row(t(lang, "b_friend"), t(lang, "b_trial"))
    k.row(t(lang, "b_sched"), t(lang, "b_help"))
    k.row(t(lang, "b_donate"))
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

def start_payload(m):
    """Что стоит после /start в ссылке t.me/бот?start=... (пусто, если человек просто нажал «Старт»)."""
    parts = (m.text or "").split(maxsplit=1)
    if parts and parts[0].split("@")[0] == "/start" and len(parts) > 1:
        return parts[1].strip()
    return ""


def invite_code():
    """Секретная часть ссылки для учеников. Можно задать свою через INVITE_CODE, иначе считается из токена."""
    custom = os.environ.get("INVITE_CODE", "").strip()
    if custom:
        return custom
    return "s_" + hashlib.sha256(("invite:" + TOKEN).encode()).hexdigest()[:10]


def ref_from_payload(p):
    """'ref_123' → 123 (ссылка «приведи друга»), иначе None."""
    return int(p[4:]) if p.startswith("ref_") and p[4:].isdigit() else None


def safe_send(uid, text, **kw):
    try:
        return bot.send_message(uid, text, **kw)
    except Exception as e:
        logging.warning("не отправилось %s: %s", uid, e)
        return None


def welcome_back(u, tg_user):
    """Личное приветствие: 哈喽 / 你好 + имя из Telegram, стикер и список возможностей."""
    lang = u.get("lang") or "ru"
    name = (tg_user.first_name or "").strip() or (u.get("name") or "").strip() or (tg_user.username or "")   # имя из Telegram
    return t(lang, "welcome_back", hi=t(lang, "hi"), name=esc(name))


@bot.message_handler(commands=["start"])
def cmd_start(m):
    uid = m.from_user.id
    STATE.pop(uid, None)
    u = db.get_user(uid)
    payload = start_payload(m)
    if payload == "donate" and u and u.get("level"):
        return send_donate(uid)
    if payload.startswith("par_"):                       # родитель пришёл по ссылке от ребёнка
        return parent_start(m, payload[4:])
    if not (u and u.get("level")) and db.children_of(uid):      # уже подключённый родитель нажал /start
        return bot.send_message(uid, t(lang_of(uid), "pa_home", child=esc(_first(db.children_of(uid)[0]))))
    invited = start_payload(m) == invite_code()        # пришёл по ссылке ученика
    if u and u.get("level"):
        if invited and not u.get("is_student") and not is_owner(uid):
            db.save_user(uid, is_student=1)
            bot.send_message(uid, t(u["lang"], "student_welcome"))
            notify_owner(f"🎓 <b>{esc(u['name'] or '?')}</b> (@{esc(u['username'] or '—')}) "
                         f"перешёл(ла) по твоей ссылке и теперь ученик.")
        send_sticker(uid, "hello")
        return bot.send_message(uid, welcome_back(u, m.from_user), reply_markup=kb_main(uid))
    STATE[uid] = {"step": "lang", "data": {"student": invited, "ref": ref_from_payload(start_payload(m))}}
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
        try:
            bot.delete_message(uid, c.message.message_id)
        except Exception:
            pass
        send_sticker(uid, "hello")
        bot.send_message(uid, t(lang, "greet"), reply_markup=types.ReplyKeyboardRemove())
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
    ref = d.get("ref")
    ref_ok = bool(ref) and not is_owner(uid) and ref != uid and bool(db.get_user(ref)) and not db.get_user(uid)
    db.save_user(uid, name=d.get("name", ""), username=c.from_user.username or "",
                 lang=lang, level=level, source="От друга" if ref_ok else d.get("source", ""))
    if d.get("student") and not is_owner(uid):
        db.save_user(uid, is_student=1)
    bot.edit_message_text(t(lang, "done", name=esc(d.get("name", ""))), uid, c.message.message_id)
    bot.send_message(uid, t(lang, "features"), reply_markup=kb_main(uid))
    notify_owner(
        f"🆕 <b>Новый пользователь</b>\n{esc(d.get('name',''))} (@{esc(c.from_user.username or '—')})\n"
        f"Язык: {lang} · Уровень: {level}\nИсточник: {esc(d.get('source',''))}\n"
        + ("🎓 Пришёл(ла) по ссылке ученика: уже отмечен(а) учеником\n" if d.get("student") and not is_owner(uid) else "") +
        f"ID: <code>{uid}</code>")
    if ref_ok and db.referral_add(uid, ref):
        referrer = db.get_user(ref) or {}
        rl = referrer.get("lang") or "ru"
        db.game_add_lives(ref, 3, practice.LIVES_PER_DAY)
        safe_send(uid, t(lang, "ref_welcome", name=esc(referrer.get("name") or "")))
        safe_send(ref, t(rl, "ref_got1", friend=esc(d.get("name", "")), reward=t(rl, "ref_r1")))
        notify_owner(f"🎁 {esc(d.get('name',''))} пришёл(ла) по ссылке друга: {esc(referrer.get('name') or '?')}.")


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

def user_hsk(uid):
    m = re.search(r"\d", (db.get_user(uid) or {}).get("level") or "")
    return int(m.group()) if m else 0


def pick(uid, kind, items, key, allow=None, prefer=None):
    """Выбирает то, что человеку ещё не показывали. Когда всё показано, начинает круг заново.
    prefer: что показывать в первую очередь (например, то, что переведено на его язык)."""
    seen = db.seen_keys(uid, kind)
    pool = [i for i in items if allow is None or allow(i)]
    fresh = [i for i in pool if key(i) not in seen]
    if not fresh:                                    # подходящее по уровню кончилось: берём любое новое
        fresh = [i for i in items if key(i) not in seen]
    if not fresh:                                    # показано вообще всё: круг заново
        db.reset_seen(uid, kind)
        fresh = pool or items
    if prefer:
        fresh = [i for i in fresh if prefer(i)] or fresh
    item = random.choice(fresh)
    db.mark_seen(uid, kind, key(item))
    return item


BKRS_URL = "https://bkrs.info/slovo.php?ch={q}"      # если ссылка перестанет открываться, поменяй только эту строку


def bkrs_url(q):
    return BKRS_URL.format(q=quote(q, safe=""))


def bkrs_line(lang, q):
    """Строка со ссылкой на БКРС (только для русско- и узбекоязычных): там значения по-русски."""
    text = t(lang, "bkrs_more", url=html.escape(bkrs_url(q), quote=True))
    return ("\n\n" + text) if text and text != "bkrs_more" else ""


def bkrs_button(lang, q):
    label = t(lang, "bkrs_btn")
    if not label or label == "bkrs_btn" or not q:
        return None
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton(label, url=bkrs_url(q)))
    return k


def has_own(lang):
    """Что считать «переведено на язык человека»: узбекскому сойдёт и русский."""
    if lang == "uz":
        return lambda x: bool(x.get("uz") or x.get("ru"))
    if lang == "ru":
        return lambda x: bool(x.get("ru"))
    return None


def send_word(uid):
    db.log_event(uid, "word"); lang = lang_of(uid)
    n = user_hsk(uid)
    lo, hi = max(1, n - 1), max(2, n + 1)           # слова вокруг уровня человека; сленг и культура (0) подходят всем
    w = pick(uid, "word", C.WORDS, key=lambda x: x["zh"],
             allow=lambda x: x["hsk"] == 0 or lo <= x["hsk"] <= hi, prefer=has_own(lang))
    if w.get("tag") == "slang":
        mark = t(lang, "slang_label")
    elif w["hsk"]:
        mark = f"🏷 HSK {w['hsk']}" + ("+" if w["hsk"] >= 7 else "") + (f" ({w['scheme']})" if w.get("scheme") else "")
    else:
        mark = ""
    pos = f" <i>({esc(w['pos'])})</i>" if w.get("pos") and lang in ("ru", "uz") else ""
    ex = ""
    if w.get("examples") and lang in ("ru", "uz"):
        ex = "\n💬 <i>" + esc(w["examples"][0]) + "</i>"
    shown_en = C.meaning_lang(w, lang) == "en"
    extra = bkrs_line(lang, w["zh"]) if lang in ("ru", "uz") and shown_en else ""
    bot.send_message(uid, f"{t(lang,'word')}\n\n<b>{esc(w['zh'])}</b>\n🔊 <code>{esc(w['py'])}</code>\n"
                          f"📖 {esc(C.meaning(w, lang))}{pos}" + (f"\n{mark}" if mark else "") + ex + extra,
                     disable_web_page_preview=True)

def send_chengyu(uid):
    db.log_event(uid, "chengyu"); lang = lang_of(uid)
    n = user_hsk(uid)
    hi = max(2, n + 1)                               # чэнъюй из знаков, которые человек уже мог встретить
    c = pick(uid, "chengyu", C.CHENGYU, key=lambda x: x["zh"],
             allow=lambda x: x["hsk"] == 0 or x["hsk"] <= hi, prefer=has_own(lang))
    ex = f"\n\n<i>{esc(c['ex'])}</i>" if c.get("ex") else ""
    shown_en = C.meaning_lang(c, lang) == "en"
    extra = bkrs_line(lang, c["zh"]) if lang in ("ru", "uz") and shown_en else ""
    bot.send_message(uid, f"{t(lang,'chengyu')}\n\n<b>{esc(c['zh'])}</b>\n🔊 <code>{esc(c['py'])}</code>\n\n"
                          f"{esc(C.meaning(c, lang))}{ex}{extra}", disable_web_page_preview=True)

def send_fact(uid):
    db.log_event(uid, "fact"); lang = lang_of(uid)
    f = pick(uid, "fact", C.FACTS, key=lambda x: x["ru"][:40])
    bot.send_message(uid, f"{t(lang,'fact')}\n\n{esc(C.meaning(f, lang))}")

def ask_translate(uid):
    STATE[uid] = {"step": "translate", "data": {}}
    bot.send_message(uid, t(lang_of(uid), "tr_ask"))

def ask_language(uid):
    STATE.pop(uid, None)
    bot.send_message(uid, LANG_PROMPT, reply_markup=kb_langs())

def send_progress(uid):
    db.log_event(uid, "progress")
    lang = lang_of(uid)
    mk = None if is_owner(uid) else ikb([[(t(lang, "pa_btn"), "pa:new")]])
    bot.send_message(uid, progress_text(uid, lang), reply_markup=mk)


def next_lesson(uid, now):
    """Ближайшее занятие ученика (datetime) с учётом подтверждённых переносов, или None."""
    slots = [dict(x, user_id=uid) for x in db.get_schedule(uid)]
    moves = [m for m in db.moves_ok() if m["user_id"] == uid]
    for dt, _ in scheduler.occurrences(now, slots, moves, days=15):
        if dt > now:
            return dt
    return None


def owner_schedule_text(now, days_ahead=7):
    """Расписание преподавателя: ближайшие дни с датами и недельная сетка с именами."""
    slots = db.all_schedules()
    moves = db.moves_ok()
    if not slots and not moves:
        return ("🗓 <b>Моё расписание</b>\n\nПока пусто. Открой «👥 Мои ученики», выбери ученика "
                "и нажми «🗓 Расписание».")
    wd = WEEKDAYS["ru"]
    occ = scheduler.occurrences(now, slots, moves, days=days_ahead)
    out = ["🗓 <b>Мои уроки на 7 дней</b>", ""]
    total = 0
    for off in range(days_ahead):
        day = now.date() + timedelta(days=off)
        todays = [(dt, x) for dt, x in occ if dt.date() == day]
        label = "сегодня" if off == 0 else "завтра" if off == 1 else wd[day.weekday()]
        head = f"<b>{label}, {day.strftime('%d.%m')}</b>"
        if not todays:
            out.append(f"{head}: свободно")
            continue
        out.append(head)
        for dt, x in todays:
            mark = "✔️" if dt <= now else "▫️"
            out.append(f"  {mark} {dt.strftime('%H:%M')} · {esc(x.get('name') or '—')}" + (" 🔄 перенос" if x.get("moved") else ""))
            total += 1
    out += ["", f"Всего уроков за неделю: <b>{total}</b>", "", "<b>Постоянная сетка</b>"]
    for i in range(7):
        row = sorted((x for x in slots if x["weekday"] == i), key=lambda x: x["time"])
        if row:
            out.append(f"{wd[i]}: " + ", ".join(f"{x['time']} {esc(x['name'] or '—')}" for x in row))
    return "\n".join(out)


def send_owner_schedule(chat_id):
    bot.send_message(chat_id, owner_schedule_text(datetime.now(db.TZ)))


def send_schedule(uid):
    if is_owner(uid):
        return send_owner_schedule(uid)
    db.log_event(uid, "schedule")
    lang = lang_of(uid)
    u = db.get_user(uid) or {}
    if not u.get("is_student"):
        return bot.send_message(uid, t(lang, "sch_guest"))
    sched = db.get_schedule(uid)
    if not sched:
        return bot.send_message(uid, t(lang, "sch_empty"))
    now = datetime.now(db.TZ)
    days = ", ".join(f"{WEEKDAYS[lang][s['weekday']]} {s['time']}" for s in sched)
    out = [t(lang, "sch_title"), "", f"{t(lang, 'sch_days')}: <b>{days}</b>"]
    nxt = next_lesson(uid, now)
    if nxt:
        delta = (nxt.date() - now.date()).days
        when = t(lang, "sch_today") if delta == 0 else t(lang, "sch_tomorrow") if delta == 1 \
            else f"{WEEKDAYS[lang][nxt.weekday()]}, {nxt.strftime('%d.%m')}"
        out.append(f"{t(lang, 'sch_next')}: <b>{when}, {nxt.strftime('%H:%M')}</b>")
    out += ["", t(lang, "sch_remind")]
    k = None
    if nxt:
        k = types.InlineKeyboardMarkup()
        k.add(types.InlineKeyboardButton(t(lang, "mv_btn"), callback_data="mv:ask"))
    bot.send_message(uid, "\n".join(out), reply_markup=k)


@bot.message_handler(commands=["lessons"])
def cmd_lessons(m): send_schedule(m.from_user.id)


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

@bot.message_handler(commands=["grammar"])
def cmd_grammar(m): send_grammar(m.from_user.id)

@bot.message_handler(commands=["texts"])
def cmd_texts(m): send_texts(m.from_user.id)

@bot.message_handler(commands=["adult"])
def cmd_adult(m): send_adult(m.from_user.id)

@bot.message_handler(commands=["lang"])
def cmd_lang(m): ask_language(m.from_user.id)

@bot.message_handler(commands=["about"])
def cmd_about(m):
    lang = lang_of(m.from_user.id)
    bot.send_message(m.chat.id, t(lang, "about_head") + "\n\n" + t(lang, "features"),
                     reply_markup=kb_main(m.from_user.id))

@bot.message_handler(commands=["privacy"])
def cmd_privacy(m):
    bot.send_message(m.chat.id, t(lang_of(m.from_user.id), "privacy"))

@bot.message_handler(commands=["mydata"])
def cmd_mydata(m):
    uid = m.from_user.id
    lang = lang_of(uid)
    data = db.export_user(uid)
    if not data:
        return bot.send_message(uid, t(lang, "mydata_empty"))
    f = io.BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
    f.name = "my_data.json"
    bot.send_document(uid, f, caption=t(lang, "mydata_caption"))

@bot.message_handler(commands=["deletemydata"])
def cmd_delete_ask(m):
    uid = m.from_user.id
    lang = lang_of(uid)
    k = types.InlineKeyboardMarkup(row_width=2)
    k.add(types.InlineKeyboardButton(t(lang, "btn_del_yes"), callback_data="del:yes"),
          types.InlineKeyboardButton(t(lang, "btn_del_no"), callback_data="del:no"))
    bot.send_message(uid, t(lang, "del_ask"), reply_markup=k)

@bot.callback_query_handler(func=lambda c: c.data.startswith("del:"))
def cb_delete(c):
    uid = c.from_user.id
    lang = lang_of(uid)
    bot.answer_callback_query(c.id)
    if c.data == "del:yes":
        u = db.get_user(uid) or {}
        db.delete_user(uid)
        STATE.pop(uid, None)
        bot.edit_message_text(t(lang, "del_done"), uid, c.message.message_id)
        notify_owner(f"🗑 {esc(u.get('name') or '?')} (@{esc(u.get('username') or '—')}) удалил(а) свои данные.")
    else:
        bot.edit_message_text(t(lang, "del_cancel"), uid, c.message.message_id)

@bot.message_handler(commands=["help"])
def cmd_help(m):
    bot.send_message(m.chat.id, t(lang_of(m.from_user.id), "help"))



# ─── ГРАММАТИКА ───────────────────────────────────────────────────────────────

def grammar_level_for(uid):
    levels = sorted(C.GRAMMAR)
    if not levels:
        return None, False
    n = user_hsk(uid) or 1
    if n in levels:
        return n, False
    return (max(levels), True) if n > max(levels) else (min(levels), False)


def grammar_view(lang, lvl, idx, note=""):
    models = C.GRAMMAR[lvl]
    m = models[idx]
    out = [t(lang, "gr_title", lvl=lvl, n=idx + 1, total=len(models)), "", f"<b>{esc(m['title'])}</b>"]
    if m["text"]:
        out += ["", "\n".join(esc(x) for x in m["text"])]
    if m["formula"]:
        out += ["", f"🧩 {t(lang, 'gr_formula')}: <code>" + esc(" / ".join(m["formula"])) + "</code>"]
    for zh, py, ru in m["examples"]:
        out += ["", esc(zh), f"<code>{esc(py)}</code>", f"<i>{esc(ru)}</i>"]
    if m["note"]:
        out += ["", "💡 " + esc(" ".join(m["note"]))]
    if note:
        out += ["", "<i>" + esc(note) + "</i>"]
    if t(lang, "ru_only"):
        out += ["", "<i>" + t(lang, "ru_only") + "</i>"]
    kb = types.InlineKeyboardMarkup(row_width=3)
    total = len(models)
    kb.row(types.InlineKeyboardButton("⬅️", callback_data=f"gr:{lvl}:{(idx - 1) % total}"),
           types.InlineKeyboardButton(f"{idx + 1}/{total}", callback_data=f"gr:{lvl}:{idx}"),
           types.InlineKeyboardButton("➡️", callback_data=f"gr:{lvl}:{(idx + 1) % total}"))
    kb.row(*[types.InlineKeyboardButton(("• " if L == lvl else "") + f"HSK {L}", callback_data=f"gr:{L}:0")
             for L in sorted(C.GRAMMAR)])
    return "\n".join(out), kb


def send_grammar(uid):
    db.log_event(uid, "grammar"); lang = lang_of(uid)
    lvl, fallback = grammar_level_for(uid)
    if lvl is None:
        return bot.send_message(uid, t(lang, "tx_empty"))
    models = C.GRAMMAR[lvl]
    seen = db.seen_keys(uid, "grammar")
    idx = next((i for i, m in enumerate(models) if f"{lvl}:{m['num']}" not in seen), None)
    if idx is None:                                  # весь уровень просмотрен: начинаем заново
        db.reset_seen(uid, "grammar"); idx = 0
    db.mark_seen(uid, "grammar", f"{lvl}:{models[idx]['num']}")
    note = t(lang, "gr_fallback", lvl=lvl) if fallback else ""
    text, kb = grammar_view(lang, lvl, idx, note)
    bot.send_message(uid, text, reply_markup=kb, disable_web_page_preview=True)


@bot.callback_query_handler(func=lambda c: c.data.startswith("gr:"))
def cb_grammar(c):
    uid = c.from_user.id
    bot.answer_callback_query(c.id)
    try:
        _, lvl, idx = c.data.split(":")
        lvl, idx = int(lvl), int(idx)
        models = C.GRAMMAR[lvl]
        model = models[idx]
    except (ValueError, KeyError, IndexError):
        return
    db.mark_seen(uid, "grammar", f"{lvl}:{model['num']}")
    text, kb = grammar_view(lang_of(uid), lvl, idx)
    try:
        bot.edit_message_text(text, uid, c.message.message_id, reply_markup=kb, disable_web_page_preview=True)
    except Exception:
        pass                                         # «сообщение не изменилось»: та же страница


# ─── ТЕКСТЫ ДЛЯ ЧТЕНИЯ ────────────────────────────────────────────────────────

def texts_list(kind, lvl):
    return [x for x in C.TEXTS if x["kind"] == kind and (kind == "classic" or x["level"] == lvl)]


def text_view(lang, kind, lvl, idx):
    items = texts_list(kind, lvl)
    x = items[idx]
    level_label = t(lang, "tx_lvl_any") if kind == "classic" else f"HSK {lvl}"
    out = [t(lang, "tx_title", kind=t(lang, "tx_" + kind), lvl=level_label, n=idx + 1, total=len(items)),
           "", f"<b>{esc(x['title'])}</b>", ""]
    for zh, py in zip(x["zh"], x["py"] + [""] * len(x["zh"])):
        out += [esc(zh)] + ([f"<code>{esc(py)}</code>"] if py else [])
    if x["ru"]:
        out += ["", f"🔎 {t(lang, 'tx_translation')}: <tg-spoiler>{esc(x['ru'])}</tg-spoiler>"]
    if t(lang, "ru_only"):
        out += ["", "<i>" + t(lang, "ru_only") + "</i>"]
    total = len(items)
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.row(types.InlineKeyboardButton("⬅️", callback_data=f"tx:{kind}:{lvl}:{(idx - 1) % total}"),
           types.InlineKeyboardButton(f"{idx + 1}/{total}", callback_data=f"tx:{kind}:{lvl}:{idx}"),
           types.InlineKeyboardButton("➡️", callback_data=f"tx:{kind}:{lvl}:{(idx + 1) % total}"))
    if kind == "adapted":
        levels = sorted({y["level"] for y in C.TEXTS if y["kind"] == "adapted"})
        kb.row(*[types.InlineKeyboardButton(("• " if L == lvl else "") + f"HSK {L}", callback_data=f"tx:adapted:{L}:0")
                 for L in levels])
    other = "classic" if kind == "adapted" else "adapted"
    if any(y["kind"] == other for y in C.TEXTS):
        first_lvl = lvl if other == "adapted" else 0
        kb.row(types.InlineKeyboardButton("🏛 " + t(lang, "tx_classic") if other == "classic" else "📖 " + t(lang, "tx_adapted"),
                                          callback_data=f"tx:{other}:{first_lvl}:0"))
    return "\n".join(out), kb, x


def send_text_item(chat_id, lang, kind, lvl, idx):
    text, kb, x = text_view(lang, kind, lvl, idx)
    img = os.path.join(os.path.dirname(os.path.abspath(__file__)), x["image"]) if x.get("image") else None
    if img and os.path.exists(img) and len(text) <= 1000:
        with open(img, "rb") as f:
            return bot.send_photo(chat_id, f, caption=text, reply_markup=kb)
    return bot.send_message(chat_id, text, reply_markup=kb)


def send_texts(uid):
    db.log_event(uid, "texts"); lang = lang_of(uid)
    adapted_levels = sorted({y["level"] for y in C.TEXTS if y["kind"] == "adapted"})
    if not adapted_levels:
        return bot.send_message(uid, t(lang, "tx_empty"))
    n = max(user_hsk(uid), 1)
    lvl = n if n in adapted_levels else (max(adapted_levels) if n > max(adapted_levels) else min(adapted_levels))
    items = texts_list("adapted", lvl)
    seen = db.seen_keys(uid, "text")
    idx = next((i for i, x in enumerate(items) if x["id"] not in seen), None)
    if idx is None:
        db.reset_seen(uid, "text"); idx = 0
    db.mark_seen(uid, "text", items[idx]["id"])
    send_text_item(uid, lang, "adapted", lvl, idx)


@bot.callback_query_handler(func=lambda c: c.data.startswith("tx:"))
def cb_text(c):
    uid = c.from_user.id
    bot.answer_callback_query(c.id)
    try:
        _, kind, lvl, idx = c.data.split(":")
        lvl, idx = int(lvl), int(idx)
        items = texts_list(kind, lvl)
        x = items[idx]
    except (ValueError, IndexError):
        return
    db.mark_seen(uid, "text", x["id"])
    try:
        bot.delete_message(uid, c.message.message_id)
    except Exception:
        pass
    send_text_item(uid, lang_of(uid), kind, lvl, idx)


# ─── РАЗДЕЛ 16+ ───────────────────────────────────────────────────────────────

def adult_item_view(lang, uid):
    it = pick(uid, "adult", C.ADULT, key=lambda x: x["zh"])
    out = [t(lang, "adult_head"), "", f"<b>{esc(it['zh'])}</b>", f"🔊 <code>{esc(it['py'])}</code>",
           f"📖 {esc(C.meaning(it, lang))}", f"{t(lang, 'adult_rude')}: {t(lang, 'adult_lv' + str(it['rude']))}",
           "", t(lang, "adult_foot")]
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(t(lang, "adult_more"), callback_data="ad:more"))
    return "\n".join(out), kb


def send_adult(uid):
    db.log_event(uid, "adult"); lang = lang_of(uid)
    status = (db.get_user(uid) or {}).get("adult_ok") or 0
    if status == -1:
        return bot.send_message(uid, t(lang, "adult_closed"))
    if status != 1:
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton(t(lang, "adult_yes"), callback_data="ad:yes"),
               types.InlineKeyboardButton(t(lang, "adult_no"), callback_data="ad:no"))
        return bot.send_message(uid, t(lang, "adult_gate"), reply_markup=kb)
    text, kb = adult_item_view(lang, uid)
    bot.send_message(uid, text, reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data.startswith("ad:"))
def cb_adult(c):
    uid = c.from_user.id
    lang = lang_of(uid)
    bot.answer_callback_query(c.id)
    status = (db.get_user(uid) or {}).get("adult_ok") or 0
    if status == -1:
        return bot.send_message(uid, t(lang, "adult_closed"))
    action = c.data.split(":")[1]
    if action == "no":
        return bot.edit_message_text(t(lang, "adult_declined"), uid, c.message.message_id)
    if action == "yes":
        db.save_user(uid, adult_ok=1)
        status = 1
    if status != 1:                                  # «ещё» без подтверждения: сначала подтверждение
        return send_adult(uid)
    text, kb = adult_item_view(lang, uid)
    try:
        bot.edit_message_text(text, uid, c.message.message_id, reply_markup=kb)
    except Exception:
        bot.send_message(uid, text, reply_markup=kb)


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
        send_sticker(uid, "study")


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


def send_digest(now):
    """Утром: какие уроки сегодня и кто подтвердил. Пустой день — молчим."""
    todays = [(dt, x) for dt, x in scheduler.occurrences(now, db.all_schedules(), db.moves_ok(), days=1)]
    if not todays:
        return
    lines = [f"☀️ <b>Сегодня уроков: {len(todays)}</b>", ""]
    for dt, x in todays:
        st = db.attendance_status(x["user_id"], dt.strftime("%Y-%m-%dT%H:%M"))
        mark = ""
        if st and st[0] == "yes":
            mark = " ✅ подтвердил(а)"
        elif st:
            mark = " ❌ не придёт" + (f": {esc(st[1])}" if st[1] else "")
        lines.append(f"▫️ {dt.strftime('%H:%M')} · {esc(x.get('name') or '—')}" + (" 🔄" if x.get("moved") else "") + mark)
    hw = db.hw_all_open()
    if hw:
        lines += ["", f"📚 Открытых домашек: {len(hw)}"]
    notify_owner("\n".join(lines))


def send_weekly(now):
    since = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    lessons = db.lessons_count_since(since)
    new = db.users_since(since)
    absent = db.absences_since(since)
    top = db.top_events_since(since)
    labels = {"word": "Слово дня", "chengyu": "Чэнъюй", "fact": "Факт", "progress": "Прогресс",
              "translate": "Перевод", "grammar": "Грамматика", "texts": "Тексты", "adult": "Раздел 16+",
              "quiz": "Викторина", "cards": "Карточки", "tea": "Чайная лавка"}
    low = []
    for s in db.students():
        _, _, left = db.balance(s["user_id"])
        if left <= 0:
            low.append(f"· {esc(s['name'])}: " + (f"остаток 0" if left == 0 else f"долг {abs(left)}"))
    txt = [f"📊 <b>Итоги недели</b>", "",
           f"Уроков проведено: <b>{lessons}</b>", f"Новых в боте: <b>{new}</b>",
           f"Отмен от учеников: <b>{absent}</b>"]
    det = db.absences_detail(since)
    if det:
        txt += ["", "<b>Отмены и причины</b>"]
        for r in det[:10]:
            when = (r["lesson"] or "")[:16].replace("T", " ")
            txt.append(f"· {esc(r['name'] or '—')} {when}: {esc(r['reason'] or 'без причины')}")
    if top:
        txt += ["", "<b>Чем пользуются чаще всего</b>"]
        txt += [f"· {labels.get(e['kind'], e['kind'])}: {e['n']}" for e in top]
    miss = db.top_missing(since, 5)
    if miss:
        txt += ["", "<b>Искали в переводчике и не нашли</b>"] + [f"· {esc(r['query'])}: {r['n']}" for r in miss]
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
          types.InlineKeyboardButton("🔗 Ссылка для ученика", callback_data="a:invite"),
          types.InlineKeyboardButton("➕ Сделать учеником", callback_data="a:make"),
          types.InlineKeyboardButton("📚 Задать домашку", callback_data="a:hw"),
          types.InlineKeyboardButton("👥 Группы", callback_data="a:groups"),
          types.InlineKeyboardButton("🗓 Моё расписание", callback_data="a:sched"),
          types.InlineKeyboardButton("🗂 Бывшие ученики", callback_data="a:alumni"),
          types.InlineKeyboardButton("📊 Статистика бота", callback_data="a:stats"))
    bot.send_message(m.chat.id, f"<b>Панель преподавателя</b>\n\nВсего в боте: {len(db.all_users())}\n"
                                f"Учеников: {len(db.students())}", reply_markup=k)


@bot.message_handler(commands=["schedule"])
def cmd_schedule_owner(m):
    if is_owner(m.from_user.id):
        send_owner_schedule(m.chat.id)


@bot.message_handler(commands=["missing"])
def cmd_missing(m):
    if not is_owner(m.from_user.id):
        return
    rows = db.top_missing(limit=25)
    if not rows:
        return bot.send_message(m.chat.id, "Пока все запросы в переводчике находились 🎉")
    lines = [f"· {esc(r['query'])}: {r['n']}" for r in rows]
    bot.send_message(m.chat.id, "<b>Что искали и не нашли</b>\n\n" + "\n".join(lines) +
                     "\n\nПополнить можно, дописав строки в <code>content_words.txt</code>.")


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


@bot.callback_query_handler(func=lambda c: c.data == "a:invite")
@owner_only
def cb_invite(c):
    bot.answer_callback_query(c.id)
    try:
        uname = bot.get_me().username
    except Exception:
        uname = ""
    if not uname:
        return bot.send_message(c.message.chat.id, "Не удалось узнать имя бота. Попробуй ещё раз через минуту.")
    link = f"https://t.me/{uname}?start={invite_code()}"
    bot.send_message(c.message.chat.id,
                     "🔗 <b>Ссылка для учеников</b>\n\nОтправь её ученику. Он нажмёт «Старт», познакомится с ботом "
                     "и сразу окажется в списке «Мои ученики», вручную отмечать не нужно.\n\n"
                     f"<code>{link}</code>\n\n"
                     "Потом открой «👥 Мои ученики», выбери его и задай расписание (кнопка «Расписание»), "
                     "чтобы пошли напоминания. Уроки, оплаты и тесты вносятся там же.\n\n"
                     "<i>Ссылку лучше давать только своим ученикам: по ней любой становится учеником.</i>",
                     disable_web_page_preview=True)


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
             f"Расписание: {days}", f"Zoom: {'есть' if u.get('zoom_link') else 'не задан'}",
             "Раздел 16+: " + {1: "подтвердил(а) возраст", -1: "закрыт тобой"}.get(u.get("adult_ok") or 0, "не открывал(а)")]
    hw = db.hw_open(uid)
    if hw:
        lines += ["", f"📚 Открытых домашек: {len(hw)}"]
    for r in db.rewards_open(uid):
        lines.append(f"🎁 Ждёт выдачи: {esc(r['text'][:90])}")
    rs = db.referral_stats(uid)
    if rs["joined"]:
        lines += [f"🎁 Привёл друзей: {rs['joined']} (пробный: {rs['trial']}, занимается: {rs['paid']})"]
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
    k.add(types.InlineKeyboardButton("📚 Домашка", callback_data=f"hwn:{uid}"),
          types.InlineKeyboardButton("📈 KPI-заметка", callback_data=f"kpi:{uid}"))
    k.add(types.InlineKeyboardButton("👨‍👩‍👧 Ссылка для родителей", callback_data=f"pa:o:{uid}"))
    k.add(types.InlineKeyboardButton("💬 Напомнить об оплате", callback_data=f"nd:{uid}"),
          types.InlineKeyboardButton("🔞 Закрыть / открыть 16+", callback_data=f"adx:{uid}"))
    k.add(types.InlineKeyboardButton("⏸ Завершить занятия", callback_data=f"fin:{uid}"),
          types.InlineKeyboardButton("🗑 Удалить из базы", callback_data=f"dst:{uid}"))
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


@bot.callback_query_handler(func=lambda c: c.data.startswith("adx:"))
@owner_only
def cb_adult_toggle(c):
    uid = int(c.data.split(":")[1])
    cur = (db.get_user(uid) or {}).get("adult_ok") or 0
    db.save_user(uid, adult_ok=0 if cur == -1 else -1)
    bot.answer_callback_query(c.id, "Раздел 16+ закрыт" if cur != -1 else "Раздел 16+ снова доступен")
    bot.send_message(c.message.chat.id, student_card(uid))

# ─── ЗАВЕРШЕНИЕ ЗАНЯТИЙ, АРХИВ И УДАЛЕНИЕ УЧЕНИКА ─────────────────────────────

def _name_of(uid):
    return esc((db.get_user(uid) or {}).get("name") or "—")


@bot.callback_query_handler(func=lambda c: c.data == "a:sched")
@owner_only
def cb_owner_sched(c):
    bot.answer_callback_query(c.id)
    send_owner_schedule(c.message.chat.id)


@bot.callback_query_handler(func=lambda c: c.data == "a:alumni")
@owner_only
def cb_alumni(c):
    bot.answer_callback_query(c.id)
    rows = db.alumni()
    if not rows:
        return bot.send_message(c.message.chat.id, "Бывших учеников пока нет. Сюда попадают те, "
                                                   "с кем ты нажала «⏸ Завершить занятия».")
    k = types.InlineKeyboardMarkup(row_width=1)
    for u in rows[:40]:
        done, paid, left = db.balance(u["user_id"])
        k.add(types.InlineKeyboardButton(f"{u['name'] or '—'} · {done} ур.", callback_data=f"al:{u['user_id']}"))
    bot.send_message(c.message.chat.id, "<b>Бывшие ученики</b>\nИстория уроков и оплат сохранена.", reply_markup=k)


@bot.callback_query_handler(func=lambda c: c.data.startswith("al:"))
@owner_only
def cb_alumnus(c):
    uid = int(c.data.split(":")[1])
    k = types.InlineKeyboardMarkup(row_width=1)
    k.add(types.InlineKeyboardButton("↩️ Вернуть в ученики", callback_data=f"mk:{uid}"),
          types.InlineKeyboardButton("🗑 Удалить из базы", callback_data=f"dst:{uid}"))
    bot.send_message(c.message.chat.id, student_card(uid), reply_markup=k)
    bot.answer_callback_query(c.id)


@bot.callback_query_handler(func=lambda c: c.data == "cx")
@owner_only
def cb_cancel(c):
    bot.answer_callback_query(c.id, "Отменено")
    try:
        bot.edit_message_text("Отменено, ничего не изменилось.", c.message.chat.id, c.message.message_id)
    except Exception:
        pass


@bot.callback_query_handler(func=lambda c: c.data.startswith("fin:"))
@owner_only
def cb_finish_ask(c):
    uid = int(c.data.split(":")[1])
    k = types.InlineKeyboardMarkup(row_width=2)
    k.add(types.InlineKeyboardButton("Да, завершить", callback_data=f"fin1:{uid}"),
          types.InlineKeyboardButton("Отмена", callback_data="cx"))
    bot.send_message(c.message.chat.id,
                     f"Завершить занятия с <b>{_name_of(uid)}</b>?\n\n"
                     "· расписание и напоминания отключатся\n"
                     "· история уроков, оплат и тестов останется\n"
                     "· ученик найдётся в «🗂 Бывшие ученики», оттуда можно вернуть его обратно\n"
                     "· ботом он сможет пользоваться как обычный пользователь", reply_markup=k)
    bot.answer_callback_query(c.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("fin1:"))
@owner_only
def cb_finish_do(c):
    uid = int(c.data.split(":")[1])
    if uid == OWNER_ID:
        return bot.answer_callback_query(c.id, "Себя нельзя")
    db.save_user(uid, is_student=0)
    db.set_schedule(uid, [])
    bot.edit_message_text(f"⏸ Занятия с {_name_of(uid)} завершены. История сохранена, напоминания отключены.",
                          c.message.chat.id, c.message.message_id)
    bot.answer_callback_query(c.id, "Готово")


@bot.callback_query_handler(func=lambda c: c.data.startswith("dst:"))
@owner_only
def cb_destroy_ask(c):
    uid = int(c.data.split(":")[1])
    if uid == OWNER_ID:
        return bot.answer_callback_query(c.id, "Себя удалить нельзя")
    k = types.InlineKeyboardMarkup(row_width=2)
    k.add(types.InlineKeyboardButton("Да, удалить насовсем", callback_data=f"dst1:{uid}"),
          types.InlineKeyboardButton("Отмена", callback_data="cx"))
    bot.send_message(c.message.chat.id,
                     f"Удалить <b>{_name_of(uid)}</b> из базы полностью?\n\n"
                     "Пропадут уроки, оплаты, тесты, расписание и всё остальное. Это не отменить, "
                     "но перед удалением я пришлю тебе файл-копию с этими данными.\n\n"
                     "<i>Если хочешь только остановить занятия и сохранить историю, лучше «⏸ Завершить занятия».</i>",
                     reply_markup=k)
    bot.answer_callback_query(c.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("dst1:"))
@owner_only
def cb_destroy_do(c):
    uid = int(c.data.split(":")[1])
    if uid == OWNER_ID:
        return bot.answer_callback_query(c.id, "Себя удалить нельзя")
    data = db.export_user(uid)
    if not data:
        return bot.answer_callback_query(c.id, "Этого человека уже нет в базе")
    name = _name_of(uid)
    f = io.BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
    f.name = f"student_{uid}_backup.json"
    try:
        bot.send_document(c.message.chat.id, f, caption=f"Копия данных: {name}. Сохрани, если нужна история.")
    except Exception as e:
        logging.warning("не удалось отправить копию перед удалением: %s", e)
        return bot.answer_callback_query(c.id, "Копия не отправилась, ничего не удалено")
    db.delete_user(uid)
    STATE.pop(uid, None)
    bot.edit_message_text(f"🗑 {name} удалён(а) из базы. Файл-копия выше.",
                          c.message.chat.id, c.message.message_id)
    bot.answer_callback_query(c.id, "Удалено")


# ─── ПРАКТИКА: ВИКТОРИНА, КАРТОЧКИ, ЧАЙНАЯ ЛАВКА ──────────────────────────────

QUIZ, CARDS, TEA = {}, {}, {}          # сессии в памяти; после перезапуска бота кнопки «устаревают»


def ikb(rows):
    """rows: [[(текст, callback_data), ...], ...] → InlineKeyboardMarkup."""
    k = types.InlineKeyboardMarkup()
    for row in rows:
        k.row(*[types.InlineKeyboardButton(a, callback_data=b) for a, b in row])
    return k


def edit_or_send(c, text, markup=None):
    try:
        bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=markup)
    except Exception:
        bot.send_message(c.message.chat.id, text, reply_markup=markup)


def send_practice(uid):
    lang = lang_of(uid)
    k = ikb([
        [(t(lang, "pr_quiz"), "pr:quiz")], [(t(lang, "pr_marathon"), "pr:mara")],
        [(t(lang, "pr_cards"), "pr:cards")], [(t(lang, "pr_tea"), "pr:tea")],
        [(t(lang, "pr_top"), "pr:top")], [(t(lang, "pr_rules"), "pr:rules")]])
    if WEBAPP_URL.startswith("https://"):
        k.keyboard.insert(0, [types.InlineKeyboardButton(t(lang, "pr_quest"), web_app=types.WebAppInfo(url=WEBAPP_URL + "/?tab=quest"))])
        k.keyboard.insert(1, [types.InlineKeyboardButton(t(lang, "pr_app"), web_app=types.WebAppInfo(url=WEBAPP_URL))])
    bot.send_message(uid, t(lang, "pr_title"), reply_markup=k)


@bot.callback_query_handler(func=lambda c: c.data.startswith("pr:"))
def cb_practice(c):
    uid = c.from_user.id
    bot.answer_callback_query(c.id)
    kind = c.data.split(":")[1]
    {"quiz": start_quiz, "cards": start_cards, "tea": send_tea, "mara": send_marathon_menu,
     "top": send_board, "rules": send_rules}.get(kind, lambda u: None)(uid)


# ── викторина ──

def start_quiz(uid):
    db.log_event(uid, "quiz")
    QUIZ[uid] = {"n": 0, "score": 0, "wrong": [], "seen": [], "q": None, "answered": True}
    ask_quiz(uid)


def ask_quiz(uid):
    lang, sess = lang_of(uid), QUIZ.get(uid)
    if not sess:
        return
    q = practice.make_question(lang, user_hsk(uid), exclude=sess["seen"])
    if not q:
        return bot.send_message(uid, t(lang, "qz_fail"))
    sess.update(n=sess["n"] + 1, q=q, answered=False)
    sess["seen"].append(q["zh"])
    k = types.InlineKeyboardMarkup(row_width=1)
    for i, opt in enumerate(q["options"]):
        k.add(types.InlineKeyboardButton(opt, callback_data=f"qz:{sess['n']}:{i}"))
    bot.send_message(uid, t(lang, "qz_q", n=sess["n"], total=practice.QUIZ_LEN, zh=esc(q["zh"]), py=esc(q["py"])),
                     reply_markup=k)


@bot.callback_query_handler(func=lambda c: c.data.startswith("qz:"))
def cb_quiz(c):
    uid, lang = c.from_user.id, lang_of(c.from_user.id)
    parts = c.data.split(":")
    sess = QUIZ.get(uid)
    if parts[1] == "new":
        bot.answer_callback_query(c.id)
        return start_quiz(uid)
    if parts[1] == "add":
        bot.answer_callback_query(c.id)
        if not sess:
            return bot.send_message(uid, t(lang, "qz_stale"))
        for w in sess["wrong"]:
            db.card_add(uid, w["zh"])
        n = len(sess["wrong"])
        try:
            bot.edit_message_reply_markup(uid, c.message.message_id, reply_markup=None)
        except Exception:
            pass
        return bot.send_message(uid, t(lang, "qz_added", n=n))
    try:
        n, i = int(parts[1]), int(parts[2])
    except (ValueError, IndexError):
        return bot.answer_callback_query(c.id)
    if not sess or sess["n"] != n or sess["answered"]:
        return bot.answer_callback_query(c.id, t(lang, "qz_stale"), show_alert=True)
    sess["answered"] = True
    bot.answer_callback_query(c.id)
    q = sess["q"]
    ok = i == q["answer"]
    if ok:
        sess["score"] += 1
    else:
        sess["wrong"].append({"zh": q["zh"], "py": q["py"], "right": q["right"]})
    base = t(lang, "qz_q", n=n, total=practice.QUIZ_LEN, zh=esc(q["zh"]), py=esc(q["py"]))
    verdict = t(lang, "qz_right") if ok else t(lang, "qz_wrong", right=esc(q["right"]))
    try:
        bot.edit_message_text(base + "\n\n" + verdict, uid, c.message.message_id, reply_markup=None)
    except Exception:
        pass
    if n < practice.QUIZ_LEN:
        return ask_quiz(uid)
    score = sess["score"]
    emoji = "🏆" if score == practice.QUIZ_LEN else "👏" if score >= 3 else "🌱"
    out = [t(lang, "qz_end", score=score, total=practice.QUIZ_LEN, emoji=emoji)]
    if sess["wrong"]:
        out += ["", t(lang, "qz_mistakes")] + [f"· <b>{esc(w['zh'])}</b> {esc(w['py'])} — {esc(w['right'])}" for w in sess["wrong"]]
    rows = []
    if sess["wrong"]:
        rows.append([(t(lang, "qz_add"), "qz:add")])
    rows.append([(t(lang, "qz_again"), "qz:new")])
    bot.send_message(uid, "\n".join(out), reply_markup=ikb(rows))


# ── карточки ──

def start_cards(uid):
    db.log_event(uid, "cards")
    lang = lang_of(uid)
    due = db.cards_due(uid, 20)
    if not due:
        new = practice.new_cards(lang, user_hsk(uid), db.card_have(uid))
        for w in new:
            db.card_add(uid, w["zh"])
        if new:
            bot.send_message(uid, t(lang, "fc_new", n=len(new)))
        due = db.cards_due(uid, 20)
    if not due:
        return bot.send_message(uid, t(lang, "fc_done", known=0, total=0))
    CARDS[uid] = {"queue": [d["zh"] for d in due], "box": {d["zh"]: d["box"] for d in due},
                  "total": len(due), "known": 0, "seq": 0, "failed": set()}
    show_card(uid)


def card_front(uid, lang, sess):
    w = practice.word_by_zh(sess["queue"][0]) or {"zh": sess["queue"][0], "py": ""}
    return t(lang, "fc_front", zh=esc(w["zh"]), py=esc(w["py"])), w


def show_card(uid, c=None):
    lang, sess = lang_of(uid), CARDS.get(uid)
    if not sess:
        return
    if not sess["queue"]:
        text, markup = t(lang, "fc_done", known=sess["known"], total=sess["total"]), None
    else:
        sess["seq"] += 1
        text, _ = card_front(uid, lang, sess)
        markup = ikb([[(t(lang, "fc_show"), f"fc:show:{sess['seq']}")]])
    if c:
        return edit_or_send(c, text, markup)
    bot.send_message(uid, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith("fc:"))
def cb_cards(c):
    uid, lang = c.from_user.id, lang_of(c.from_user.id)
    parts = c.data.split(":")
    sess = CARDS.get(uid)
    try:
        act, seq = parts[1], int(parts[2])
    except (ValueError, IndexError):
        return bot.answer_callback_query(c.id)
    if not sess or sess["seq"] != seq or not sess["queue"]:
        return bot.answer_callback_query(c.id, t(lang, "fc_stale"), show_alert=True)
    bot.answer_callback_query(c.id)
    zh = sess["queue"][0]
    if act == "show":
        w = practice.word_by_zh(zh) or {"zh": zh, "py": "", "hsk": 0}
        text = t(lang, "fc_back", zh=esc(w["zh"]), py=esc(w.get("py", "")), meaning=esc(C.meaning(w, lang) or "—"))
        return edit_or_send(c, text, ikb([[(t(lang, "fc_know"), f"fc:ok:{seq}"), (t(lang, "fc_again"), f"fc:no:{seq}")]]))
    box = sess["box"].get(zh, 0)
    sess["queue"].pop(0)
    if act == "ok":
        nb = practice.grade(box, True)
        db.card_set(uid, zh, nb, practice.next_due(nb, db.today()))
        if zh not in sess["failed"]:
            sess["known"] += 1
    else:
        db.card_set(uid, zh, 0, db.today())
        sess["box"][zh] = 0
        sess["failed"].add(zh)
        sess["queue"].append(zh)
        sess["queue"] = sess["queue"][:30]
    show_card(uid, c)


# ── Чайная лавка ──

def tea_status(uid, lang):
    g = db.game_get(uid, practice.LIVES_PER_DAY)
    emoji, title_key = practice.tea_title(g["served"])[1:]
    return g, t(lang, "tea_intro", lives=g["lives"], coins=g["coins"], emoji=emoji, title=t(lang, title_key))


def lives_closed(lang):
    """Сообщение «жизни закончились» + предложение продлить практику (оплата не через Stars)."""
    base = practice.LIVES_PER_DAY
    return (t(lang, "tea_closed", max=base) + "\n\n" + t(lang, "lx_offer", base=base, pro=base * db.PRO_MULT, days=PRO_DAYS),
            ikb([[(t(lang, "lx_btn"), "lx:info")]]))


def send_tea(uid):
    db.log_event(uid, "tea")
    lang = lang_of(uid)
    g, text = tea_status(uid, lang)
    if g["lives"] <= 0:
        closed, mk = lives_closed(lang)
        return bot.send_message(uid, text + "\n\n" + closed, reply_markup=mk)
    bot.send_message(uid, text, reply_markup=ikb([[(t(lang, "tea_start"), "ts:go:0")]]))


def ask_order(uid, c=None):
    lang = lang_of(uid)
    sess = TEA.setdefault(uid, {"seq": 0, "queue": [], "gap": 0, "recent": [], "order": None, "answered": True})
    g = db.game_get(uid, practice.LIVES_PER_DAY)
    if g["lives"] <= 0:
        return
    order = None
    if sess["queue"] and sess["gap"] >= 2:
        order = practice.order_for_item(lang, sess["queue"].pop(0))
        sess["gap"] = 0
    if not order:
        order = practice.make_order(lang, avoid=sess["recent"][-4:])
        sess["gap"] += 1
    sess["recent"].append(order["item"])
    sess["seq"] += 1
    sess.update(order=order, answered=False)
    k = types.InlineKeyboardMarkup(row_width=1)
    for i, opt in enumerate(order["options"]):
        k.add(types.InlineKeyboardButton(opt, callback_data=f"ts:a:{sess['seq']}:{i}"))
    text = t(lang, "tea_order", zh=esc(order["zh"]), py=esc(order["py"]), lives=g["lives"])
    if c:
        return edit_or_send(c, text, k)
    bot.send_message(uid, text, reply_markup=k)


@bot.callback_query_handler(func=lambda c: c.data.startswith("ts:"))
def cb_tea(c):
    uid, lang = c.from_user.id, lang_of(c.from_user.id)
    parts = c.data.split(":")
    act = parts[1]
    sess = TEA.get(uid)
    if act == "go":
        bot.answer_callback_query(c.id)
        TEA.pop(uid, None)
        return ask_order(uid, c)
    if act == "stop":
        bot.answer_callback_query(c.id)
        TEA.pop(uid, None)
        return edit_or_send(c, tea_status(uid, lang)[1], ikb([[(t(lang, "tea_start"), "ts:go:0")]]))
    try:
        seq = int(parts[2])
    except (ValueError, IndexError):
        return bot.answer_callback_query(c.id)
    if not sess or sess["seq"] != seq:
        return bot.answer_callback_query(c.id, t(lang, "tea_stale"), show_alert=True)
    if act == "n":
        bot.answer_callback_query(c.id)
        if not sess["answered"]:
            return
        return ask_order(uid, c)
    if act != "a" or sess["answered"]:
        return bot.answer_callback_query(c.id)
    sess["answered"] = True
    bot.answer_callback_query(c.id)
    o = sess["order"]
    g = db.game_get(uid, practice.LIVES_PER_DAY)
    head = t(lang, "tea_order", zh=esc(o["zh"]), py=esc(o["py"]), lives=g["lives"])
    ok = int(parts[3]) == o["answer"]
    before = practice.tea_title(g["served"])[0]
    extra = ""
    if ok:
        streak = g["streak"] + 1
        gain = 1 + (3 if streak % 5 == 0 else 0)
        served = g["served"] + 1
        db.game_save(uid, coins=g["coins"] + gain, served=served, streak=streak)
        db.score_add(uid, gain, 1, 0, practice.BOARD_DAILY_CAP)
        verdict = t(lang, "tea_right", coins=gain)
        if practice.tea_title(served)[0] != before:
            e, tk = practice.tea_title(served)[1:]
            extra = "\n\n" + t(lang, "tea_levelup", emoji=e, title=t(lang, tk))
            db.feed_add(uid, "levelup", tk)
    else:
        lives = max(0, g["lives"] - 1)
        db.game_save(uid, lives=lives, streak=0)
        db.score_add(uid, 0, 0, 1, practice.BOARD_DAILY_CAP)
        sess["queue"].append(o["item"])
        verdict = t(lang, "tea_wrong", right=esc(o["right"]), lives=lives)
        if lives <= 0:
            TEA.pop(uid, None)
            closed, mk = lives_closed(lang)
            return edit_or_send(c, head + "\n\n" + verdict + "\n\n" + closed, mk)
    edit_or_send(c, head + "\n\n" + verdict + extra,
                 ikb([[(t(lang, "tea_next"), f"ts:n:{seq}"), (t(lang, "tea_stop"), "ts:stop:0")]]))


# ─── РОДИТЕЛИ: недельная сводка ───────────────────────────────────────────────

def _first(uid):
    w = ((db.get_user(uid) or {}).get("name") or "").split()
    return w[0] if w else "—"


def _tg_lang(tg_user):
    code = (getattr(tg_user, "language_code", "") or "")[:2].lower()
    return code if code in T else "ru"


def parent_link_for(child_id):
    name = bot_username()
    return f"https://t.me/{name}?start=par_{db.par_code_new(child_id)}" if name else ""


def parent_consent_markup(code, lang):
    k = types.InlineKeyboardMarkup()
    k.row(types.InlineKeyboardButton(t(lang, "pa_yes"), callback_data=f"pa:yes:{code}"),
          types.InlineKeyboardButton(t(lang, "pa_no"), callback_data="pa:no"))
    k.row(*[types.InlineKeyboardButton(lb, callback_data=f"pa:l:{code}:{lc}")
            for lb, lc in (("🇷🇺", "ru"), ("🇺🇿", "uz"), ("🇬🇧", "en"), ("🇨🇳", "zh"))])
    return k


def parent_start(m, code):
    uid = m.from_user.id
    child = db.par_code_child(code)
    if not child or child == uid or not db.get_user(child):
        lang = lang_of(uid) if db.get_user(uid) else _tg_lang(m.from_user)
        return bot.send_message(uid, t(lang, "pa_bad"))
    u = db.get_user(uid)
    if u and u.get("lang"):
        lang = u["lang"]
    else:
        lang = _tg_lang(m.from_user)
        db.save_user(uid, name=(m.from_user.first_name or "")[:60], username=m.from_user.username, lang=lang)
    bot.send_message(uid, t(lang, "pa_consent", child=esc(_first(child))), reply_markup=parent_consent_markup(code, lang))


@bot.callback_query_handler(func=lambda c: c.data.startswith("pa:"))
def cb_parent(c):
    uid = c.from_user.id
    parts = c.data.split(":")
    act = parts[1]
    bot.answer_callback_query(c.id)
    lang = lang_of(uid) if db.get_user(uid) else _tg_lang(c.from_user)
    if act == "o" and is_owner(uid):                               # владелица берёт ссылку для родителей ученика
        link = parent_link_for(int(parts[2]))
        return bot.send_message(uid, f"👨‍👩‍👧 Ссылка для родителей {_name_of(int(parts[2]))}. Перешли её маме или папе:\n{link}",
                                disable_web_page_preview=True)
    if act == "new":                                               # ученик берёт ссылку для своих родителей
        link = parent_link_for(uid)
        if not link:
            return
        return bot.send_message(uid, t(lang, "pa_new", link=link), disable_web_page_preview=True)
    if act == "l":                                                 # смена языка на экране согласия
        code, nl = parts[2], parts[3]
        child = db.par_code_child(code)
        if nl not in T or not child:
            return
        db.save_user(uid, lang=nl)
        return edit_or_send(c, t(nl, "pa_consent", child=esc(_first(child))), parent_consent_markup(code, nl))
    if act == "no":
        return edit_or_send(c, t(lang, "hw_cancelled"))
    if act == "yes":
        child = db.par_code_child(parts[2])
        if not child or child == uid:
            return edit_or_send(c, t(lang, "pa_bad"))
        db.parent_link(uid, child)
        edit_or_send(c, t(lang, "pa_done"))
        safe_send(child, t(lang_of(child), "pa_child_note"))
        pu = db.get_user(uid) or {}
        return notify_owner(f"👨‍👩‍👧 К <b>{_name_of(child)}</b> подключился родитель: {esc(pu.get('name') or '?')} (@{esc(pu.get('username') or '—')}). "
                            f"Сводка придёт в воскресенье вечером.")
    if act == "off":
        for par in db.parents_of(uid):
            db.parent_unlink(par, uid)
        return edit_or_send(c, t(lang, "pa_off_done"))


@bot.message_handler(commands=["parents"])
def cmd_parents(m):
    uid, lang = m.from_user.id, lang_of(m.from_user.id)
    if is_owner(uid):
        links = db.all_parent_links()
        if not links:
            return bot.send_message(uid, "Родители пока не подключены. Ссылка для родителей лежит в карточке ученика (кнопка «👨‍👩‍👧 Ссылка для родителей»).")
        by = {}
        for l in links:
            by.setdefault(l["child_id"], []).append(_name_of(l["parent_id"]))
        return bot.send_message(uid, "👨‍👩‍👧 <b>Подключённые родители</b>\n\n" + "\n".join(
            f"· {_name_of(ch)}: {', '.join(ps)}" for ch, ps in by.items()))
    n = len(db.parents_of(uid))
    if not n:
        return bot.send_message(uid, t(lang, "pa_list_none"), reply_markup=ikb([[(t(lang, "pa_btn"), "pa:new")]]))
    bot.send_message(uid, t(lang, "pa_list", n=n), reply_markup=ikb([[(t(lang, "pa_off_all"), "pa:off")], [(t(lang, "pa_btn"), "pa:new")]]))


@bot.message_handler(commands=["stop"])
def cmd_stop(m):
    """Родитель отключает сводку."""
    uid = m.from_user.id
    if db.children_of(uid):
        db.parent_unlink(uid)
        return bot.send_message(uid, t(lang_of(uid), "pa_stopped"))


def parent_summary(child, lang, now):
    """Текст недельной сводки родителю: только итоги, без слов, ответов и переписки."""
    start, end = practice.week_bounds(now.date())
    df = lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%d.%m")
    out = [t(lang, "pw_title", child=esc(_first(child)), start=df(start), end=df(end)), ""]
    ls = db.lessons_between(child, start, end)
    ab = db.absences_between(child, start, end)
    if ls:
        line = t(lang, "pw_lessons", n=len(ls), dates=", ".join(df(x["date"]) for x in ls))
        out.append(line + (t(lang, "pw_abs", a=ab) if ab else ""))
    else:
        out.append(t(lang, "pw_nolessons") + (t(lang, "pw_abs", a=ab) if ab else ""))
    ts = db.tests_between(child, start, end)
    if ts:
        allt = db.tests(child)
        last = ts[-1]
        pct = last["score"] / last["max_score"] * 100
        idx = next((i for i, x in enumerate(allt) if x["id"] == last["id"]), 0)
        delta = ""
        if idx > 0:
            prev = allt[idx - 1]["score"] / allt[idx - 1]["max_score"] * 100
            delta = f" ({pct - prev:+.0f})" if abs(pct - prev) >= 1 else ""
        out.append(t(lang, "pw_test", title=esc(last["title"] or "—"), pct=f"{pct:.0f}", delta=delta))
    else:
        out.append(t(lang, "pw_notests"))
    g, d, late = db.hw_stats(child, start, end)
    if g or late:
        out.append(t(lang, "pw_hw", g=g, d=d) + (t(lang, "pw_late", n=late) if late else ""))
    else:
        out.append(t(lang, "pw_nohw"))
    sc = db.score_between(child, start, end)
    if sc["days"]:
        acc = sc["correct"] * 100 // max(sc["correct"] + sc["wrong"], 1)
        out.append(t(lang, "pw_prac", days=sc["days"], pts=sc["points"], acc=acc))
    else:
        out.append(t(lang, "pw_noprac"))
    slots = [x for x in db.all_schedules() if x["user_id"] == child]
    moves = [mv for mv in db.moves_ok() if mv["user_id"] == child]
    occ = scheduler.occurrences(now, slots, moves, days=7, start_offset=7 - now.weekday()) if (slots or moves) else []
    out.append("")
    if occ:
        rows = "\n".join(f"· {WEEKDAYS[lang][dt.weekday()]} {dt.strftime('%d.%m')} {dt.strftime('%H:%M')}" for dt, _ in occ)
        out.append(t(lang, "pw_sched", rows=rows))
    else:
        out.append(t(lang, "pw_nosched"))
    done, paid, left = db.balance(child)
    out.append("")
    if left < 0:
        out.append(t(lang, "pw_pay_debt", n=abs(left)))
    elif paid or done:
        out.append(t(lang, "pw_pay_zero" if left == 0 else "pw_pay_low" if left == 1 else "pw_pay_ok", left=left))
    out += ["", t(lang, "pw_outro")]
    return "\n".join(out)


def parent_hook(now):
    """Воскресенье с 18:00: сводка каждому подключённому родителю (по разу в неделю)."""
    if now.weekday() != 6 or now.hour < 18:
        return
    sent = 0
    for l in db.all_parent_links():
        key = f"par:{l['child_id']}:{now.date().isoformat()}"
        if db.was_sent(l["parent_id"], key):
            continue
        db.mark_sent(l["parent_id"], key)
        if safe_send(l["parent_id"], parent_summary(l["child_id"], lang_of(l["parent_id"]), now)):
            sent += 1
    if sent and not db.was_sent(0, f"par_note:{now.date().isoformat()}"):
        db.mark_sent(0, f"par_note:{now.date().isoformat()}")
        notify_owner(f"👨‍👩‍👧 Родителям отправлено сводок: {sent}")


@bot.message_handler(commands=["parentsum"])
def cmd_parentsum(m):
    """Для владелицы: предпросмотр сводки ученика, чтобы увидеть, что получит родитель. /parentsum Имя"""
    if not is_owner(m.from_user.id):
        return
    q = (m.text or "").split(maxsplit=1)[1].strip().lower() if len((m.text or "").split(maxsplit=1)) > 1 else ""
    st = [s_ for s_ in db.students() if q and q in (s_["name"] or "").lower()]
    if not st:
        return bot.send_message(m.chat.id, "Напиши так: <code>/parentsum Имя</code> (часть имени ученика).")
    bot.send_message(m.chat.id, parent_summary(st[0]["user_id"], "ru", datetime.now(db.TZ)))


# ── продление практики без Telegram Stars: реквизиты → «я оплатил(а)» → подтверждение владелицей ──

@bot.callback_query_handler(func=lambda c: c.data.startswith("lx:"))
def cb_extend(c):
    uid, lang = c.from_user.id, lang_of(c.from_user.id)
    parts = c.data.split(":")
    act = parts[1]
    base = practice.LIVES_PER_DAY
    if act in ("ok", "no"):                                   # решение владелицы
        if not is_owner(uid):
            return bot.answer_callback_query(c.id)
        r = db.lx_get(int(parts[2]))
        if not r or r["status"] != "new":
            return bot.answer_callback_query(c.id, "Эта заявка уже обработана")
        sid = r["user_id"]
        sl = lang_of(sid)
        bot.answer_callback_query(c.id, "Готово")
        if act == "ok":
            db.lx_set(r["id"], "ok")
            until = db.game_set_pro(sid, PRO_DAYS, base)
            edit_or_send(c, f"✅ Расширенная практика для {_name_of(sid)} включена до {_fmt_full(until)}.")
            safe_send(sid, t(sl, "lx_ok", until=_fmt_full(until), pro=base * db.PRO_MULT))
        else:
            db.lx_set(r["id"], "no")
            edit_or_send(c, f"❌ Платёж от {_name_of(sid)} не подтверждён.")
            safe_send(sid, t(sl, "lx_no"))
        return
    bot.answer_callback_query(c.id)
    if is_owner(uid):
        return
    if act == "info":
        if not (PAY_INFO or PAY_URL):                         # способ оплаты ещё не задан: просим написать преподавателю
            u = db.get_user(uid) or {}
            sent = notify_owner(f"💳 <b>{esc(u.get('name') or '?')}</b> (@{esc(u.get('username') or '—')}) хочет продлить практику. "
                                f"Задай PAY_INFO/PAY_URL, чтобы бот сам присылал реквизиты.\n\n<i>Ответь на это сообщение, и я перешлю ответ.</i>")
            if sent:
                db.save_inbox(sent.message_id, uid)
            return bot.send_message(uid, t(lang, "lx_off"))
        rows = []
        if PAY_URL.lower().startswith("http"):
            k = types.InlineKeyboardMarkup()
            k.row(types.InlineKeyboardButton(t(lang, "lx_url"), url=PAY_URL))
            k.row(types.InlineKeyboardButton(t(lang, "lx_paid"), callback_data="lx:paid"))
        else:
            k = ikb([[(t(lang, "lx_paid"), "lx:paid")]])
        return bot.send_message(uid, t(lang, "lx_info", base=base, pro=base * db.PRO_MULT, days=PRO_DAYS,
                                       price=esc(PAY_PRICE or "—"), pay=esc(PAY_INFO or "—")), reply_markup=k,
                                disable_web_page_preview=True)
    if act == "paid":
        rid, new = db.lx_open(uid)
        if not new:
            return bot.send_message(uid, t(lang, "lx_dup"))
        u = db.get_user(uid) or {}
        sent = notify_owner(f"💳 <b>{esc(u.get('name') or '?')}</b> (@{esc(u.get('username') or '—')}) нажал(а) «Я оплатил(а)»: "
                            f"расширенная практика на {PRO_DAYS} дней" + (f", {esc(PAY_PRICE)}" if PAY_PRICE else "") + ".\n"
                            f"Проверь поступление и подтверди.",
                            reply_markup=ikb([[("✅ Оплата пришла", f"lx:ok:{rid}"), ("❌ Не нашёл", f"lx:no:{rid}")]]))
        if sent:
            db.save_inbox(sent.message_id, uid)
        return bot.send_message(uid, t(lang, "lx_sent"))


# ─── ПРОБНЫЙ УРОК И «ПРИВЕДИ ДРУГА» ──────────────────────────────────────────

_BOT_NAME = []


def bot_username():
    if not _BOT_NAME:
        try:
            _BOT_NAME.append(bot.get_me().username or "")
        except Exception:
            return ""
    return _BOT_NAME[0]


def ask_trial(uid):
    lang = lang_of(uid)
    if is_owner(uid) or (db.get_user(uid) or {}).get("is_student"):
        return bot.send_message(uid, t(lang, "trial_students"))
    STATE[uid] = {"step": "trial_when", "data": {}}
    bot.send_message(uid, t(lang, "trial_ask"))


def finish_trial(uid, txt):
    lang = lang_of(uid)
    u = db.get_user(uid) or {}
    ref = db.referral_of(uid)
    lines = [f"📝 <b>Заявка на пробный урок</b>", "",
             f"{esc(u.get('name') or '?')} (@{esc(u.get('username') or '—')})",
             f"Язык: {u.get('lang')} · Уровень: {esc(u.get('level') or '—')}",
             f"Откуда: {esc(u.get('source') or '—')}"]
    if ref:
        rn = (db.get_user(ref["referrer_id"]) or {}).get("name") or "?"
        lines.append(f"🎁 Пришёл(ла) от друга: {esc(rn)}")
    lines += ["", f"Пожелания: {esc(txt[:500])}", "", "<i>Ответь на это сообщение, и я перешлю ответ.</i>"]
    sent = notify_owner("\n".join(lines))
    if sent:
        db.save_inbox(sent.message_id, uid)
    bot.send_message(uid, t(lang, "trial_sent"), reply_markup=kb_main(uid))
    if ref and db.referral_mark(uid, "trial"):
        rid = ref["referrer_id"]
        rl = (db.get_user(rid) or {}).get("lang") or "ru"
        safe_send(rid, t(rl, "ref_got2", friend=esc(u.get("name") or ""), reward=t(rl, "ref_r2")))
        rn = (db.get_user(rid) or {}).get("name") or "?"
        give_note(rid, "card", f"Китайское имя и открытка с иероглифами (друг {u.get('name') or '?'} записался на пробный)")


def referral_paid(sid):
    """Первая оплата друга: сообщаем тому, кто пригласил, и преподавателю."""
    if db.payments_count(sid) != 1:
        return
    ref = db.referral_of(sid)
    if ref and db.referral_mark(sid, "paid"):
        rid = ref["referrer_id"]
        rl = (db.get_user(rid) or {}).get("lang") or "ru"
        fname = (db.get_user(sid) or {}).get("name") or ""
        safe_send(rid, t(rl, "ref_got3", friend=esc(fname), reward=t(rl, "ref_r3")))
        db.discount_queue_add(rid, sid)
        st = db.discount_state(rid)
        notify_owner(f"💸 <b>{_name_of(rid)}</b> привела друга ({esc(fname)}), и он начал заниматься: +1 скидочный месяц (30%).\n"
                     f"В очереди: {st['queued']}" + (f"; сейчас идёт скидка до {_fmt_full(st['active']['end'])}" if st["active"] else "")
                     + ".\nПредложу применить скидку, когда ты запишешь её следующую оплату.")


def send_friend(uid):
    lang = lang_of(uid)
    name = bot_username()
    if not name:
        return bot.send_message(uid, t(lang, "qz_fail"))
    link = f"https://t.me/{name}?start=ref_{uid}"
    rewards = "\n".join(t(lang, k) for k in ("ref_r1", "ref_r2", "ref_r3"))
    text = t(lang, "friend_text", link=link, rewards=rewards, **db.referral_stats(uid))
    st = db.discount_state(uid)
    if st["active"]:
        text += "\n\n" + t(lang, "disc_active", end=_fmt_full(st["active"]["end"]))
    if st["queued"]:
        text += "\n" + t(lang, "disc_queue", n=st["queued"])
    bot.send_message(uid, text, disable_web_page_preview=True)


# ─── ДОМАШНИЕ ЗАДАНИЯ ─────────────────────────────────────────────────────────

def fmt_due(due, lang="ru"):
    return datetime.strptime(due, "%Y-%m-%d").strftime("%d.%m") if due else t(lang, "hw_nodue")


@bot.callback_query_handler(func=lambda c: c.data.startswith("hwn:"))
@owner_only
def cb_hw_new(c):
    uid = int(c.data.split(":")[1])
    STATE[c.from_user.id] = {"step": "hw_text", "data": {"uid": uid, "uids": [uid]}}
    bot.send_message(c.message.chat.id, f"Домашка для {_name_of(uid)}. Что задать? Напиши текст задания.")
    bot.answer_callback_query(c.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("hwd:"))
def cb_hw_done(c):
    uid, lang = c.from_user.id, lang_of(c.from_user.id)
    try:
        hid = int(c.data.split(":")[1])
    except ValueError:
        return bot.answer_callback_query(c.id)
    h = db.hw_get(hid)
    if not h or h["user_id"] != uid:
        return bot.answer_callback_query(c.id)
    bot.answer_callback_query(c.id)
    try:
        bot.edit_message_reply_markup(uid, c.message.message_id, reply_markup=None)
    except Exception:
        pass
    if h["done"]:
        return
    db.hw_done(hid)
    bot.send_message(uid, t(lang, "hw_thanks"))
    notify_owner(f"✅ {_name_of(uid)} сделал(а) домашку: «{esc(h['text'][:80])}»")


def send_hw_list(uid):
    lang = lang_of(uid)
    if is_owner(uid):
        rows = db.hw_all_open()
        if not rows:
            return bot.send_message(uid, t(lang, "hw_none"))
        today = db.today()
        out = [t(lang, "hw_title"), ""]
        for h in sorted(rows, key=lambda x: x["due"] or "9999"):
            late = " ⚠️ просрочено" if h["due"] and h["due"] < today else ""
            out.append(f"· {_name_of(h['user_id'])}: {esc(h['text'][:60])} ({fmt_due(h['due'])}){late}")
        return bot.send_message(uid, "\n".join(out))
    rows = db.hw_open(uid)
    if not rows:
        return bot.send_message(uid, t(lang, "hw_none"))
    bot.send_message(uid, t(lang, "hw_title"))
    for h in rows:
        bot.send_message(uid, t(lang, "hw_new", text=esc(h["text"]), due=fmt_due(h["due"], lang)),
                         reply_markup=hw_markup(h["id"], lang))


def hw_hook(now):
    """Раз в минуту: напоминание в день срока (после 10:00) и один раз сообщение тебе о просрочке."""
    if now.hour < 10:
        return
    today = now.strftime("%Y-%m-%d")
    for h in db.hw_all_open():
        if not h["due"]:
            continue
        if h["due"] == today and not db.was_sent(h["user_id"], f"hwr:{h['id']}"):
            db.mark_sent(h["user_id"], f"hwr:{h['id']}")
            safe_send(h["user_id"], t(lang_of(h["user_id"]), "hw_remind", text=esc(h["text"][:80])))
        elif h["due"] < today and not db.was_sent(h["user_id"], f"hwo:{h['id']}"):
            db.mark_sent(h["user_id"], f"hwo:{h['id']}")
            notify_owner(f"⚠️ {_name_of(h['user_id'])} не отметил(а) домашку «{esc(h['text'][:60])}» "
                         f"(срок был {fmt_due(h['due'])}).")


# ─── ПЕРЕНОС УРОКА ────────────────────────────────────────────────────────────

def when_label(dt, lang):
    return f"{WEEKDAYS[lang][dt.weekday()]}, {dt.strftime('%d.%m %H:%M')}"


@bot.callback_query_handler(func=lambda c: c.data == "mv:ask")
def cb_move_ask(c):
    uid, lang = c.from_user.id, lang_of(c.from_user.id)
    bot.answer_callback_query(c.id)
    nxt = next_lesson(uid, datetime.now(db.TZ))
    if not nxt:
        return bot.send_message(uid, t(lang, "mv_none"))
    STATE[uid] = {"step": "move_when", "data": {"orig": nxt.strftime("%Y-%m-%dT%H:%M")}}
    bot.send_message(uid, t(lang, "mv_ask", when=when_label(nxt, lang)))


def finish_move(uid, txt):
    lang, st = lang_of(uid), STATE.get(uid)
    now = datetime.now(db.TZ)
    new = practice.parse_when(txt, now)
    if not new:
        return bot.send_message(uid, t(lang, "mv_bad"))
    STATE.pop(uid, None)
    orig = st["data"]["orig"]
    new_iso = new.strftime("%Y-%m-%dT%H:%M")
    if new_iso == orig:
        return bot.send_message(uid, t(lang, "mv_bad"))
    mid = db.move_add(uid, orig, new_iso)
    clash = [x for dt, x in scheduler.occurrences(now, db.all_schedules(), db.moves_ok(), days=31)
             if dt == new and x["user_id"] != uid]
    o = datetime.strptime(orig, "%Y-%m-%dT%H:%M")
    text = (f"🔄 <b>{_name_of(uid)}</b> просит перенести урок\n{o.strftime('%d.%m %H:%M')} → "
            f"<b>{new.strftime('%d.%m %H:%M')}</b> ({WEEKDAYS['ru'][new.weekday()]})")
    if clash:
        text += f"\n⚠️ В это время уже урок с {esc(clash[0].get('name') or '—')}"
    notify_owner(text, reply_markup=ikb([[("✅ Подтвердить", f"mvy:{mid}"), ("✖️ Отказать", f"mvn:{mid}")]]))
    bot.send_message(uid, t(lang, "mv_sent"), reply_markup=kb_main(uid))


def _move_answer(c, ok):
    mid = int(c.data.split(":")[1])
    m = db.move_get(mid)
    if not m or m["status"] != "pending":
        bot.answer_callback_query(c.id, "Уже обработано")
        return None
    db.move_set(mid, "ok" if ok else "no")
    bot.answer_callback_query(c.id, "Готово")
    uid = m["user_id"]
    lang = lang_of(uid)
    new = datetime.strptime(m["new"], "%Y-%m-%dT%H:%M")
    verdict = f"{'✅ Перенос подтверждён' if ok else '✖️ Отказала'}: {_name_of(uid)}, {new.strftime('%d.%m %H:%M')}"
    try:
        bot.edit_message_text(verdict, c.message.chat.id, c.message.message_id)
    except Exception:
        pass
    safe_send(uid, t(lang, "mv_ok", when=when_label(new, lang)) if ok else t(lang, "mv_no"))


@bot.callback_query_handler(func=lambda c: c.data.startswith("mvy:"))
@owner_only
def cb_move_yes(c): _move_answer(c, True)


@bot.callback_query_handler(func=lambda c: c.data.startswith("mvn:"))
@owner_only
def cb_move_no(c): _move_answer(c, False)


# ─── ОТЗЫВЫ ───────────────────────────────────────────────────────────────────

REVIEW_AT = (8, 24)        # после какого по счёту урока просим отзыв


def maybe_ask_review(sid):
    done = db.balance(sid)[0]
    if done not in REVIEW_AT or db.was_sent(sid, f"rv:{done}") or is_owner(sid):
        return
    db.mark_sent(sid, f"rv:{done}")
    lang = lang_of(sid)
    safe_send(sid, t(lang, "rv_ask", n=done), reply_markup=ikb([[(f"{'⭐' * r}", f"rv:r:{r}") for r in (1, 2, 3, 4, 5)]]))


@bot.callback_query_handler(func=lambda c: c.data.startswith("rv:"))
def cb_review(c):
    uid, lang = c.from_user.id, lang_of(c.from_user.id)
    parts = c.data.split(":")
    bot.answer_callback_query(c.id)
    if parts[1] == "r":
        try:
            STATE[uid] = {"step": "rv_text", "data": {"rating": max(1, min(5, int(parts[2])))}}
        except ValueError:
            return
        return edit_or_send(c, t(lang, "rv_text"))
    st = STATE.get(uid)
    if parts[1] == "p" and st and st["step"] == "rv_public":
        STATE.pop(uid, None)
        d = st["data"]
        public = parts[2] == "1"
        db.review_add(uid, d["rating"], d["text"], public)
        edit_or_send(c, t(lang, "rv_thanks"))
        notify_owner(f"⭐ Отзыв от {_name_of(uid)}: <b>{d['rating']}/5</b>\n"
                     f"{esc(d['text']) or '—'}\nПоказывать в постах: {'да' if public else 'нет'}")


# ─── KPI-ТОЧКА РАЗ В 4 НЕДЕЛИ ─────────────────────────────────────────────────

KPI_LIST = ["Удержание", "Активация словаря", "Беглость речи", "Аудирование",
            "Точность", "Иероглифы", "Спонтанная продукция", "Результат тестов"]


def kpi_hook(now):
    if now.hour < 10:
        return
    today = now.date()
    for s in db.students():
        first = db.first_lesson_date(s["user_id"])
        if not first:
            continue
        days = (today - datetime.strptime(first, "%Y-%m-%d").date()).days
        period = days // 28
        key = f"kpi:{period}"
        if period >= 1 and not db.was_sent(s["user_id"], key):
            db.mark_sent(s["user_id"], key)
            notify_owner(f"📈 <b>KPI-точка: {esc(s['name'] or '—')}</b>\nЗанимается уже {days // 7} нед. "
                         f"Пора внести 8 показателей:\n" + "\n".join(f"{i}. {n}" for i, n in enumerate(KPI_LIST, 1)) +
                         "\n\nНажми кнопку и напиши коротко цвет каждого (🟢🟡🔴) и что меняем.",
                         reply_markup=ikb([[("📝 Записать", f"kpi:{s['user_id']}")]]))


@bot.callback_query_handler(func=lambda c: c.data.startswith("kpi:"))
@owner_only
def cb_kpi(c):
    _ask(c, "kpi_note", "Запиши KPI-точку одним сообщением, например:\n"
                        "<code>1🟢 2🟡 3🟡 4🟢 5🟢 6🟢 7🟡 8🟢; усилить речь +10 минут</code>")


# ─── ВЫГРУЗКА В CSV ───────────────────────────────────────────────────────────

@bot.message_handler(commands=["csv"])
def cmd_csv(m):
    if not is_owner(m.from_user.id):
        return
    parts = (m.text or "").split()
    ym = parts[1] if len(parts) > 1 else datetime.now(db.TZ).strftime("%Y-%m")
    if not re.fullmatch(r"\d{4}-\d{2}", ym):
        return bot.send_message(m.chat.id, "Формат: <code>/csv 2026-10</code> (или просто /csv за этот месяц).")
    rows = db.month_rows(ym)
    if not rows:
        return bot.send_message(m.chat.id, f"За {ym} записей нет.")
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(["Дата", "Ученик", "Что", "Количество уроков", "Заметка"])
    w.writerows(rows)
    f = io.BytesIO(("﻿" + buf.getvalue()).encode("utf-8"))      # BOM: Excel открывает русский текст без кракозябр
    f.name = f"hanzhu_{ym}.csv"
    bot.send_document(m.chat.id, f, caption=f"Уроки и оплаты за {ym}: {len(rows)} строк")


# ─── КОМАНДЫ НОВЫХ ФУНКЦИЙ ────────────────────────────────────────────────────

@bot.message_handler(commands=["practice"])
def cmd_practice(m): send_practice(m.from_user.id)

@bot.message_handler(commands=["quiz"])
def cmd_quiz(m): start_quiz(m.from_user.id)

@bot.message_handler(commands=["cards"])
def cmd_cards(m): start_cards(m.from_user.id)

@bot.message_handler(commands=["tea"])
def cmd_tea(m): send_tea(m.from_user.id)

@bot.message_handler(commands=["friend"])
def cmd_friend(m): send_friend(m.from_user.id)

@bot.message_handler(commands=["trial"])
def cmd_trial(m): ask_trial(m.from_user.id)

@bot.message_handler(commands=["hw"])
def cmd_hw(m): send_hw_list(m.from_user.id)


# ─── МАРАФОН ВИКТОРИНЫ (100 / 150 вопросов) ───────────────────────────────────

MARA = {}                               # uid → текущий вопрос (в памяти); прогресс лежит в базе


def mr_total(level):
    return practice.MARATHON_LEN[level]


def send_marathon_menu(uid, c=None):
    lang = lang_of(uid)
    runs = {r["level"]: r for r in db.marathon_all(uid)}
    rows = []
    for lv in range(1, 7):
        r, tot = runs.get(lv), mr_total(lv)
        if r and r["finished"]:
            label = f"✅ HSK {lv} · {r['correct']}/{tot}"
        elif r and r["done"]:
            label = f"▶️ HSK {lv} · {r['done']}/{tot}"
        else:
            label = f"HSK {lv} · {tot}"
        rows.append([(label, f"mr:l:{lv}")])
    if c:
        return edit_or_send(c, t(lang, "mr_pick"), ikb(rows))
    bot.send_message(uid, t(lang, "mr_pick"), reply_markup=ikb(rows))


def ask_marathon(uid, level, c=None, prev=""):
    lang = lang_of(uid)
    r, total = db.marathon_get(uid, level), mr_total(level)
    if not r:
        return
    if r["done"] >= total:
        return finish_marathon(uid, level, c)
    q = practice.marathon_question(lang, level, r["seen"])
    if not q:                                           # слова уровня кончились раньше (например, сменили язык)
        if r["done"]:
            return finish_marathon(uid, level, c)
        return bot.send_message(uid, t(lang, "qz_fail"))
    n = r["done"] + 1
    MARA[uid] = {"level": level, "n": n, "q": q, "answered": False}
    rows = [[(opt, f"mr:a:{level}:{n}:{i}")] for i, opt in enumerate(q["options"])]
    rows.append([(t(lang, "mr_pause"), f"mr:p:{level}")])
    text = t(lang, "mr_q", level=level, n=n, total=total, bar=bar(r["done"] / total * 100, 15),
             prev=prev, zh=esc(q["zh"]), py=esc(q["py"]))
    if c:
        return edit_or_send(c, text, ikb(rows))
    bot.send_message(uid, text, reply_markup=ikb(rows))


def finish_marathon(uid, level, c=None):
    lang = lang_of(uid)
    r = db.marathon_get(uid, level)
    total, correct = r["done"], r["correct"]
    db.marathon_save(uid, level, finished=db.today())
    db.feed_add(uid, "marathon", str(level))
    pct = correct * 100 // max(total, 1)
    tk = practice.marathon_title(correct, total)
    wz, wpy, wd = WISHES[level]
    meaning, wish = wd.get(lang) or wd["ru"]
    text = t(lang, "mr_done", level=level, total=total, correct=correct, pct=pct, title=t(lang, "mr_title_" + tk),
             zh=wz, py=esc(wpy), meaning=esc(meaning), wish=esc(wish))
    if not db.was_sent(uid, f"mrg:{level}"):                         # подарок за уровень один раз
        db.mark_sent(uid, f"mrg:{level}")
        db.game_add_lives(uid, 5, practice.LIVES_PER_DAY)
        text += t(lang, "mr_gift", n=5)
    rows = []
    name = bot_username()
    if name:
        link = f"https://t.me/{name}?start=ref_{uid}"
        share = "https://t.me/share/url?url=" + quote(link) + "&text=" + quote(
            t(lang, "mr_share_text", level=level, correct=correct, total=total))
        rows.append([types.InlineKeyboardButton(t(lang, "mr_share"), url=share)])
    if r["wrong"]:
        rows.append([types.InlineKeyboardButton(t(lang, "mr_add", n=len(r["wrong"])), callback_data=f"mr:add:{level}")])
    rows.append([types.InlineKeyboardButton(t(lang, "mr_more"), callback_data="mr:menu")])
    markup = types.InlineKeyboardMarkup()
    for row in rows:
        markup.row(*row)
    MARA.pop(uid, None)
    if c:
        edit_or_send(c, text, markup)
    else:
        bot.send_message(uid, text, reply_markup=markup)
    if not is_owner(uid):
        notify_owner(f"🏅 {_name_of(uid)} прошёл(ла) марафон HSK {level}: {correct}/{total} ({pct}%). "
                     f"Можно поздравить лично.")


@bot.callback_query_handler(func=lambda c: c.data.startswith("mr:"))
def cb_marathon(c):
    uid, lang = c.from_user.id, lang_of(c.from_user.id)
    parts = c.data.split(":")
    act = parts[1]
    try:
        if act == "menu":
            bot.answer_callback_query(c.id)
            return send_marathon_menu(uid, c)
        level = int(parts[2])
        if level not in practice.MARATHON_LEN:
            return bot.answer_callback_query(c.id)
    except (ValueError, IndexError):
        return bot.answer_callback_query(c.id)
    r = db.marathon_get(uid, level)

    if act == "l":
        bot.answer_callback_query(c.id)
        if not r:
            db.log_event(uid, "marathon")
            db.marathon_start(uid, level)
            return ask_marathon(uid, level, c)
        if r["finished"]:
            return edit_or_send(c, t(lang, "mr_again_ask"), ikb([[(t(lang, "mr_restart_btn"), f"mr:new:{level}")],
                                                                  [(t(lang, "mr_back"), "mr:menu")]]))
        if r["done"] == 0:
            return ask_marathon(uid, level, c)
        return edit_or_send(c, t(lang, "mr_resume", n=r["done"] + 1, total=mr_total(level)),
                            ikb([[(t(lang, "mr_resume_btn"), f"mr:go:{level}")],
                                 [(t(lang, "mr_restart_btn"), f"mr:new:{level}")], [(t(lang, "mr_back"), "mr:menu")]]))
    if act == "go":
        bot.answer_callback_query(c.id)
        return ask_marathon(uid, level, c)
    if act == "new":
        bot.answer_callback_query(c.id)
        db.log_event(uid, "marathon")
        db.marathon_start(uid, level)
        return ask_marathon(uid, level, c)
    if act == "p":
        bot.answer_callback_query(c.id)
        MARA.pop(uid, None)
        done = r["done"] if r else 0
        return edit_or_send(c, t(lang, "mr_paused", done=done, total=mr_total(level)))
    if act == "add":
        bot.answer_callback_query(c.id)
        if not r:
            return
        for zh in r["wrong"]:
            db.card_add(uid, zh)
        try:
            bot.edit_message_reply_markup(uid, c.message.message_id, reply_markup=None)
        except Exception:
            pass
        return bot.send_message(uid, t(lang, "qz_added", n=len(r["wrong"])))
    if act == "a":
        try:
            n, i = int(parts[3]), int(parts[4])
        except (ValueError, IndexError):
            return bot.answer_callback_query(c.id)
        sess = MARA.get(uid)
        if not r or not sess or sess["level"] != level or sess["n"] != n or sess["answered"] or r["done"] + 1 != n:
            bot.answer_callback_query(c.id, t(lang, "mr_stale"))
            return ask_marathon(uid, level, c)
        sess["answered"] = True
        q = sess["q"]
        ok = i == q["answer"]
        r["seen"].append(q["zh"])
        if not ok:
            r["wrong"].append(q["zh"])
        db.marathon_save(uid, level, done=r["done"] + 1, correct=r["correct"] + (1 if ok else 0),
                         seen=r["seen"], wrong=r["wrong"])
        bot.answer_callback_query(c.id, t(lang, "mr_toast_ok") if ok else t(lang, "mr_toast_no", right=q["right"]))
        prev = t(lang, "mr_prev_ok" if ok else "mr_prev_no", zh=esc(q["zh"]), right=esc(q["right"]))
        return ask_marathon(uid, level, c, prev)


# ─── ГРУППЫ УЧЕНИКОВ И РАССЫЛКА ДОМАШКИ ───────────────────────────────────────

PICK = {}                               # выбор учеников у преподавателя: {owner_id: {mode, gid, sel}}


def picker_markup(uid):
    p = PICK[uid]
    rows = []
    if p["mode"] == "hw":
        for g in db.group_list():
            if g["n"]:
                rows.append([(f"👥 {g['name']} ({g['n']})", f"pk:g:{g['id']}")])
    for s in db.students()[:60]:
        rows.append([(("☑️ " if s["user_id"] in p["sel"] else "⬜ ") + (s["name"] or "—"), f"pk:t:{s['user_id']}")])
    rows.append([(f"✅ Готово ({len(p['sel'])})", "pk:ok"), ("✖️ Отмена", "pk:x")])
    return ikb(rows)


def start_picker(uid, mode, prompt, gid=None, sel=()):
    PICK[uid] = {"mode": mode, "gid": gid, "sel": set(sel)}
    if not db.students():
        PICK.pop(uid, None)
        return bot.send_message(uid, "Учеников пока нет. Сначала отметь кого-нибудь через «➕ Сделать учеником».")
    bot.send_message(uid, prompt, reply_markup=picker_markup(uid))


def group_view(chat_id, gid, c=None):
    g = db.group_get(gid)
    if not g:
        return bot.send_message(chat_id, "Такой группы уже нет.")
    mem = db.group_members(gid)
    text = f"👥 <b>{esc(g['name'])}</b>\nУчеников в группе: {len(mem)}\n\n" + (
        "\n".join(f"· {esc(m['name'] or '—')}" for m in mem) or "Пока пусто.")
    markup = ikb([[("✏️ Состав", f"grp:e:{gid}"), ("📚 Задать домашку", f"grp:h:{gid}")],
                  [("🗑 Удалить группу", f"grp:d:{gid}")], [("⬅️ Все группы", "grp:list")]])
    if c:
        return edit_or_send(c, text, markup)
    bot.send_message(chat_id, text, reply_markup=markup)


def send_groups(chat_id, c=None):
    gs = db.group_list()
    text = ("👥 <b>Группы учеников</b>\n\nГруппа нужна, чтобы отправить одну домашку сразу нескольким людям. "
            "Один ученик может быть в нескольких группах." if gs else
            "👥 <b>Группы учеников</b>\n\nГрупп пока нет. Создай первую: в неё можно собрать учеников и "
            "отправлять им одну домашку одним нажатием.")
    rows = [[(f"{g['name']} ({g['n']})", f"grp:v:{g['id']}")] for g in gs] + [[("➕ Новая группа", "grp:new")]]
    if c:
        return edit_or_send(c, text, ikb(rows))
    bot.send_message(chat_id, text, reply_markup=ikb(rows))


@bot.message_handler(commands=["groups"])
def cmd_groups(m):
    if is_owner(m.from_user.id):
        send_groups(m.chat.id)


@bot.callback_query_handler(func=lambda c: c.data == "a:groups")
@owner_only
def cb_groups_menu(c):
    bot.answer_callback_query(c.id)
    send_groups(c.message.chat.id)


@bot.callback_query_handler(func=lambda c: c.data == "a:hw")
@owner_only
def cb_hw_menu(c):
    bot.answer_callback_query(c.id)
    start_picker(c.from_user.id, "hw", "📚 <b>Кому задать домашку?</b>\nМожно выбрать группу целиком и/или отдельных учеников.")


@bot.callback_query_handler(func=lambda c: c.data.startswith("grp:"))
@owner_only
def cb_group(c):
    uid = c.from_user.id
    parts = c.data.split(":")
    act = parts[1]
    bot.answer_callback_query(c.id)
    if act == "list":
        return send_groups(c.message.chat.id, c)
    if act == "new":
        STATE[uid] = {"step": "grp_name", "data": {}}
        return bot.send_message(uid, "Как назвать группу? Например: «Вторники HSK 2».")
    gid = int(parts[2])
    if act == "v":
        return group_view(c.message.chat.id, gid, c)
    if act == "e":
        g = db.group_get(gid)
        if not g:
            return
        return start_picker(uid, "members", f"✏️ <b>Кто в группе «{esc(g['name'])}»?</b>", gid=gid,
                            sel=[m["user_id"] for m in db.group_members(gid)])
    if act == "h":
        g, mem = db.group_get(gid), db.group_members(gid)
        if not g or not mem:
            return bot.send_message(uid, "В группе нет учеников. Сначала добавь их через «✏️ Состав».")
        STATE[uid] = {"step": "hw_text", "data": {"uids": [m["user_id"] for m in mem]}}
        return bot.send_message(uid, f"Домашка для группы «{esc(g['name'])}» ({len(mem)} чел.).\nЧто задать? Напиши текст задания.")
    if act == "d":
        g = db.group_get(gid)
        if g:
            edit_or_send(c, f"Удалить группу «{esc(g['name'])}»? Ученики и их история останутся, исчезнет только группа.",
                         ikb([[("Да, удалить", f"grp:d1:{gid}"), ("Отмена", f"grp:v:{gid}")]]))
        return
    if act == "d1":
        db.group_delete(gid)
        return send_groups(c.message.chat.id, c)


@bot.callback_query_handler(func=lambda c: c.data.startswith("pk:"))
@owner_only
def cb_pick(c):
    uid = c.from_user.id
    p = PICK.get(uid)
    parts = c.data.split(":")
    act = parts[1]
    if not p:
        return bot.answer_callback_query(c.id, "Выбор устарел, начни заново")
    if act == "x":
        PICK.pop(uid, None)
        bot.answer_callback_query(c.id)
        return edit_or_send(c, "Отменено.")
    if act == "t":
        u = int(parts[2])
        p["sel"].symmetric_difference_update({u})
    elif act == "g":
        ids = {m["user_id"] for m in db.group_members(int(parts[2]))}
        if ids <= p["sel"]:
            p["sel"] -= ids
        else:
            p["sel"] |= ids
    elif act == "ok":
        if not p["sel"]:
            return bot.answer_callback_query(c.id, "Никто не выбран")
        PICK.pop(uid, None)
        bot.answer_callback_query(c.id)
        if p["mode"] == "members":
            db.group_set_members(p["gid"], sorted(p["sel"]))
            return group_view(c.message.chat.id, p["gid"], c)
        names = ", ".join(_name_of(u) for u in sorted(p["sel"])[:8]) + (" …" if len(p["sel"]) > 8 else "")
        edit_or_send(c, f"Домашка для {len(p['sel'])} чел.: {names}")
        STATE[uid] = {"step": "hw_text", "data": {"uids": sorted(p["sel"])}}
        return bot.send_message(uid, "Что задать? Напиши текст задания.")
    bot.answer_callback_query(c.id)
    try:
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=picker_markup(uid))
    except Exception:
        pass


# ─── СДАЧА ДОМАШКИ УЧЕНИКОМ ───────────────────────────────────────────────────

HW_OK_EXT = {"jpg", "jpeg", "png", "heic", "webp", "pdf", "doc", "docx", "txt", "mp3", "m4a", "ogg", "oga", "wav"}
HW_WINDOW = 30 * 60                     # сколько минут открыта сдача, если человек ушёл


def hw_markup(hid, lang):
    return ikb([[(t(lang, "hw_submit_btn"), f"hws:ask:{hid}")], [(t(lang, "hw_btn"), f"hwd:{hid}")]])


def deliver_hw(uids, text, due):
    ok, fail = [], []
    for u in uids:
        hid = db.hw_add(u, text, due)
        sl = lang_of(u)
        sent = safe_send(u, t(sl, "hw_new", text=esc(text), due=fmt_due(due, sl)), reply_markup=hw_markup(hid, sl))
        (ok if sent else fail).append(u)
    return ok, fail


def file_ok(m):
    if m.content_type in ("photo", "voice", "audio"):
        return True
    if m.content_type == "document" and m.document:
        name = (m.document.file_name or "").lower()
        ext = name.rsplit(".", 1)[-1] if "." in name else ""
        mime = m.document.mime_type or ""
        return ext in HW_OK_EXT or mime.startswith(("image/", "audio/")) or mime == "application/pdf"
    return False


def hw_sub_state(uid):
    """Открытая сдача домашки или None (просроченную закрывает)."""
    st = STATE.get(uid)
    if not st or st["step"] != "hw_submit":
        return None
    if time.time() - st["data"]["ts"] > HW_WINDOW:
        STATE.pop(uid, None)
        return None
    return st


def take_submission(uid, m):
    st = hw_sub_state(uid)
    d, lang = st["data"], lang_of(uid)
    h = db.hw_get(d["hid"]) or {"text": ""}
    if d["n"] == 0:
        notify_owner(f"📥 <b>{_name_of(uid)}</b> присылает домашку «{esc(h['text'][:80])}»:")
    try:
        bot.copy_message(OWNER_ID, m.chat.id, m.message_id)
    except Exception as e:
        logging.warning("не удалось переслать домашку: %s", e)
        return bot.send_message(uid, t(lang, "hw_bad_fmt"))
    d["n"] += 1
    d["ts"] = time.time()
    gid = getattr(m, "media_group_id", None)
    if gid and d.get("last_group") == gid:
        return                                           # альбом: отвечаем один раз
    d["last_group"] = gid
    bot.send_message(uid, t(lang, "hw_got", n=d["n"]), reply_markup=ikb([[(t(lang, "hw_finish"), f"hws:fin:{d['hid']}")]]))


def finish_submission(uid):
    st = hw_sub_state(uid)
    if not st:
        return False
    d, lang = st["data"], lang_of(uid)
    STATE.pop(uid, None)
    h = db.hw_get(d["hid"]) or {"text": ""}
    db.hw_done(d["hid"])
    sid = db.sub_add(d["hid"], uid, d["n"])
    sent = notify_owner(f"✅ <b>{_name_of(uid)}</b> сдал(а) домашку «{esc(h['text'][:80])}»: файлов/сообщений {d['n']}.\n\n"
                        f"<i>Ответь на это сообщение, и я перешлю ответ ученику.</i>",
                        reply_markup=ikb([[("✅ Принять", f"hwa:{sid}"), ("🔁 Доработать", f"hwr:{sid}")]]))
    if sent:
        db.save_inbox(sent.message_id, uid)
    bot.send_message(uid, t(lang, "hw_sent"), reply_markup=kb_main(uid))
    return True


@bot.callback_query_handler(func=lambda c: c.data.startswith("hws:"))
def cb_hw_submit(c):
    uid, lang = c.from_user.id, lang_of(c.from_user.id)
    parts = c.data.split(":")
    act = parts[1]
    bot.answer_callback_query(c.id)
    if act == "no":
        if hw_sub_state(uid):
            STATE.pop(uid, None)
        return edit_or_send(c, t(lang, "hw_cancelled"))
    try:
        hid = int(parts[2])
    except (ValueError, IndexError):
        return
    h = db.hw_get(hid)
    if not h or h["user_id"] != uid:
        return bot.send_message(uid, t(lang, "hw_stale"))
    if act == "ask":                                     # каждый раз сначала предупреждаем о формате
        return bot.send_message(uid, t(lang, "hw_fmt"), reply_markup=ikb([[(t(lang, "hw_fmt_ok"), f"hws:go:{hid}")],
                                                                          [(t(lang, "hw_cancel"), "hws:no")]]))
    if act == "go":
        STATE[uid] = {"step": "hw_submit", "data": {"hid": hid, "n": 0, "ts": time.time(), "last_group": None}}
        return edit_or_send(c, t(lang, "hw_send_now"), ikb([[(t(lang, "hw_cancel"), "hws:no")]]))
    if act == "fin":
        st = hw_sub_state(uid)
        if not st or st["data"]["hid"] != hid:
            return bot.send_message(uid, t(lang, "hw_stale"))
        if st["data"]["n"] == 0:
            return bot.send_message(uid, t(lang, "hw_empty"))
        try:
            bot.edit_message_reply_markup(uid, c.message.message_id, reply_markup=None)
        except Exception:
            pass
        finish_submission(uid)


@bot.message_handler(content_types=["photo", "document", "voice", "audio", "video", "video_note", "animation"])
def on_file(m):
    uid = m.from_user.id
    lang = lang_of(uid)
    if not hw_sub_state(uid):
        if not is_owner(uid) and db.hw_open(uid):
            bot.send_message(uid, t(lang, "hw_hint"))
        return
    if not file_ok(m):
        return bot.send_message(uid, t(lang, "hw_bad_fmt"))
    take_submission(uid, m)


def _sub_answer(c, ok):
    sid = int(c.data.split(":")[1])
    sub = db.sub_get(sid)
    if not sub:
        return bot.answer_callback_query(c.id, "Не нашёл")
    bot.answer_callback_query(c.id, "Готово")
    h = db.hw_get(sub["hw_id"]) or {"text": "", "user_id": sub["user_id"]}
    u, lang = sub["user_id"], lang_of(sub["user_id"])
    db.sub_set(sid, "ok" if ok else "redo")
    try:
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=None)
    except Exception:
        pass
    if ok:
        safe_send(u, t(lang, "hw_accepted", text=esc(h["text"][:80])))
    else:
        db.hw_reopen(sub["hw_id"])
        safe_send(u, t(lang, "hw_redo", text=esc(h["text"][:80])))
        safe_send(u, t(lang, "hw_new", text=esc(h["text"]), due=fmt_due(h.get("due"), lang)),
                  reply_markup=hw_markup(sub["hw_id"], lang))
    bot.send_message(c.message.chat.id, f"{'✅ Принято' if ok else '🔁 Отправила на доработку'}: {_name_of(u)}")


@bot.callback_query_handler(func=lambda c: c.data.startswith("hwa:"))
@owner_only
def cb_sub_ok(c): _sub_answer(c, True)


@bot.callback_query_handler(func=lambda c: c.data.startswith("hwr:"))
@owner_only
def cb_sub_redo(c): _sub_answer(c, False)


# ─── ПРАВИЛА ИГРЫ И РЕЙТИНГ НЕДЕЛИ ────────────────────────────────────────────

def send_rules(uid):
    lang = lang_of(uid)
    bot.send_message(uid, t(lang, "rules", lives=practice.LIVES_PER_DAY, cap=practice.BOARD_DAILY_CAP,
                            min=practice.BOARD_MIN_POINTS),
                     reply_markup=ikb([[(t(lang, "pr_top"), "pr:top")]]), disable_web_page_preview=True)


def _fmt_d(s):
    return datetime.strptime(s, "%Y-%m-%d").strftime("%d.%m")


def board_name(uid):
    """Что видят другие: только ник. Тем, кто вступил в версии 9 и ник ещё не выбрал, подставляем «Игрок-123»."""
    return db.nick_get(uid)[0] or practice.anon_nick(uid)


def board_lines(ranked, limit, mark_uid=None):
    medals = ["🥇", "🥈", "🥉"]
    out = []
    for i, r in enumerate(ranked[:limit]):
        name = board_name(r["user_id"])
        out.append(f"{medals[i] if i < 3 else str(i + 1) + '.'} {esc(name)} — {r['points']}" + (" 👈" if r["user_id"] == mark_uid else ""))
    return "\n".join(out)


def week_ranking(day):
    start, end = practice.week_bounds(day)
    return start, end, practice.rank(db.score_week(start, end), db.board_joined(), exclude={OWNER_ID})


def send_board(uid, c=None):
    lang = lang_of(uid)
    now = datetime.now(db.TZ)
    start, end, ranked = week_ranking(now.date())
    days_left = (datetime.strptime(end, "%Y-%m-%d").date() - now.date()).days + 1
    body = board_lines(ranked, practice.BOARD_TOP, uid) or t(lang, "top_empty")
    text = t(lang, "top_title", start=_fmt_d(start), end=_fmt_d(end), days=days_left, rows=body)
    joined = db.board_joined(uid)
    place = next((i + 1 for i, r in enumerate(ranked) if r["user_id"] == uid), None)
    if joined and place:
        text += "\n\n" + t(lang, "top_you", place=place, pts=ranked[place - 1]["points"])
    elif joined:
        text += "\n\n" + t(lang, "top_you_zero")
    else:
        text += "\n\n" + t(lang, "top_you_out")
    if joined:
        mynick = db.nick_get(uid)[0]
        text += "\n" + (t(lang, "top_you_nick", nick=esc(mynick)) if mynick else t(lang, "top_need_nick"))
    text += "\n\n" + t(lang, "top_prize", min=practice.BOARD_MIN_POINTS)
    rows = [[(t(lang, "top_leave") if joined else t(lang, "top_join"), "bd:leave" if joined else "bd:join")]]
    if joined:
        rows.append([(t(lang, "top_change"), "bd:nick")])
    rows.append([(t(lang, "top_rules"), "bd:rules")])
    if c:
        return edit_or_send(c, text, ikb(rows))
    bot.send_message(uid, text, reply_markup=ikb(rows))


@bot.callback_query_handler(func=lambda c: c.data.startswith("bd:"))
def cb_board(c):
    uid, lang = c.from_user.id, lang_of(c.from_user.id)
    act = c.data.split(":")[1]
    bot.answer_callback_query(c.id)
    if act == "rules":
        return send_rules(uid)
    if act == "reset" and is_owner(uid):                        # неподходящий ник: сбрасываем и просим выбрать новый
        target = int(c.data.split(":")[2])
        nick = db.nick_get(target)[0]
        db.nick_clear(target)
        db.board_set(target, False)
        edit_or_send(c, f"🚫 Ник «{esc(nick or '—')}» ({_name_of(target)}) сброшен, участник выведен из рейтинга.")
        return safe_send(target, t(lang_of(target), "nk_bad") + "\n\n" + t(lang_of(target), "top_need_nick"))
    if is_owner(uid):
        return
    if act == "join":
        return edit_or_send(c, t(lang, "top_consent"),
                            ikb([[(t(lang, "top_consent_yes"), "bd:yes"), (t(lang, "top_no"), "bd:no")]]))
    if act in ("yes", "nick"):
        nick, since = db.nick_get(uid)
        if act == "yes" and nick:                                # ник уже был, просто возвращаем в рейтинг
            db.board_set(uid, True)
            edit_or_send(c, t(lang, "top_joined", nick=esc(nick), cap=practice.BOARD_DAILY_CAP))
            return send_board(uid)
        if act == "nick" and nick and since:
            nxt = datetime.strptime(since, "%Y-%m-%d") + timedelta(days=practice.NICK_CHANGE_DAYS)
            if nxt.date() > datetime.now(db.TZ).date():
                return bot.send_message(uid, t(lang, "nk_wait", days=practice.NICK_CHANGE_DAYS, date=nxt.strftime("%d.%m.%Y")))
        STATE[uid] = {"step": "nick", "data": {}}
        return edit_or_send(c, t(lang, "nk_ask", min=practice.NICK_MIN, max=practice.NICK_MAX))
    if act == "leave":
        db.board_set(uid, False)
        return edit_or_send(c, t(lang, "top_left"))
    if act == "no":
        return edit_or_send(c, t(lang, "hw_cancelled"))


def board_hook(now):
    """В понедельник после 9:00: итоги прошлой недели участникам и приз победителю (один раз за неделю)."""
    if now.hour < 9:
        return
    cur_mon = now.date() - timedelta(days=now.weekday())
    prev = cur_mon - timedelta(days=7)
    key = f"board:{prev}"
    if db.was_sent(0, key):
        return
    db.mark_sent(0, key)
    start, end, ranked = week_ranking(prev)
    if not ranked:
        return
    s, e = _fmt_d(start), _fmt_d(end)
    for i, r in enumerate(ranked):
        pl = (db.get_user(r["user_id"]) or {}).get("lang") or "ru"
        you = t(pl, "top_you", place=i + 1, pts=r["points"])
        safe_send(r["user_id"], t(pl, "board_result", start=s, end=e, rows=board_lines(ranked, 3, r["user_id"]), you=you))
    win = ranked[0]
    if win["points"] >= practice.BOARD_MIN_POINTS:
        wid = win["user_id"]
        safe_send(wid, t((db.get_user(wid) or {}).get("lang") or "ru", "board_win"))
        u = db.get_user(wid) or {}
        db.feed_add(wid, "win", f"{s}–{e}")
        give_note(wid, "prize_lesson", f"Авторский урок на тему по выбору — победитель недели {s}–{e}, ник «{board_name(wid)}», "
                                       f"{u.get('name') or '?'} "
                                       f"({win['points']} очков, точность {win['acc'] * 100:.0f}%). "
                                       f"Свяжись, чтобы выбрать тему (она не должна нарушать правила игры) и время. "
                                       f"@{u.get('username') or '—'}")
    else:
        notify_owner(f"🏆 Итоги недели {s}–{e}: лучший результат {win['points']} очков, это меньше минимума "
                     f"({practice.BOARD_MIN_POINTS}). Приз на этой неделе не выдан.")


# ─── ПОДАРКИ, КОТОРЫЕ ВЫДАЁШЬ ТЫ (список и отметка «выдано») ──────────────────

def give_note(uid, kind, text):
    """Записывает подарок в список и присылает тебе сообщение с кнопкой «Выдано»."""
    rid = db.reward_add(uid, kind, text)
    notify_owner(f"🎁 <b>Подарок для {_name_of(uid)}</b>\n{esc(text)}",
                 reply_markup=ikb([[("✅ Выдано", f"rw:done:{rid}")]]))
    return rid


def _fmt_full(d):
    return datetime.strptime(d, "%Y-%m-%d").strftime("%d.%m.%Y")


def maybe_discount(sid):
    """После оплаты: если у ученицы есть скидочные месяцы за друзей, предлагаем применить следующий.
    Скидки не суммируются: пока идёт один месяц (30 дней), следующий ждёт в очереди."""
    st = db.discount_state(sid)
    if st["active"]:
        if st["queued"]:
            notify_owner(f"💸 У <b>{_name_of(sid)}</b> уже идёт скидочный месяц до {_fmt_full(st['active']['end'])}. "
                         f"Скидки не суммируются, ещё в очереди: {st['queued']}.")
        return
    if st["queued"]:
        notify_owner(f"💸 У <b>{_name_of(sid)}</b> есть скидочных месяцев за друзей: {st['queued']}. "
                     f"Применить скидку 30% к только что записанной оплате? Она будет действовать 30 дней.",
                     reply_markup=ikb([[("✅ Применить", f"dsc:ok:{sid}"), ("Позже", "cx")]]))


@bot.callback_query_handler(func=lambda c: c.data.startswith("dsc:"))
@owner_only
def cb_discount(c):
    sid = int(c.data.split(":")[2])
    d = db.discount_activate(sid)
    if not d:
        bot.answer_callback_query(c.id, "Сейчас применять нечего: очередь пуста или месяц уже идёт")
        return
    bot.answer_callback_query(c.id, "Применено")
    st = db.discount_state(sid)
    edit_or_send(c, f"✅ Скидка 30% для {_name_of(sid)} применена: с {_fmt_full(d['start'])} по {_fmt_full(d['end'])}. "
                    f"В очереди ещё: {st['queued']}.")
    safe_send(sid, t(lang_of(sid), "disc_applied", end=_fmt_full(d["end"]), n=st["queued"]))


@bot.message_handler(commands=["discounts"])
def cmd_discounts(m):
    if not is_owner(m.from_user.id):
        return
    rows = db.discount_all_queued()
    lines = [f"· {esc(r['name'] or '—')}: в очереди {r['n']}" for r in rows]
    act = []
    for s_ in db.students():
        st = db.discount_state(s_["user_id"])
        if st["active"]:
            act.append(f"· {esc(s_['name'] or '—')}: скидка идёт до {_fmt_full(st['active']['end'])}")
    if not lines and not act:
        return bot.send_message(m.chat.id, "Скидочных месяцев в очереди нет.")
    bot.send_message(m.chat.id, "💸 <b>Скидки за друзей</b>\n\n" + ("Идут сейчас:\n" + "\n".join(act) + "\n\n" if act else "")
                     + ("Ждут своей очереди:\n" + "\n".join(lines) if lines else ""))


@bot.message_handler(commands=["rewards"])
def cmd_rewards(m):
    if not is_owner(m.from_user.id):
        return
    rows = db.rewards_open()
    if not rows:
        return bot.send_message(m.chat.id, "Подарков, которые ждут выдачи, нет 🎉")
    for r in rows:
        bot.send_message(m.chat.id, f"🎁 <b>{esc(r['name'] or '—')}</b> · с {r['created']}\n{esc(r['text'])}",
                         reply_markup=ikb([[("✅ Выдано", f"rw:done:{r['id']}")]]))


@bot.callback_query_handler(func=lambda c: c.data.startswith("rw:done:"))
@owner_only
def cb_reward_done(c):
    rid = int(c.data.split(":")[2])
    r = db.reward_get(rid)
    if not r:
        return bot.answer_callback_query(c.id, "Не нашёл")
    db.reward_done(rid)
    bot.answer_callback_query(c.id, "Отмечено")
    edit_or_send(c, f"✅ Выдано: {_name_of(r['user_id'])} — {esc(r['text'][:120])}")


@bot.message_handler(commands=["who"])
def cmd_who(m):
    """Только владелица: кто стоит за каждым ником в рейтинге (чтобы проверить победителей)."""
    if not is_owner(m.from_user.id):
        return
    rows = db.board_members()
    if not rows:
        return bot.send_message(m.chat.id, "В рейтинге пока никого нет.")
    start, end = practice.week_bounds(datetime.now(db.TZ).date())
    pts = {r["user_id"]: r["points"] for r in db.score_week(start, end)}
    lines = [f"🔒 <b>Кто есть кто</b> (видно только тебе)\nНеделя {_fmt_d(start)}–{_fmt_d(end)}\n"]
    k = types.InlineKeyboardMarkup()
    for r in rows:
        lines.append(f"· «{esc(r['nick'] or practice.anon_nick(r['user_id']))}» — <b>{esc(r['name'] or '—')}</b> "
                     f"@{esc(r['username'] or '—')} · {pts.get(r['user_id'], 0)} очк.")
        if r["nick"]:
            k.row(types.InlineKeyboardButton(f"🚫 Сбросить ник «{r['nick']}»", callback_data=f"bd:reset:{r['user_id']}"))
    bot.send_message(m.chat.id, "\n".join(lines), reply_markup=k)


@bot.message_handler(commands=["rules"])
def cmd_rules(m): send_rules(m.from_user.id)


@bot.message_handler(commands=["top"])
def cmd_top(m): send_board(m.from_user.id)


# ─── ТЕКСТОВЫЕ СООБЩЕНИЯ ──────────────────────────────────────────────────────

@bot.message_handler(content_types=["sticker"])
def on_sticker(m):
    uid = m.from_user.id
    if not is_owner(uid):
        return
    STATE[uid] = {"step": "sticker_pick", "data": {"file_id": m.sticker.file_id}}
    k = types.InlineKeyboardMarkup(row_width=1)
    for name, label in STICKER_ROLES.items():
        k.add(types.InlineKeyboardButton(label, callback_data=f"stk:{name}"))
    bot.send_message(uid, "Для чего этот стикер?", reply_markup=k)


@bot.callback_query_handler(func=lambda c: c.data.startswith("stk:"))
@owner_only
def cb_sticker(c):
    st = STATE.get(c.from_user.id)
    name = c.data.split(":", 1)[1]
    if not st or st["step"] != "sticker_pick" or name not in STICKER_ROLES:
        return bot.answer_callback_query(c.id, "Пришли стикер заново")
    STATE.pop(c.from_user.id, None)
    db.set_sticker(name, st["data"]["file_id"])
    bot.answer_callback_query(c.id, "Сохранила")
    bot.edit_message_text(f"✅ Сохранила: {STICKER_ROLES[name]}", c.message.chat.id, c.message.message_id)


@bot.message_handler(commands=["stickers"])
def cmd_stickers(m):
    if not is_owner(m.from_user.id):
        return
    have = db.sticker_names()
    lines = [f"{'✅' if n in have else '▫️'} {label}" for n, label in STICKER_ROLES.items()]
    bot.send_message(m.chat.id, "<b>Стикеры бота</b>\n\n" + "\n".join(lines) +
                     "\n\nЧтобы задать или заменить, просто пришли мне стикер.")


def menu_labels(lang):
    keys = ("b_word", "b_chengyu", "b_fact", "b_tr", "b_progress", "b_lang", "b_grammar", "b_texts",
            "b_adult", "b_sched", "b_practice", "b_friend", "b_trial", "b_rules", "b_channel", "b_help", "b_donate")
    return {t(lang, k) for k in keys}


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

    st = hw_sub_state(uid) or STATE.get(uid)
    if st and st["step"] == "hw_submit" and txt in menu_labels(lang_of(uid)):      # кнопка меню посреди сдачи
        if st["data"]["n"]:
            finish_submission(uid)
        else:
            STATE.pop(uid, None)
        st = None
    if st and st["step"] in ("translate", "trial_when", "move_when", "rv_text", "rv_public", "nick") \
            and txt in menu_labels(lang_of(uid)):          # нажала кнопку меню посреди диалога: диалог закрываем
        STATE.pop(uid, None)
        st = None
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
            answer, bq = dictionary.translate_ex(txt, lang)
            if not answer:
                db.log_missing(txt)
                kb = bkrs_button(lang, txt) if re.search(r"[\u4e00-\u9fff\u0400-\u04ff]", txt) else None
                bot.send_message(uid, t(lang, "tr_none", q=esc(txt[:60])), reply_markup=kb)
                return send_sticker(uid, "thinking")
            return bot.send_message(uid, answer, reply_markup=bkrs_button(lang, bq))

        if step == "hw_submit":
            return take_submission(uid, m)

        if step == "nick":
            u_ = db.get_user(uid) or {}
            real = [*(u_.get("name") or "").replace(",", " ").split(), u_.get("username") or "",
                    getattr(m.from_user, "first_name", "") or "", getattr(m.from_user, "last_name", "") or "", getattr(m.from_user, "username", "") or ""]
            nick, err = practice.valid_nick(txt, real)
            if err:
                return bot.send_message(uid, t(lang, err, min=practice.NICK_MIN, max=practice.NICK_MAX))
            if db.nick_taken(nick, uid):
                return bot.send_message(uid, t(lang, "nk_taken"))
            if not db.nick_set(uid, nick):
                return bot.send_message(uid, t(lang, "nk_taken"))
            STATE.pop(uid, None)
            bot.send_message(uid, t(lang, "nk_ok", nick=esc(nick)))
            bot.send_message(uid, t(lang, "top_joined", nick=esc(nick), cap=practice.BOARD_DAILY_CAP))
            return send_board(uid)

        if step == "trial_when":
            STATE.pop(uid, None)
            return finish_trial(uid, txt)

        if step == "move_when":
            return finish_move(uid, txt)

        if step == "rv_text":
            d["text"] = "" if txt == "-" else txt[:500]
            st["step"] = "rv_public"
            return bot.send_message(uid, t(lang, "rv_public"),
                                    reply_markup=ikb([[(t(lang, "rv_yes"), "rv:p:1"), (t(lang, "rv_no"), "rv:p:0")]]))

        if step == "rv_public":
            return bot.send_message(uid, t(lang, "rv_public"),
                                    reply_markup=ikb([[(t(lang, "rv_yes"), "rv:p:1"), (t(lang, "rv_no"), "rv:p:0")]]))

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
                lesson_balance_alert(sid)
                return maybe_ask_review(sid)

            if step == "pay_count":
                if not txt.lstrip("+-").isdigit():
                    return bot.send_message(uid, "Нужно число. Попробуй ещё раз.")
                STATE.pop(uid, None)
                db.add_payment(sid, int(txt))
                bot.send_message(uid, f"💰 Оплата записана.\n\n{student_card(sid)}")
                referral_paid(sid)
                maybe_discount(sid)
                try:
                    bot.send_message(sid, "💰 Оплата получена, спасибо!\n\n" + progress_text(sid, lang_of(sid)))
                    send_sticker(sid, "thanks")
                except Exception:
                    pass
                return

            if step == "hw_text":
                d["text"] = txt[:500]
                st["step"] = "hw_due"
                return bot.send_message(uid, "К какому сроку? Напиши «сегодня», «завтра», «послезавтра», дату вроде "
                                             "<code>15.10</code> или «-», если без срока.")

            if step == "hw_due":
                due = practice.parse_due(txt, db.today())
                if due is None:
                    return bot.send_message(uid, "Не поняла срок. Примеры: завтра, 15.10, «-».")
                STATE.pop(uid, None)
                ok, fail = deliver_hw(d.get("uids") or [sid], d["text"], due)
                msg_ = f"📚 Домашка отправлена: {len(ok)} чел."
                if fail:
                    msg_ += "\n⚠️ Не дошла (человек мог закрыть бота): " + ", ".join(_name_of(u) for u in fail)
                if len(ok) + len(fail) == 1 and sid:
                    msg_ += f"\n\n{student_card(sid)}"
                return bot.send_message(uid, msg_)

            if step == "grp_name":
                STATE.pop(uid, None)
                gid = db.group_add(txt[:60])
                return start_picker(uid, "members", f"✏️ <b>Кого добавить в «{esc(txt[:60])}»?</b>", gid=gid)

            if step == "kpi_note":
                STATE.pop(uid, None)
                db.kpi_add(sid, txt[:800])
                return bot.send_message(uid, f"📈 KPI-точка записана.\n\n{student_card(sid)}")

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
                prev = db.tests(sid)
                prev_pct = prev[-1]["score"] / prev[-1]["max_score"] * 100 if prev else None
                db.add_test(sid, parts[0][:80], sc, mx)
                grew = prev_pct is not None and sc / mx * 100 > prev_pct
                bot.send_message(uid, f"📝 Результат записан.\n\n{student_card(sid)}")
                try:
                    bot.send_message(sid, "📝 Появился новый результат теста!\n\n" + progress_text(sid, lang_of(sid)))
                    if grew:
                        send_sticker(sid, "celebrate")
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
               t(lang, "b_progress"): send_progress, t(lang, "b_lang"): ask_language,
               t(lang, "b_grammar"): send_grammar, t(lang, "b_texts"): send_texts, t(lang, "b_adult"): send_adult,
               t(lang, "b_sched"): send_schedule, t(lang, "b_practice"): send_practice,
               t(lang, "b_friend"): send_friend, t(lang, "b_trial"): ask_trial, t(lang, "b_rules"): send_rules}
    if txt in actions:
        return actions[txt](uid)
    if txt == t(lang, "b_channel"):
        return bot.send_message(uid, t(lang, "channel"))
    if txt == t(lang, "b_help"):
        return bot.send_message(uid, t(lang, "help"))
    if txt == t(lang, "b_donate"):
        return send_donate(uid)

    # ── незнакомый человек → знакомство; знакомый → вопрос уходит преподавателю ──
    u = db.get_user(uid)
    if db.children_of(uid) and not (u and u.get("level")):          # подключённый родитель: вопрос уходит преподавателю
        kids = ", ".join(_name_of(ch) for ch in db.children_of(uid))
        sent = notify_owner(f"👨‍👩‍👧 Родитель ({kids}) — {esc((u or {}).get('name') or '?')} (@{esc((u or {}).get('username') or '—')}):\n{esc(txt)}\n\n"
                            f"<i>Ответь на это сообщение, и я перешлю ответ.</i>")
        if sent:
            db.save_inbox(sent.message_id, uid)
        return bot.send_message(uid, t(lang, "pa_q_sent"))
    if not u or not u.get("level"):
        return cmd_start(m)
    if is_owner(uid):
        return bot.send_message(uid, t(lang, "menu"), reply_markup=kb_main(uid))
    sent = notify_owner(f"💬 <b>{esc(u['name'] or '?')}</b> (@{esc(u['username'] or '—')}):\n{esc(txt)}\n\n"
                        f"<i>Ответь на это сообщение, и я перешлю ответ.</i>")
    if sent:
        db.save_inbox(sent.message_id, uid)
    bot.send_message(uid, t(lang, "q_sent"), reply_markup=kb_main(uid))



# ─── ВЕРСИЯ 11: ИГРА, TELEGRAM STARS, ПОДДЕРЖКА ПРОЕКТА ───────────────────────

def make_invoice_link(title, desc, payload, stars):
    """Ссылка на оплату звёздами (XTR). Токен платёжной системы для звёзд не нужен."""
    return bot.create_invoice_link(title=title, description=desc, payload=payload, provider_token="", currency="XTR",
                                   prices=[types.LabeledPrice(label=title, amount=int(stars))])


def send_donate(uid):
    lang = lang_of(uid)
    text = t(lang, "dn_text")
    if DONATE_INFO:
        text += t(lang, "dn_info", info=esc(DONATE_INFO))
    rows = []
    if DONATE_URL.startswith("http"):
        rows.append([types.InlineKeyboardButton(t(lang, "dn_url_btn"), url=DONATE_URL)])
    k = types.InlineKeyboardMarkup()
    for r in rows:
        k.row(*r)
    if STARS_ON:
        text += "\n\n" + t(lang, "dn_stars")
        k.row(*[types.InlineKeyboardButton(f"⭐ {n}", callback_data=f"dn:{n}") for n in quest.DONATE_STARS])
    bot.send_message(uid, text, reply_markup=k)


@bot.message_handler(commands=["donate", "support"])
def cmd_donate(m): send_donate(m.from_user.id)


@bot.message_handler(commands=["terms"])
def cmd_terms(m):
    """Условия покупок за Telegram Stars (этого требует Telegram перед приёмом платежей)."""
    lang = lang_of(m.from_user.id)
    tx = {
        "ru": "📄 <b>Условия покупок за ⭐</b>\n\nЗа звёзды можно купить внутри игры: ещё одну сцену, жизни, наряды героя, а также поддержать проект. Всё это цифровые товары, они выдаются сразу после оплаты.\n\nЕсли оплата прошла, а покупка не появилась, напиши прямо в этот чат: мы всё проверим и вернём звёзды. Поддержка Telegram по покупкам в боте не помогает. Играть можно и без покупок: одна сцена в день бесплатно.",
        "uz": "📄 <b>⭐ bilan xaridlar shartlari</b>\n\nYulduzlar bilan o'yin ichida yana bir sahna, jonlar, qahramon kiyimlari sotib olish va loyihani qo'llab-quvvatlash mumkin. Bular raqamli mahsulotlar, to'lovdan so'ng darhol beriladi.\n\nTo'lov o'tib, xarid chiqmasa, shu chatga yozing: tekshirib, yulduzlarni qaytaramiz. Telegram yordam xizmati bot xaridlariga yordam bermaydi. O'yinni xaridsiz ham o'ynash mumkin: kuniga bitta sahna bepul.",
        "en": "📄 <b>Terms for purchases with ⭐</b>\n\nWith Stars you can buy inside the game: an extra scene, lives, hero outfits, and support the project. These are digital goods delivered right after payment.\n\nIf you paid but did not get your purchase, write in this chat: we will check and refund the Stars. Telegram support cannot help with purchases made in this bot. You can play without buying anything: one scene a day is free.",
        "zh": "📄 <b>⭐ 购买条款</b>\n\n可用星星在游戏内购买：额外一幕、生命、角色装扮，也可以支持项目。这些都是数字商品，付款后立即发放。\n\n如果已付款但没有收到商品，请直接在此聊天中留言，我们会核实并退还星星。Telegram 客服无法处理本机器人内的购买。不购买也可以玩：每天一幕免费。",
    }
    bot.send_message(m.chat.id, tx.get(lang, tx["ru"]))


@bot.message_handler(commands=["paysupport"])
def cmd_paysupport(m):
    """Помощь с платежом: человек пишет в чат, сообщение уходит владелице."""
    lang = lang_of(m.from_user.id)
    tx = {
        "ru": "💬 Проблема с оплатой? Напиши сюда номер операции (он есть в сообщении об оплате) и что именно не получилось. Сообщение придёт Лазизе, она ответит и при необходимости вернёт звёзды.",
        "uz": "💬 To'lovda muammo bormi? Shu yerga operatsiya raqamini (to'lov xabarida bor) va nima chiqmaganini yozing. Xabar Lazizaga boradi, u javob beradi va kerak bo'lsa yulduzlarni qaytaradi.",
        "en": "💬 Problem with a payment? Write here the operation number (it is in the payment message) and what went wrong. The message goes to Laziza, who will reply and refund the Stars if needed.",
        "zh": "💬 付款有问题？请在这里写下交易编号（在付款消息中）和遇到的问题。消息会转给 Laziza，她会回复并在需要时退还星星。",
    }
    bot.send_message(m.chat.id, tx.get(lang, tx["ru"]))


@bot.callback_query_handler(func=lambda c: c.data.startswith("dn:"))
def cb_donate(c):
    uid = c.from_user.id
    bot.answer_callback_query(c.id)
    try:
        n = int(c.data.split(":")[1])
    except ValueError:
        return
    if n not in quest.DONATE_STARS or not STARS_ON:
        return
    lang = lang_of(uid)
    try:
        bot.send_invoice(uid, title=t(lang, "dn_title"), description=t(lang, "dn_desc"), invoice_payload=f"dn:{n}",
                         provider_token="", currency="XTR", prices=[types.LabeledPrice(label=t(lang, "dn_title"), amount=n)])
    except Exception as e:
        logging.warning("счёт на поддержку не отправился: %s", e)


@bot.pre_checkout_query_handler(func=lambda q: True)
def on_pre_checkout(q):
    """Telegram ждёт ответ до 10 секунд. Проверяем, что товар существует, сумма верная и платит тот, кому выписан счёт."""
    ok = False
    try:
        pl = q.invoice_payload or ""
        if q.currency == "XTR" and STARS_ON:
            if pl.startswith("dn:"):
                ok = pl[3:].isdigit() and int(pl[3:]) in quest.DONATE_STARS and q.total_amount == int(pl[3:])
            else:
                parsed = quest.parse_payload(pl)
                if parsed:
                    item, owner_uid, _ = parsed
                    p = quest.parse_item(item)
                    ok = bool(p) and owner_uid == q.from_user.id and q.total_amount == p[3] and bool(quest.char_get(owner_uid))
    except Exception:
        logging.exception("pre_checkout")
    try:
        bot.answer_pre_checkout_query(q.id, ok=ok, error_message=None if ok else t(lang_of(q.from_user.id), "pre_err"))
    except Exception as e:
        logging.warning("pre_checkout ответ не ушёл: %s", e)


def _who(uid):
    u = db.get_user(uid) or {}
    return f"<b>{esc(u.get('name') or '?')}</b> (@{esc(u.get('username') or '—')})"


@bot.message_handler(content_types=["successful_payment"])
def on_successful_payment(m):
    sp = m.successful_payment
    uid = m.from_user.id
    lang = lang_of(uid)
    if sp.currency != "XTR":
        return
    stars, charge, pl = int(sp.total_amount), sp.telegram_payment_charge_id, sp.invoice_payload or ""
    try:
        if pl.startswith("dn:"):
            if quest.log_donation(uid, stars, charge):
                bot.send_message(uid, t(lang, "dn_thanks"))
                notify_owner(f"💝 Поддержка проекта: <b>{stars} ⭐</b> от {_who(uid)}")
            return
        parsed = quest.parse_payload(pl)
        res = quest.grant_stars(uid, parsed[0], stars, charge, parsed[2]) if parsed else None
        if res is None:
            notify_owner(f"⚠️ Пришла оплата {stars} ⭐ от {_who(uid)}, но выдать покупку не вышло (payload: {esc(pl)}).\n"
                         f"Номер операции для возврата: <code>{esc(charge)}</code>. Команда: /refund {esc(charge)}")
            return
        if res == "dup":
            return
        bot.send_message(uid, t(lang, "qs_coins" if res == "coins" else "qs_thanks"))
        label = quest.item_text("ru", parsed[0])[0]
        notify_owner(f"⭐ Оплата в игре: <b>{stars} ⭐</b>, «{esc(label)}», {_who(uid)}")
    except Exception:
        logging.exception("successful_payment")
        notify_owner(f"⚠️ Ошибка при обработке оплаты {stars} ⭐ от {_who(uid)}. Номер операции: <code>{esc(charge)}</code>")


@bot.message_handler(commands=["stars"])
def cmd_stars(m):
    if not is_owner(m.from_user.id):
        return
    r = quest.stars_report(30)
    tot, mon = r["total"], r["month"]
    names = {"life": "жизнь", "refill": "все жизни", "extra": "ещё одна сцена", "donate": "поддержка проекта"}
    def label(i):
        return names.get(i) or ("наряд" if i.startswith("skin") else "пакет монет" if i.startswith("pack") else i)
    usd = lambda n: f"≈ ${n * 0.013:.2f}"
    lines = [f"⭐ <b>Звёзды</b>\nЗа 30 дней: <b>{mon[0]} ⭐</b> ({usd(mon[0])}), оплат: {mon[1]}, плательщиков: {mon[2]}",
             f"За всё время: <b>{tot[0]} ⭐</b> ({usd(tot[0])}), оплат: {tot[1]}, плательщиков: {tot[2]}"]
    if r["by_item"]:
        lines.append("\nЗа 30 дней по товарам:")
        for item, n, st in r["by_item"]:
            lines.append(f"· {label(item)}: {n} шт., {st} ⭐")
    lines.append("\nВывод возможен от 1000 ⭐ (около $13 по курсу выплаты). Звёзды приходят с задержкой до 21 дня.")
    bot.send_message(m.chat.id, "\n".join(lines))


@bot.message_handler(commands=["refund"])
def cmd_refund(m):
    """/refund <номер операции>: вернуть звёзды человеку (если оплата прошла, а покупка не выдалась)."""
    if not is_owner(m.from_user.id):
        return
    parts = (m.text or "").split()
    if len(parts) < 2:
        return bot.send_message(m.chat.id, "Напиши так: /refund НОМЕР_ОПЕРАЦИИ (он есть в уведомлении об оплате).")
    row = quest.pay_lookup(parts[1])
    uid = row["user_id"] if row else (int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None)
    if not uid:
        return bot.send_message(m.chat.id, "Не нашёл такую операцию. Если оплата не записалась, добавь номер человека: /refund НОМЕР ID_ЧЕЛОВЕКА.")
    try:
        bot.refund_star_payment(uid, parts[1])
        bot.send_message(m.chat.id, "↩️ Звёзды возвращены.")
    except Exception as e:
        bot.send_message(m.chat.id, f"Не получилось вернуть: {esc(e)}")


@bot.message_handler(commands=["prize"])
def cmd_prize(m):
    """/prize: сколько участников розыгрыша скина и кто уже выиграл."""
    if not is_owner(m.from_user.id):
        return
    r = quest.prize_report()
    lines = [f"🎁 <b>Розыгрыш уникального скина</b>\nУчастников в барабане: <b>{r['waiting']}</b> (всего прошли первую сцену: {r['total']})"]
    if r["winners"]:
        lines.append("\nПобедители:")
        for w in r["winners"]:
            lines.append(f"· {esc(w['hero'] or '?')} — {_who(w['user_id'])}, {w['ts']}")
    lines.append("\nПровести розыгрыш: /prize_draw")
    bot.send_message(m.chat.id, "\n".join(lines))


@bot.message_handler(commands=["prize_draw"])
def cmd_prize_draw(m):
    """/prize_draw: случайно выбирает победителя среди участников, которые ещё не выигрывали, и пишет ему."""
    if not is_owner(m.from_user.id):
        return
    w = quest.prize_draw()
    if not w:
        return bot.send_message(m.chat.id, "В барабане пока никого: нужно, чтобы кто-то прошёл первую сцену.")
    uid, hero = w
    try:
        bot.send_message(uid, t(lang_of(uid), "pz_win"))
        sent = "Сообщение победителю отправлено."
    except Exception as e:
        sent = f"Написать победителю не вышло ({esc(e)}). Свяжись с ним сама."
    bot.send_message(m.chat.id, f"🎉 Победитель: <b>{esc(hero)}</b> — {_who(uid)}\n{sent}\nЕго ответ придёт сюда как обычное сообщение: ответь на него, и я перешлю.")


@bot.message_handler(commands=["qtop"])
def cmd_qtop(m):
    """/qtop: рейтинг игры «Путешествие с Чачей» за неделю (для всех)."""
    uid = m.from_user.id
    r = quest.board(uid, "week", exclude=(OWNER_ID,))
    lang = lang_of(uid)
    if not r["rows"]:
        return bot.send_message(uid, t(lang, "qt_empty"))
    medals = ["🥇", "🥈", "🥉"]
    lines = [t(lang, "qt_title")]
    for x in r["rows"][:10]:
        lines.append(f"{medals[x['place'] - 1] if x['place'] <= 3 else str(x['place']) + '.'} <b>{esc(x['hero'])}</b> · {x['pts']} 🪙")
    if r["me"] and r["me"].get("place") and r["me"]["place"] > 10:
        lines.append(f"…\n{r['me']['place']}. {t(lang, 'qt_you')} · {r['me']['pts']} 🪙")
    bot.send_message(uid, "\n".join(lines))


# ─── ПРОФИЛЬ БОТА В TELEGRAM ──────────────────────────────────────────────────

def apply_profile():
    """Имя, «о боте» и описание на четырёх языках. Применяется только если тексты изменились:
    Telegram ограничивает частоту смены имени, поэтому на каждом запуске не дёргаем."""
    stamp = "profile:" + hashlib.md5(json.dumps(PROFILE, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if db.was_sent(0, stamp):
        return True
    failed = False
    targets = [(None, PROFILE["en"])] + [(code, p) for code, p in PROFILE.items()]   # None = язык по умолчанию
    for code, p in targets:
        for call, value in ((bot.set_my_name, p["name"]),
                            (bot.set_my_description, p["description"]),
                            (bot.set_my_short_description, p["short"])):
            try:
                call(value, language_code=code)
            except Exception as e:
                failed = True
                logging.warning("профиль бота (%s, %s): %s", code or "по умолчанию", call.__name__, e)
    if not failed:
        db.mark_sent(0, stamp)
    return not failed


# ─── MINI APP ─────────────────────────────────────────────────────────────────

def start_webapp():
    """Поднимает сайт Mini App в этом же процессе (адрес из WEBAPP_URL, порт из PORT, который задаёт хостинг)."""
    port = os.environ.get("PORT", "").strip()
    if not (port or WEBAPP_URL):
        return
    try:
        import webapp
        deps = {"token": TOKEN, "owner_id": OWNER_ID, "bot_username": bot_username, "notify_owner": notify_owner,
                "ikb": ikb, "pay": {"info": PAY_INFO, "price": PAY_PRICE, "url": PAY_URL, "days": PRO_DAYS},
                "webapp_url": WEBAPP_URL,
                "create_invoice": make_invoice_link if STARS_ON else None,
                "donate": {"on": True, "card": bool(DONATE_INFO or DONATE_URL)}}
        threading.Thread(target=webapp.serve, args=(deps, int(port or 8080)), daemon=True).start()
        if WEBAPP_URL.startswith("https://"):
            bot.set_chat_menu_button(menu_button=types.MenuButtonWebApp(text="Game", web_app=types.WebAppInfo(url=WEBAPP_URL)))
        logging.info("Mini App: порт %s, адрес %s", port or 8080, WEBAPP_URL or "не задан")
    except Exception:
        logging.exception("Mini App не запустился (бот работает без него)")


# ─── ЗАПУСК ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    dictionary.ensure()
    apply_profile()
    try:
        bot.set_my_commands([
            types.BotCommand("menu", "меню"), types.BotCommand("word", "слово дня"),
            types.BotCommand("chengyu", "чэнъюй"), types.BotCommand("fact", "факт о Китае"),
            types.BotCommand("progress", "мой прогресс"), types.BotCommand("lessons", "мои занятия"),
            types.BotCommand("grammar", "грамматика"), types.BotCommand("texts", "тексты"),
            types.BotCommand("practice", "практика: викторина, карточки, игра"), types.BotCommand("top", "рейтинг недели"),
            types.BotCommand("rules", "правила игры"), types.BotCommand("quiz", "викторина"),
            types.BotCommand("cards", "карточки"), types.BotCommand("tea", "Чайная лавка"),
            types.BotCommand("friend", "пригласить друга"), types.BotCommand("trial", "пробный урок"),
            types.BotCommand("parents", "родители: недельная сводка"),
            types.BotCommand("hw", "домашние задания"),
            types.BotCommand("lang", "язык"), types.BotCommand("about", "что я умею"),
            types.BotCommand("privacy", "конфиденциальность"), types.BotCommand("donate", "поддержать проект"),
            types.BotCommand("terms", "условия покупок за ⭐"), types.BotCommand("paysupport", "помощь с оплатой"),
            types.BotCommand("mydata", "копия моих данных")])
        if OWNER_ID:
            bot.set_my_commands([
                types.BotCommand("admin", "панель преподавателя"), types.BotCommand("schedule", "мои уроки"),
                types.BotCommand("menu", "меню"), types.BotCommand("backup", "копия базы"),
                types.BotCommand("csv", "уроки и оплаты за месяц"), types.BotCommand("hw", "открытые домашки"),
                types.BotCommand("practice", "практика"), types.BotCommand("groups", "группы учеников"),
                types.BotCommand("rewards", "подарки, которые ждут выдачи"),
                types.BotCommand("who", "кто за какими никами в рейтинге"), types.BotCommand("discounts", "скидки за друзей"),
                types.BotCommand("parents", "родители, подключённые к сводке"), types.BotCommand("parentsum", "предпросмотр сводки родителю"),
                types.BotCommand("missing", "что не нашли в переводчике"),
                types.BotCommand("stars", "звёзды: сколько заработано")],
                scope=types.BotCommandScopeChat(OWNER_ID))
    except Exception as e:
        logging.warning("не удалось задать команды: %s", e)
    threading.Thread(target=scheduler.loop, args=(send_reminder, send_weekly, send_digest, (hw_hook, kpi_hook, board_hook, parent_hook)), daemon=True).start()
    start_webapp()
    print("🐉 汉助 HanZhu запущен. Останови сочетанием Ctrl+C.")
    bot.infinity_polling(skip_pending=True, timeout=30)
