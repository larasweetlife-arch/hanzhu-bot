"""
Учебный контент бота. Слова, чэнъюй и факты лежат в обычных текстовых файлах рядом с кодом:
    content_words.txt   content_chengyu.txt   content_facts.txt
Добавить новое можно, дописав строку в файл (формат описан в начале каждого файла).
Строки с ошибками бот пропускает и пишет об этом в лог, остальное продолжает работать.
"""
import re
import logging
from pathlib import Path

BASE = Path(__file__).parent


def _lines(name, optional=False):
    path = BASE / name
    if not path.exists():
        if not optional:
            logging.error("Нет файла %s, использую запасной минимум.", name)
        return []
    out = []
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if line and not line.startswith("#"):
            out.append((n, line))
    return out


def _load_words():
    items = []
    for n, line in _lines("content_words.txt"):
        p = [x.strip() for x in line.split("|")]
        if len(p) not in (6, 7) or not p[0] or not p[1] or not re.fullmatch(r"\d", p[2]):
            logging.warning("content_words.txt, строка %d пропущена (нужно 6 полей, уровень цифрой): %s", n, line[:60])
            continue
        zh, py, hsk, ru, uz, en = p[:6]
        items.append({"zh": zh, "py": py, "hsk": int(hsk), "ru": ru or en, "uz": uz or en or ru, "en": en or ru,
                      "tag": p[6] if len(p) == 7 else "", "own": True})
    return items


def _load_hsk():
    """Большой список слов HSK: только английские значения, русский и узбекский не заполнены."""
    items = []
    for n, line in _lines("content_hsk.txt"):
        p = [x.strip() for x in line.split("|")]
        if len(p) != 4 or not p[0] or not p[1] or not p[3] or not re.fullmatch(r"\d", p[2]):
            logging.warning("content_hsk.txt, строка %d пропущена: %s", n, line[:60])
            continue
        items.append({"zh": p[0], "py": p[1], "hsk": int(p[2]), "ru": "", "uz": "", "en": p[3], "tag": "", "own": False})
    return items


def _load_hsk30():
    """Твои списки HSK 3.0, уровни 1–4: с русским переводом и частью речи."""
    items = []
    for n, line in _lines("content_hsk30.txt"):
        p = [x.strip() for x in line.split("|")]
        if len(p) != 5 or not p[0] or not p[1] or not p[3] or not re.fullmatch(r"\d", p[2]):
            logging.warning("content_hsk30.txt, строка %d пропущена: %s", n, line[:60])
            continue
        items.append({"zh": p[0], "py": p[1], "hsk": int(p[2]), "ru": p[3], "uz": "", "en": "", "pos": p[4],
                      "tag": "", "own": True, "scheme": "3.0", "examples": []})
    return items


def _load_hsk5():
    """Список HSK 2.0 (уровни 1–5) с русским переводом и примерами."""
    items = []
    for n, line in _lines("content_hsk5.txt"):
        p = [x.strip() for x in line.split("|")]
        if len(p) < 5 or not p[0] or not p[1] or not p[3] or not re.fullmatch(r"\d", p[2]):
            logging.warning("content_hsk5.txt, строка %d пропущена: %s", n, line[:60])
            continue
        ex = [e.strip() for e in p[4].split("||") if e.strip()] if len(p) > 4 else []
        items.append({"zh": p[0], "py": p[1], "hsk": int(p[2]), "ru": p[3], "uz": "", "en": "", "pos": "",
                      "tag": "", "own": True, "scheme": "2.0", "examples": ex})
    return items


def _load_chengyu():
    items = []
    for n, line in _lines("content_chengyu.txt"):
        p = [x.strip() for x in line.split("|")]
        if len(p) != 6 or not p[0] or not p[1]:
            logging.warning("content_chengyu.txt, строка %d пропущена (нужно 6 полей): %s", n, line[:60])
            continue
        zh, py, ru, uz, en, ex = p
        items.append({"zh": zh, "py": py, "ru": ru or en, "uz": uz or en or ru, "en": en or ru, "ex": ex,
                      "hsk": 0, "own": True})
    return items


