"""Проверка трёх глав игры: целостность данных, арт для каждой сцены, переход между главами, финал игры.
Запуск из папки hanzhu4:  BOT_TOKEN=1:x OWNER_ID=1 DATA_DIR=$(mktemp -d) python3 ../test_chapters.py"""
import sys, json, re, time, hmac, hashlib, types as ty
from urllib.parse import urlencode
from datetime import date
sys.path.insert(0, ".")
import bot, db, quest, webapp

fails = []
def check(name, cond, extra=None):
    print(("OK   " if cond else "FAIL ") + name + ("" if cond or extra is None else "  -> " + str(extra)))
    if not cond: fails.append(name)

quest.load_chapters()
chs = quest._CACHE["ch"]
scenes = quest._CACHE["scenes"]
ids = [s["id"] for s in scenes]
check("3 chapters, 24 scenes, ids s1..s24 in order", len(chs) == 3 and ids == [f"s{i}" for i in range(1, 25)], ids)
check("8 scenes per chapter", all(len(c["scenes"]) == 8 for c in chs))
check("boss = last scene of each chapter", [s["id"] for s in scenes if s["boss"]] == ["s8", "s16", "s24"])

LANGS = ("ru", "uz", "en")
def tr_ok(d): return isinstance(d, dict) and all(isinstance(d.get(l), str) and d[l].strip() for l in LANGS)
def toks_ok(toks, where):
    bad = []
    for t in toks:
        if "h" in t and not (t["h"] and t.get("p")): bad.append((where, t))
        if not any(k in t for k in ("h", "x", "name")): bad.append((where, t))
    return bad

bad_tok, bad_tr, bad_cast, bad_cnt, bad_name = [], [], [], [], []
for c in chs:
    cast = c["cast"] if "cast" in c else {}
for s in scenes:
    sid = s["id"]
    for k in ("title_tr", "bg_tr", "obstacle", "culture"):
        if not tr_ok(s[k]): bad_tr.append((sid, k))
    for i, d in enumerate(s["dialogue"]):
        bad_tok += toks_ok(d["zh"], (sid, "dlg", i))
        if not tr_ok(d["tr"]): bad_tr.append((sid, "dlg", i))
    n_od = n_tr = 0
    for i, t in enumerate(s["tasks"]):
        k = t["t"]
        if k == "rp":
            bad_tok += toks_ok(t["npc"], (sid, i))
            for o in t["opts"]: bad_tok += toks_ok(o, (sid, i))
            if not (isinstance(t["ok"], int) and 0 <= t["ok"] < len(t["opts"])): bad_cnt.append((sid, i, "rp ok index"))
        elif k == "tn":
            if not (t["h"] and isinstance(t["correct"], str) and t["wrong"] and t["correct"] not in t["wrong"]): bad_cnt.append((sid, i, "tn"))
        elif k == "od":
            n_od += 1
            bad_tok += toks_ok(t["words"], (sid, i))
            if not tr_ok(t["hint"]): bad_tr.append((sid, i, "od hint"))
        elif k == "tr":
            n_tr += 1
            bad_tok += toks_ok(t["zh"], (sid, i))
            if not (isinstance(t["ok"], int) and 0 <= t["ok"] < len(t["opts_tr"])): bad_cnt.append((sid, i, "tr ok index"))
            if not all(tr_ok(o) for o in t["opts_tr"]): bad_tr.append((sid, i, "tr opts"))
        elif k == "mt":
            if len(t["pairs"]) < 3: bad_cnt.append((sid, i, "mt pairs"))
    if not 4 <= len(s["tasks"]) <= 6: bad_cnt.append((sid, "tasks", len(s["tasks"])))
    blob = json.dumps(s, ensure_ascii=False)
    if "Чача" in blob or "Chacha" in blob: bad_name.append(sid)
check("every pinyin syllable present on every hanzi token", not bad_tok, bad_tok[:3])
check("ru/uz/en text complete everywhere", not bad_tr, bad_tr[:5])
check("task shapes valid, 4-6 tasks per scene", not bad_cnt, bad_cnt[:5])
check("mascot always 茶茶 in hieroglyphs", not bad_name, bad_name)
check("no feminine forms for the mascot in ru", not any(re.search(r"茶茶[^.]{0,40}(устала|рада|сказала|ответила)|(устала|рада|сказала|ответила)[^.]{0,20}茶茶", json.dumps(s, ensure_ascii=False)) for s in scenes))

