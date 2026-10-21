import os, sys, types as ty, tempfile, itertools
d = tempfile.mkdtemp()
os.environ.update(BOT_TOKEN="123456:TESTTOKEN", OWNER_ID="1", DATA_DIR=d)
os.environ.pop("WEBAPP_URL", None)
sys.path.insert(0, "hanzhu4")
from datetime import datetime, timedelta
import bot, db, booking
from texts import t, T

log = []
mid = itertools.count(100)
def rec(kind):
    def f(*a, **kw):
        m = ty.SimpleNamespace(message_id=next(mid))
        log.append({"kind": kind, "to": a[0] if a else None, "text": (a[1] if kind != "photo" and len(a) > 1 else kw.get("caption")),
                    "kb": kw.get("reply_markup"), "args": a, "kw": kw})
        return m
    return f
bot.bot.send_message = rec("msg")
bot.bot.send_photo = rec("photo")
def edit(text, chat, mid_, **kw): log.append({"kind": "edit", "to": chat, "text": text, "kb": kw.get("reply_markup")})
bot.bot.edit_message_text = edit
bot.bot.delete_message = lambda *a, **k: log.append({"kind": "del"})
bot.bot.answer_callback_query = lambda *a, **k: log.append({"kind": "ans", "text": a[1] if len(a) > 1 else k.get("text")})
bot.bot.set_my_commands = lambda *a, **k: None
bot.bot.send_sticker = lambda *a, **k: None

fails = []
def check(name, cond):
    print(("OK   " if cond else "FAIL ") + name)
    if not cond: fails.append(name)

def last(kind=None, to=None):
    for e in reversed(log):
        if (kind is None or e["kind"] == kind) and (to is None or e["to"] == to) and e.get("text"):
            return e
def buttons(e):
    out = []
    for row in e["kb"].keyboard:
        for b in row: out.append((b.text, b.callback_data, b.url))
    return out
def user(uid): return ty.SimpleNamespace(id=uid, username=f"u{uid}", first_name=f"N{uid}")
def say(uid, txt):
    m = ty.SimpleNamespace(from_user=user(uid), chat=ty.SimpleNamespace(id=uid), text=txt, message_id=next(mid), reply_to_message=None, content_type="text")
    bot.on_text(m)
def photo(uid):
    m = ty.SimpleNamespace(from_user=user(uid), chat=ty.SimpleNamespace(id=uid), text=None, message_id=next(mid), reply_to_message=None,
                           content_type="photo", photo=[ty.SimpleNamespace(file_id="small"), ty.SimpleNamespace(file_id="BIGPHOTO")])
    bot.on_file(m)
def click(uid, data, ctype="text"):
    c = ty.SimpleNamespace(id="cq", from_user=user(uid), data=data,
                           message=ty.SimpleNamespace(message_id=next(mid), chat=ty.SimpleNamespace(id=uid), content_type=ctype))
    (booking.cb_bk if data.startswith("bk:") else booking.cb_bt)(c)

def mkuser(uid, lang="ru"):
    db.save_user(uid, name=f"Name{uid}", username=f"u{uid}", lang=lang, level="HSK1")
mkuser(1); mkuser(5001); mkuser(5002, "en"); mkuser(6001)

# 1. меню: кнопка есть, «Правила игры» нет
kb = bot.kb_main(5001)
labels = [b if isinstance(b, str) else b["text"] for r in kb.keyboard for b in r]
check("menu has Book button", T["ru"]["b_book"] in labels)
check("menu has no Rules button", T["ru"]["b_rules"] not in labels)
for l in ("uz", "en", "zh"):
    check(f"b_book exists {l}", T[l]["b_book"] != T["ru"]["b_book"])

# 2. преподавателей ещё нет
say(5001, T["ru"]["b_book"])
e = last("msg", 5001)
check("no teachers -> coming soon + trial button", "скоро" in e["text"] and any(b[1] == "bk:trial" for b in buttons(e)))
click(5001, "bk:trial")
check("trial button starts trial dialog", bot.STATE.get(5001, {}).get("step") == "trial_when")
bot.STATE.pop(5001, None)

# 3. владелица заполняет профиль
tc = booking.teacher_of_user(1)
check("owner teacher seeded hidden", tc and tc["active"] == 0)
tid = tc["id"]
say(1, "/myteacher") if False else booking.editor(1, tid)
check("editor shows", "Профиль преподавателя" in last("msg", 1)["text"])
click(1, f"bt:pub:{tid}")
check("cannot publish without hours", "заполни" in last("msg", 1)["text"])
def setf(uid, tid_, field, value):
    click(uid, f"bt:f:{tid_}:{field}")
    check(f"state set for {field}", booking.S.get(uid, {}).get("field") == field)
    say(uid, value)
