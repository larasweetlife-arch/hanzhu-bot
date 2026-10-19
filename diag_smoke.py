"""Сквозная диагностика бота без сети: эмулируем Telegram, жмём все кнопки меню и все inline-кнопки,
которые бот сам нам показывает (обход вглубь), и ловим то, из-за чего в жизни «ничего не происходит»:
текст длиннее 4096, битый HTML, callback_data длиннее 64 байт, исключения в обработчиках, молчаливые кнопки, медленные ответы."""
import sys, os, json, time, re, collections, traceback
sys.path.insert(0, "hanzhu4")
os.chdir("hanzhu4")
sys.path.insert(0, ".")
from telebot import apihelper
import bot, db, quest

CALLS = []          # (method, params)
PROBLEMS = []       # (kind, where, detail)
CUR = {"where": ""}
OK_TAGS = {"b", "strong", "i", "em", "u", "ins", "s", "strike", "del", "a", "code", "pre", "tg-spoiler", "span", "blockquote", "tg-emoji"}


def check_html(txt):
    stack = []
    for m in re.finditer(r"<(/?)([a-zA-Z\-]+)([^>]*)>", txt):
        close, name = m.group(1), m.group(2).lower()
        if name not in OK_TAGS:
            return f"неподдерживаемый тег <{name}>"
        if not close:
            stack.append(name)
        else:
            if not stack or stack[-1] != name:
                return f"лишний/неверный закрывающий </{name}>"
            stack.pop()
    if stack:
        return f"не закрыт тег <{stack[-1]}>"
    # голые < и & вне тегов
    plain = re.sub(r"<[^>]*>", "", txt)
    if "<" in plain or ">" in plain.replace("&gt;", ""):
        pass
    return None


def check_markup(rm, where):
    if not rm:
        return []
    if isinstance(rm, str):
        rm = json.loads(rm)
    out = []
    for row in rm.get("inline_keyboard", []):
        for b in row:
            if not b.get("text"):
                PROBLEMS.append(("пустой текст кнопки", where, str(b)))
            cd = b.get("callback_data")
            if cd is not None and len(cd.encode()) > 64:
                PROBLEMS.append(("callback_data длиннее 64 байт", where, cd))
            if cd is not None:
                out.append(cd)
    return out


NEW_CB = []


def fake_request(token, method_name, method="get", params=None, files=None):
    params = params or {}
    CALLS.append((method_name, params))
    if method_name in ("sendMessage", "editMessageText"):
        txt = params.get("text", "")
        if len(txt) > 4096:
            PROBLEMS.append(("текст > 4096 (Telegram отклонит)", CUR["where"], f"{len(txt)} симв."))
            raise apihelper.ApiTelegramException(method_name, "x", {"error_code": 400, "description": "Bad Request: message is too long"})
        if not txt.strip():
            PROBLEMS.append(("пустой текст", CUR["where"], method_name))
            raise apihelper.ApiTelegramException(method_name, "x", {"error_code": 400, "description": "Bad Request: message text is empty"})
        if params.get("parse_mode") == "HTML":
            e = check_html(txt)
            if e:
                PROBLEMS.append(("битый HTML (Telegram отклонит)", CUR["where"], e + " :: " + txt[:80].replace("\n", " ")))
                raise apihelper.ApiTelegramException(method_name, "x", {"error_code": 400, "description": "Bad Request: can't parse entities"})
        NEW_CB.extend(check_markup(params.get("reply_markup"), CUR["where"]))
        return {"message_id": 1000 + len(CALLS), "chat": {"id": int(params.get("chat_id", 0) or 0), "type": "private"}, "date": int(time.time()), "text": txt}
    if method_name in ("sendPhoto", "sendDocument", "sendVoice", "sendAudio", "sendSticker", "sendVideo", "sendAnimation", "sendInvoice"):
        NEW_CB.extend(check_markup(params.get("reply_markup"), CUR["where"]))
        cap = params.get("caption", "")
        if len(cap) > 1024:
            PROBLEMS.append(("подпись > 1024", CUR["where"], f"{len(cap)}"))
            raise apihelper.ApiTelegramException(method_name, "x", {"error_code": 400, "description": "Bad Request: message caption is too long"})
        return {"message_id": 1000 + len(CALLS), "chat": {"id": int(params.get("chat_id", 0) or 0), "type": "private"}, "date": int(time.time())}
    if method_name == "editMessageReplyMarkup":
        NEW_CB.extend(check_markup(params.get("reply_markup"), CUR["where"]))
        return True
    if method_name == "getMe":
        return {"id": 99, "is_bot": True, "first_name": "Bot", "username": "hanzhu_chinesebot"}
    return True


apihelper._make_request = fake_request
bot.bot.threaded = False
bot.bot.exception_handler = None
bot.bot.skip_pending = True
import telebot
from telebot import types

_uid = {"n": 0}


def user_obj(uid, lang):
    return {"id": uid, "is_bot": False, "first_name": f"U{uid}", "username": f"u{uid}", "language_code": lang}


def msg_update(uid, text, lang="ru"):
    _uid["n"] += 1
    return types.Update.de_json({"update_id": _uid["n"], "message": {
        "message_id": 500 + _uid["n"], "date": int(time.time()), "chat": {"id": uid, "type": "private", "first_name": f"U{uid}"},
        "from": user_obj(uid, lang), "text": text,
        **({"entities": [{"type": "bot_command", "offset": 0, "length": len(text.split()[0])}]} if text.startswith("/") else {})}})


