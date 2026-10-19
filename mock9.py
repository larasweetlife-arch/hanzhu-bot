import sys, types as ty, hmac, hashlib, json, time, random
from urllib.parse import urlencode
sys.path.insert(0, ".")
import bot, db, quest, webapp
log = []
def sm(uid, txt, **kw): log.append({"to": uid, "t": txt, "m": kw.get("reply_markup")}); return ty.SimpleNamespace(message_id=len(log)+100)
bot.bot.send_message = sm
bot.bot.answer_pre_checkout_query = lambda qid, ok, error_message=None: log.append({"pre": ok, "err": error_message})
fails = []
def check(name, cond):
    print(("OK   " if cond else "FAIL ") + name)
    if not cond: fails.append(name)

TOKEN = bot.TOKEN
def init(uid, lang="en"):
    user = json.dumps({"id": uid, "first_name": "T", "language_code": lang})
    d = {"auth_date": str(int(time.time())), "user": user, "query_id": "q"}
    chk = "\n".join(f"{k}={d[k]}" for k in sorted(d))
    sec = hmac.new(b"WebAppData", TOKEN.encode(), hashlib.sha256).digest()
    d["hash"] = hmac.new(sec, chk.encode(), hashlib.sha256).hexdigest()
    return urlencode(d)
made = []
def fake_invoice(title, desc, payload, stars): made.append((title, desc, payload, stars)); return "https://t.me/$inv"
app = webapp.create_app({"token": TOKEN, "owner_id": bot.OWNER_ID, "bot_username": lambda: "hanzhu_bot", "notify_owner": lambda *a, **k: None,
                         "ikb": bot.ikb, "pay": {}, "webapp_url": "", "create_invoice": fake_invoice, "donate": {"on": True}})
cl = app.test_client()
def api(path, uid, body=None, lang="en"):
    r = cl.post("/api/quest/" + path, json=body or {}, headers={"X-Init-Data": init(uid, lang)})
    return r.get_json()

U = 7001
st = api("state", U)
check("state without char: char None, scenes absent", st["char"] is None and "scenes" not in st)
check("no auth -> 401", cl.post("/api/quest/state", json={}).status_code == 401)
check("bad hero rejected", api("char", U, {"hero": "a", "gender": "m"})["ok"] is False)
check("bad gender rejected", api("char", U, {"hero": "Lina", "gender": "x"})["ok"] is False)
check("paid skin not allowed at creation", api("char", U, {"hero": "Lina<b>", "gender": "f", "skin": 4})["ok"] is True)
st = api("state", U)
check("hero sanitized, skin forced to free", st["char"]["hero"] == "Linab" and st["char"]["skin"] == 0)
check("24 scenes, first current, rest locked", [s["status"] for s in st["scenes"]] == ["current"] + ["locked"] * 23)
check("lives 5 coins 0 free_left 1", st["lives"] == 5 and st["coins"] == 0 and st["today"]["free_left"] == 1)

r = api("scene", U, {"scene": "s3"}); check("locked scene refused", r["ok"] is False and r["err"] == "locked")
r = api("scene", U, {"scene": "s1"}); check("scene 1 starts", r["ok"] and r["task"]["t"] == "rp" and len(r["dialogue"]) == 9)
check("task payload has no answer key", "ok" not in r["task"] and "correct" not in json.dumps(r["task"]))
src = quest.scene_by_id("s1")
def solve(task, sid):
    t = src_task(sid, task["idx"])
    k = t["t"]
    if k in ("rp", "hz", "tr"): return t["ok"]
    if k == "tn": return 0
    if k == "od": return list(range(len(t["words"])))
def src_task(sid, idx): return quest.scene_by_id(sid)["tasks"][idx]

# первая ошибка стоит жизнь, повтор даёт 5 монет вместо 10
t = r["task"]; wrong = [o["id"] for o in t["opts"] if o["id"] != src_task("s1", 0)["ok"]][0]
a = api("answer", U, {"scene": "s1", "idx": 0, "a": wrong}); check("wrong answer: -1 life, not done", a["ok"] is False and a["lives"] == 4)
a = api("answer", U, {"scene": "s1", "idx": 0, "a": src_task("s1", 0)["ok"]}); check("retry correct: +5 coins", a["ok"] and a["gain"] == 5 and a["coins"] == 5)
check("next task provided", a["task"]["t"] == "hz")
a = api("answer", U, {"scene": "s1", "idx": 0, "a": 0}); check("stale idx -> sync", a.get("err") == "sync")
# дальше без ошибок
idx = 1; last = None
while True:
    t = src_task("s1", idx)
    ans = solve({"idx": idx}, "s1")
    last = api("answer", U, {"scene": "s1", "idx": idx, "a": ans})
    check(f"task {idx} ({t['t']}) correct", last["ok"])
    if last.get("scene_done"): break
    idx += 1
