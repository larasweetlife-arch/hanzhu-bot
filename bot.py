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
import io
import json
import hashlib
import random
import re
from urllib.parse import quote
import logging
import threading
from datetime import datetime, timedelta

import telebot
from telebot import types

import db
import scheduler
import dictionary
import content as C
from texts import t, T, LANG_PROMPT, WEEKDAYS, PROFILE

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
    "hello":     "👋 Приветствие (после знакомства)",
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
    k.row(t(lang, "b_help"))
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
    db.save_user(uid, name=d.get("name", ""), username=c.from_user.username or "",
                 lang=lang, level=level, source=d.get("source", ""))
    bot.edit_message_text(t(lang, "done", name=esc(d.get("name", ""))), uid, c.message.message_id)
    bot.send_message(uid, t(lang, "features"), reply_markup=kb_main(uid))
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


def send_weekly(now):
    since = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    lessons = db.lessons_count_since(since)
    new = db.users_since(since)
    absent = db.absences_since(since)
    top = db.top_events_since(since)
    labels = {"word": "Слово дня", "chengyu": "Чэнъюй", "fact": "Факт", "progress": "Прогресс",
              "translate": "Перевод", "grammar": "Грамматика", "texts": "Тексты", "adult": "Раздел 16+"}
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
          types.InlineKeyboardButton("➕ Сделать учеником", callback_data="a:make"),
          types.InlineKeyboardButton("📊 Статистика бота", callback_data="a:stats"))
    bot.send_message(m.chat.id, f"<b>Панель преподавателя</b>\n\nВсего в боте: {len(db.all_users())}\n"
                                f"Учеников: {len(db.students())}", reply_markup=k)


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
    k.add(types.InlineKeyboardButton("💬 Напомнить об оплате", callback_data=f"nd:{uid}"),
          types.InlineKeyboardButton("🔞 Закрыть / открыть 16+", callback_data=f"adx:{uid}"))
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
            answer, bq = dictionary.translate_ex(txt, lang)
            if not answer:
                db.log_missing(txt)
                kb = bkrs_button(lang, txt) if re.search(r"[\u4e00-\u9fff\u0400-\u04ff]", txt) else None
                bot.send_message(uid, t(lang, "tr_none", q=esc(txt[:60])), reply_markup=kb)
                return send_sticker(uid, "thinking")
            return bot.send_message(uid, answer, reply_markup=bkrs_button(lang, bq))

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
                    send_sticker(sid, "thanks")
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
               t(lang, "b_grammar"): send_grammar, t(lang, "b_texts"): send_texts, t(lang, "b_adult"): send_adult}
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


# ─── ЗАПУСК ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    dictionary.ensure()
    apply_profile()
    try:
        bot.set_my_commands([
            types.BotCommand("menu", "меню"), types.BotCommand("word", "слово дня"),
            types.BotCommand("chengyu", "чэнъюй"), types.BotCommand("fact", "факт о Китае"),
            types.BotCommand("progress", "мой прогресс"),
            types.BotCommand("grammar", "грамматика"), types.BotCommand("texts", "тексты"), types.BotCommand("lang", "язык"), types.BotCommand("about", "что я умею"),
            types.BotCommand("privacy", "конфиденциальность"),
            types.BotCommand("mydata", "копия моих данных")])
    except Exception as e:
        logging.warning("не удалось задать команды: %s", e)
    threading.Thread(target=scheduler.loop, args=(send_reminder, send_weekly), daemon=True).start()
    print("🐉 汉助 HanZhu запущен. Останови сочетанием Ctrl+C.")
    bot.infinity_polling(skip_pending=True, timeout=30)
