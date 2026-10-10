# -*- coding: utf-8 -*-
"""Квест «Путешествие с Чачей» (茶茶的旅行): прогресс, жизни, монеты, магазин, оплата Telegram Stars.

Все правила живут здесь, на сервере. Приложение только показывает: ответы проверяются тут,
поэтому монеты и жизни нельзя «накрутить» через консоль браузера.
Данные глав лежат в quest_data/chN.json (создаются генератором quest/gen_game.py)."""
import json
import logging
import os
import random
import re
import threading
import time
from pathlib import Path

import db

DATA_PATH = Path(__file__).parent / "quest_data"

# ── правила экономики (1 монета ≈ 2 звезды: всё, что продаётся за звёзды, можно заработать монетами) ──
LIVES_MAX = 5
LIFE_REGEN_SEC = 3600           # +1 жизнь в час
COIN_TASK_FIRST = 10            # задание с первой попытки
COIN_TASK_RETRY = 5             # после ошибок
COIN_SCENE = 20                 # бонус за сцену
COIN_BOSS = 50                  # бонус за финал главы
REVIVES_PER_DAY = 3             # «повтори карточки» → +1 жизнь, раз в день не больше
CARDS_N = 5
CARDS_MIN_SEC = 20              # карточки нельзя «пролистать» быстрее
FREE_SKINS = (0, 1, 2)          # 6 нарядов, первые три бесплатно

ITEMS = {                       # id: (монеты, звёзды)
    "life": (25, 50),           # одна жизнь
    "refill": (150, 300),       # все жизни сразу
    "extra": (300, 600),        # ещё одна сцена сегодня
    "skin": (150, 300),         # новый наряд
}
COIN_PER_STAR = 0.5             # если человек заплатил, а покупка потеряла смысл: возвращаем монетами
PACKS = {}                      # пакетов монет за звёзды больше нет: монеты только зарабатываются
DONATE_STARS = (10, 50, 100)
PRIZE_ON = os.getenv("PRIZE_ON", "1") != "0"     # розыгрыш скина среди прошедших первую сцену

ITEM_TXT = {
    "ru": {"life": ("Жизнь", "+1 жизнь в игре «Путешествие с Чачей»"),
           "refill": ("Все жизни", "Сразу пять жизней в игре «Путешествие с Чачей»"),
           "extra": ("Ещё одна сцена", "Продолжить путь сегодня: ещё одна сцена в игре «Путешествие с Чачей»"),
           "skin": ("Новый наряд", "Наряд для героя в игре «Путешествие с Чачей»"),
           "donate": ("Поддержать проект", "Спасибо, что помогаешь проекту «清越» расти 🍵")},
    "uz": {"life": ("Jon", "«Chacha bilan sayohat» o'yinida +1 jon"),
           "refill": ("Barcha jonlar", "«Chacha bilan sayohat» o'yinida birdaniga besh jon"),
           "extra": ("Yana bir sahna", "Bugun yo'lni davom ettirish: «Chacha bilan sayohat»da yana bir sahna"),
           "skin": ("Yangi kiyim", "«Chacha bilan sayohat» o'yinida qahramon uchun kiyim"),
           "donate": ("Loyihani qo'llab-quvvatlash", "«清越» loyihasi o'sishiga yordam berganingiz uchun rahmat 🍵")},
    "en": {"life": ("Life", "+1 life in “Journey with Chacha”"),
           "refill": ("All lives", "Five lives at once in “Journey with Chacha”"),
           "extra": ("One more scene", "Keep going today: one more scene in “Journey with Chacha”"),
           "skin": ("New outfit", "An outfit for your hero in “Journey with Chacha”"),
           "donate": ("Support the project", "Thank you for helping 清越 grow 🍵")},
    "zh": {"life": ("生命", "《茶茶的旅行》+1 条生命"),
           "refill": ("全部生命", "《茶茶的旅行》一次补满五条生命"),
           "extra": ("再来一幕", "今天继续旅行：《茶茶的旅行》再玩一幕"),
           "skin": ("新装扮", "《茶茶的旅行》主角的新装扮"),
           "donate": ("支持项目", "感谢你帮助「清越」成长 🍵")},
}

_LOCK = threading.RLock()
_CACHE = {}


# ───────────────────────── данные глав ─────────────────────────

def load_chapters():
    if "ch" not in _CACHE:
        chs = []
        for p in sorted(DATA_PATH.glob("ch*.json")):
            chs.append(json.loads(p.read_text(encoding="utf-8")))
        _CACHE["ch"] = chs
        _CACHE["scenes"] = [s for c in chs for s in c["scenes"]]
        _CACHE["by_id"] = {s["id"]: s for s in _CACHE["scenes"]}
        _CACHE["cast"] = {}
        for c in chs:
            _CACHE["cast"].update(c["cast"])
    return _CACHE["ch"]