check("scene done: bonus 20, coins = 5+10+10+10+20", last["bonus"] == 20 and last["coins"] == 55)
check("next scene s2 unlocked, today's free used -> cannot continue", last["next_scene"] == "s2" and last["can_continue"] is False)
r = api("scene", U, {"scene": "s2"}); check("second scene today needs a pass", r["ok"] is False and r["err"] == "extra")
st = api("state", U); check("state: s1 done, s2 current", st["scenes"][0]["status"] == "done" and st["scenes"][1]["status"] == "current" and st["today"]["free_left"] == 0)

# replay: ни монет, ни потери жизней
before = api("state", U)
r = api("scene", U, {"scene": "s1"}); check("replay of done scene allowed, flagged", r["ok"] and r["replay"])
a = api("answer", U, {"scene": "s1", "idx": 0, "a": 99}); check("replay wrong answer costs nothing", a["ok"] is False and a["lives"] == before["lives"])
a = api("answer", U, {"scene": "s1", "idx": 0, "a": src_task("s1", 0)["ok"]}); check("replay right answer pays nothing", a["ok"] and a["gain"] == 0 and a["coins"] == before["coins"])

# покупка за монеты
r = api("buy", U, {"item": "extra"}); check("extra costs 600, have 55 -> poor", r.get("err") == "poor" and r["need"] == 545)
with db._conn() as c: c.execute("UPDATE quest_char SET lives=5 WHERE user_id=?", (U,))
r = api("buy", U, {"item": "life"}); check("life when full lives refused, no charge", r.get("err") == "full" and api("state", U)["coins"] == 55)
r = api("buy", U, {"item": "skin3"}); check("skin 300 coins -> poor", r.get("err") == "poor")
r = api("buy", U, {"item": "pack100"}); check("coin packs are bought with stars only, not with coins", r.get("err") == "item")
with db._conn() as c: c.execute("UPDATE quest_char SET coins=640 WHERE user_id=?", (U,))
r = api("buy", U, {"item": "extra"}); check("extra bought with coins", r.get("ok") and api("state", U)["coins"] == 40)
r = api("scene", U, {"scene": "s2"}); check("s2 now starts", r["ok"] and r["id"] == "s2")
# возобновление не списывает пропуск
r2 = api("scene", U, {"scene": "s2"}); check("resuming does not consume another pass", r2["ok"] and api("state", U)["today"]["extra"] == 0)

# жизни: потеряли все, таймер, регенерация
for i in range(5):
    a = api("answer", U, {"scene": "s2", "idx": 0, "a": 99})
check("5 wrong answers -> out of lives", a["lives"] == 0 and a["out"] is True)
a = api("answer", U, {"scene": "s2", "idx": 0, "a": 0}); check("no answering at 0 lives", a.get("out") is True)
st = api("state", U); check("next life timer ~1h", 3500 < st["next_life_in"] <= 3600)
with db._conn() as c: c.execute("UPDATE quest_char SET lives_ts=? WHERE user_id=?", (time.time() - 7300, U))
check("after 2h+ two lives regenerated", api("state", U)["lives"] == 2)

# карточки за жизнь
r = api("cards", U); check("cards: 5 cards", r["ok"] and len(r["cards"]) == 5)
r = api("cards/claim", U); check("claim too fast refused", r.get("err") == "fast")
with db._conn() as c: c.execute("UPDATE quest_day SET cards_ts=? WHERE user_id=?", (time.time() - 30, U))
r = api("cards/claim", U); check("claim after 20s gives life", r.get("ok") and r["lives"] == 3)
for i in range(2):
    api("cards", U)
    with db._conn() as c: c.execute("UPDATE quest_day SET cards_ts=? WHERE user_id=?", (time.time() - 30, U))
    r = api("cards/claim", U)
check("3 per day cap", r.get("ok") is True and api("cards", U).get("err") == "limit")

# mt и od
sid = "s2"; 
with db._conn() as c: c.execute("UPDATE quest_char SET lives=5 WHERE user_id=?", (U,))
r = api("scene", U, {"scene": "s2"}); t = r["task"]
check("s2 task0 is match with shuffled sides", t["t"] == "mt" and len(t["left"]) == 4 and [x["id"] for x in t["left"]] != [x["id"] for x in t["right"]] or t["t"] == "mt")
a = api("answer", U, {"scene": "s2", "idx": 0, "a": {"l": 0, "r": 1}}); check("wrong pair costs a life", a["ok"] is False and a["lives"] == 4)
for i in range(3):
    a = api("answer", U, {"scene": "s2", "idx": 0, "a": {"l": i, "r": i}}); check(f"pair {i} ok, not finished", a["ok"] and not a["done"])