# все говорящие есть в cast сцены, у каждого есть внешность в quest_art.js
art = open("webapp_static/quest_art.js", encoding="utf-8").read()
npc_block = art[art.index("const NPC = {"): art.index("const BOY_STYLES")]
npc = set(re.findall(r"^\s+(\w+):\s+\{", npc_block, re.M))
missing = set(); notcast = []
for s in scenes:
    for who in {d["who"] for d in s["dialogue"]} | {t["who"] for t in s["tasks"] if t["t"] == "rp"}:
        if who != "me" and who not in s["cast"]: notcast.append((s["id"], who))
        if who not in npc and who not in ("me", "cc"): missing.add(who)
    for who in s["cast"]:
        if who not in npc and who not in ("me", "cc"): missing.add(who)
check("every speaker is in the scene cast", not notcast, notcast[:5])
check("every NPC has a look in quest_art.js", not missing, missing)

# у каждой сцены есть палитра, препятствия, ориентир, определена тема цвета
w1 = open("webapp_static/quest_world.js", encoding="utf-8").read()
w2 = open("webapp_static/quest_world2.js", encoding="utf-8").read()
w3 = open("webapp_static/quest_world3.js", encoding="utf-8").read()
css = open("webapp_static/quest_game.css", encoding="utf-8").read()
qjs = open("webapp_static/quest.js", encoding="utf-8").read()
pal_ids = set(re.findall(r"^\s+(s\d+): \{ theme:", w1 + w2, re.M))
kinds = set(re.findall(r"\b(s\d+): \[\"", w1 + w2))
marks = set(re.findall(r"case \"(s\d+)\": return", w1)) | set(re.findall(r"L\.(s\d+) =", w3))
check("palette for each of the 24 scenes", pal_ids == set(ids), set(ids) ^ pal_ids)
check("obstacle kinds for each scene", set(ids) <= kinds, set(ids) - kinds)
check("landmark for each scene", set(ids) <= marks, set(ids) - marks)
themes = set(re.findall(r"theme: \"(\w+)\"(?!, indoor)", w1 + w2))
check("colour grade css for each theme", all((f"g-{t}" in css) for t in themes), [t for t in themes if f"g-{t}" not in css])
check("falling-leaf colours for each theme", all((f" {t}: [" in qjs or f"{t}: [\"" in qjs) for t in themes), [t for t in themes if f"{t}: [\"" not in qjs])
check("new art files are served and listed", "quest_world2.js" in open("webapp.py", encoding="utf-8").read() and "quest_world3.js" in open("webapp_static/index.html", encoding="utf-8").read())

# ── прохождение: из первой главы во вторую и в третью, финал игры ──
TOKEN = bot.TOKEN
def init(uid, lang="ru"):
    user = json.dumps({"id": uid, "first_name": "T", "language_code": lang})
    d = {"auth_date": str(int(time.time())), "user": user, "query_id": "q"}
    chk = "\n".join(f"{k}={d[k]}" for k in sorted(d))
    d["hash"] = hmac.new(hmac.new(b"WebAppData", TOKEN.encode(), hashlib.sha256).digest(), chk.encode(), hashlib.sha256).hexdigest()
    return urlencode(d)
app = webapp.create_app({"token": TOKEN, "owner_id": 1, "bot_username": lambda: "x", "notify_owner": lambda *a, **k: None, "ikb": bot.ikb,
                         "pay": {}, "webapp_url": "", "create_invoice": lambda *a: "x", "donate": {"on": True}})
cl = app.test_client()
def api(path, uid, body=None):
    return cl.post("/api/quest/" + path, json=body or {}, headers={"X-Init-Data": init(uid)}).get_json()
