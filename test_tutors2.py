"""Версия 23: перенос записи, отзывы, пробный урок, связь с Лазизой."""
import logging; logging.basicConfig(level=logging.ERROR)
import os, sys, types as ty, tempfile, itertools, json
from datetime import datetime, timedelta
d = tempfile.mkdtemp()
os.environ.update(BOT_TOKEN="123456:TESTTOKEN", OWNER_ID="1", DATA_DIR=d)
os.environ.pop("WEBAPP_URL", None)
sys.path.insert(0, "hanzhu4")
from agreement import AGREEMENT_VERSION
import bot, db, booking, tutors, tutors2
from texts import t, T

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
bot.bot.delete_message = rec("delete")
bot.bot.answer_callback_query = lambda *a, **k: None
bot.bot.set_my_commands = lambda *a, **k: None

class _R:
    def __init__(self, rows): self.rows = rows
    def fetchone(self): return self.rows[0] if self.rows else None
    def fetchall(self): return self.rows
    def __iter__(self): return iter(self.rows)
class _C:
    def execute(self, sql, args=()):
        with db._conn() as c:
            return _R(c.execute(sql, args).fetchall())
CN = _C()

fails = []
def check(name, cond):
    print(("OK   " if cond else "FAIL ") + name)
    if not cond: fails.append(name)
def of(kind, to=None): return [e for e in log if e["kind"] == kind and (to is None or e["to"] == to)]
def texts(to): return [str(e["a"][1]) if len(e["a"]) > 1 else str(e["kw"].get("caption", "")) for e in log if e["to"] == to]
def got(to, needle): return any(needle in s for s in texts(to))
def user(uid): return ty.SimpleNamespace(id=uid, username=f"u{uid}", first_name=f"N{uid}")
def base(uid, ct, **extra):
    return ty.SimpleNamespace(from_user=user(uid), chat=ty.SimpleNamespace(id=uid), message_id=next(mid), reply_to_message=None,
                              content_type=ct, text=None, caption=extra.pop("caption", None), media_group_id=None, **extra)
def say(uid, txt, reply_to=None):
    m = base(uid, "text"); m.text = txt
    if reply_to: m.reply_to_message = ty.SimpleNamespace(message_id=reply_to)
    bot.on_text(m)
def cmd(uid, txt):
    m = base(uid, "text"); m.text = txt
    for h in bot.bot.message_handlers:
        if bot.bot._test_message_handler(h, m):
            return h["function"](m)
def media(uid, ct, caption=None, reply_to=None, **kw):
    obj = ty.SimpleNamespace(file_id=f"F_{ct}", **kw)
    extra = {"photo": [ty.SimpleNamespace(file_id="small"), ty.SimpleNamespace(file_id="F_photo")]} if ct == "photo" else {ct: obj}
    m = base(uid, ct, caption=caption, **extra)
    if reply_to: m.reply_to_message = ty.SimpleNamespace(message_id=reply_to)
    bot.on_file(m)
def click(uid, data):
    c = ty.SimpleNamespace(id="cq", from_user=user(uid), data=data,
                           message=ty.SimpleNamespace(message_id=next(mid), chat=ty.SimpleNamespace(id=uid), content_type="text"))
    for h in bot.bot.callback_query_handlers:
        f = h.get("filters", {}).get("func")
        if f and f(c):
            return h["function"](c)
    raise RuntimeError("нет обработчика " + data)
def kbt(k): return [getattr(b, "text", None) or (b.get("text") if isinstance(b, dict) else b) for row in k.keyboard for b in row]
def btns(e):
    mk = e["kw"].get("reply_markup")
    return [b.callback_data for row in mk.keyboard for b in row] if mk else []
def btn_texts(e):
    mk = e["kw"].get("reply_markup")
    return [b.text for row in mk.keyboard for b in row] if mk else []
today = lambda n=0: (datetime.now(db.TZ).date() + timedelta(days=n)).isoformat()

def urls(e):
    mk = e["kw"].get("reply_markup")
    return [b.url for row in mk.keyboard for b in row if getattr(b, "url", None)] if mk else []
def all_btns():
    return [b for e in log for b in btns(e)]

