# -*- coding: utf-8 -*-
"""ch1.json (build.py) + quest_tr -> hanzhu4/quest_data/ch1.json (формат движка, 3 языка)."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import quest_tr as T

src = json.load(open("ch1_build.json", encoding="utf-8"))
ch = src["chapter"]

def tri(ru, uz, en):
    return {"ru": ru, "uz": uz, "en": en}

out = {"chapter": {
    "id": ch["id"], "title_zh": ch["title_zh"], "level": ch["level"],
    "title": tri(ch["title_ru"], T.CHAPTER["title"]["uz"], T.CHAPTER["title"]["en"]),
    "city": tri(ch["city_ru"], T.CHAPTER["city"]["uz"], T.CHAPTER["city"]["en"]),
    "goal": tri(ch["goal_ru"], T.CHAPTER["goal"]["uz"], T.CHAPTER["goal"]["en"]),
    "next": tri(ch["next_ru"], T.CHAPTER["next"]["uz"], T.CHAPTER["next"]["en"]),
}, "cast": {}, "scenes": []}

for k, c in src["cast"].items():
    uz, en = T.CAST[k]
    out["cast"][k] = {"zh": c["zh"], "py": c["py"], "role": tri(c["ru"], uz, en)}

problems = []
for sc in src["scenes"]:
    t = T.SC[sc["id"]]
    n_dlg = len(sc["dialogue"]); 
    if len(t["dialogue"]) != n_dlg:
        problems.append(f"{sc['id']}: dialogue {n_dlg} vs {len(t['dialogue'])}")
    hints = [x for x in sc["tasks"] if x["t"] == "od"]
    trs = [x for x in sc["tasks"] if x["t"] == "tr"]
    if len(t["hints"]) != len(hints): problems.append(f"{sc['id']}: hints")
    if len(t["tr"]) != len(trs): problems.append(f"{sc['id']}: tr")
    o = {
        "id": sc["id"], "boss": bool(sc.get("boss")), "cast": sc["cast"], "title": sc["title"],
        "title_tr": tri(sc["title_ru"], *t["title"]),
        "bg_tr": tri(sc["bg"], *t["bg"]),
        "obstacle": tri(sc["obstacle_ru"], *t["obstacle"]),
        "culture": tri(sc["culture_ru"], *t["culture"]),
        "dialogue": [], "tasks": [],
    }
    for ln, (uz, en) in zip(sc["dialogue"], t["dialogue"]):
        o["dialogue"].append({"who": ln["who"], "zh": ln["zh"], "tr": tri(ln["ru"], uz, en)})
    hi = ti = 0
    for tk in sc["tasks"]:
        tk = dict(tk)
        if tk["t"] == "od":
            uz, en = t["hints"][hi]; hi += 1
            tk["hint"] = tri(tk.pop("hint_ru"), uz, en)
        elif tk["t"] == "tr":
            uzs, ens = t["tr"][ti]; ti += 1
            rus = tk.pop("opts_ru")
            if not (len(rus) == len(uzs) == len(ens) == 4): problems.append(f"{sc['id']}: tr opts")
            tk["opts_tr"] = [tri(a, b, c) for a, b, c in zip(rus, uzs, ens)]
            tk["ok"] = 0
        o["tasks"].append(tk)
    out["scenes"].append(o)

if problems:
    print("PROBLEMS", problems); sys.exit(1)
dst = "../hanzhu4/quest_data"
os.makedirs(dst, exist_ok=True)
json.dump(out, open(dst + "/ch1.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("ok", os.path.getsize(dst + "/ch1.json"), "bytes;", len(out["scenes"]), "scenes")