def _load_chengyu_big():
    """Чэнъюй из CC-CEDICT: английские значения, уровень = самый сложный иероглиф."""
    items = []
    for n, line in _lines("content_chengyu_cedict.txt"):
        p = [x.strip() for x in line.split("|")]
        if len(p) != 4 or not p[0] or not p[1] or not p[3] or not re.fullmatch(r"\d", p[2]):
            logging.warning("content_chengyu_cedict.txt, строка %d пропущена: %s", n, line[:60])
            continue
        items.append({"zh": p[0], "py": p[1], "ru": "", "uz": "", "en": p[3], "ex": "", "hsk": int(p[2]), "own": False})
    return items


def _load_facts():
    items = []
    for n, line in _lines("content_facts.txt"):
        p = [x.strip() for x in line.split("||")]
        if len(p) != 4 or not all(p):
            logging.warning("content_facts.txt, строка %d пропущена (нужно 4 языка через ||): %s", n, line[:60])
            continue
        items.append(dict(zip(("ru", "uz", "en", "zh"), p)))
    return items


# запасной минимум на случай, если файлы с контентом не загрузили на хостинг
_FALLBACK_WORDS = [{"zh": "你好", "py": "nǐ hǎo", "hsk": 1, "ru": "Привет", "uz": "Salom", "en": "Hello"}]
_FALLBACK_CHENGYU = [{"zh": "加油", "py": "jiā yóu", "ru": "Давай, не сдавайся!", "uz": "Qani, harakat qil!",
                      "en": "Go for it!", "ex": "加油！"}]
_FALLBACK_FACTS = [{"ru": "🔴 Красный в Китае — цвет счастья и защиты.", "uz": "🔴 Qizil rang Xitoyda baxt ramzi.",
                    "en": "🔴 Red means luck in China.", "zh": "🔴 红色在中国象征幸福。"}]

def _load_translations():
    """Переводы для слов из автоматического списка: content_translations.txt (мои) и
    content_translations_auto.txt (если ты запускала translate_words.py).
    Формат строки: иероглифы | по-русски | по-узбекски | пиньинь (необязательно)."""
    out = {}
    for name in ("content_translations.txt", "content_translations_auto.txt"):
        for n, line in _lines(name, optional=(name != "content_translations.txt")):
            p = [x.strip() for x in line.split("|")]
            if len(p) not in (3, 4) or not all(p[:3]):
                logging.warning("%s, строка %d пропущена: %s", name, n, line[:60])
                continue
            out[p[0]] = {"ru": p[1], "uz": p[2], "py": p[3] if len(p) == 4 and p[3] else ""}
    return out


def _merge_words():
    """Приоритет: твои слова с переводом на три языка, затем твои списки HSK (русский),
    затем таблица HSK 2.0, затем автоматический список (только английский). Одно слово не повторяется."""
    dataset = _load_hsk()
    tr = _load_translations()
    for w in dataset:                                   # переводы поверх автоматического списка
        t_ = tr.get(w["zh"])
        if t_:
            w["ru"], w["uz"], w["own"] = t_["ru"], t_["uz"], True
            if t_["py"]:
                w["py"] = t_["py"]
    en_by_zh = {w["zh"]: w["en"] for w in dataset}
    out, seen = [], set()
    for group in (_load_words(), _load_hsk30(), _load_hsk5(), dataset):
        for w in group:
            if w["zh"] in seen:
                continue
            seen.add(w["zh"])
            if not w.get("en"):
                w["en"] = en_by_zh.get(w["zh"], "")
            w.setdefault("pos", ""); w.setdefault("scheme", ""); w.setdefault("examples", [])
            out.append(w)
    return out


WORDS = _merge_words() or _FALLBACK_WORDS
_OWN_CY = _load_chengyu()
_CY_ZH = {x["zh"] for x in _OWN_CY}
CHENGYU = (_OWN_CY + [x for x in _load_chengyu_big() if x["zh"] not in _CY_ZH]) or _FALLBACK_CHENGYU
FACTS = _load_facts() or _FALLBACK_FACTS


_FALLBACK = {"ru": ("ru", "en"), "uz": ("uz", "ru", "en"), "en": ("en", "ru"), "zh": ("zh", "en", "ru")}


def meaning_lang(item, lang):
    """На каком языке реально будет показано значение (ru, uz, en или zh)."""
    for k in _FALLBACK.get(lang, ("ru", "en")):
        if k == "zh" and "py" in item:         # у слов и чэнъюй «zh» это сам иероглиф, а не значение
            continue
        if item.get(k):
            return k
    return "en"


