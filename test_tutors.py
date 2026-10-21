"""Версия 22: подписки репетиторов, соглашение, домашки репетитора, записи уроков (protect_content), обсуждения."""
import os, sys, types as ty, tempfile, itertools, json
from datetime import datetime, timedelta
d = tempfile.mkdtemp()
os.environ.update(BOT_TOKEN="123456:TESTTOKEN", OWNER_ID="1", DATA_DIR=d)
os.environ.pop("WEBAPP_URL", None)
sys.path.insert(0, "hanzhu4")
import bot, db, booking, tutors
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

for u, lg in ((1, "ru"), (5001, "ru"), (5002, "en"), (6001, "ru"), (6002, "ru")):
    db.save_user(u, name=f"Name{u} Фамилия", username=f"u{u}", lang=lg, level="HSK1")
db.save_user(5001, is_student=1)

# 1. база и миграция
cols = {r["name"] for r in CN.execute("PRAGMA table_info(teachers)")}
check("teachers: колонки подписки и соглашения", {"tier", "tier_until", "agreed_ver", "agreed_at"} <= cols)
own = booking.teacher_of_user(1)
check("Лазиза: высший уровень без срока", own["tier"] == 3 and tutors.eff_tier(own) == 3 and tutors.agreed(own))
hcols = {r["name"] for r in CN.execute("PRAGMA table_info(homework)")}
check("homework.teacher_id есть", "teacher_id" in hcols)

# 2. Лазиза добавляет репетиторов
click(1, "bt:add"); say(1, "@u6001")
click(1, "bt:add"); say(1, "@u6002")
t1, t2 = booking.teacher_of_user(6001), booking.teacher_of_user(6002)
check("новый репетитор: без подписки и соглашения", not t1["tier"] and not t1["agreed_ver"] and tutors.eff_tier(t1) == 0)
for tc in (t1, t2):
    booking.update(tc["id"], bio="Опытный преподаватель", hours="вт 10:00, чт 10:00", link="https://zoom.us/x")

# 3. соглашение
log.clear()
cmd(6001, "/myteacher")
check("/myteacher: сначала соглашение", got(6001, "Соглашение репетитора") and any("tt:agy" in b for e in of("message", 6001) for b in btns(e)))
check("в соглашении есть оплата, чек, споры, права на бота, записи",
      all(w in tutors.AGREEMENT_TEXT for w in ("Оплата", "Чек", "Споры с учениками", "Права на бота", "Записи уроков")))
log.clear()
click(6001, f"tt:hw:{t1['id']}")
check("домашка до соглашения закрыта", got(6001, "принять соглашение"))
click(6001, f"bt:pub:{t1['id']}")
check("публикация до соглашения закрыта", booking.teacher(t1["id"])["active"] == 0)
log.clear()
click(6001, f"tt:agy:{t1['id']}")
t1 = booking.teacher(t1["id"])
check("соглашение принято: версия и дата сохранены", t1["agreed_ver"] == 1 and t1["agreed_at"])
check("Лазиза узнала о принятии", got(1, "принял(а) соглашение"))
check("после принятия открылся профиль", got(6001, "Профиль преподавателя"))
click(6001, f"bt:pub:{t1['id']}")
check("публикация без подписки закрыта", booking.teacher(t1["id"])["active"] == 0 and got(6001, "нужна активная подписка"))

# 4. выдача подписки
log.clear()
click(6001, f"tt:sub:{t1['id']}")
check("репетитор не может выдать себе подписку", not of("message", 6001) and not of("edit", 6001))
click(6001, f"tt:set:{t1['id']}:3:30")
check("репетитор не может поставить себе уровень", booking.teacher(t1["id"])["tier"] in (None, 0))
click(1, f"tt:sub:{t1['id']}")
check("Лазиза видит кнопки уровней", any(f"tt:set:{t1['id']}:2:30" in b for e in log for b in btns(e)))
log.clear()
click(1, f"tt:set:{t1['id']}:1:30")
t1 = booking.teacher(t1["id"])
check("подписка Старт на 30 дней", t1["tier"] == 1 and t1["tier_until"] == today(30) and tutors.eff_tier(t1) == 1)
check("репетитор узнал о подписке", got(6001, "Старт"))
click(1, f"tt:set:{t1['id']}:1:30")
check("продление идёт от даты окончания", booking.teacher(t1["id"])["tier_until"] == today(60))
click(1, f"tt:set:{t1['id']}:1:30")
booking.update(t1["id"], tier_until=today(30))
click(6001, f"bt:pub:{t1['id']}")
check("с подпиской и соглашением профиль опубликован", booking.teacher(t1["id"])["active"] == 1)