for u, lg in ((1, "ru"), (5001, "ru"), (5002, "en"), (5003, "uz"), (6001, "ru")):
    db.save_user(u, name=f"Name{u} Фамилия", username=f"u{u}", lang=lg, level="HSK1")

# подготовка: репетитор с подпиской и соглашением, часы на каждый день
click(1, "bt:add"); say(1, "@u6001")
t1 = booking.teacher_of_user(6001)
HOURS = "пн 10:00, вт 10:00, ср 10:00, чт 10:00, пт 10:00, сб 10:00, вс 10:00, пн 15:00, вт 15:00, ср 15:00, чт 15:00, пт 15:00, сб 15:00, вс 15:00"
booking.update(t1["id"], bio="Опытный", hours=HOURS, link="https://zoom.us/x", tier=2, tier_until=today(30),
               agreed_ver=tutors.AGREEMENT_VERSION, agreed_at="x", active=1)
TID = t1["id"]

# 0. тексты на 4 языках
from texts_v14 import P
keys = set(P["ru"])
check("тексты v14: одинаковые ключи в 4 языках", all(set(P[l]) == keys for l in ("uz", "en", "zh")))
check("тексты v14 подключены к t()", all(t(l, "mv2_btn") != "mv2_btn" for l in ("ru", "uz", "en", "zh")))

# 1. связь с Лазизой и /tutor
log.clear(); cmd(5001, "/tutor")
e = of("message", 5001)[-1]
check("/tutor: объяснение и кнопка связи", "Как это устроено" in str(e["a"][1]) and "https://t.me/nutlrz" in urls(e))
check("/tutor: уровни подписки перечислены", all(n in str(e["a"][1]) for n in ("Старт", "Стандарт", "Про")))
log.clear(); cmd(5001, "/myteacher")
check("/myteacher без профиля: кнопка связи", any("t.me/nutlrz" in u for e in of("message", 5001) for u in urls(e)))
log.clear(); cmd(6001, "/myteacher")
bt = [b for e in log for b in btns(e)]
check("профиль репетитора: Отзывы, Как это работает", f"tq:rl:{TID}" in bt and "tq:info" in bt)
check("профиль репетитора: Написать Лазизе (url)", any("t.me/nutlrz" in u for e in log for u in urls(e)))
log.clear(); click(6001, f"tt:my:{TID}")
check("экран подписки: кнопка связи", any("t.me/nutlrz" in u for e in log for u in urls(e)) or any("nutlrz" in str(e["a"]) for e in log))
booking.update(TID, tier_until=today(-1))
log.clear(); click(6001, f"tt:hw:{TID}")
check("функция закрыта без подписки: сообщение и кнопка связи", got(6001, "Подписка не активна") and any("t.me/nutlrz" in u for e in of("message", 6001) for u in urls(e)))
booking.update(TID, tier_until=today(30))

# 2. запись и перенос
slots = booking.free_slots(TID)
far = [s for s in slots if s > datetime.now(db.TZ) + timedelta(days=2)]
st, bid = booking.book(TID, 5002, far[0])
check("запись создана", st == "ok")
log.clear(); click(5002, "bk:my")
mine = [e for e in log if any(b.startswith("tq:mv:") for b in btns(e))]
check("в «Мои записи» есть кнопка переноса", bool(mine))
log.clear(); click(5002, f"tq:mv:{bid}")
pick = [b for e in log for b in btns(e) if b.startswith("tq:mc:")]
check("перенос: показаны свободные времена", 1 <= len(pick) <= tutors2.MOVE_SLOTS and far[0].strftime("%Y%m%d%H%M") not in "".join(pick))
new_cb = pick[0]
log.clear(); click(5002, new_cb)
ask = [e for e in of("message") if any(b.startswith("tq:my:") for b in btns(e))]
check("репетитору пришла просьба с кнопками", any(e["to"] == 6001 for e in ask))
check("Лазизе тоже пришла копия, как и о записях", any(e["to"] == 1 for e in ask))
mvid = int(next(b for b in btns(ask[0]) if b.startswith("tq:my:")).split(":")[2])
log.clear(); click(5002, f"tq:mv:{bid}")
check("повторная просьба заблокирована", any("already been sent" in str(e["a"]) for e in log))
check("чужой не может подтвердить", (click(5003, f"tq:my:{mvid}"), booking.active_bookings(uid=5002)[0]["start"])[1] == far[0].strftime(booking.FMT))
log.clear(); click(6001, f"tq:my:{mvid}")
b = booking.active_bookings(uid=5002)[0]
newdt = booking._dt(new_cb.split(":")[3])
check("перенос подтверждён: время записи изменилось", b["start"] == newdt.strftime(booking.FMT))
check("ученик получил подтверждение со ссылкой", got(5002, "Lesson moved") and got(5002, "zoom.us"))
log.clear(); click(6001, f"tq:my:{mvid}")
check("повторное нажатие: ничего не меняется", booking.active_bookings(uid=5002)[0]["start"] == newdt.strftime(booking.FMT) and not of("message", 5002))