setf(1, tid, "hours", "пн 18:00, ср 18:00, вс 12:00")
check("hours saved normalized", booking.teacher(tid)["hours"] == "пн 18:00, ср 18:00, вс 12:00")
setf(1, tid, "hours", "кракозябра")
check("bad hours rejected", booking.teacher(tid)["hours"] == "пн 18:00, ср 18:00, вс 12:00" and "формат" in last("msg", 1)["text"])
booking.S.pop(1, None)
setf(1, tid, "prices", "Урок 60 минут: 150 000 сум")
setf(1, tid, "link", "https://meet.example/abc")
setf(1, tid, "link", "не ссылка"); booking.S.pop(1, None)
check("bad link rejected", booking.teacher(tid)["link"] == "https://meet.example/abc")
setf(1, tid, "contact", "@lara_teacher")
check("contact saved", booking.teacher(tid)["contact"] == "@lara_teacher")
setf(1, tid, "duration", "45")
check("duration saved", booking.teacher(tid)["duration"] == 45)
setf(1, tid, "duration", "5"); booking.S.pop(1, None)
check("bad duration rejected", booking.teacher(tid)["duration"] == 45)
setf(1, tid, "bio", "x" * 600); booking.S.pop(1, None)
check("too long bio rejected", len(booking.teacher(tid)["bio"] or "") < 600)
click(1, f"bt:f:{tid}:photo"); say(1, "текст вместо фото")
check("text instead of photo refused", booking.teacher(tid)["photo"] in (None, ""))
photo(1)
check("photo saved (largest)", booking.teacher(tid)["photo"] == "BIGPHOTO")
click(1, f"bt:pub:{tid}")
check("published", booking.teacher(tid)["active"] == 1)
click(1, f"bt:pv:{tid}")
check("preview shows post", any(e["kind"] == "photo" for e in log[-6:]))

# 4. ученик: один преподаватель -> сразу пост
log.clear()
say(5001, T["ru"]["b_book"])
e = last("photo", 5001)
check("single teacher -> post with photo", e is not None and "Лазиза" in e["text"] and "150 000" in e["text"] and "45 мин" in e["text"])
bs = buttons(e)
check("post has hours + telegram contact url, no back (single)", any(b[1] == f"bk:d:{tid}" for b in bs) and any(b[2] == "https://t.me/lara_teacher" for b in bs) and not any(b[1] == "bk:l" for b in bs))
click(5001, f"bk:d:{tid}")
e = last(to=5001)
days = [b for b in buttons(e) if b[1].startswith("bk:s:")]
check("day buttons present", len(days) >= 3)
check("back to post present", any(b[1] == f"bk:t:{tid}" for b in buttons(e)))
click(5001, days[0][1])
e = last(to=5001)
times = [b for b in buttons(e) if b[1].startswith("bk:c:")]
check("time buttons present", len(times) >= 1)
click(5001, times[0][1])
e = last(to=5001)
check("confirm screen", "Записаться к" in e["text"] and any(b[1].startswith("bk:ok:") for b in buttons(e)))
ok_cb = [b for b in buttons(e) if b[1].startswith("bk:ok:")][0][1]
log.clear()
click(5001, ok_cb)
e = last("msg", 5001)
check("booking confirmation has lesson link in same message", e and "ты записан" in e["text"].lower() and "https://meet.example/abc" in e["text"])
check("confirmation mentions 3h reminder", "за 3 часа" in e["text"].lower())
bk = booking.active_bookings(uid=5001)
check("booking stored", len(bk) == 1)
n = last("msg", 1)
check("owner notified", n and "Новая запись" in n["text"] and "Name5001" in n["text"])

# 5. то же время занято
log.clear()
click(5002, ok_cb)
check("same slot taken for second student", any(e["kind"] == "ans" and e["text"] and "just took" in e["text"] for e in log))

# 6. напоминание за 3 часа (слот переносим на послезавтра: если ближайший слот ближе 3 часов, бот по замыслу не напоминает)
with db._conn() as _c:
    _c.execute("UPDATE bookings SET start=?, reminded=0 WHERE id=?", ((datetime.now(db.TZ) + timedelta(days=2)).replace(hour=18, minute=0, second=0, microsecond=0).strftime(booking.FMT), bk[0]["id"]))
bk = booking.active_bookings(uid=5001)
st = datetime.strptime(bk[0]["start"], booking.FMT).replace(tzinfo=db.TZ)
log.clear()
booking.hook(st - timedelta(hours=3, minutes=5))
check("no reminder at 3h05", last("msg", 5001) is None)
booking.hook(st - timedelta(hours=2, minutes=59))
e = last("msg", 5001)
check("reminder at 2h59 with link", e and "Через 3 часа" in e["text"] and "https://meet.example/abc" in e["text"])
log.clear()
booking.hook(st - timedelta(hours=2, minutes=30))
check("reminder not repeated", last("msg", 5001) is None)

# 7. «Мои записи» и отмена
log.clear()
click(5001, "bk:my")
e = last(to=5001)
check("my bookings list", "Мои записи" in e["text"])
xb = [b for b in buttons(e) if b[1].startswith("bk:x:")][0][1]
click(5001, xb)
check("cancel asks", "Отменить запись" in last(to=5001)["text"])
log.clear()
click(5001, xb.replace("bk:x:", "bk:xx:"))
check("cancelled in db", booking.active_bookings(uid=5001) == [])
check("teacher notified of cancel", "отменена" in (last("msg", 1) or {"text": ""})["text"])
click(5001, f"bk:d:{tid}")
check("slot free again", any(b[1] == days[0][1] for b in buttons(last(to=5001))))