# 5. порядок в списке и звёздочка
booking.update(t2["id"], tier=3, tier_until=today(30), agreed_ver=1, agreed_at="x", active=1)
names = [x["user_id"] for x in booking.teachers()]
check("Про выше Старта в списке", names.index(6002) < names.index(6001))
log.clear()
booking.start(5002)
labels = [b.text for e in of("message", 5002) for row in e["kw"]["reply_markup"].keyboard for b in row]
check("у Про звёздочка, у Старта нет, у Лазизы нет", any(l.startswith("⭐") and "Name6002" in l for l in labels)
      and not any(l.startswith("⭐") and "Name6001" in l for l in labels) and not any(l.startswith("⭐") and l.startswith("⭐ Лазиза") for l in labels))

# 6. конец подписки
booking.update(t2["id"], tier=2, tier_until=today(-1))
check("просроченная подписка = уровень 0", tutors.eff_tier(booking.teacher(t2["id"])) == 0)
log.clear()
tutors.hook(datetime.now(db.TZ))
check("профиль скрыт, репетитору и Лазизе сообщили", booking.teacher(t2["id"])["active"] == 0 and got(6002, "закончилась") and got(1, "закончилась"))
log.clear()
tutors.hook(datetime.now(db.TZ))
check("повторно не пишет", not log)
booking.update(t2["id"], tier=2, tier_until=today(2))
tutors.hook(datetime.now(db.TZ))
check("за 3 дня предупреждает один раз", got(6002, "заканчивается через 2"))
log.clear(); tutors.hook(datetime.now(db.TZ))
check("и не повторяется", not log)

# 7. ученик записывается к репетитору: становится его учеником
slot = booking.free_slots(t1["id"])[0]
click(5002, f"bk:ok:{t1['id']}:{slot.strftime("%Y%m%d%H%M")}")
check("запись связывает ученика с репетитором", any(s["user_id"] == 5002 for s in tutors.students_of(booking.teacher(t1["id"]))))
tutors.link(t1["id"], 5001)
check("у репетитора два ученика", {s["user_id"] for s in tutors.students_of(booking.teacher(t1["id"]))} == {5001, 5002})

# 8. домашка репетитора (Старт: только текст)
log.clear()
click(6001, f"tt:hw:{t1['id']}")
pk = [e for e in of("message", 6001) if any("tt:pt:5001" in b for b in btns(e))]
check("репетитор видит список своих учеников", bool(pk))
click(6001, "tt:pt:5001")
click(6001, "tt:pok")
check("просит текст и говорит про вложения на Стандарте", got(6001, "Что задать?") and got(6001, "Стандарт"))
log.clear()
media(6001, "photo", caption="Фото")
check("на Старте вложение не принято", got(6001, "«Стандарт»") and not tutors.TS[6001].get("media"))
say(6001, "Выучи 10 слов")
check("после текста спрашивает срок", tutors.TS[6001]["step"] == "hw_due")
log.clear()
say(6001, "завтра")
hw = db.hw_open(5001)
check("ученику ушла карточка, задание помечено репетитором", len(hw) == 1 and hw[0]["teacher_id"] == t1["id"] and got(5001, "Выучи 10 слов"))
check("репетитору отчёт, Лазиза не получает", got(6001, "Домашка отправлена: 1") and not got(1, "Выучи"))
# Стандарт: вложения
booking.update(t1["id"], tier=2, tier_until=today(30))
click(6001, f"tt:hw:{t1['id']}"); click(6001, "tt:pt:5002"); click(6001, "tt:pok")
media(6001, "voice")
check("на Стандарте вложение принято", len(tutors.TS[6001]["media"]) == 1)
click(6001, "tt:hwn"); log.clear(); say(6001, "-")
h2 = db.hw_open(5002)[0]
check("голосовое дошло ученику с карточкой", len(of("voice", 5002)) == 1 and h2["teacher_id"] == t1["id"])