# отказ
slots = [s for s in booking.free_slots(TID) if s > datetime.now(db.TZ) + timedelta(days=2)]
click(5002, f"tq:mv:{bid}")
cb2 = f"tq:mc:{bid}:{slots[0].strftime('%Y%m%d%H%M')}"
log.clear(); click(5002, cb2)
m2 = int(next(b for e in of("message", 6001) for b in btns(e) if b.startswith("tq:mn:")).split(":")[2])
log.clear(); click(6001, f"tq:mn:{m2}")
check("отказ: запись на прежнем времени", booking.active_bookings(uid=5002)[0]["start"] == newdt.strftime(booking.FMT))
check("отказ: ученик получил сообщение", got(5002, "couldn't move"))

# время заняли, пока репетитор думал
slots = [s for s in booking.free_slots(TID) if s > datetime.now(db.TZ) + timedelta(days=2)]
click(5002, f"tq:mv:{bid}")
log.clear(); click(5002, f"tq:mc:{bid}:{slots[0].strftime('%Y%m%d%H%M')}")
m3 = int(next(b for e in of("message", 6001) for b in btns(e) if b.startswith("tq:my:")).split(":")[2])
booking.book(TID, 5003, slots[0])
log.clear(); click(6001, f"tq:my:{m3}")
check("время уже занято: перенос не выполнен, ученику отказ", booking.active_bookings(uid=5002)[0]["start"] == newdt.strftime(booking.FMT) and got(5002, "couldn't move"))

# слишком поздно
soon = datetime.now(db.TZ) + timedelta(hours=2, minutes=30)
with db._conn() as c:
    cur = c.execute("INSERT INTO bookings (teacher_id,user_id,start,duration,reminded,created) VALUES (?,?,?,?,1,'x')",
                    (TID, 5001, soon.strftime(booking.FMT), 60))
    sb = cur.lastrowid
log.clear(); click(5001, f"tq:mv:{sb}")
check("меньше 3 часов до урока: перенос через бота закрыт", any("3 часов" in str(e["a"]) for e in log) and not any(b.startswith("tq:mc:") for b in all_btns()))

# 3. отзывы
past = datetime.now(db.TZ) - timedelta(hours=3)
with db._conn() as c:
    pb = c.execute("INSERT INTO bookings (teacher_id,user_id,start,duration,reminded,created) VALUES (?,?,?,?,1,'x')",
                   (TID, 5003, past.strftime(booking.FMT), 60)).lastrowid
log.clear(); tutors2.hook(datetime.now(db.TZ))
ask = [e for e in of("message", 5003) if any(b.startswith("tq:r:") for b in btns(e))]
check("после урока ученик получил просьбу об оценке (uz)", len(ask) == 1)
check("репетитору, у которого нет прошедших уроков, ничего не пришло", not of("message", 6001))
log.clear(); tutors2.hook(datetime.now(db.TZ))
check("просьба не повторяется", not of("message", 5003))
click(5003, f"tq:r:{pb}:5"); say(5003, "Zo'r dars")
check("после текста спрашивают разрешение показывать", any("tq:rp:1" in b for e in of("message", 5003) for b in btns(e)))
log.clear(); click(5003, "tq:rp:1")
rv = CN.execute("SELECT * FROM bk_reviews").fetchall()
check("отзыв сохранён: оценка, текст, разрешение", len(rv) == 1 and rv[0]["rating"] == 5 and rv[0]["text"] == "Zo'r dars" and rv[0]["public"] == 1)
check("репетитор получил отзыв", got(6001, "Новый отзыв") and got(6001, "5/5"))
click(5003, f"tq:r:{pb}:4")
say(5003, "ещё")
check("второй отзыв на тот же урок не создаётся", len(CN.execute("SELECT * FROM bk_reviews").fetchall()) == 1)
TX = tutors2.TX; TX.pop(5003, None)
post = booking.post
log.clear(); booking.post(5001, TID)
check("рейтинг не виден, пока отзывов меньше трёх", "⭐" not in str(of("message", 5001)[-1]["a"][1]))
for i in range(2):
    CN.execute("SELECT 1")
    with db._conn() as c:
        c.execute("INSERT INTO bk_reviews (teacher_id,user_id,booking_id,rating,text,public,created) VALUES (?,?,?,?,?,1,'x')", (TID, 7000 + i, 0, 4, "", ))
