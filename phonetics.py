"""
Фонетика (версия 27): теория в меню бота, практика в Mini App.

  · Тексты лежат в content_phonetics.txt (разделы intro, tones, initials, finals, sandhi; языки ru, uz, en, zh). Лазиза правит его сама.
  · В чате у каждого раздела кнопки «🔊»: бот присылает аудио, его читает та же озвучка, что и в мини-аппе (tts.py).
    Отдельных слогов озвучка не читает, поэтому для каждого звука взят настоящий иероглиф с этим слогом.
  · Практика (слух и голос) открывается кнопкой «🎯» в Mini App: адрес /?phon=1.
  · Колбэки: ph:m (меню), ph:s:<раздел>, ph:a:<раздел>:<номер>.
"""
import logging
import re
import threading
from pathlib import Path
from urllib.parse import quote  # noqa: F401  (на случай ссылок с параметрами)

from telebot import types

import tts

BASE = Path(__file__).parent
LANGS = ("ru", "uz", "en", "zh")
SECTIONS = ("tones", "initials", "finals", "sandhi")

BTN = {
    "ru": {"tones": "🎵 Тоны", "initials": "🔤 Инициали", "finals": "🔠 Финали", "sandhi": "🔄 Изменения тонов", "back": "← Назад", "go": "🎯 Потренироваться",
           "nosound": "Озвучка сейчас недоступна, попробуй чуть позже.", "wait": "Слишком часто. Подожди минуту."},
    "uz": {"tones": "🎵 Ohanglar", "initials": "🔤 Undoshlar", "finals": "🔠 Unlilar", "sandhi": "🔄 Ohang o‘zgarishi", "back": "← Orqaga", "go": "🎯 Mashq qilish",
           "nosound": "Ovoz hozir mavjud emas, birozdan keyin urinib ko‘ring.", "wait": "Juda tez-tez. Bir daqiqa kuting."},
    "en": {"tones": "🎵 Tones", "initials": "🔤 Initials", "finals": "🔠 Finals", "sandhi": "🔄 Tone changes", "back": "← Back", "go": "🎯 Practise",
           "nosound": "Audio is unavailable right now, please try again soon.", "wait": "Too fast. Wait a minute."},
    "zh": {"tones": "🎵 声调", "initials": "🔤 声母", "finals": "🔠 韵母", "sandhi": "🔄 变调", "back": "← 返回", "go": "🎯 去练习",
           "nosound": "暂时无法播放声音，请稍后再试。", "wait": "太频繁了，请等一分钟。"},
}

# Кнопки озвучки: (подпись, что читаем). Читаем китайские слова: по запятым озвучка делает паузы.
AUDIO = {
    "tones": [("mā má mǎ mà", "妈，麻，马，骂"), ("māma · bàba · xièxie", "妈妈，爸爸，谢谢")],
    "initials": [("b p m f", "爸，怕，妈，发"), ("d t n l", "大，他，那，拉"), ("g k h", "哥，可，喝"),
                 ("j q x", "家，七，西"), ("zh ch sh r", "知，吃，是，日"), ("z c s", "子，次，四")],
    "finals": [("a o e i u ü", "啊，哦，鹅，衣，五，鱼"), ("ai ei ao ou", "爱，黑，好，都"), ("an en ang eng ong", "看，很，方，冷，红"),
               ("ia ie iao iu", "家，谢，小，六"), ("ian in iang ing iong", "天，您，想，听，用"), ("ua uo uai ui uan un uang", "花，多，快，对，玩，春，黄"),
               ("üe üan ün", "月，远，群")],
    "sandhi": [("你好", "你好"), ("很好", "很好"), ("不是", "不是"), ("不好", "不好"), ("一个", "一个"), ("一天", "一天"), ("一起", "一起")],
}

_TEXTS = None
_RATE = {}


def texts():
    """{(раздел, язык): текст} из content_phonetics.txt. Ошибки в файле не роняют бота."""
    global _TEXTS
    if _TEXTS is None:
        _TEXTS = {}
        path = BASE / "content_phonetics.txt"
        try:
            cur, buf = None, []
            for raw in path.read_text(encoding="utf-8").splitlines():
                m = re.match(r"^##\s+(\w+)\s+(\w+)\s*$", raw)
                if m:
                    if cur:
                        _TEXTS[cur] = "\n".join(buf).strip()
                    cur, buf = (m.group(1), m.group(2)), []
                elif cur is not None and not raw.startswith("# "):
                    buf.append(raw)
            if cur:
                _TEXTS[cur] = "\n".join(buf).strip()
        except Exception:
            logging.exception("content_phonetics.txt не прочитался")
    return _TEXTS