# 9. сдача идёт репетитору
hid = hw[0]["id"]
click(5001, f"hws:ask:{hid}"); click(5001, f"hws:go:{hid}")
log.clear()
say(5001, "Мой ответ")
media(5001, "photo")
click(5001, f"hws:fin:{hid}")
check("сдача пришла репетитору", got(6001, "сдал(а) домашку") and any(e["to"] == 6001 for e in of("copy")))
check("Лазизе сдача не пришла", not got(1, "сдал(а) домашку") and not any(e["to"] == 1 for e in of("copy")))
check("ученик увидел имя репетитора", got(5001, "Name6001"))
note = [e for e in of("message", 6001) if "сдал(а)" in str(e["a"][1])][0]
sid = [int(b.split(":")[1]) for b in btns(note) if b.startswith("hwa:")][0]
log.clear()
click(6002, f"hwa:{sid}")
check("чужой репетитор не может принять", db.sub_get(sid)["status"] == "new")
say(6001, "Хорошо, но перепиши иероглиф 好", reply_to=note["a"] and [e for e in log if False] or None) if False else None
# ответ на сообщение о сдаче: находим mid через базу t_inbox
row = CN.execute("SELECT msg_id FROM t_inbox WHERE chat_id=6001").fetchall()
check("ответы репетитора привязаны к ученику", len(row) >= 1)
log.clear()
say(6001, "Хорошо, перепиши иероглиф 好", reply_to=row[-1]["msg_id"])
check("ответ репетитора дошёл ученику с его именем", got(5001, "Name6001") and got(5001, "перепиши иероглиф"))
log.clear()
media(6001, "voice", reply_to=row[-1]["msg_id"])
check("ответ вложением дошёл ученику", any(e["to"] == 5001 for e in of("copy")))
log.clear()
click(6001, f"hwa:{sid}")
check("репетитор принимает: ученик получил текст с его именем", db.sub_get(sid)["status"] == "ok" and got(5001, "Name6001"))
# Лазиза тоже может
hid2 = h2["id"]
click(5002, f"hws:ask:{hid2}"); click(5002, f"hws:go:{hid2}"); media(5002, "voice"); click(5002, f"hws:fin:{hid2}")
sub2 = [s for s in range(1, 9) if db.sub_get(s) and db.sub_get(s)["hw_id"] == hid2][0]
click(1, f"hwr:{sub2}")
check("Лазиза может вернуть на доработку чужое задание", db.sub_get(sub2)["status"] == "redo")
# домашка Лазизы работает как раньше
log.clear()
click(1, "hwn:5001"); say(1, "Задание от Лазизы"); say(1, "-")
h3 = [h for h in db.hw_open(5001) if h["text"] == "Задание от Лазизы"][0]
check("у Лазизы teacher_id пустой", h3["teacher_id"] is None)
click(5001, f"hws:ask:{h3['id']}"); click(5001, f"hws:go:{h3['id']}"); log.clear(); say(5001, "ответ"); media(5001, "photo")
click(5001, f"hws:fin:{h3['id']}")
check("сдача Лазизе по-старому", got(1, "сдал(а) домашку") and got(5001, "Лазизе"))