def scenes():
    load_chapters()
    return _CACHE["scenes"]


def scene_by_id(sid):
    load_chapters()
    return _CACHE["by_id"].get(sid)


def scene_index(sid):
    for i, s in enumerate(scenes()):
        if s["id"] == sid:
            return i
    return -1


# ───────────────────────── БД ─────────────────────────

def init_db():
    with db._conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS quest_char (
            user_id INTEGER PRIMARY KEY, hero TEXT, gender TEXT, skin INTEGER DEFAULT 0, owned TEXT DEFAULT '[0,1,2]',
            coins INTEGER DEFAULT 0, lives INTEGER DEFAULT 5, lives_ts REAL DEFAULT 0, created TEXT
        );
        CREATE TABLE IF NOT EXISTS quest_prog (
            user_id INTEGER, scene_id TEXT, done_day TEXT, mistakes INTEGER DEFAULT 0, PRIMARY KEY (user_id, scene_id)
        );
        CREATE TABLE IF NOT EXISTS quest_run (
            user_id INTEGER, scene_id TEXT, idx INTEGER DEFAULT 0, errs INTEGER DEFAULT 0, mistakes INTEGER DEFAULT 0,
            earned INTEGER DEFAULT 0, st TEXT DEFAULT '{}', replay INTEGER DEFAULT 0, started TEXT, PRIMARY KEY (user_id, scene_id)
        );
        CREATE TABLE IF NOT EXISTS quest_day (
            user_id INTEGER, day TEXT, free_used INTEGER DEFAULT 0, extra INTEGER DEFAULT 0, revives INTEGER DEFAULT 0,
            cards_ts REAL DEFAULT 0, PRIMARY KEY (user_id, day)
        );
        CREATE TABLE IF NOT EXISTS quest_pay (
            charge_id TEXT PRIMARY KEY, nonce TEXT, user_id INTEGER, item TEXT, stars INTEGER, ts TEXT
        );
        CREATE INDEX IF NOT EXISTS quest_pay_nonce ON quest_pay(nonce);
        CREATE TABLE IF NOT EXISTS quest_score (
            user_id INTEGER, day TEXT, pts INTEGER DEFAULT 0, PRIMARY KEY (user_id, day)
        );
        CREATE TABLE IF NOT EXISTS quest_prize (
            user_id INTEGER PRIMARY KEY, ts TEXT, won INTEGER DEFAULT 0
        );
        """)
        cols = {r[1] for r in c.execute("PRAGMA table_info(quest_char)").fetchall()}
        if "hide" not in cols:
            c.execute("ALTER TABLE quest_char ADD COLUMN hide INTEGER DEFAULT 0")
        # те, кто прошёл первую сцену до появления розыгрыша, тоже участвуют
        first = scenes()[0]["id"] if scenes() else None
        if first:
            c.execute("INSERT OR IGNORE INTO quest_prize (user_id, ts) SELECT user_id, done_day FROM quest_prog WHERE scene_id=?", (first,))


def _row(c, sql, a=()):
    r = c.execute(sql, a).fetchone()
    return dict(r) if r else None


def char_get(uid):
    with db._conn() as c:
        return _row(c, "SELECT * FROM quest_char WHERE user_id=?", (uid,))


def _owned(ch):
    try:
        return [int(x) for x in json.loads(ch.get("owned") or "[]")]
    except Exception:
        return list(FREE_SKINS)


def clean_hero(raw):
    s = re.sub(r"[<>&\"'`{}\\\[\]|^@#]", "", str(raw or "")).strip()
    s = re.sub(r"\s+", " ", s)
    return s[:16] if len(s) >= 2 else ""


def char_save(uid, hero, gender, skin):
    hero = clean_hero(hero)
    if not hero:
        return None, "hero"
    if gender not in ("m", "f"):
        return None, "gender"
    with _LOCK, db._conn() as c:
        cur = _row(c, "SELECT * FROM quest_char WHERE user_id=?", (uid,))
        if not cur:
            skin = skin if skin in FREE_SKINS else 0
            c.execute("INSERT INTO quest_char (user_id, hero, gender, skin, owned, coins, lives, lives_ts, created) VALUES (?,?,?,?,?,?,?,?,?)",
                      (uid, hero, gender, skin, json.dumps(list(FREE_SKINS)), 0, LIVES_MAX, time.time(), db.today()))
        else:
            if skin not in _owned(cur):
                skin = cur["skin"]
            c.execute("UPDATE quest_char SET hero=?, gender=?, skin=? WHERE user_id=?", (hero, gender, skin, uid))
        return _row(c, "SELECT * FROM quest_char WHERE user_id=?", (uid,)), None


def _regen(c, ch, now=None):
    """Дорисовывает жизни за прошедшее время. Меняет ch и пишет в БД."""
    now = now or time.time()
    if ch["lives"] >= LIVES_MAX:
        return ch
    gained = int((now - (ch["lives_ts"] or now)) // LIFE_REGEN_SEC)
    if gained > 0:
        ch["lives"] = min(LIVES_MAX, ch["lives"] + gained)
        ch["lives_ts"] = now if ch["lives"] >= LIVES_MAX else ch["lives_ts"] + gained * LIFE_REGEN_SEC
        c.execute("UPDATE quest_char SET lives=?, lives_ts=? WHERE user_id=?", (ch["lives"], ch["lives_ts"], ch["user_id"]))
    return ch


def _set_lives(c, ch, n):
    """Ставит число жизней. Если было полно, а стало меньше, запускает таймер заново."""
    n = max(0, min(LIVES_MAX, n))
    if ch["lives"] >= LIVES_MAX and n < LIVES_MAX:
        ch["lives_ts"] = time.time()
    ch["lives"] = n
    c.execute("UPDATE quest_char SET lives=?, lives_ts=? WHERE user_id=?", (n, ch["lives_ts"], ch["user_id"]))


def _day_row(c, uid, day=None):
    day = day or db.today()
    c.execute("INSERT OR IGNORE INTO quest_day (user_id, day) VALUES (?,?)", (uid, day))
    return _row(c, "SELECT * FROM quest_day WHERE user_id=? AND day=?", (uid, day))


def _add_score(c, uid, pts, day=None):
    """Очки рейтинга = всё, что игрок заработал в игре (покупки их не меняют и не уменьшают)."""
    if pts <= 0:
        return
    day = day or db.today()
    c.execute("INSERT INTO quest_score (user_id, day, pts) VALUES (?,?,?) ON CONFLICT(user_id, day) DO UPDATE SET pts=pts+excluded.pts", (uid, day, pts))


def done_ids(c, uid):
    return {r[0] for r in c.execute("SELECT scene_id FROM quest_prog WHERE user_id=?", (uid,)).fetchall()}


# ───────────────────────── состояние для приложения ─────────────────────────

def shop_view(owned):
    return {"items": {k: {"coins": v[0], "stars": v[1]} for k, v in ITEMS.items()},
            "owned": owned, "free": list(FREE_SKINS)}


def state(uid, stars_on=True, donate=None):
    load_chapters()
    with _LOCK, db._conn() as c:
        ch = _row(c, "SELECT * FROM quest_char WHERE user_id=?", (uid,))
        out = {"chapters": [{k: v for k, v in x["chapter"].items() if k in ("id", "title_zh", "title", "city", "goal", "next", "level")}
                            for x in _CACHE["ch"]],
               "stars_on": bool(stars_on), "donate": donate or {"on": False}, "constants": {
                   "lives_max": LIVES_MAX, "regen": LIFE_REGEN_SEC, "revives_per_day": REVIVES_PER_DAY, "cards_min": CARDS_MIN_SEC,
                   "scene_bonus": COIN_SCENE, "task_coins": COIN_TASK_FIRST}}
        if not ch:
            out["char"] = None
            out["shop"] = shop_view(list(FREE_SKINS))
            return out
        _regen(c, ch)
        owned = _owned(ch)
        done = done_ids(c, uid)
        runs = {r["scene_id"]: dict(r) for r in c.execute("SELECT * FROM quest_run WHERE user_id=?", (uid,)).fetchall()}
        day = _day_row(c, uid)
        sc_out = []
        current_found = False
        for i, s in enumerate(_CACHE["scenes"]):
            if s["id"] in done:
                status = "done"
            elif not current_found:
                status, current_found = "current", True
            else:
                status = "locked"
            run = runs.get(s["id"])
            sc_out.append({"id": s["id"], "n": i + 1, "title": s["title"], "title_tr": s["title_tr"], "status": status,
                           "boss": s["boss"], "tasks": len(s["tasks"]),
                           "progress": run["idx"] if (run and not run["replay"] and status == "current") else 0})
        free_left = 0 if day["free_used"] else 1
        out["char"] = {"hero": ch["hero"], "gender": ch["gender"], "skin": ch["skin"], "owned": owned}
        out["coins"] = ch["coins"]
        out["lives"] = ch["lives"]
        out["next_life_in"] = 0 if ch["lives"] >= LIVES_MAX else max(1, int(LIFE_REGEN_SEC - (time.time() - ch["lives_ts"])))
        out["scenes"] = sc_out
        out["today"] = {"free_left": free_left, "extra": day["extra"], "revives_left": max(0, REVIVES_PER_DAY - day["revives"]),
                        "done_scenes": len(done), "chapter_done": len(done) >= len(_CACHE["scenes"])}
        out["shop"] = shop_view(owned)
        out["prize"] = prize_view(c, uid)
        out["hide"] = bool(ch.get("hide"))
        return out


def prize_view(c, uid):
    if not PRIZE_ON:
        return {"on": False}
    n = c.execute("SELECT COUNT(*) FROM quest_prize").fetchone()[0]
    mine = _row(c, "SELECT * FROM quest_prize WHERE user_id=?", (uid,))
    w = c.execute("SELECT ch.hero FROM quest_prize p JOIN quest_char ch ON ch.user_id=p.user_id WHERE p.won=1 ORDER BY p.ts DESC LIMIT 1").fetchone()
    return {"on": True, "entered": bool(mine), "won": bool(mine and mine["won"]), "count": n, "winner": w[0] if w else None}


# ───────────────────────── задания ─────────────────────────

def _rng(uid, sid, idx):
    return random.Random(f"{uid}:{sid}:{idx}")


def public_task(uid, sid, idx, st=None):
    """Задание без ответа, с перемешанными вариантами. id вариантов = номер в исходнике."""
    s = scene_by_id(sid)
    t = s["tasks"][idx]
    r = _rng(uid, sid, idx)
    k = t["t"]
    out = {"t": k, "idx": idx, "of": len(s["tasks"])}
    if k in ("rp", "hz"):
        order = list(range(len(t["opts"]))); r.shuffle(order)
        out["opts"] = [{"id": i, "zh": t["opts"][i]} for i in order]
        if k == "rp":
            out["who"] = t["who"]; out["npc"] = t["npc"]
        else:
            out["emoji"] = t["emoji"]
    elif k == "tn":
        opts = [t["correct"]] + list(t["wrong"])
        order = list(range(len(opts))); r.shuffle(order)
        out["h"] = t["h"]
        out["opts"] = [{"id": i, "p": opts[i]} for i in order]
    elif k == "od":
        order = list(range(len(t["words"]))); r.shuffle(order)
        if order == list(range(len(order))) and len(order) > 1:
            order = order[1:] + order[:1]
        out["words"] = [{"id": i, **t["words"][i]} for i in order]
        out["end"] = t["end"]; out["hint"] = t["hint"]
    elif k == "mt":
        n = len(t["pairs"])
        lo = list(range(n)); ro = list(range(n)); r.shuffle(lo); r.shuffle(ro)
        out["left"] = [{"id": i, "h": t["pairs"][i]["h"], "p": t["pairs"][i]["p"]} for i in lo]
        out["right"] = [{"id": i, "x": t["pairs"][i]["x"]} for i in ro]
        out["matched"] = list((st or {}).get("matched", []))
    elif k == "tr":
        order = list(range(len(t["opts_tr"]))); r.shuffle(order)
        out["zh"] = t["zh"]
        out["opts"] = [{"id": i, "tr": t["opts_tr"][i]} for i in order]
    return out


def dialogue_view(s):
    return [{"who": ln["who"], "zh": ln["zh"], "tr": ln["tr"]} for ln in s["dialogue"]]


def cast_view(s):
    return {w: _CACHE["cast"][w] for w in s["cast"] + ["me"] if w in _CACHE["cast"]}


def scene_payload(uid, s, run, ch):
    st = json.loads(run["st"] or "{}")
    return {"id": s["id"], "title": s["title"], "title_tr": s["title_tr"], "bg_tr": s["bg_tr"], "obstacle": s["obstacle"],
            "culture": s["culture"], "boss": s["boss"], "cast": cast_view(s), "dialogue": dialogue_view(s),
            "replay": bool(run["replay"]), "idx": run["idx"], "total": len(s["tasks"]),
            "task": public_task(uid, s["id"], run["idx"], st) if run["idx"] < len(s["tasks"]) else None,
            "lives": ch["lives"], "coins": ch["coins"]}


def start_scene(uid, sid):
    """(payload, err). err: 'nochar' | 'locked' | 'extra' (нужен пропуск на сегодня)."""
    s = scene_by_id(sid)
    if not s:
        return None, "none"
    with _LOCK, db._conn() as c:
        ch = _row(c, "SELECT * FROM quest_char WHERE user_id=?", (uid,))
        if not ch:
            return None, "nochar"
        _regen(c, ch)
        done = done_ids(c, uid)
        run = _row(c, "SELECT * FROM quest_run WHERE user_id=? AND scene_id=?", (uid, sid))
        replay = sid in done
        if replay:
            if not run or not run["replay"]:
                c.execute("INSERT OR REPLACE INTO quest_run (user_id, scene_id, idx, replay, started) VALUES (?,?,0,1,?)", (uid, sid, db.today()))
                run = _row(c, "SELECT * FROM quest_run WHERE user_id=? AND scene_id=?", (uid, sid))
            return scene_payload(uid, s, run, ch), None
        # новая сцена должна быть первой непройденной
        first = next((x["id"] for x in scenes() if x["id"] not in done), None)
        if sid != first:
            return None, "locked"
        if run and not run["replay"]:
            return scene_payload(uid, s, run, ch), None          # продолжение начатой: бесплатно
        day = _day_row(c, uid)
        if not day["free_used"]:
            c.execute("UPDATE quest_day SET free_used=1 WHERE user_id=? AND day=?", (uid, day["day"]))
        elif day["extra"] > 0:
            c.execute("UPDATE quest_day SET extra=extra-1 WHERE user_id=? AND day=?", (uid, day["day"]))
        else:
            return None, "extra"
        c.execute("INSERT OR REPLACE INTO quest_run (user_id, scene_id, idx, replay, started) VALUES (?,?,0,0,?)", (uid, sid, db.today()))
        run = _row(c, "SELECT * FROM quest_run WHERE user_id=? AND scene_id=?", (uid, sid))
        return scene_payload(uid, s, run, ch), None


def _check(t, st, a):
    """-> (верно, задание_закончено, обновлённое_состояние). Для mt верная пара ещё не конец."""
    k = t["t"]
    if k in ("rp", "hz", "tr"):
        return (isinstance(a, int) and a == t["ok"]), True, st
    if k == "tn":
        return (isinstance(a, int) and a == 0), True, st
    if k == "od":
        n = len(t["words"])
        return (isinstance(a, list) and a == list(range(n))), True, st
    if k == "mt":
        if not isinstance(a, dict):
            return False, False, st
        l, r = a.get("l"), a.get("r")
        n = len(t["pairs"])
        if not (isinstance(l, int) and isinstance(r, int) and 0 <= l < n and 0 <= r < n):
            return False, False, st
        matched = set(st.get("matched", []))
        if l != r:
            return False, False, st
        matched.add(l)
        st = dict(st, matched=sorted(matched))
        return True, len(matched) == n, st
    return False, False, st


def answer(uid, sid, idx, a):
    """Ответ на текущее задание. Возвращает словарь для приложения."""
    s = scene_by_id(sid)
    if not s:
        return {"err": "none"}
    with _LOCK, db._conn() as c:
        ch = _row(c, "SELECT * FROM quest_char WHERE user_id=?", (uid,))
        run = _row(c, "SELECT * FROM quest_run WHERE user_id=? AND scene_id=?", (uid, sid))
        if not ch or not run:
            return {"err": "norun"}
        _regen(c, ch)
        if idx != run["idx"] or run["idx"] >= len(s["tasks"]):
            return {"err": "sync", "idx": run["idx"]}
        replay = bool(run["replay"])
        if not replay and ch["lives"] <= 0:
            return {"ok": False, "out": True, "lives": 0, "coins": ch["coins"], "next_life_in": _next_in(ch)}
        t = s["tasks"][idx]
        st = json.loads(run["st"] or "{}")
        ok, finished, st = _check(t, st, a)
        res = {"ok": bool(ok), "lives": ch["lives"], "coins": ch["coins"], "done": False}
        if t["t"] == "mt":
            res["matched"] = st.get("matched", [])
        if not ok:
            if not replay:
                _set_lives(c, ch, ch["lives"] - 1)
                c.execute("UPDATE quest_run SET errs=errs+1, mistakes=mistakes+1 WHERE user_id=? AND scene_id=?", (uid, sid))
                res["lives"] = ch["lives"]
                res["out"] = ch["lives"] <= 0
                res["next_life_in"] = _next_in(ch)
            return res
        if not finished:                       # верная пара в «соедини»
            c.execute("UPDATE quest_run SET st=? WHERE user_id=? AND scene_id=?", (json.dumps(st), uid, sid))
            return res
        gain = 0
        if not replay:
            gain = COIN_TASK_FIRST if run["errs"] == 0 else COIN_TASK_RETRY
        new_idx = idx + 1
        earned = run["earned"] + gain
        scene_done = new_idx >= len(s["tasks"])
        bonus = 0
        if scene_done and not replay:
            bonus = COIN_BOSS if s["boss"] else COIN_SCENE
            c.execute("INSERT OR IGNORE INTO quest_prog (user_id, scene_id, done_day, mistakes) VALUES (?,?,?,?)",
                      (uid, sid, db.today(), run["mistakes"]))
        total_gain = gain + bonus
        if total_gain:
            ch["coins"] += total_gain
            c.execute("UPDATE quest_char SET coins=? WHERE user_id=?", (ch["coins"], uid))
            _add_score(c, uid, total_gain)
        prize_new = False
        if scene_done and not replay and PRIZE_ON and sid == scenes()[0]["id"]:
            prize_new = c.execute("INSERT OR IGNORE INTO quest_prize (user_id, ts) VALUES (?,?)", (uid, db.today())).rowcount > 0
        if scene_done:
            c.execute("DELETE FROM quest_run WHERE user_id=? AND scene_id=?", (uid, sid))
        else:
            c.execute("UPDATE quest_run SET idx=?, errs=0, st='{}', earned=? WHERE user_id=? AND scene_id=?", (new_idx, earned, uid, sid))
        res.update({"done": True, "gain": gain, "bonus": bonus, "coins": ch["coins"], "scene_done": scene_done,
                    "retry": run["errs"] > 0, "idx": new_idx})
        if scene_done:
            res["earned"] = earned + bonus
            res["mistakes"] = run["mistakes"]
            res["replay"] = replay
            done = done_ids(c, uid) | {sid}
            res["chapter_done"] = len(done) >= len(scenes())
            nxt = next((x for x in scenes() if x["id"] not in done), None)
            res["next_scene"] = nxt["id"] if nxt else None
            day = _day_row(c, uid)
            res["can_continue"] = bool(nxt) and (not day["free_used"] or day["extra"] > 0)
            if prize_new:
                res["prize_new"] = True
        else:
            res["task"] = public_task(uid, sid, new_idx, {})
        return res


def _next_in(ch):
    if ch["lives"] >= LIVES_MAX:
        return 0
    return max(1, int(LIFE_REGEN_SEC - (time.time() - (ch["lives_ts"] or time.time()))))


# ───────────────────────── «повтори карточки» ─────────────────────────

def cards_start(uid):
    with _LOCK, db._conn() as c:
        ch = _row(c, "SELECT * FROM quest_char WHERE user_id=?", (uid,))
        if not ch:
            return None, "nochar"
        day = _day_row(c, uid)
        if day["revives"] >= REVIVES_PER_DAY:
            return None, "limit"
        done = done_ids(c, uid)
        pool = [s for s in scenes() if s["id"] in done] or scenes()[:1]
        lines = [(s["id"], ln) for s in pool for ln in s["dialogue"]]
        rnd = random.Random(f"{uid}:{time.time()}")
        pick = rnd.sample(lines, min(CARDS_N, len(lines)))
        c.execute("UPDATE quest_day SET cards_ts=? WHERE user_id=? AND day=?", (time.time(), uid, day["day"]))
        return [{"zh": ln["zh"], "tr": ln["tr"]} for _, ln in pick], None


def cards_claim(uid):
    with _LOCK, db._conn() as c:
        ch = _row(c, "SELECT * FROM quest_char WHERE user_id=?", (uid,))
        if not ch:
            return {"err": "nochar"}
        _regen(c, ch)
        day = _day_row(c, uid)
        if day["revives"] >= REVIVES_PER_DAY:
            return {"err": "limit"}
        if not day["cards_ts"] or time.time() - day["cards_ts"] < CARDS_MIN_SEC:
            return {"err": "fast"}
        if ch["lives"] >= LIVES_MAX:
            return {"err": "full", "lives": ch["lives"]}
        _set_lives(c, ch, ch["lives"] + 1)
        c.execute("UPDATE quest_day SET revives=revives+1, cards_ts=0 WHERE user_id=? AND day=?", (uid, day["day"]))
        return {"ok": True, "lives": ch["lives"], "revives_left": REVIVES_PER_DAY - day["revives"] - 1, "next_life_in": _next_in(ch)}


# ───────────────────────── покупки ─────────────────────────

def parse_item(item):
    """'life' | 'refill' | 'extra' | 'skin3' -> (kind, arg, coins, stars) или None."""
    m = re.fullmatch(r"skin([0-5])", item or "")
    if m:
        return "skin", int(m.group(1)), ITEMS["skin"][0], ITEMS["skin"][1]
    if item in ("life", "refill", "extra"):
        return item, None, ITEMS[item][0], ITEMS[item][1]
    return None


def _apply(c, uid, kind, arg):
    """Выдаёт покупку. Вызывать внутри транзакции. -> (ok, err)"""
    ch = _row(c, "SELECT * FROM quest_char WHERE user_id=?", (uid,))
    if not ch:
        return False, "nochar"
    _regen(c, ch)
    if kind == "life":
        if ch["lives"] >= LIVES_MAX:
            return False, "full"
        _set_lives(c, ch, ch["lives"] + 1)
    elif kind == "refill":
        if ch["lives"] >= LIVES_MAX:
            return False, "full"
        _set_lives(c, ch, LIVES_MAX)
    elif kind == "extra":
        day = _day_row(c, uid)
        c.execute("UPDATE quest_day SET extra=extra+1 WHERE user_id=? AND day=?", (uid, day["day"]))
    elif kind == "skin":
        owned = _owned(ch)
        if arg in owned:
            return False, "owned"
        owned.append(arg)
        c.execute("UPDATE quest_char SET owned=? WHERE user_id=?", (json.dumps(sorted(owned)), uid))
    return True, None


def buy_coins(uid, item):
    p = parse_item(item)
    if not p:
        return {"err": "item"}
    kind, arg, price, _ = p
    with _LOCK, db._conn() as c:
        ch = _row(c, "SELECT * FROM quest_char WHERE user_id=?", (uid,))
        if not ch:
            return {"err": "nochar"}
        if ch["coins"] < price:
            return {"err": "poor", "need": price - ch["coins"]}
        # сначала проверяем, что покупка имеет смысл (жизни полны, наряд уже есть), и только потом списываем
        ok, err = _apply(c, uid, kind, arg)
        if not ok:
            return {"err": err}
        c.execute("UPDATE quest_char SET coins=coins-? WHERE user_id=?", (price, uid))
    return {"ok": True}


def grant_stars(uid, item, stars, charge_id, nonce=""):
    """Вызывается после успешной оплаты Stars. Идемпотентно по charge_id. -> (kind, текст-для-владельца) или None."""
    p = parse_item(item)
    if not p:
        return None
    kind, arg, _, price_stars = p
    with _LOCK, db._conn() as c:
        if c.execute("SELECT 1 FROM quest_pay WHERE charge_id=?", (charge_id,)).fetchone():
            return "dup"
        c.execute("INSERT INTO quest_pay (charge_id, nonce, user_id, item, stars, ts) VALUES (?,?,?,?,?,?)",
                  (charge_id, nonce, uid, item, stars, db.today()))
        ok, err = _apply(c, uid, kind, arg)
        if not ok and err in ("full", "owned"):
            # человек уже заплатил, а покупка потеряла смысл (жизни полные, наряд есть): отдаём равноценное в монетах
            c.execute("UPDATE quest_char SET coins=coins+? WHERE user_id=?", (max(1, int(stars * COIN_PER_STAR)), uid))
            return "coins"
        return kind


def paid_state(uid, nonce):
    with db._conn() as c:
        return bool(nonce) and bool(c.execute("SELECT 1 FROM quest_pay WHERE user_id=? AND nonce=?", (uid, nonce)).fetchone())


def log_donation(uid, stars, charge_id):
    with _LOCK, db._conn() as c:
        if c.execute("SELECT 1 FROM quest_pay WHERE charge_id=?", (charge_id,)).fetchone():
            return False
        c.execute("INSERT INTO quest_pay (charge_id, nonce, user_id, item, stars, ts) VALUES (?,?,?,?,?,?)",
                  (charge_id, "", uid, "donate", stars, db.today()))
        return True


def pay_lookup(charge_id):
    with db._conn() as c:
        return _row(c, "SELECT * FROM quest_pay WHERE charge_id=?", (charge_id,))


def stars_report(days=30):
    from datetime import datetime, timedelta
    since = (datetime.now(db.TZ) - timedelta(days=days)).strftime("%Y-%m-%d")
    with db._conn() as c:
        tot = c.execute("SELECT COALESCE(SUM(stars),0), COUNT(*), COUNT(DISTINCT user_id) FROM quest_pay").fetchone()
        mon = c.execute("SELECT COALESCE(SUM(stars),0), COUNT(*), COUNT(DISTINCT user_id) FROM quest_pay WHERE ts>=?", (since,)).fetchone()
        by = c.execute("SELECT item, COUNT(*), SUM(stars) FROM quest_pay WHERE ts>=? GROUP BY item ORDER BY SUM(stars) DESC", (since,)).fetchall()
    return {"total": tuple(tot), "month": tuple(mon), "by_item": [tuple(r) for r in by]}


# ───────────────────────── рейтинг ─────────────────────────

BOARD_TOP = 20


def _week_start():
    from datetime import datetime, timedelta
    d = datetime.now(db.TZ).date()
    return (d - timedelta(days=d.weekday())).strftime("%Y-%m-%d")


def set_hide(uid, hide):
    with _LOCK, db._conn() as c:
        c.execute("UPDATE quest_char SET hide=? WHERE user_id=?", (1 if hide else 0, uid))


def board(uid, tab="week", exclude=()):
    """Таблица лидеров: за неделю (с понедельника) или за всё время. Видны только ники героев."""
    tab = "all" if tab == "all" else "week"
    since = _week_start() if tab == "week" else "0000-00-00"
    ex = tuple(int(x) for x in exclude if x)
    with db._conn() as c:
        rows = c.execute(
            "SELECT s.user_id AS uid, SUM(s.pts) AS pts, ch.hero, ch.gender, ch.skin, ch.hide, "
            "(SELECT COUNT(*) FROM quest_prog p WHERE p.user_id=s.user_id) AS scenes "
            "FROM quest_score s JOIN quest_char ch ON ch.user_id=s.user_id WHERE s.day>=? GROUP BY s.user_id HAVING pts>0 "
            "ORDER BY pts DESC, scenes DESC, s.user_id ASC", (since,)).fetchall()
        rows = [dict(r) for r in rows if r["uid"] not in ex]
        shown = [r for r in rows if not r["hide"]]
        out = []
        for i, r in enumerate(shown[:BOARD_TOP]):
            out.append({"place": i + 1, "hero": r["hero"], "gender": r["gender"], "skin": r["skin"], "pts": r["pts"], "scenes": r["scenes"], "me": r["uid"] == uid})
        me = None
        for i, r in enumerate(shown):
            if r["uid"] == uid:
                me = {"place": i + 1, "pts": r["pts"], "scenes": r["scenes"]}
                break
        if me is None:
            mine = next((r for r in rows if r["uid"] == uid), None)
            if mine:
                me = {"place": None, "pts": mine["pts"], "scenes": mine["scenes"], "hidden": bool(mine["hide"])}
        return {"tab": tab, "rows": out, "me": me, "total": len(shown), "week_start": _week_start()}


# ───────────────────────── розыгрыш скина ─────────────────────────

def prize_report():
    """Для владельца: сколько участников и кто уже выиграл."""
    with db._conn() as c:
        n = c.execute("SELECT COUNT(*) FROM quest_prize WHERE won=0").fetchone()[0]
        won = [dict(r) for r in c.execute(
            "SELECT p.user_id, p.ts, ch.hero FROM quest_prize p LEFT JOIN quest_char ch ON ch.user_id=p.user_id WHERE p.won=1 ORDER BY p.ts").fetchall()]
        tot = c.execute("SELECT COUNT(*) FROM quest_prize").fetchone()[0]
    return {"waiting": n, "total": tot, "winners": won}


def prize_draw():
    """Случайный победитель среди ещё не выигравших. -> (uid, hero) или None."""
    with _LOCK, db._conn() as c:
        rows = c.execute("SELECT p.user_id, ch.hero FROM quest_prize p LEFT JOIN quest_char ch ON ch.user_id=p.user_id WHERE p.won=0").fetchall()
        if not rows:
            return None
        r = random.SystemRandom().choice(rows)
        c.execute("UPDATE quest_prize SET won=1, ts=? WHERE user_id=?", (db.today(), r[0]))
        return r[0], (r[1] or "?")


def item_text(lang, item):
    tx = ITEM_TXT.get(lang) or ITEM_TXT["ru"]
    p = parse_item(item)
    if item == "donate":
        return tx["donate"]
    if not p:
        return ("?", "?")
    kind, arg = p[0], p[1]
    ti, de = tx[kind]
    return ti.format(n=arg), de


def payload_for(uid, item, nonce):
    return f"q1:{item}:{uid}:{nonce}"


def parse_payload(payload):
    m = re.fullmatch(r"q1:([a-z0-9]+):(\d+):([A-Za-z0-9]{4,24})", payload or "")
    if not m:
        return None
    return m.group(1), int(m.group(2)), m.group(3)
