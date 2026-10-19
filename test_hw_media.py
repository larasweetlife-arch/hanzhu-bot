"""Домашка с вложениями: Лазиза задаёт фото/видео/аудио/голос/кружок/файл + текст, ученик сдаёт то же самое."""
import os, sys, types as ty, tempfile, itertools, json
d = tempfile.mkdtemp()
os.environ.update(BOT_TOKEN="123456:TESTTOKEN", OWNER_ID="1", DATA_DIR=d)
os.environ.pop("WEBAPP_URL", None)
sys.path.insert(0, "hanzhu4")
import bot, db
from texts import t

log, mid = [], itertools.count(100)
def rec(kind):
    def f(*a, **kw):
        log.append({"kind": kind, "to": a[0] if a else None, "a": a, "kw": kw})
        return ty.SimpleNamespace(message_id=next(mid))
    return f
for k in ("message", "photo", "video", "audio", "voice", "video_note", "document", "animation", "sticker"):
    setattr(bot.bot, "send_" + k, rec(k))
bot.bot.copy_message = rec("copy")
bot.bot.edit_message_text = rec("edit")
bot.bot.edit_message_reply_markup = rec("editmk")
bot.bot.answer_callback_query = lambda *a, **k: None
bot.bot.set_my_commands = lambda *a, **k: None
bot._orig_send_message = bot.bot.send_message

fails = []
def check(name, cond):
    print(("OK   " if cond else "FAIL ") + name)
    if not cond: fails.append(name)
def of(kind, to=None): return [e for e in log if e["kind"] == kind and (to is None or e["to"] == to)]
def user(uid): return ty.SimpleNamespace(id=uid, username=f"u{uid}", first_name=f"N{uid}")
def base(uid, ct, **extra):
    return ty.SimpleNamespace(from_user=user(uid), chat=ty.SimpleNamespace(id=uid), message_id=next(mid), reply_to_message=None,
                              content_type=ct, text=None, caption=extra.pop("caption", None), media_group_id=None, **extra)
def say(uid, txt):
    m = base(uid, "text"); m.text = txt; bot.on_text(m)
def media(uid, ct, caption=None, **kw):
    obj = ty.SimpleNamespace(file_id=f"F_{ct}", **kw)
    extra = {"photo": [ty.SimpleNamespace(file_id="small"), ty.SimpleNamespace(file_id="F_photo")]} if ct == "photo" else {ct: obj}
    bot.on_file(base(uid, ct, caption=caption, **extra))
def click(uid, data):
    c = ty.SimpleNamespace(id="cq", from_user=user(uid), data=data,
                           message=ty.SimpleNamespace(message_id=next(mid), chat=ty.SimpleNamespace(id=uid), content_type="text"))
    for h in bot.bot.callback_query_handlers:
        f = h.get("filters", {}).get("func")
        if f and f(c):
            return h["function"](c)
    raise RuntimeError("нет обработчика " + data)

for u, lg in ((1, "ru"), (5001, "ru"), (5002, "en")):
    db.save_user(u, name=f"Name{u}", username=f"u{u}", lang=lg, level="HSK1")

# 1. задание: фото с подписью + видео + текст
click(1, "hwn:5001")
check("owner: просит текст или вложения", "видео" in log[-1]["a"][1] and log[-1]["to"] == 1)
media(1, "photo", caption="Выучи слова на фото")
check("owner: фото принято, шаг остался hw_text", bot.STATE[1]["step"] == "hw_text" and len(bot.STATE[1]["data"]["media"]) == 1)
check("owner: подпись стала текстом задания", bot.STATE[1]["data"]["text"] == "Выучи слова на фото")
media(1, "video", mime_type="video/mp4")
check("owner: второе вложение принято", len(bot.STATE[1]["data"]["media"]) == 2)
say(1, "Посмотри видео и повтори")
check("owner: текст заменил подпись и перешёл к сроку", bot.STATE[1]["step"] == "hw_due" and bot.STATE[1]["data"]["text"] == "Посмотри видео и повтори")
log.clear()
say(1, "завтра")
check("ученику ушло фото и видео, затем карточка с кнопками",
      len(of("photo", 5001)) == 1 and len(of("video", 5001)) == 1 and len(of("message", 5001)) == 1
      and of("message", 5001)[0]["kw"].get("reply_markup") is not None)
