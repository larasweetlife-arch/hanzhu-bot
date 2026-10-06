"""
Словарь для перевода.
 1. Свои слова (content_words.txt): русский, узбекский, английский <-> китайский.
 2. CC-CEDICT (cedict.txt.gz, около 120 тысяч статей): китайский -> английский, английский -> китайский.
CC-CEDICT распространяется по лицензии CC BY-SA 4.0 (см. NOTICE.md).
"""
import gzip
import html
import os
import re
import sqlite3
import logging
import threading
from pathlib import Path

import db
import content as C
from texts import t

SRC = Path(__file__).parent / "cedict.txt.gz"
DICT_PATH = db.DATA_DIR / "dict.db"

_LINE = re.compile(r"^(\S+) (\S+) \[([^\]]+)\] /(.+)/\s*$")
_SKIP = ("cl:", "see ", "variant of", "old variant", "also written", "erhua", "abbr", "surname", "used in", "taiwan pr")
_HAN = re.compile(r"[\u4e00-\u9fff]")
_lock = threading.Lock()
_ready = False
esc = lambda s: html.escape(str(s), quote=False)   # только < > &: апострофы узбекского (o', g') не трогаем

_TONES = {"a": "āáǎà", "e": "ēéěè", "i": "īíǐì", "o": "ōóǒò", "u": "ūúǔù", "ü": "ǖǘǚǜ"}


def _syllable(s):
    s = s.replace("u:", "ü").replace("U:", "Ü")
    m = re.fullmatch(r"([A-Za-zÜü]+)([1-5])?", s)
    if not m or not m.group(2) or m.group(2) == "5":
        return m.group(1) if m else s
    base, tone = m.group(1), int(m.group(2)) - 1
    low = base.lower()
    vowels = [i for i, c in enumerate(low) if c in "aeiouü"]
    if not vowels:                       # «m», «ng»: гласной нет, значок тона ставить некуда
        return base
    idx = next((low.index(c) for c in "ae" if c in low), None)
    if idx is None:
        idx = low.index("o") if "ou" in low else vowels[-1]
    mark = _TONES[low[idx]][tone]
    return base[:idx] + (mark.upper() if base[idx].isupper() else mark) + base[idx + 1:]


def pinyin_marks(numbered):
    """'ni3 hao3' -> 'nǐ hǎo'"""
    return " ".join(_syllable(x) for x in numbered.split())


def _gloss_keys(g):
    g = g.lower().strip()
    if len(g) > 50 or g.startswith(_SKIP):
        return []
    keys = {g, re.sub(r"\s+", " ", re.sub(r"\([^)]*\)", "", g)).strip()}
    for k in list(keys):
        if k.startswith("to "):
            keys.add(k[3:])
    return [k for k in keys if k]


def _build():
    logging.info("Собираю словарь из %s (один раз, около 10 секунд)...", SRC.name)
    dest = Path(DICT_PATH)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = str(dest) + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    c = sqlite3.connect(tmp)
    c.executescript("""
        CREATE TABLE entries (id INTEGER PRIMARY KEY, simp TEXT, trad TEXT, pinyin TEXT, glosses TEXT);
        CREATE TABLE gloss_idx (gloss TEXT, entry_id INTEGER, pos INTEGER);
        CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT);""")
    rows, idx, eid = [], [], 0
    with gzip.open(SRC, "rt", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            m = _LINE.match(line)
            if not m:
                continue
            trad, simp, py, gl = m.groups()
            glosses = [g.strip() for g in gl.split("/") if g.strip()]
            eid += 1
            rows.append((eid, simp, trad, pinyin_marks(py), "/".join(glosses)))
            for pos, g in enumerate(glosses):
                idx.extend((k, eid, pos) for k in _gloss_keys(g))
    c.executemany("INSERT INTO entries VALUES (?,?,?,?,?)", rows)
    c.executemany("INSERT INTO gloss_idx VALUES (?,?,?)", idx)
    c.executescript("CREATE INDEX i_simp ON entries(simp); CREATE INDEX i_trad ON entries(trad); "
                    "CREATE INDEX i_gloss ON gloss_idx(gloss);")
    c.execute("INSERT INTO meta VALUES ('size', ?)", (str(SRC.stat().st_size),))
    c.commit()
    c.close()
    os.replace(tmp, dest)
    logging.info("Словарь готов: %d статей.", eid)


def available():
    return SRC.exists()


def ensure():
    """Готовит словарь к работе. Если файл cedict.txt.gz не загружен, бот работает на своих словах."""
    global _ready
    if _ready:
        return True
    if not available():
        logging.error("Нет файла %s: переводчик будет знать только слова из content_words.txt.", SRC.name)
        return False
    with _lock:
        if _ready:
            return True
        ok = False
        if Path(DICT_PATH).exists():
            try:
                c = sqlite3.connect(DICT_PATH)
                r = c.execute("SELECT v FROM meta WHERE k='size'").fetchone()
                ok = bool(r) and r[0] == str(SRC.stat().st_size)
                c.close()
            except Exception:
                ok = False
        if not ok:
            _build()
        _ready = True
    return True


def _rows(sql, args=()):
    c = sqlite3.connect(DICT_PATH)
    c.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in c.execute(sql, args)]
    finally:
        c.close()


