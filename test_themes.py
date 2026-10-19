import os, sys, tempfile, time, hmac, hashlib, json
from urllib.parse import urlencode
from datetime import date, timedelta, datetime
d = tempfile.mkdtemp()
os.environ.update(BOT_TOKEN="123456:TESTTOKEN", OWNER_ID="1", DATA_DIR=d)
sys.path.insert(0, "hanzhu4")
import bot, db, quest, themes, webapp, practice
fails = []
def check(n, c, extra=None):
    print(("OK   " if c else "FAIL ") + n + ("" if c or extra is None else "  -> " + str(extra)))
    if not c: fails.append(n)
sent = []
bot.bot.send_message = lambda to, text, **kw: sent.append((to, text)) or type("M", (), {"message_id": 1})()
def init(uid, lang="ru"):
    user = json.dumps({"id": uid, "first_name": "T", "language_code": lang})
    dd = {"auth_date": str(int(time.time())), "user": user, "query_id": "q"}
    chk = "\n".join(f"{k}={dd[k]}" for k in sorted(dd))
    sec = hmac.new(b"WebAppData", bot.TOKEN.encode(), hashlib.sha256).digest()
    dd["hash"] = hmac.new(sec, chk.encode(), hashlib.sha256).hexdigest()
    return urlencode(dd)
made = []
app = webapp.create_app({"token": bot.TOKEN, "owner_id": 1, "bot_username": lambda: "x", "notify_owner": lambda *a, **k: None,
                         "ikb": bot.ikb, "pay": {}, "webapp_url": "", "create_invoice": lambda t_, d_, p, s: made.append((t_, d_, p, s)) or "https://t.me/$inv", "donate": {"on": True}})
cl = app.test_client()
def api(path, uid, body=None, lang="ru"):
    return cl.post(path, json=body or {}, headers={"X-Init-Data": init(uid, lang)}).get_json()
def mk(uid, name, lang="ru", pts=0, coins=0, day=None):
    db.save_user(uid, name=name, username=f"u{uid}", lang=lang, level="HSK1")
    quest.char_save(uid, name, "f", 0, 0, 0)
    with db._conn() as c:
        c.execute("UPDATE quest_char SET coins=? WHERE user_id=?", (coins, uid))
        if pts: c.execute("INSERT OR REPLACE INTO quest_score (user_id, day, pts) VALUES (?,?,?)", (uid, day or db.today(), pts))
# ── каталог
check("12 weekly + 6 shop themes", len(themes.WEEKLY) == 12 and len(themes.SHOP) == 6)
check("all themes have 4 names + required vars", all(set(x["name"]) == {"ru","uz","en","zh"} and {"bg","card","ink","jade","onjade","line"} <= set(x["vars"]) for x in themes.CATALOG))
# разные оформления у соседних недель и у двух рейтингов
mon = date(2026, 10, 5)
ids = [themes.weekly_theme_id(mon + timedelta(days=7 * i), "word") for i in range(30)]
check("consecutive weeks never repeat (word)", all(ids[i] != ids[i + 1] for i in range(29)))
check("12 weeks in a row are all different", len(set(ids[:12])) == 12)
check("word and quest differ in the same week", all(themes.weekly_theme_id(mon + timedelta(days=7 * i), "word") != themes.weekly_theme_id(mon + timedelta(days=7 * i), "quest") for i in range(30)))
# ── итоги недели
prev = date.today() - timedelta(days=date.today().weekday() + 7)
pstart, pend = practice.week_bounds(prev)
W, Q = 5001, 5002
mk(W, "Wina"); mk(Q, "Qina", pts=0)
with db._conn() as c:
    c.execute("INSERT OR REPLACE INTO quest_score (user_id, day, pts) VALUES (?,?,?)", (Q, pstart, 150))
db.nick_set(W, "WinNick"); db.board_set(W, True)

with db._conn() as c:
    c.execute("INSERT OR REPLACE INTO tea_score (user_id, day, points, correct, wrong, last_at) VALUES (?,?,?,?,?,?)", (W, pstart, 50, 40, 5, "x"))
