"""Шкафчик (v29): каталог всех слов по ящичкам HSK и (v32) по темам, поиск, статусы, карточка слова, «Знаю это слово»."""
import unicodedata
import content as C
import db
import practice
import hanzi
import topics as TP

PAGE = 50          # слов за один запрос
PART = 1000        # размер части ящичка HSK 7–9
KNOWN_BOX = 4      # ящик «помню» (как в db.card_stats)
PREF = {"ru": ["ru", "en"], "uz": ["uz", "ru", "en"], "en": ["en", "ru"], "zh": ["en", "ru"]}

_IDX = None        # слова в порядке списка + строки для поиска


def _plain(s):
    """без тонов, пробелов и апострофов: nǐ hǎo -> nihao, nǚ -> nu"""
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(ch for ch in s if ch.isalpha() and not unicodedata.combining(ch))


def _build():
    global _IDX
    if _IDX is not None:
        return _IDX
    words = [w for w in C.WORDS if w.get("zh")]
    seven = [i for i, w in enumerate(words) if w.get("hsk") == 7]
    part_of = {i: n // PART + 1 for n, i in enumerate(seven)}
    drawers, by_id = [], {}
    def add(did, level, part):
        d = {"id": did, "level": level, "part": part, "idx": []}
        drawers.append(d); by_id[did] = d
    for lv in range(1, 7):
        add(f"h{lv}", lv, 0)
    parts = (len(seven) + PART - 1) // PART
    for p in range(1, parts + 1):
        add(f"h7p{p}", 7, p)
    add("h0", 0, 0)
    for i, w in enumerate(words):
        lv = w.get("hsk") or 0
        did = "h0" if lv not in range(1, 8) else (f"h7p{part_of[i]}" if lv == 7 else f"h{lv}")
        by_id[did]["idx"].append(i)
    blobs = [((w["zh"]), _plain(w.get("py", "")), (w.get("ru") or "").lower(), (w.get("uz") or "").lower(), (w.get("en") or "").lower()) for w in words]
    pos = {w["zh"]: i for i, w in enumerate(words)}
    drawers = [d for d in drawers if d["idx"]]
    topics, topic_of = [], {}
    for code, zhs in TP.load():
        idx = [pos[z] for z in zhs if z in pos]
        if idx:
            by_id["t:" + code] = {"id": "t:" + code, "idx": idx}
            topics.append("t:" + code)
            for i in idx:
                topic_of[words[i]["zh"]] = code
    _IDX = {"topics": topics, "topic_of": topic_of, "words": words, "drawers": drawers, "by_id": by_id, "blobs": blobs, "pos": pos, "parts": parts}
    return _IDX


def pick_tr(w, lang):
    """(перевод, язык перевода, пометка). Пометка нужна, если языка пользователя нет и взят другой."""
    order = PREF.get(lang, PREF["ru"])
    for l in order:
        if w.get(l):
            return w[l], l, (l.upper() if lang in ("ru", "uz", "en") and l != lang else "")
    return "", "", ""


def status(zh, cards, today):
    c = cards.get(zh)
    if c is None:
        return "new"
    if c[0] >= KNOWN_BOX:
        return "known"
    return "due" if c[1] <= today else "learn"


def _row(w, lang, cards, today):
    text, _l, tag = pick_tr(w, lang)
    return {"zh": w["zh"], "py": w.get("py", ""), "tr": text, "tag": tag, "st": status(w["zh"], cards, today)}


def drawers(uid):
    I = _build()
    cards = db.cards_all(uid)
    today = db.today()
    out, cnt = [], {"learn": 0, "known": 0, "due": 0}
    for d in I["drawers"]:
        known = 0
        for i in d["idx"]:
            st = status(I["words"][i]["zh"], cards, today)
            if st == "known":
                known += 1
            if st != "new":
                cnt["known" if st == "known" else "learn"] += 1
                if st == "due":
                    cnt["due"] += 1
        out.append({"id": d["id"], "level": d["level"], "part": d["part"], "parts": I["parts"] if d["level"] == 7 else 0, "total": len(d["idx"]), "known": known})
    # «Учу» = всё в карточках, что ещё не выучено; «Повторить» = часть из них, у кого пришёл срок
    tp = []
    for tid in I["topics"]:
        idx = I["by_id"][tid]["idx"]
        tp.append({"id": tid[2:], "total": len(idx), "known": sum(1 for i in idx if status(I["words"][i]["zh"], cards, today) == "known")})
    return {"drawers": out, "topics": tp, "counts": {"learn": cnt["learn"], "known": cnt["known"], "due": cnt["due"]}, "total": len(I["words"])}


def _match(i, q, I):
    zh, py, ru, uz, en = I["blobs"][i]
    if q["han"]:
        return q["raw"] in zh
    t = q["plain"]
    if t and t in py:
        return True
    r = q["raw"]
    return r in ru or r in uz or r in en


def _rank(i, q, I):
    zh, py, ru, uz, en = I["blobs"][i]
    r, t = q["raw"], q["plain"]
    if zh == r or (not q["han"] and (py == t or r in (ru, uz, en))):
        return 0
    if zh.startswith(r) or (not q["han"] and (py.startswith(t) or ru.startswith(r) or uz.startswith(r) or en.startswith(r))):
        return 1
    return 2


def _query(text):
    raw = (text or "").strip().lower()[:40]
    if not raw:
        return None
    han = any("一" <= ch <= "鿿" for ch in raw)
    return {"raw": raw, "plain": _plain(raw), "han": han}


def listing(uid, lang, drawer, flt, text, offset):
    I = _build()
    cards = db.cards_all(uid)
    today = db.today()
    q = _query(text)
    if q:
        idx = [i for i in range(len(I["words"])) if _match(i, q, I)]
        idx.sort(key=lambda i: _rank(i, q, I))      # сортировка устойчивая: внутри ранга порядок списка
    else:
        d = I["by_id"].get(drawer)
        idx = list(d["idx"]) if d else (list(range(len(I["words"]))) if flt in ("learn", "known", "due") else [])
    if flt in ("learn", "known", "due"):
        keep = []
        for i in idx:
            st = status(I["words"][i]["zh"], cards, today)
            if (flt == "known" and st == "known") or (flt == "learn" and st in ("learn", "due")) or (flt == "due" and st == "due"):
                keep.append(i)
        idx = keep
    offset = max(0, int(offset or 0))
    page = idx[offset:offset + PAGE]
    return {"items": [_row(I["words"][i], lang, cards, today) for i in page], "total": len(idx), "next": offset + PAGE if offset + PAGE < len(idx) else None}


def word(uid, lang, zh):
    I = _build()
    i = I["pos"].get(zh)
    if i is None:
        return None
    w = I["words"][i]
    cards = db.cards_all(uid)
    r = _row(w, lang, cards, db.today())
    lv = w.get("hsk") or 0
    r.update({"hsk": lv, "topic": I["topic_of"].get(w["zh"], ""), "pos": w.get("pos") or "", "examples": (w.get("examples") or [])[:4],
              "chars": [c for c in dict.fromkeys(w["zh"]) if hanzi.HAN.match(c) and c in hanzi.stroke_chars()][:4]})
    return r


def know(uid, zh):
    """«Знаю это слово»: слово попадает в карточки сразу в ящик «помню»."""
    I = _build()
    if zh not in I["pos"]:
        return False
    db.card_add(uid, zh)
    db.card_set(uid, zh, KNOWN_BOX, practice.next_due(KNOWN_BOX, db.today()))
    db.log_event(uid, "locker_know")
    return True


# ─── ЭТАПЫ (v30): уровни HSK, этап пройден, когда все слова уровня в «Помню» ───

def stages(uid):
    """[{level, total, known, done}] для HSK 1–6 и 7–9 (одним этапом) + номер текущего этапа (первый не пройденный)."""
    I = _build()
    if "stage_totals" not in I:
        tot, lv_of = {}, {}
        for w in I["words"]:
            lv = w.get("hsk") or 0
            if 1 <= lv <= 7:
                tot[lv] = tot.get(lv, 0) + 1
                lv_of[w["zh"]] = lv
        I["stage_totals"], I["stage_level"] = tot, lv_of
    known = {}
    for zh, (box, _due) in db.cards_all(uid).items():
        lv = I["stage_level"].get(zh)
        if lv and box >= KNOWN_BOX:
            known[lv] = known.get(lv, 0) + 1
    out = []
    for lv in range(1, 8):
        total = I["stage_totals"].get(lv, 0)
        k = known.get(lv, 0)
        out.append({"level": lv, "total": total, "known": k, "done": total > 0 and k >= total})
    cur = next((s["level"] for s in out if not s["done"] and s["total"]), None)
    return {"stages": out, "current": cur}


def stage_badges(uid):
    """{s_hsk1: получен ли, ...}: по одному значку за пройденный этап"""
    return {f"s_hsk{s['level']}": s["done"] for s in stages(uid)["stages"]}