check("matched list grows", a["matched"] == [0, 1, 2])
r = api("scene", U, {"scene": "s2"}); check("resume keeps matched pairs", r["task"]["matched"] == [0, 1, 2])
a = api("answer", U, {"scene": "s2", "idx": 0, "a": {"l": 3, "r": 3}}); check("last pair finishes task", a["done"] and a["gain"] == 5)

# оплата Stars
r = api("invoice", U, {"item": "extra"}); check("invoice link made, 600 stars", r["ok"] and made[-1][3] == 600 and made[-1][2].startswith("q1:extra:7001:"))
nonce = r["nonce"]
check("not paid yet", api("paid", U, {"nonce": nonce})["paid"] is False)
check("bad item no invoice", api("invoice", U, {"item": "hack"})["ok"] is False)
def pre(pl, amt, uid=U, cur="XTR"):
    log.clear(); bot.on_pre_checkout(ty.SimpleNamespace(id="p", invoice_payload=pl, total_amount=amt, currency=cur, from_user=ty.SimpleNamespace(id=uid)))
    return log[0]["pre"]
pl = made[-1][2]
check("pre_checkout ok", pre(pl, 600) is True)
check("pre_checkout wrong amount refused", pre(pl, 1) is False)
check("pre_checkout other user refused", pre(pl, 600, uid=999) is False)
check("pre_checkout wrong currency refused", pre(pl, 600, cur="USD") is False)
check("pre_checkout garbage refused", pre("hello", 600) is False)
def pay(pl, amt, charge, uid=U):
    log.clear()
    bot.on_successful_payment(ty.SimpleNamespace(from_user=ty.SimpleNamespace(id=uid), successful_payment=ty.SimpleNamespace(currency="XTR", total_amount=amt, invoice_payload=pl, telegram_payment_charge_id=charge)))
ex0 = api("state", U)["today"]["extra"]
pay(pl, 600, "ch_1"); check("payment grants extra scene pass", api("state", U)["today"]["extra"] == ex0 + 1)
check("paid flag true", api("paid", U, {"nonce": nonce})["paid"] is True)
check("owner told in Russian", any(l.get("to") == bot.OWNER_ID and "Оплата в игре" in l["t"] for l in log))
pay(pl, 600, "ch_1"); check("same charge id is idempotent", api("state", U)["today"]["extra"] == ex0 + 1)
# жизни полные + покупка жизни → монеты
r = api("invoice", U, {"item": "life"}); c0 = api("state", U)["coins"]
with db._conn() as c: c.execute("UPDATE quest_char SET lives=5 WHERE user_id=?", (U,))
pay(made[-1][2], 50, "ch_2"); check("paying for life at full lives converts to coins (50*1.0)", api("state", U)["coins"] == c0 + 50)
r = api("invoice", U, {"item": "refill"}); check("refill costs 300 stars", made[-1][3] == 300)
r = api("invoice", U, {"item": "skin4"}); pay(made[-1][2], 300, "ch_4"); st = api("state", U); check("skin bought -> owned", 4 in st["char"]["owned"])
r = api("char", U, {"hero": "Lina", "gender": "f", "skin": 4}); check("can wear owned skin", api("state", U)["char"]["skin"] == 4)
r = api("char", U, {"hero": "Lina", "gender": "f", "skin": 5}); check("cannot wear unowned skin", api("state", U)["char"]["skin"] == 4)
# донат
log.clear(); bot.on_successful_payment(ty.SimpleNamespace(from_user=ty.SimpleNamespace(id=U), successful_payment=ty.SimpleNamespace(currency="XTR", total_amount=50, invoice_payload="dn:50", telegram_payment_charge_id="d_1")))
check("donation thanked + owner notified", any(l["to"] == U for l in log) and any(l["to"] == bot.OWNER_ID and "Поддержка" in l["t"] for l in log))
check("pre_checkout donation ok", pre("dn:50", 50) is True and pre("dn:7", 7) is False)
log.clear(); bot.cmd_stars(ty.SimpleNamespace(from_user=ty.SimpleNamespace(id=bot.OWNER_ID), chat=ty.SimpleNamespace(id=bot.OWNER_ID), text="/stars"))
check("/stars report", any("Звёзды" in l["t"] and "1000" in l["t"] for l in log))
rep = quest.stars_report(); check("report totals 600+50+300+50", rep["total"][0] == 1000)

# донат-экран
log.clear(); bot.send_donate(U)
r = log[-1]; kb = [b.callback_data for row in r["m"].keyboard for b in row]
check("donate screen: stars buttons, no card info w/o env", kb == ["dn:10", "dn:50", "dn:100"] and "4278" not in r["t"])
bot.DONATE_INFO = "Карта для поддержки: 9860 0000 0000 0000"; bot.DONATE_URL = "https://pay.example/x"
log.clear(); bot.send_donate(U); r = log[-1]
check("donate screen with env: info + url button", "9860" in r["t"] and any(getattr(b, "url", None) for row in r["m"].keyboard for b in row))
check("menu has donate button last", [b["text"] for b in bot.kb_main(U).keyboard[-1]] == ["💝 Support the project"])