nowmon = datetime.combine(prev + timedelta(days=7), datetime.min.time(), tzinfo=db.TZ).replace(hour=10)
sent.clear()
bot.board_hook(nowmon)
check("word winner got weekly theme", themes.equipped(W) == themes.weekly_theme_id(prev, "word"))
check("quest winner got weekly theme (different)", themes.equipped(Q) == themes.weekly_theme_id(prev, "quest") and themes.equipped(Q) != themes.equipped(W))
msgs = {}
for to, tx in sent: msgs[to] = msgs.get(to, "") + "\n" + tx
check("winners notified", W in msgs and "оформлени" in msgs[W].lower() and Q in msgs and "оформлени" in msgs[Q].lower())
check("owner summary sent", 1 in msgs and "Итоги недели" in msgs[1])
check("no author-lesson reward note", "Авторский урок" not in " ".join(tx for _, tx in sent))
exp = themes.owned(W)[themes.equipped(W)]["expires"]
check("expires on Sunday of current week", date.fromisoformat(exp) == prev + timedelta(days=13) and date.fromisoformat(exp).weekday() == 6)
check("wins counted", themes.wins(W) == {"word": 1, "quest": 0, "total": 1} and themes.wins(Q)["quest"] == 1)
sent.clear(); bot.board_hook(nowmon)
check("second call does nothing (idempotent)", not sent and themes.wins(W)["total"] == 1)
# повторная победа в следующую неделю: другое оформление, старое ещё действует до воскресенья
nxt = prev + timedelta(days=7)
with db._conn() as c:
    c.execute("INSERT OR REPLACE INTO tea_score (user_id, day, points, correct, wrong, last_at) VALUES (?,?,?,?,?,?)", (W, nxt.isoformat(), 55, 40, 5, "x"))
bot.board_hook(datetime.combine(nxt + timedelta(days=7), datetime.min.time(), tzinfo=db.TZ).replace(hour=10))
t1, t2 = themes.weekly_theme_id(prev, "word"), themes.weekly_theme_id(nxt, "word")
check("back-to-back wins give different themes", t1 != t2 and themes.wins(W)["word"] == 2)
# просрочка: сегодня в воскресенье ещё действует, в понедельник нет
th = themes.weekly_theme_id(prev, "quest")
import unittest.mock as um
class FakeDB: pass
real_today = db.today
db.today = lambda: (prev + timedelta(days=13)).isoformat()
check("valid on last Sunday", themes.has(Q, th))
db.today = lambda: (prev + timedelta(days=14)).isoformat()
check("expired on Monday", not themes.has(Q, th) and themes.equipped(Q) is None)
db.today = real_today
# ── API
mk(6001, "Buyer", coins=400)
r = api("/api/themes", 6001)
check("themes api: catalog, no owned, packs, coins", len(r["catalog"]) == 18 and r["owned"] == {} and len(r["packs"]) == 3 and r["coins"] == 400 and r["has_hero"])
r = api("/api/themes/equip", 6001, {"id": "matcha"}); check("cannot equip unowned theme", r["ok"] is False)
r = api("/api/quest/buy", 6001, {"item": "theme_matcha"}); check("buy rare theme with coins (300)", r.get("ok") and themes.has(6001, "matcha"))
check("coins deducted", quest.char_get(6001)["coins"] == 100)
r = api("/api/quest/buy", 6001, {"item": "theme_matcha"}); check("buy twice refused", r.get("err") == "owned")
r = api("/api/quest/buy", 6001, {"item": "theme_dragongate"}); check("too poor for legendary", r.get("err") == "poor")
r = api("/api/quest/buy", 6001, {"item": "pack100"}); check("coin pack cannot be bought with coins", r.get("err") == "item")
r = api("/api/quest/buy", 6001, {"item": "theme_sakura"}); check("weekly themes are not for sale", r.get("err") == "item")
r = api("/api/themes/equip", 6001, {"id": "matcha"}); check("equip owned", r["ok"] and r["equipped"] == "matcha")
r = api("/api/themes/equip", 6001, {"id": None}); check("unequip", r["ok"] and r["equipped"] is None)
# звёзды: счёт и выдача
r = api("/api/quest/invoice", 6001, {"item": "theme_dragongate"})
check("invoice for theme 980 stars", r.get("ok") and made[-1][3] == 980 and "Врата дракона" in made[-1][0], r)
payload = made[-1][2]
parsed = quest.parse_payload(payload)
check("payload parses (underscore id)", parsed and parsed[0] == "theme_dragongate")
res = quest.grant_stars(6001, parsed[0], 980, "ch1", parsed[2]); check("stars grant theme", res == "theme" and themes.has(6001, "dragongate"))
check("duplicate charge ignored", quest.grant_stars(6001, parsed[0], 980, "ch1", parsed[2]) == "dup")
r = api("/api/quest/invoice", 6001, {"item": "pack270"}); check("invoice for coin pack 250 stars", r.get("ok") and made[-1][3] == 250)
before = quest.char_get(6001)["coins"]
res = quest.grant_stars(6001, "pack270", 250, "ch2", "abcd1234"); check("coin pack adds 270 coins", res == "coins" and quest.char_get(6001)["coins"] == before + 270, res)
with db._conn() as c:
    pts_before = c.execute("SELECT COALESCE(SUM(pts),0) FROM quest_score WHERE user_id=6001").fetchone()[0]