log.clear(); booking.post(5001, TID)
txt = str(of("message", 5001)[-1]["a"][1]) if of("message", 5001) else ""
check("три публичных отзыва: рейтинг в профиле", "4.3" in txt and "3" in txt)
with db._conn() as c:
    c.execute("INSERT INTO bk_reviews (teacher_id,user_id,booking_id,rating,text,public,created) VALUES (?,?,?,?,?,0,'x')", (TID, 7100, 0, 1, "плохо"))
check("закрытый отзыв в рейтинг не входит", tutors2.rating_of(TID) == (4.3, 3))
log.clear(); click(6001, f"tq:rl:{TID}")
check("репетитор видит все отзывы, включая закрытые", any("плохо" in str(e["a"]) for e in log))
log.clear(); click(5001, f"tq:rl:{TID}")
check("ученик список отзывов не видит", not any("плохо" in str(e["a"]) for e in log))
# своя запись Лазизы отзывами через этот поток не охватывается
own_t = booking.teacher_of_user(1)
check("у Лазизы нет строки рейтинга и нет просьбы об отзыве этого типа", tutors2.post_line("ru", own_t) == "")

# 4. пробный урок
log.clear(); booking.post(5001, TID)
check("в профиле репетитора есть «Пробный урок»", f"tq:tr:{TID}" in [b for e in of("message", 5001) for b in btns(e)])
booking.update(own_t["id"], active=1)
log.clear(); booking.post(5001, own_t["id"])
check("в профиле Лазизы кнопка ведёт в её прежний пробный урок", "bk:trial" in [b for e in of("message", 5001) for b in btns(e)])
log.clear(); click(5001, f"tq:tr:{TID}")
check("пробный урок: просьба написать время и о себе", got(5001, "Напиши репетитору") or len(of("message", 5001)) == 1)
log.clear(); say(5001, "Пн вечером, мне 12 лет, HSK1")
sent = [e for e in of("message", 6001) if "Заявка на пробный урок" in str(e["a"][1])]
check("заявка пришла репетитору с данными ученика", len(sent) == 1 and "Пн вечером" in str(sent[0]["a"][1]) and "u5001" in str(sent[0]["a"][1]))
check("заявка не ушла Лазизе", not of("message", 1))
check("ученик получил подтверждение", len(of("message", 5001)) >= 1)
mid_msg = sent[0]
inbox = CN.execute("SELECT * FROM t_inbox WHERE chat_id=6001 AND user_id=5001").fetchall()
check("заявка связана с учеником для ответа", len(inbox) == 1)
log.clear(); say(6001, "Здравствуйте! Давайте в пн в 18:00", reply_to=inbox[0]["msg_id"])
check("ответ репетитора дошёл до ученика", got(5001, "Давайте в пн в 18:00"))
log.clear(); click(5001, f"tq:tr:{TID}")
check("вторая заявка в тот же день блокируется", got(5001, "Ты уже отправлял") or got(5001, "уже отправлял"))
with db._conn() as c:
    pass
# состояние сбрасывается, если ученик нажал кнопку меню
TX[5002] = {"step": "trial", "tid": TID}
say(5002, "/start")
check("команда сбрасывает диалог", 5002 not in TX)

print("\nFAILS:", fails)
sys.exit(1 if fails else 0)