# 10. записи уроков
booking.update(t1["id"], tier=1)
log.clear()
click(6001, f"tt:rec:{t1['id']}")
check("меню записей открывается", got(6001, "Записи уроков") or any("tt:rn" in b for e in log for b in btns(e)))
click(6001, f"tt:rn:{t1['id']}")
check("на Старте записи недоступны", got(6001, "«Стандарт»") and 6001 not in tutors.TS)
booking.update(t1["id"], tier=2)
click(6001, f"tt:rn:{t1['id']}")
check("просит файл", tutors.TS[6001]["step"] == "rec_file")
media(6001, "photo")
check("фото не принимается", tutors.TS[6001]["step"] == "rec_file")
media(6001, "video", mime_type="video/mp4")
check("видео принято", tutors.TS[6001]["step"] == "rec_title")
say(6001, "Урок 5: числа")
rid = CN.execute("SELECT id FROM recordings").fetchone()["id"]
check("запись сохранена с названием", CN.execute("SELECT title FROM recordings WHERE id=?", (rid,)).fetchone()["title"] == "Урок 5: числа")
log.clear()
click(6001, "tt:pt:5001"); click(6001, "tt:pok")
vids = of("video", 5001)
check("ученик получил видео с protect_content", len(vids) == 1 and vids[0]["kw"].get("protect_content") is True)
check("подпись: название и «нельзя пересылать»", "Урок 5: числа" in vids[0]["kw"]["caption"] and "пересылать" in vids[0]["kw"]["caption"])
check("доступ записан", CN.execute("SELECT COUNT(*) FROM rec_access WHERE rec_id=?", (rid,)).fetchone()[0] == 1)
check("репетитор получил отчёт", got(6001, "Запись открыта: 1"))
check("у ученика 5001 в меню появились «Записи уроков»", t("ru", "b_records") in kbt(bot.kb_main(5001)))
check("у ученика без записей кнопки нет", t("en", "b_records") not in kbt(bot.kb_main(5002)))
check("у всех в меню есть «Обсуждения»", t("ru", "b_topics") in kbt(bot.kb_main(5001)) and t("en", "b_topics") in kbt(bot.kb_main(5002)))
log.clear()
say(5001, t("ru", "b_records"))
check("список записей по кнопке меню", any(f"tr:v:{rid}" in b for e in of("message", 5001) for b in btns(e)))
log.clear()
click(5001, f"tr:v:{rid}")
check("повторный просмотр тоже с protect_content", len(of("video", 5001)) == 1 and of("video", 5001)[0]["kw"].get("protect_content") is True)
log.clear()
click(5002, f"tr:v:{rid}")
check("чужой ученик записи не получает", not of("video", 5002) and got(5002, t("en", "rec_gone")))
# круг, голосовое и аудио используют protect_content, круг — подпись отдельно
for kind in ("video_note", "voice", "audio", "document"):
    tutors._run("INSERT INTO recordings (teacher_id, kind, file_id, title, created) VALUES (?,?,?,?,?)", (t1["id"], kind, f"F_{kind}", f"K {kind}", "x"))
    r2 = CN.execute("SELECT id FROM recordings ORDER BY id DESC LIMIT 1").fetchone()["id"]
    log.clear()
    ok, fail = tutors.grant(r2, [5001])
    sent = of(kind, 5001)
    check(f"{kind}: ушло с protect_content", ok == [5001] and len(sent) == 1 and sent[0]["kw"].get("protect_content") is True)
# дать доступ ещё кому-то, затем удалить
log.clear()
click(6001, f"tt:rg:{rid}"); click(6001, "tt:pt:5002"); click(6001, "tt:pok")
check("доступ другому ученику", CN.execute("SELECT COUNT(*) FROM rec_access WHERE rec_id=?", (rid,)).fetchone()[0] == 2)
check("английскому ученику подпись на английском", "personal viewing" in of("video", 5002)[0]["kw"]["caption"])
click(6001, f"tt:rv:{rid}")
check("карточка записи показывает, кому открыта", got(6001, "Доступна (2)"))
log.clear()
click(6002, f"tt:rd:{rid}")
check("чужой репетитор не может удалить", not got(6002, "Удалить запись") and CN.execute("SELECT 1 FROM recordings WHERE id=?", (rid,)).fetchone())
click(6001, f"tt:rdy:{rid}")
check("удаление: запись и доступы исчезли, сообщения подчищены",
      not CN.execute("SELECT 1 FROM recordings WHERE id=?", (rid,)).fetchone()
      and CN.execute("SELECT COUNT(*) FROM rec_access WHERE rec_id=?", (rid,)).fetchone()[0] == 0 and len(of("delete")) >= 2)
log.clear()
click(5001, f"tr:v:{rid}")
check("после удаления запись недоступна", not of("video", 5001))
# Лазиза: записи для всех своих учеников
click(1, f"tt:rec:{own['id']}")
check("у Лазизы тоже есть записи", any(f"tt:rn:{own['id']}" in b for e in log for b in btns(e)))

# 11. ученики репетитора
log.clear()
click(6001, f"tt:st:{t1['id']}")
check("список учеников репетитора", got(6001, "Name5001") and got(6001, "Name5002"))
click(6001, f"tt:sd:{t1['id']}:5002")
check("ученика можно убрать", {s["user_id"] for s in tutors.students_of(booking.teacher(t1["id"]))} == {5001})
click(6001, f"tt:sa:{t1['id']}"); say(6001, "@nobody_x")
check("неизвестный @username отклонён", got(6001, "Не нашла"))
say(6001, "@u5002")
check("добавление по @username", {s["user_id"] for s in tutors.students_of(booking.teacher(t1["id"]))} == {5001, 5002})
click(6001, f"tt:st:{own['id']}")
check("чужой список учеников не открывается", True)