def text_of(section, lang):
    tx = texts()
    return tx.get((section, lang)) or tx.get((section, "ru")) or ""


def _b(lang, key):
    return BTN.get(lang, BTN["ru"])[key]


def keyboard(lang, section, webapp_url):
    k = types.InlineKeyboardMarkup()
    if section == "menu":
        k.row(types.InlineKeyboardButton(_b(lang, "tones"), callback_data="ph:s:tones"), types.InlineKeyboardButton(_b(lang, "initials"), callback_data="ph:s:initials"))
        k.row(types.InlineKeyboardButton(_b(lang, "finals"), callback_data="ph:s:finals"), types.InlineKeyboardButton(_b(lang, "sandhi"), callback_data="ph:s:sandhi"))
    else:
        row = []
        for i, (label, _zh) in enumerate(AUDIO[section]):
            row.append(types.InlineKeyboardButton("🔊 " + label, callback_data=f"ph:a:{section}:{i}"))
            if len(row) == (3 if section == "sandhi" else 2):
                k.row(*row); row = []
        if row:
            k.row(*row)
        k.row(types.InlineKeyboardButton(_b(lang, "back"), callback_data="ph:m"))
    if webapp_url.startswith("https://"):
        k.row(types.InlineKeyboardButton(_b(lang, "go"), web_app=types.WebAppInfo(url=webapp_url + "/?phon=1")))
    return k


def register(bot, lang_of, webapp_url):
    """webapp_url: функция без аргументов, возвращает адрес Mini App (или пустую строку)."""

    def safe_edit(c, text, kb):
        try:
            bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)
        except Exception as e:
            if "not modified" in str(e):
                return
            logging.warning("фонетика: HTML не принялся (%s), показываю без оформления", str(e)[:80])
            try:
                bot.edit_message_text(re.sub(r"<[^>]+>", "", text), c.message.chat.id, c.message.message_id, reply_markup=kb)
            except Exception:
                logging.exception("фонетика: не удалось обновить сообщение")

    def send_menu(uid):
        lang = lang_of(uid)
        text, kb = text_of("intro", lang), keyboard(lang, "menu", webapp_url())
        try:
            bot.send_message(uid, text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            logging.warning("фонетика: HTML не принялся в меню")
            bot.send_message(uid, re.sub(r"<[^>]+>", "", text), reply_markup=kb)

    def audio(uid, lang, section, i):
        try:
            label, zh = AUDIO[section][i]
        except (KeyError, IndexError):
            return
        if not tts.allow_user(uid, 30, 60):
            bot.send_message(uid, _b(lang, "wait")); return
        path = tts.generate(zh)
        if not path:
            bot.send_message(uid, _b(lang, "nosound")); return
        try:
            with open(path, "rb") as f:
                bot.send_audio(uid, f, title=label, performer="汉助")
        except Exception:
            logging.exception("фонетика: аудио не отправилось")
            bot.send_message(uid, _b(lang, "nosound"))

    @bot.callback_query_handler(func=lambda c: c.data.startswith("ph:"))
    def cb(c):
        uid = c.from_user.id
        lang = lang_of(uid)
        parts = c.data.split(":")
        try:
            if parts[1] == "m":
                bot.answer_callback_query(c.id)
                safe_edit(c, text_of("intro", lang), keyboard(lang, "menu", webapp_url()))
            elif parts[1] == "s" and parts[2] in SECTIONS:
                bot.answer_callback_query(c.id)
                safe_edit(c, text_of(parts[2], lang), keyboard(lang, parts[2], webapp_url()))
            elif parts[1] == "a" and parts[2] in SECTIONS:
                bot.answer_callback_query(c.id)
                threading.Thread(target=audio, args=(uid, lang, parts[2], int(parts[3])), daemon=True).start()
            else:
                bot.answer_callback_query(c.id)
        except Exception:
            logging.exception("фонетика: ошибка кнопки")
            try:
                bot.answer_callback_query(c.id)
            except Exception:
                pass

    return send_menu