def cb_update(uid, data, lang="ru"):
    _uid["n"] += 1
    return types.Update.de_json({"update_id": _uid["n"], "callback_query": {
        "id": str(_uid["n"]), "from": user_obj(uid, lang), "chat_instance": "x", "data": data,
        "message": {"message_id": 700, "date": int(time.time()), "chat": {"id": uid, "type": "private"},
                    "from": {"id": 99, "is_bot": True, "first_name": "Bot", "username": "hanzhu_chinesebot"}, "text": "menu"}}})


SLOW = []
SILENT = []


def run(update, where):
    CUR["where"] = where
    n0 = len(CALLS)
    t0 = time.time()
    try:
        bot.bot.process_new_updates([update])
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)[-1]
        PROBLEMS.append(("исключение в обработчике", where, f"{type(e).__name__}: {e} ({os.path.basename(tb.filename)}:{tb.lineno})"))
    dt = time.time() - t0
    if dt > 0.4:
        SLOW.append((where, round(dt, 2)))
    return CALLS[n0:]


def mkuser(uid, lang, level="hsk1"):
    db.save_user(uid, name=f"Тест{uid}", username=f"u{uid}", lang=lang, level=level, source="test")


def crawl(uid, lang, start_cbs, limit=250):
    seen, queue, clicks = set(), list(dict.fromkeys(start_cbs)), 0
    while queue and clicks < limit:
        cd = queue.pop(0)
        if cd in seen:
            continue
        seen.add(cd)
        clicks += 1
        NEW_CB.clear()
        calls = run(cb_update(uid, cd, lang), f"[{lang}] кнопка «{cd}»")
        visible = [c for c in calls if c[0] != "answerCallbackQuery" or c[1].get("text")]
        if not visible:
            SILENT.append((lang, cd))
        for n in dict.fromkeys(NEW_CB):
            if n not in seen:
                queue.append(n)
    return clicks


def main():
    if os.environ.get("NOSPLIT"):
        bot.bot.send_message = bot._orig_send_message
    owner = int(os.environ.get("OWNER_ID", "1"))
    total_clicks = 0
    for lang, uid in (("ru", 9101), ("uz", 9102), ("en", 9103), ("zh", 9104)):
        mkuser(uid, lang)
        # 1) /start и все кнопки нижнего меню
        NEW_CB.clear()
        run(msg_update(uid, "/start", lang), f"[{lang}] /start")
        start_cbs = list(NEW_CB)
        labels = sorted(bot.menu_labels(lang))
        for lb in labels:
            NEW_CB.clear()
            calls = run(msg_update(uid, lb, lang), f"[{lang}] меню «{lb}»")
            start_cbs += list(NEW_CB)
            if not [c for c in calls if c[0] in ("sendMessage", "sendPhoto", "sendVoice", "sendAudio", "sendDocument", "sendSticker", "sendInvoice")]:
                PROBLEMS.append(("кнопка меню без ответа", f"[{lang}]", lb))
        for cmd in ("/help", "/terms", "/paysupport", "/progress", "/word", "/myteacher", "/rules", "/practice", "/book", "/menu", "/lang", "/donate", "/trial", "/schedule"):
            NEW_CB.clear()
            run(msg_update(uid, cmd, lang), f"[{lang}] команда {cmd}")
            start_cbs += list(NEW_CB)
        total_clicks += crawl(uid, lang, start_cbs)
    # владелец: обходим админ-панель
    mkuser(owner, "ru")
    NEW_CB.clear()
    run(msg_update(owner, "/start", "ru"), "[owner] /start")
    cbs = list(NEW_CB)
    for cmd in ("/admin", "/panel", "/students", "/stats", "/teachers", "/stickers", "/help", "/menu", "/myteacher"):
        NEW_CB.clear()
        run(msg_update(owner, cmd, "ru"), f"[owner] команда {cmd}")
        cbs += list(NEW_CB)
    for lb in sorted(bot.menu_labels("ru")):
        NEW_CB.clear()
        run(msg_update(owner, lb, "ru"), f"[owner] меню «{lb}»")
        cbs += list(NEW_CB)
    total_clicks += crawl(owner, "ru", cbs, 400)

    print(f"\nвсего нажатий кнопок: {total_clicks}, вызовов API: {len(CALLS)}")
    agg = collections.OrderedDict()
    for k, w, d in PROBLEMS:
        agg.setdefault((k, d), []).append(w)
    print(f"\n=== ПРОБЛЕМЫ: {len(agg)} уникальных ===")
    for (k, d), ws in agg.items():
        print(f"- {k}: {d}\n    где: {ws[0]}" + (f" (+ещё {len(ws)-1})" if len(ws) > 1 else ""))
    print(f"\n=== МОЛЧАЛИВЫЕ КНОПКИ (нажатие без видимой реакции): {len(SILENT)} ===")
    for lang, cd in SILENT[:60]:
        print(f"- [{lang}] {cd}")
    print(f"\n=== МЕДЛЕННЫЕ (>0.4с без сети): {len(SLOW)} ===")
    for w, dt in sorted(SLOW, key=lambda x: -x[1])[:20]:
        print(f"- {dt}с {w}")


if __name__ == "__main__":
    main()