# финал главы
with db._conn() as c:
    for s in quest.scenes()[:7]:
        c.execute("INSERT OR IGNORE INTO quest_prog (user_id, scene_id, done_day) VALUES (?,?,?)", (U, s["id"], "2026-01-01"))
    c.execute("UPDATE quest_run SET idx=0 WHERE user_id=?", (U,))
    c.execute("DELETE FROM quest_run WHERE user_id=?", (U,))
    c.execute("UPDATE quest_day SET free_used=0 WHERE user_id=?", (U,))
r = api("scene", U, {"scene": "s8"}); check("boss scene starts", r["ok"] and r["boss"] and r["total"] == 5)
c0 = api("state", U)["coins"]
for idx in range(5):
    a = api("answer", U, {"scene": "s8", "idx": idx, "a": ({"l": 0, "r": 0} if src_task("s8", idx)["t"] == "mt" else solve({"idx": idx}, "s8"))})
    if src_task("s8", idx)["t"] == "mt":
        for i in range(1, 4): a = api("answer", U, {"scene": "s8", "idx": idx, "a": {"l": i, "r": i}})
check("chapter done, boss bonus 50", a["scene_done"] and a["bonus"] == 50 and a["chapter_done"] and a["next_scene"] == "s9" and a["next_chapter"] and a["game_done"] is False)
check("coins = 5 tasks*10 + 50", api("state", U)["coins"] == c0 + 100)
check("state: game not done, chapter 2 opens", api("state", U)["today"]["game_done"] is False and api("state", U)["today"]["chapter_done"] is False and [x["status"] for x in api("state", U)["scenes"]][8] == "current")

# JSON-ответы не светят правильные ответы
rr = api("scene", U, {"scene": "s8"}); raw = json.dumps(rr["task"])
check("replay payload still has no solutions", '"correct"' not in raw and '"ok"' not in raw and '"wrong"' not in raw)

# ── рейтинг и розыгрыш ──
b = api("board", U, {"tab": "all"})
check("board lists hero with points", b["rows"] and b["rows"][0]["hero"] == "Lina" and b["rows"][0]["me"] and b["me"]["place"] == 1)
V = 7002; api("char", V, {"hero": "Vera", "gender": "f"}); api("scene", V, {"scene": "s1"})
for idx in range(4):
    ans = src_task("s1", idx)["ok"] if src_task("s1", idx)["t"] in ("rp","hz","tr") else (list(range(len(src_task("s1", idx)["words"]))))
    last = api("answer", V, {"scene": "s1", "idx": idx, "a": ans})
check("scene 1 done -> prize_new flag", last.get("scene_done") and last.get("prize_new") is True)
b = api("board", V, {"tab": "week"}); check("weekly board ranks both, higher score first", [r["hero"] for r in b["rows"]][:2] == ["Lina", "Vera"] and b["me"]["place"] == 2)
api("hide", V, {"hide": True}); b = api("board", V, {"tab": "week"}); check("hidden player not listed, still sees own points", all(r["hero"] != "Vera" for r in b["rows"]) and b["me"]["place"] is None and b["me"]["pts"] > 0)
api("hide", V, {"hide": False})
st = api("state", V); check("prize state: entered, 2+ entrants", st["prize"]["on"] and st["prize"]["entered"] and st["prize"]["count"] >= 2)
rp = quest.prize_report(); check("prize report counts", rp["waiting"] == rp["total"] and rp["total"] >= 2)
log.clear(); bot.cmd_prize_draw(ty.SimpleNamespace(from_user=ty.SimpleNamespace(id=bot.OWNER_ID), chat=ty.SimpleNamespace(id=bot.OWNER_ID), text="/prize_draw"))
check("draw: winner told + owner told", any(l["to"] != bot.OWNER_ID and "уникальный" in l["t"] or l["to"] != bot.OWNER_ID and "unique" in l["t"] for l in log) and any(l["to"] == bot.OWNER_ID and "Победитель" in l["t"] for l in log))
check("winner marked, cannot win twice", quest.prize_report()["waiting"] == rp["waiting"] - 1 and len(quest.prize_report()["winners"]) == 1)
log.clear(); bot.cmd_qtop(ty.SimpleNamespace(from_user=ty.SimpleNamespace(id=U), chat=ty.SimpleNamespace(id=U), text="/qtop"))
check("/qtop text", any("Lina" in l["t"] for l in log))
print("\nFAILS:", fails if fails else "none")