def meaning(item, lang):
    """Значение на языке человека; если его нет, то ближайшее доступное."""
    return item.get(meaning_lang(item, lang)) or ""


# ─── поиск по своим словам (для переводчика) ─────────────────────────────────

def _norm(s):
    s = re.sub(r"\([^)]*\)|«|»|[.!?…]", "", s.lower())
    return " ".join(s.split())


WORD_BY_ZH = {}
_BY_TEXT = {}
for _w in WORDS:
    if not _w.get("own"):
        continue                                   # большой список HSK в поиск по русскому не идёт
    WORD_BY_ZH.setdefault(_w["zh"], _w)
    for _lang in ("ru", "uz", "en"):
        _m = _w[_lang]
        keys = {_norm(_m)} | {_norm(x) for x in re.split(r"[,;/]", _m)}
        for _k in keys:
            if _k:
                _BY_TEXT.setdefault(_k, [])
                if _w not in _BY_TEXT[_k]:
                    _BY_TEXT[_k].append(_w)


def find_by_text(query):
    """Слова из наших списков по русскому, узбекскому или английскому значению. Сначала попроще."""
    found = list(_BY_TEXT.get(_norm(query), []))
    found.sort(key=lambda w: (0 if w["hsk"] == 0 else 1, w["hsk"] if w["hsk"] else 0))
    return found


# ─── грамматика ───────────────────────────────────────────────────────────────

def _load_grammar():
    """content_grammar.txt: @level, @model, @title, @text, @formula, @note и строки примеров через |."""
    out, cur = {}, None
    for n, line in _lines("content_grammar.txt"):
        if line.startswith("@level "):
            lvl = int(line.split(None, 1)[1]); out.setdefault(lvl, []); cur = {"level": lvl, "text": [], "formula": [], "note": [], "examples": []}
            continue
        if cur is None:
            continue
        if line.startswith("@model "):
            cur["num"] = int(line.split(None, 1)[1]); out[cur["level"]].append(cur)
        elif line.startswith("@title "):
            cur["title"] = line.split(None, 1)[1]
        elif line.startswith(("@text ", "@formula ", "@note ")):
            key, val = line[1:].split(None, 1)
            cur[key].append(val)
        else:
            p = [x.strip() for x in line.split("|")]
            if len(p) == 3 and all(p):
                cur["examples"].append(tuple(p))
            else:
                logging.warning("content_grammar.txt, строка %d пропущена: %s", n, line[:60])
    for lvl in out:
        out[lvl] = [m for m in out[lvl] if m.get("title") and "num" in m]
        out[lvl].sort(key=lambda m: m["num"])
    return {k: v for k, v in out.items() if v}


GRAMMAR = _load_grammar()


# ─── раздел 16+ (ругательства) ────────────────────────────────────────────────

def _load_adult():
    items = []
    for n, line in _lines("content_adult.txt"):
        p = [x.strip() for x in line.split("|")]
        if len(p) != 6 or not p[0] or not p[1] or p[2] not in ("1", "2", "3"):
            logging.warning("content_adult.txt, строка %d пропущена: %s", n, line[:60])
            continue
        items.append({"zh": p[0], "py": p[1], "rude": int(p[2]), "ru": p[3], "uz": p[4] or p[3], "en": p[5] or p[3]})
    return items


ADULT = _load_adult()


# ─── тексты для чтения ────────────────────────────────────────────────────────

def _load_texts():
    out, cur = [], None
    for n, line in _lines("content_texts.txt"):
        if line.startswith("@id "):
            cur = {"id": line.split(None, 1)[1], "kind": "adapted", "level": 0, "title": "", "image": "",
                   "zh": [], "py": [], "ru": ""}
            out.append(cur)
        elif cur is None or not line.startswith("@"):
            continue
        else:
            key, _, val = line[1:].partition(" ")
            val = val.strip()
            if key in ("zh", "py"):
                cur[key].append(val)
            elif key == "level" and val.isdigit():
                cur["level"] = int(val)
            elif key in ("kind", "title", "image", "ru"):
                cur[key] = val
    return [x for x in out if x["title"] and x["zh"] and x["kind"] in ("adapted", "classic")]


TEXTS = _load_texts()