def task(sid, idx): return quest.scene_by_id(sid)["tasks"][idx]
def play(uid, sid):
    r = api("scene", uid, {"scene": sid}); assert r["ok"], r
    last = None
    for idx in range(r["total"]):
        t = task(sid, idx); k = t["t"]
        if k in ("rp", "hz", "tr"): a = t["ok"]
        elif k == "tn": a = 0
        elif k == "od": a = list(range(len(t["words"])))
        if k == "mt":
            n = len(t["pairs"])
            last = api("answer", uid, {"scene": sid, "idx": idx, "a": {"l": 0, "r": 0}})
            for i in range(1, n): last = api("answer", uid, {"scene": sid, "idx": idx, "a": {"l": i, "r": i}})
        else:
            last = api("answer", uid, {"scene": sid, "idx": idx, "a": a})
        if not last.get("ok"): return last, f"{sid} task {idx} ({k}) rejected: {last}"
    return last, None
def grant(uid, n_scenes):
    with db._conn() as c:
        for sid in ids[:n_scenes]:
            c.execute("INSERT OR IGNORE INTO quest_prog (user_id, scene_id, done_day, mistakes) VALUES (?,?,?,0)", (uid, sid, "2026-01-01"))
        c.execute("DELETE FROM quest_run WHERE user_id=?", (uid,))
        c.execute("UPDATE quest_day SET free_used=0 WHERE user_id=?", (uid,))

U = 9101
db.save_user(U, name="T", username="t", lang="ru", level="HSK1")
api("state", U); api("char", U, {"hero": "Lina", "gender": "f"})
st = api("state", U)
check("chapters in state: 3 with 8 scenes each, chapter 2 locked at start", [c["count"] for c in st["chapters"]] == [8, 8, 8] and [s["ch"] for s in st["scenes"]] == [0] * 8 + [1] * 8 + [2] * 8)
check("scene numbering restarts per chapter", [s["n"] for s in st["scenes"]][:9] == [1, 2, 3, 4, 5, 6, 7, 8, 1])
r = api("scene", U, {"scene": "s9"}); check("chapter 2 scene locked before chapter 1 is done", r["ok"] is False and r["err"] == "locked")

grant(U, 7)
a, err = play(U, "s8"); check("boss s8 played through the API", not err, err)
check("ch1 done -> chapter_done, next chapter, next scene s9, game not over", a["chapter_done"] and a["chapter"] == 0 and a["next_scene"] == "s9" and a["game_done"] is False and a["bonus"] == 50, a)
st = api("state", U); check("s9 current after ch1", st["scenes"][8]["status"] == "current" and st["today"]["game_done"] is False)
b = quest.journey_badges(U); check("badge: chapter 1 yes, Xi'an no", b["j_chapter"] and not b["j_xian"] and not b["j_chengdu"], b)
grant(U, 15)
a, err = play(U, "s16"); check("boss s16 played through the API", not err, err)
check("ch2 done -> chapter 1 index, next scene s17", a["chapter_done"] and a["chapter"] == 1 and a["next_scene"] == "s17" and a["game_done"] is False and a["bonus"] == 50, a)
b = quest.journey_badges(U); check("badge: Xi'an yes, Chengdu no", b["j_xian"] and not b["j_chengdu"], b)
grant(U, 16)
a2 = api("scene", U, {"scene": "s17"}); check("s17 opens, cast has its characters", a2["ok"] and "chuan" in a2["cast"], a2.get("err"))
grant(U, 23)
a, err = play(U, "s24"); check("finale s24 played through the API", not err, err)
check("game done: no next scene, no next chapter", a["game_done"] and a["chapter_done"] and a["chapter"] == 2 and a["next_scene"] is None and a["next_chapter"] is None and a["can_continue"] is False, a)
st = api("state", U); check("state: all 24 done, game_done flag", all(s["status"] == "done" for s in st["scenes"]) and st["today"]["game_done"] is True)
b = quest.journey_badges(U); check("badges: all three journey chapters", b["j_chapter"] and b["j_xian"] and b["j_chengdu"], b)
r = api("scene", U, {"scene": "s20"}); check("replay of a chapter 3 scene works and pays nothing", r["ok"] and r["replay"])

# фразы для озвучки берутся из всех глав
import tts, glob
ph = set()
for f in sorted(glob.glob("quest_data/ch*.json")): ph |= tts.phrases_from(json.load(open(f, encoding="utf-8")))
check("TTS phrase list covers chapters 2-3", any("兵马俑" in p for p in ph) and any("熊猫" in p for p in ph), len(ph))

print("\nFAILS:", fails if fails else "none")
sys.exit(1 if fails else 0)