h = db.hw_open(5001)[0]
check("в базе вложения сохранены", len(json.loads(h["media_id"])) == 2 and h["text"] == "Посмотри видео и повтори")
check("owner: получила отчёт", any("Домашка отправлена: 1" in (e["a"][1] if len(e["a"]) > 1 else "") for e in of("message", 1)))

# 2. одно голосовое без текста: подпись и кнопки сразу на нём
click(1, "hwn:5002")
media(1, "voice")
click(1, "hwm:next")
check("«Дальше» переводит к сроку", bot.STATE[1]["step"] == "hw_due")
log.clear()
say(1, "-")
v = of("voice", 5002)
check("голосовое отправлено с карточкой-подписью и кнопками", len(v) == 1 and "New homework" in v[0]["kw"]["caption"] and v[0]["kw"].get("reply_markup"))
h2 = db.hw_open(5002)[0]
check("текст по умолчанию: значок и дата, не пусто", h2["text"].startswith("🎙") and len(h2["text"]) > 3)

# 3. кружок: сам без подписи, карточка отдельным сообщением
bot.STATE[1] = {"step": "hw_text", "data": {"uids": [5001, 5002]}}
media(1, "video_note", length=240)
check("кружок принят", len(bot.STATE[1]["data"]["media"]) == 1)
say(1, "Расскажи о себе вот так")
log.clear()
say(1, "-")
check("кружок ушёл обоим + карточка с кнопками", len(of("video_note")) == 2 and len(of("message", 5001)) == 1 and len(of("message", 5002)) == 1)

# 4. список домашки у ученика снова показывает вложения
log.clear()
bot.send_hw_list(5001)
check("список /hw: вложения переотправлены", len(of("photo", 5001)) == 1 and len(of("video", 5001)) == 1 and len(of("video_note", 5001)) == 1)

# 5. сдача: все форматы + текст
hid = db.hw_open(5001)[0]["id"]
click(5001, f"hws:ask:{hid}")
check("ученик: подсказка про форматы упоминает видео", "видео" in log[-1]["a"][1].lower())
click(5001, f"hws:go:{hid}")
log.clear()
media(5001, "video", mime_type="video/mp4")
media(5001, "video_note", length=240)
media(5001, "animation", mime_type="video/mp4")
media(5001, "audio", mime_type="audio/mpeg")
media(5001, "voice")
media(5001, "photo")
media(5001, "document", file_name="speech.MOV", mime_type="video/quicktime")
media(5001, "document", file_name="work.pdf", mime_type="application/pdf")
say(5001, "Вот мой ответ текстом")
check("ученик: принято 9 вложений/сообщений", len(of("copy")) == 9 and bot.STATE[5001]["data"]["n"] == 9)
media(5001, "document", file_name="archive.zip", mime_type="application/zip")
check("ученик: архив отклонён", len(of("copy")) == 9 and bot.STATE[5001]["data"]["n"] == 9)
click(5001, f"hws:fin:{hid}")
subs = [s for s in range(1, 5) if db.sub_get(s)]
check("сдача записана: 9 файлов, задание закрыто", db.sub_get(subs[0])["files"] == 9 and db.hw_get(hid)["done"] == 1)
check("owner уведомлена про сдачу", any("сдал" in str(e["a"][1]) for e in of("message", 1) if len(e["a"]) > 1))

# 6. «Доработать» — задание целиком (с вложениями) снова у ученика
log.clear()
click(1, f"hwr:{subs[0]}")
check("redo: вложения и карточка отправлены заново", len(of("photo", 5001)) == 1 and len(of("video", 5001)) == 1 and db.hw_get(hid)["done"] == 0)

# 7. старые текстовые задания работают как раньше
log.clear()
click(1, "hwn:5001")
say(1, "Только текст")
say(1, "-")
check("текстовое задание: одно сообщение без медиа", len(of("message", 5001)) == 1 and not any(of(k, 5001) for k in ("photo", "video", "voice")))
# 8. длинные подписи
big = "Ы" * 600
click(1, "hwn:5001"); media(1, "photo", caption=big); say(1, "-") if False else None
bot.STATE[1]["step"] = "hw_due"
log.clear(); say(1, "-")
cap = of("photo", 5001)[0]["kw"]["caption"]
check("подпись ≤ 1024", len(cap) <= 1024)

print("\nПРОВАЛЕНО:" if fails else "\nВсе проверки пройдены", fails or "")
sys.exit(1 if fails else 0)