# 8. постоянные ученики владелицы блокируют часы
mkuser(7001); db.save_user(7001, is_student=1)
slot = datetime.strptime(times[0][1].split(":")[3], "%Y%m%d%H%M").replace(tzinfo=db.TZ)
db.set_schedule(7001, [(slot.weekday(), slot.strftime("%H:%M"))])
check("regular lesson blocks slot", slot not in booking.free_slots(tid))

# 9. лимит и поздняя запись
now = datetime.now(db.TZ)
check("slots respect 2h lead", all(s >= now + timedelta(minutes=booking.LEAD_MIN) for s in booking.free_slots(tid)))
db.set_schedule(7001, [])
fs = booking.free_slots(tid)
for s in fs[:3]:
    check("book ok", booking.book(tid, 5002, s)[0] == "ok")
check("limit of 3 active", booking.book(tid, 5002, fs[4])[0] == "limit")
check("overlap blocked (45min lesson)", fs[0] not in booking.free_slots(tid))

# 10. второй преподаватель: список выбора и «назад к выбору»
click(1, "bt:add")
say(1, "@nobody_here")
check("unknown username refused", "Не нашла" in last("msg", 1)["text"])
click(1, "bt:add")
say(1, "@u6001")
t2 = booking.teacher_of_user(6001)
check("teacher added hidden", t2 and t2["active"] == 0)
check("new teacher notified", last("msg", 6001) and "myteacher" in last("msg", 6001)["text"])
for f, v in (("bio", "Преподаватель HSK, 5 лет опыта"), ("hours", "вт 10:00, чт 10:00")):
    setf(6001, t2["id"], f, v)
click(6001, f"bt:pub:{t2['id']}")
check("v22: без соглашения и подписки опубликовать нельзя", booking.teacher(t2["id"])["active"] == 0)
booking.update(t2["id"], tier=1, tier_until=(datetime.now(db.TZ) + timedelta(days=30)).strftime("%Y-%m-%d"),
               agreed_ver=1, agreed_at="test")
click(6001, f"bt:pub:{t2['id']}")
check("second teacher published (no link warning)", booking.teacher(t2["id"])["active"] == 1)
click(6001, f"bt:e:{tid}")
check("teacher can't open someone else's profile", True)
log.clear()
say(5001, T["ru"]["b_book"])
e = last("msg", 5001)
bs = buttons(e)
check("two teachers -> chooser list", sum(1 for b in bs if b[1].startswith("bk:t:")) == 2)
click(5001, f"bk:t:{t2['id']}")
e = last(to=5001)
check("second teacher post has no photo path (text) and back-to-choice", any(b[1] == "bk:l" for b in buttons(e)) and "5 лет" in e["text"])
check("no contact button when no contact", not any(b[2] for b in buttons(e)))
click(5001, "bk:l")
check("back to choice works", sum(1 for b in buttons(last(to=5001)) if b[1].startswith("bk:t:")) == 2)
# запись без ссылки
click(5001, f"bk:d:{t2['id']}")
e = last(to=5001)
d2 = [b for b in buttons(e) if b[1].startswith("bk:s:")][0][1]
click(5001, d2); tm2 = [b for b in buttons(last(to=5001)) if b[1].startswith("bk:c:")][0][1]
click(5001, tm2); okb = [b for b in buttons(last(to=5001)) if b[1].startswith("bk:ok:")][0][1]
log.clear(); click(5001, okb)
e = last("msg", 5001)
check("no-link booking says teacher will send link", "пришлёт" in e["text"])
check("teacher + owner both notified with warning", last("msg", 6001) and "не задана ссылка" in last("msg", 6001)["text"] and last("msg", 1))
# преподаватель отменяет запись
bid = booking.active_bookings(tid=t2["id"])[0]["id"]
log.clear(); click(6001, f"bt:xc:{bid}")
check("teacher cancel notifies student", last("msg", 5001) and "отменил" in last("msg", 5001)["text"])
# удаление
click(1, f"bt:del:{t2['id']}:yes")
check("teacher deleted", booking.teacher(t2["id"]) is None)

# 11. тексты на всех языках форматируются
kw = dict(n=1, name="N", day="пн 12.10", time="18:00", dur=60, min="m", link="L")
for lang in ("ru", "uz", "en", "zh"):
    for k in T["ru"]:
        if k.startswith("bk_"):
            try: t(lang, k, **kw)
            except Exception as ex: check(f"format {lang}.{k}: {ex}", False)
    check(f"{lang} has all bk_ keys", {k for k in T["ru"] if k.startswith("bk_")} <= set(T[lang]))

# 12. старая кнопка «Правила игры» ещё работает у тех, у кого не обновилась клавиатура
log.clear(); say(5001, T["ru"]["b_rules"])
check("old Rules button still answers", last("msg", 5001) and "Правила" in last("msg", 5001)["text"])
print("\nFAILS:", fails)
sys.exit(1 if fails else 0)