check("bought coins do not count for rating", pts_before == 0)
res = quest.grant_stars(6001, "theme_dragongate", 980, "ch3", "zzzz1234"); check("paid for already owned theme -> refunded in coins", res == "coins")
# ── карточки игроков
rb = api("/api/quest/board", 5002, {"tab": "all"})
row = rb["rows"][0]
check("quest board rows carry ref+theme", row.get("ref") and "theme" in row and "uid" not in row)
pp = api("/api/profile/public", 6001, {"ref": row["ref"], "kind": "quest"})
check("public profile (quest): hero, wins, theme, no coins/uid", pp["ok"] and pp["name"] == "Qina" and pp["wins"]["quest"] == 1 and "coins" not in json.dumps(pp) and "user_id" not in json.dumps(pp))
check("public profile has points", pp["week"] >= 0 and pp["total"] >= 150)
pp2 = api("/api/profile/public", 6001, {"ref": "deadbeef0000", "kind": "quest"}); check("unknown ref refused", pp2["ok"] is False)
api("/api/quest/hide", 5002, {"hide": True})
pp3 = api("/api/profile/public", 6001, {"ref": row["ref"], "kind": "quest"}); check("hidden player has no public card", pp3["ok"] is False)
api("/api/quest/hide", 5002, {"hide": False})
bw = api("/api/board", 6001, {"tab": "week"})
check("word board rows carry ref+theme", bw["rows"] and bw["rows"][0].get("ref") is not None)
ww = api("/api/profile/public", 6001, {"ref": themes.ref(W), "kind": "word"})
check("public profile (word) for joined player", ww["ok"] and ww["name"] == "WinNick" and ww["wins"]["word"] == 2 and "emoji" in ww, ww)
nj = api("/api/profile/public", 6001, {"ref": themes.ref(6001), "kind": "word"}); check("word card refused for non-participants", nj["ok"] is False)
own = api("/api/profile/public", 1, {"ref": themes.ref(1), "kind": "quest"}); check("owner card never shown", own["ok"] is False)
# ── /stars labels
check("rules mention theme prize, no lesson prize", "оформление профиля" in bot.t("ru", "rules", lives=1, cap=1, min=1) and "авторский урок" not in bot.t("ru", "rules", lives=1, cap=1, min=1))
for l in ("uz", "en", "zh"):
    r_ = bot.t(l, "rules", lives=1, cap=1, min=1)
    check(f"rules[{l}] formats", "{" not in r_)
print("FAILS:", fails); sys.exit(1 if fails else 0)