def _entry(r):
    return {"simp": r["simp"], "trad": r["trad"], "pinyin": r["pinyin"], "glosses": r["glosses"].split("/")}


def lookup_zh(word, limit=3):
    return [_entry(r) for r in _rows(
        "SELECT * FROM entries WHERE simp=? OR trad=? ORDER BY id LIMIT ?", (word, word, limit))]


def lookup_en(query, limit=4):
    q = " ".join(query.lower().split())
    rows = _rows(
        "SELECT e.* FROM gloss_idx g JOIN entries e ON e.id=g.entry_id "
        "WHERE g.gloss IN (?, ?) GROUP BY e.id ORDER BY MIN(g.pos), length(e.simp), e.id LIMIT ?",
        (q, "to " + q, limit))
    return [_entry(r) for r in rows]


def segment(text, max_len=8):
    """Режет фразу на слова: всегда берёт самое длинное слово, которое есть в словаре."""
    text = "".join(ch for ch in text if _HAN.match(ch))[:30]
    out, i = [], 0
    while i < len(text):
        for size in range(min(max_len, len(text) - i), 0, -1):
            piece = text[i:i + size]
            hit = lookup_zh(piece, 1)
            if hit:
                out.append(hit[0])
                i += size
                break
        else:
            out.append({"simp": text[i], "trad": text[i], "pinyin": "", "glosses": []})
            i += 1
    return out


# ─── оформление ответа ────────────────────────────────────────────────────────

def _own_block(w, lang):
    lines = [f"🔤 <b>{esc(w['zh'])}</b>", f"🔊 <code>{esc(w['py'])}</code>", f"📖 {esc(C.meaning(w, lang))}"]
    if w["hsk"]:
        lines.append(f"🏷 HSK {w['hsk']}")
    return "\n".join(lines)


def _cedict_block(e, lang):
    head = f"🔤 <b>{esc(e['simp'])}</b>" + (f" ({esc(e['trad'])})" if e["trad"] != e["simp"] else "")
    gl = "; ".join(g for g in e["glosses"][:4])
    flag = "🇬🇧 " if lang != "en" else ""
    return f"{head}\n🔊 <code>{esc(e['pinyin'])}</code>\n📖 {flag}{esc(gl)}"


def translate_ex(text, lang):
    """Возвращает (готовый HTML-ответ, слово для поиска в БКРС) или (None, None), если ничего не нашли.
    Слово для БКРС отдаётся, когда значение пришло из CC-CEDICT, то есть по-английски."""
    q = " ".join(text.strip().split())[:60]
    if not q:
        return None, None
    use_cedict = ensure()
    blocks, bkrs_q = [], None

    if _HAN.search(q):
        own = C.WORD_BY_ZH.get(q)
        if own:
            blocks.append(_own_block(own, lang))
        elif use_cedict:
            found = lookup_zh(q, 3)
            if found:
                blocks = [_cedict_block(e, lang) for e in found]
                bkrs_q = found[0]["simp"]
            elif len(q) > 1:
                parts = segment(q)
                if any(p["glosses"] for p in parts):
                    lines = [t(lang, "tr_split")]
                    for p in parts:
                        gl = "; ".join(p["glosses"][:2]) if p["glosses"] else "?"
                        lines.append(f"· <b>{esc(p['simp'])}</b> <code>{esc(p['pinyin'])}</code>: {esc(gl)}")
                    note = t(lang, "tr_en_note")
                    return "\n".join(lines) + ("\n\n<i>" + note + "</i>" if note else ""), q
    else:
        own = C.find_by_text(q)
        if own:
            blocks = [_own_block(w, lang) for w in own[:3]]
        elif use_cedict and re.search(r"[A-Za-z]", q):
            found = lookup_en(q, 4)
            if found:
                blocks = [_cedict_block(e, "en") for e in found]
                bkrs_q = found[0]["simp"]

    if not blocks:
        return None, None
    out = "\n\n".join(blocks)
    if bkrs_q and lang != "en" and t(lang, "tr_en_note"):
        out += "\n\n<i>" + t(lang, "tr_en_note") + "</i>"
    return out, bkrs_q


def translate(text, lang):
    return translate_ex(text, lang)[0]