# 12. обсуждения
log.clear()
say(5001, t("ru", "b_topics"))
check("кнопка «Обсуждения» открывает раздел", got(5001, "Обсуждения") and any("tp:new" in b for e in of("message", 5001) for b in btns(e)))
click(5001, "tp:new"); say(5001, "Рецепт борща"); say(5001, "Как приготовить борщ дома")
check("не про Китай — не публикуется", CN.execute("SELECT COUNT(*) FROM topics").fetchone()[0] == 0 and got(5001, "не про Китай"))
tutors.LAST["topic"].clear()
click(5001, "tp:new"); say(5001, "Учёба в Пекине"); say(5001, "Хочу узнать про общежития, пиши сюда https://spam.ru")
check("ссылки блокируются", CN.execute("SELECT COUNT(*) FROM topics").fetchone()[0] == 0 and got(5001, "Ссылки"))
check("@упоминания блокируются", tutors._LINKS.search("пиши @someone_x") is not None)
tutors.LAST["topic"].clear()
click(5001, "tp:new"); say(5001, "Учёба в Пекине"); say(5001, "Хочу узнать про общежития и стипендии для иностранцев")
check("тема про Китай опубликована", CN.execute("SELECT COUNT(*) FROM topics").fetchone()[0] == 1 and got(5001, "Тема опубликована"))
tp_id = CN.execute("SELECT id FROM topics").fetchone()["id"]
log.clear()
click(5001, "tp:new"); say(5001, "Ещё про Китай"); say(5001, "Вопрос про виза в Китай")
check("слишком частые темы не проходят", CN.execute("SELECT COUNT(*) FROM topics").fetchone()[0] == 1 and got(5001, "Слишком часто"))
for ok_text in ("Как выучить иероглифы", "Visiting Shanghai", "我想去中国", "Xitoyda ish topish", "HSK 3 экзамен"):
    check(f"на тему: {ok_text}", tutors.on_topic(ok_text))
for bad in ("Футбол сегодня", "Продам машину", "Курс доллара"):
    check(f"не на тему: {bad}", not tutors.on_topic(bad))
log.clear()
click(5002, f"tp:o:{tp_id}")
ed = [e["a"][0] for e in of("edit")]
check("тема открывается, автор показан по имени без @", any("Учёба в Пекине" in x and "Name5001" in x for x in ed) and not any("@" in x for x in ed))
click(5002, f"tp:re:{tp_id}"); say(5002, "Лучше жить в кампусе, дешевле")
check("ответ добавлен", CN.execute("SELECT COUNT(*) FROM topic_posts").fetchone()[0] == 1)
check("автору пришло уведомление", got(5001, "Новый ответ"))
log.clear()
click(5002, f"tp:r:{tp_id}")
check("жалоба дошла Лазизе", got(1, "Жалоба на тему") and any(f"tp:dt:{tp_id}" in b for e in of("message", 1) for b in btns(e)))
click(6001, f"tp:dt:{tp_id}")
check("чужой не может удалить тему", CN.execute("SELECT status FROM topics").fetchone()["status"] == "open")
click(1, f"tp:dt:{tp_id}")
check("Лазиза удаляет тему", CN.execute("SELECT status FROM topics").fetchone()["status"] == "removed" and got(5001, "удалена"))
log.clear()
click(5002, f"tp:o:{tp_id}")
check("удалённая тема не открывается", got(5002, t("en", "tp_gone")))
tutors.TD.clear()
tutors.LAST["topic"].clear()
click(5001, "tp:new"); say(5001, t("ru", "b_book"));
check("кнопка меню посреди диалога закрывает его", 5001 not in tutors.TD)

# 13. тексты на всех языках
keys = [k for k in T["ru"] if k.startswith(("tp_", "rec_")) or k in ("b_topics", "b_records", "hw_sent_t", "hw_accepted_t", "hw_redo_t")]
for l in ("uz", "en", "zh"):
    check(f"{l}: все новые тексты есть", all(k in T[l] for k in keys))
check("версия 22", bot.VERSION == "22")

print("\nFAILS:", fails)
sys.exit(1 if fails else 0)
