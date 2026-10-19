import os, sys, tempfile, json, time, hmac, hashlib
from urllib.parse import urlencode
from datetime import date, timedelta
d = tempfile.mkdtemp()
os.environ.update(BOT_TOKEN="123456:TESTTOKEN", OWNER_ID="1", DATA_DIR=d)
sys.path.insert(0, "hanzhu4")
import bot, db, quest, themes, webapp
fails = []
def check(n, c, extra=None):
    print(("OK   " if c else "FAIL ") + n + ("" if c or extra is None else "  -> " + str(extra)))
    if not c: fails.append(n)
def mk(uid):
    db.save_user(uid, name=f"U{uid}", username=f"u{uid}", lang="ru", level="HSK1")
    quest.char_save(uid, f"H{uid}", "f", 0, 0, 0)
quest.load_chapters()
ids = [s["id"] for s in quest._CACHE["scenes"]]
mk(1001)
b = quest.journey_badges(1001)
check("14 journey badges, fresh player has none", len(b) == 14 and not any(b.values()) and set(b) == set(quest.JOURNEY_BADGES), b)
today = date.today()
with db._conn() as c:
    for i, sid in enumerate(ids[:4]):
        c.execute("INSERT INTO quest_prog (user_id, scene_id, done_day, mistakes) VALUES (?,?,?,?)", (1001, sid, (today - timedelta(days=3 - i)).isoformat(), 0 if i < 2 else 1))
        c.execute("INSERT OR REPLACE INTO quest_score (user_id, day, pts) VALUES (?,?,?)", (1001, (today - timedelta(days=3 - i)).isoformat(), 90))
b = quest.journey_badges(1001)
check("first, half, perfect, streak3, coins earned", b["j_first"] and b["j_half"] and b["j_perfect"] and b["j_streak3"] and b["j_coins"], b)
check("not yet: chapter, streak7, wardrobe, theme, friend, winner", not (b["j_chapter"] or b["j_streak7"] or b["j_wardrobe"] or b["j_theme"] or b["j_friend"] or b["j_winner"]), b)
with db._conn() as c:
    for sid in ids[4:]:
        c.execute("INSERT INTO quest_prog (user_id, scene_id, done_day, mistakes) VALUES (?,?,?,0)", (1001, sid, today.isoformat()))
    c.execute("UPDATE quest_char SET owned='[0,1,2,3]' WHERE user_id=1001")
themes.grant(1001, "matcha", "buy")
b = quest.journey_badges(1001, friends=1, wins=1)
check("chapter, wardrobe, theme, friend, winner", b["j_chapter"] and b["j_wardrobe"] and b["j_theme"] and b["j_friend"] and b["j_winner"], b)
# через API профиля
user = json.dumps({"id": 1001, "first_name": "T", "language_code": "ru"})
dd = {"auth_date": str(int(time.time())), "user": user, "query_id": "q"}
chk = "\n".join(f"{k}={dd[k]}" for k in sorted(dd))
dd["hash"] = hmac.new(hmac.new(b"WebAppData", bot.TOKEN.encode(), hashlib.sha256).digest(), chk.encode(), hashlib.sha256).hexdigest()
app = webapp.create_app({"token": bot.TOKEN, "owner_id": 1, "bot_username": lambda: "x", "notify_owner": lambda *a, **k: None, "ikb": bot.ikb, "pay": {}, "webapp_url": "", "create_invoice": lambda *a: "x", "donate": {"on": True}})
r = app.test_client().post("/api/me", json={}, headers={"X-Init-Data": urlencode(dd)}).get_json()
check("/api/me returns journey badges", r and set(r["badges"]) == set(quest.JOURNEY_BADGES) and r["badges"]["j_chapter"], list((r or {}).get("badges", {}))[:3])
js = open("hanzhu4/webapp_static/i18n.js", encoding="utf-8").read()
check("all badge texts exist in 4 languages", all(js.count("b_" + k + ":") == 4 for k in quest.JOURNEY_BADGES))
app_js = open("hanzhu4/webapp_static/app.js", encoding="utf-8").read()
check("all badge icons exist", all((k + ":") in app_js for k in quest.JOURNEY_BADGES))
print("FAILS:", fails); sys.exit(1 if fails else 0)
