"""
Каллиграфия (версия 25) и проверка тонов (версия 26): данные для карточки иероглифа в Mini App.

  · Порядок черт лежит в webapp_static/hz/s0..s15.json (Hanzi Writer читает их в браузере).
  · Разбор по ключам и составным частям: hanzi_parts.json (Make Me a Hanzi, LGPL-3.0+).
  · Ассоциации пишет Лазиза в content_assoc.txt: иероглиф | по-русски | по-узбекски | по-английски.
  · Значения составных частей: свой список на русском (RADICALS_RU), потом русское значение из списка слов,
    потом английское определение из Make Me a Hanzi.
Бот и Mini App только читают эти файлы. Если файла нет, карточка просто показывается без этой части.
"""
import json
import logging
import re
from pathlib import Path

import content as C
import db

BASE = Path(__file__).parent
STATIC = BASE / "webapp_static"
IDS = set("⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻？")
HAN = re.compile(r"[一-鿿]")
CYR = re.compile("[а-яёА-ЯЁ]")

RADICALS_RU = {
    "一": "один; горизонтальная черта", "丨": "вертикальная черта", "丶": "точка", "丿": "откидная влево",
    "二": "два", "亠": "«крышка»", "人": "человек", "亻": "человек", "儿": "ноги; человек", "入": "входить",
    "八": "восемь; разделять", "冂": "рамка", "冖": "покрытие; крыша", "冫": "лёд", "几": "столик", "凵": "ёмкость",
    "刀": "нож", "刂": "нож", "力": "сила", "勹": "обнимать", "匕": "ложка", "匚": "ящик", "十": "десять",
    "卜": "гадание", "卩": "печать", "厂": "утёс; навес", "厶": "личное", "又": "снова; рука", "口": "рот",
    "囗": "ограда", "土": "земля", "士": "учёный; воин", "夂": "идти", "夕": "вечер", "大": "большой",
    "女": "женщина", "子": "ребёнок", "宀": "крыша; дом", "寸": "дюйм; рука", "小": "маленький", "尸": "тело",
    "山": "гора", "川": "река", "巛": "река", "工": "работа", "己": "сам", "巾": "платок; ткань", "干": "сухой",
    "幺": "нить", "广": "навес; здание", "廴": "шаг", "廾": "руки", "弓": "лук", "彐": "рука; свиная голова",
    "彡": "узор; перья", "彳": "шаг", "心": "сердце", "忄": "сердце", "戈": "копьё", "户": "дверь", "戶": "дверь",
    "手": "рука", "扌": "рука", "支": "ветвь", "攵": "ударять", "攴": "ударять", "文": "письмо; текст",
    "斗": "ковш", "斤": "топор", "方": "сторона", "日": "солнце; день", "曰": "говорить", "月": "луна; месяц",
    "木": "дерево", "欠": "зевать; недоставать", "止": "остановиться", "歹": "смерть; плохое", "殳": "оружие",
    "毋": "не", "比": "сравнивать", "毛": "шерсть; волосы", "氏": "род; фамилия", "气": "пар; воздух", "水": "вода",
    "氵": "вода", "火": "огонь", "灬": "огонь", "爪": "коготь", "爫": "коготь", "父": "отец", "片": "ломоть; пластина",
    "牙": "зуб", "牛": "корова; бык", "牜": "корова; бык", "犬": "собака", "犭": "зверь; собака", "玉": "нефрит",
    "王": "правитель; нефрит", "瓜": "дыня", "瓦": "черепица", "甘": "сладкий", "生": "жизнь; рождаться",
    "用": "использовать", "田": "поле", "疒": "болезнь", "白": "белый", "皮": "кожа", "皿": "посуда", "目": "глаз",
    "矛": "копьё", "矢": "стрела", "石": "камень", "示": "алтарь; ритуал", "礻": "алтарь; ритуал", "禾": "злак",
    "穴": "отверстие; пещера", "立": "стоять", "竹": "бамбук", "⺮": "бамбук", "米": "рис", "糸": "шёлк; нить",
    "纟": "шёлк; нить", "缶": "кувшин", "网": "сеть", "罒": "сеть", "羊": "овца", "羽": "перо; крыло", "老": "старый",
    "耒": "плуг", "耳": "ухо", "聿": "кисть", "肉": "мясо", "⺼": "плоть; мясо", "臣": "чиновник", "自": "сам; из",
    "至": "достигать", "臼": "ступка", "舌": "язык", "舟": "лодка", "色": "цвет", "艸": "трава", "艹": "трава",
    "虍": "тигр", "虫": "насекомое", "血": "кровь", "行": "идти; ряд", "衣": "одежда", "衤": "одежда", "襾": "покрывать",
    "见": "видеть", "見": "видеть", "角": "рог; угол", "言": "речь", "讠": "речь", "谷": "долина", "豆": "бобы",
    "豕": "свинья", "豸": "зверь", "贝": "раковина; деньги", "貝": "раковина; деньги", "赤": "красный",
    "走": "идти; бежать", "足": "нога", "⻊": "нога", "身": "тело", "车": "повозка", "車": "повозка", "辛": "горький",
    "辶": "дорога; идти", "⻌": "дорога; идти", "阝": "холм; город", "酉": "вино; сосуд", "里": "деревня; внутри",
    "金": "металл; золото", "钅": "металл", "长": "длинный", "長": "длинный", "门": "ворота; дверь", "門": "ворота; дверь",
    "隹": "птичка", "雨": "дождь", "青": "зелёный; синий", "非": "не", "面": "лицо", "革": "кожа", "音": "звук",
    "页": "страница; голова", "頁": "страница; голова", "风": "ветер", "風": "ветер", "飞": "летать", "飛": "летать",
    "食": "еда", "饣": "еда", "首": "голова", "香": "аромат", "马": "лошадь", "馬": "лошадь", "骨": "кость",
    "高": "высокий", "髟": "волосы", "鬼": "дух", "鱼": "рыба", "魚": "рыба", "鸟": "птица", "鳥": "птица",
    "鹿": "олень", "麦": "пшеница", "麥": "пшеница", "麻": "конопля", "黄": "жёлтый", "黃": "жёлтый", "黑": "чёрный",
    "鼓": "барабан", "鼠": "мышь", "鼻": "нос", "齿": "зуб", "齒": "зуб", "龙": "дракон", "龍": "дракон",
    "夫": "муж; мужчина", "无": "нет", "不": "не", "天": "небо", "中": "середина", "上": "верх", "下": "низ",
}

_PARTS = None
_RU = None
_ASSOC = None
_STROKE_CHARS = None
_LISTS = None
_SINGLE = None


def _parts():
    global _PARTS
    if _PARTS is None:
        try:
            _PARTS = json.loads((BASE / "hanzi_parts.json").read_text(encoding="utf-8"))["p"]
        except Exception as e:
            logging.warning("hanzi_parts.json не загрузился: %s", e)
            _PARTS = {}
    return _PARTS


def _ru_extra():
    """content_hanzi_ru.txt: иероглиф | значение (для иероглифов, которых нет в списке слов отдельным словом)."""
    global _RU
    if _RU is None:
        _RU = {}
        path = BASE / "content_hanzi_ru.txt"
        if path.exists():
            for raw in path.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if line and not line.startswith("#") and "|" in line:
                    a, b = [x.strip() for x in line.split("|", 1)]
                    if len(a) == 1 and b:
                        _RU[a] = b
    return _RU


def _assoc():
    """content_assoc.txt: иероглиф | по-русски | по-узбекски (необязательно) | по-английски (необязательно)"""
    global _ASSOC
    if _ASSOC is None:
        _ASSOC = {}
        path = BASE / "content_assoc.txt"
        if path.exists():
            for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                p = [x.strip() for x in line.split("|")]
                if len(p) < 2 or len(p[0]) != 1 or not p[1]:
                    logging.warning("content_assoc.txt, строка %d пропущена: %s", n, line[:60])
                    continue
                _ASSOC[p[0]] = {"ru": p[1], "uz": p[2] if len(p) > 2 else "", "en": p[3] if len(p) > 3 else ""}
    return _ASSOC


def stroke_chars():
    """Иероглифы, для которых в webapp_static/hz есть порядок черт."""
    global _STROKE_CHARS
    if _STROKE_CHARS is None:
        _STROKE_CHARS = set()
        for f in (STATIC / "hz").glob("s*.json"):
            try:
                _STROKE_CHARS |= set(json.loads(f.read_text(encoding="utf-8")))
            except Exception as e:
                logging.warning("%s не прочитался: %s", f.name, e)
    return _STROKE_CHARS


def _single():
    """Однознаковые слова из общего списка: {иероглиф: слово}."""
    global _SINGLE
    if _SINGLE is None:
        _SINGLE = {}
        for w in C.WORDS:
            if len(w["zh"]) == 1 and w["zh"] not in _SINGLE:
                _SINGLE[w["zh"]] = w
    return _SINGLE


def level_of(ch):
    best = None
    for w in C.WORDS:
        if ch in w["zh"] and w.get("scheme") == "3.0" and w["hsk"]:
            best = w["hsk"] if best is None else min(best, w["hsk"])
    return best


def lists():
    """Иероглифы по уровням для экрана выбора (только с порядком черт): [{"level": 1, "chars": [...]}, ...]."""
    global _LISTS
    if _LISTS is None:
        have = stroke_chars()
        seen, by = set(), {}
        for w in C.WORDS:
            if w.get("scheme") != "3.0" or not w["hsk"] or w["hsk"] > 2:
                continue
            for ch in w["zh"]:
                if ch in have and ch not in seen:
                    seen.add(ch)
                    by.setdefault(w["hsk"], []).append(ch)
        _LISTS = [{"level": k, "chars": by[k]} for k in sorted(by)]
    return _LISTS


def _pick(d, lang):
    for k in {"ru": ("ru", "en"), "uz": ("uz", "ru", "en"), "en": ("en", "ru"), "zh": ("en", "ru")}.get(lang, ("ru", "en")):
        if d.get(k):
            return d[k]
    return ""


def _short_en(s):
    return re.split(r"[;,]", s or "")[0].strip()


def meaning_of_part(ch, lang):
    """Значение составной части: свой русский список, затем русское слово, затем английское определение."""
    if lang in ("ru", "uz", "zh"):
        if ch in RADICALS_RU:
            return RADICALS_RU[ch]
        w = _single().get(ch)
        if w and CYR.search(w.get("ru") or ""):
            return w["ru"]
        return _ru_extra().get(ch, "")                       # русского нет: лучше без значения, чем на английском
    w = _single().get(ch)
    if w and w.get("en"):
        return _short_en(w["en"])
    p = _parts().get(ch)
    return _short_en(p[5]) if p and p[5] else ""


def word_ru(ch, lang):
    """Значение самого иероглифа: однознаковое слово, иначе английское определение."""
    w = _single().get(ch)
    if w and (lang == "en" or CYR.search(w.get("ru") or "")):
        return C.meaning(w, lang)
    if lang != "en" and ch in _ru_extra():
        return _ru_extra()[ch]
    if w:
        return C.meaning(w, lang)
    p = _parts().get(ch)
    return _short_en(p[5]) if p and p[5] else ""


def pinyin_of(ch):
    w = _single().get(ch)
    if w:
        return w["py"]
    p = _parts().get(ch)
    return p[7] if p and len(p) > 7 else ""


def info(ch, lang="ru"):
    """Карточка одного иероглифа или None, если такого нет."""
    if len(ch) != 1 or not HAN.match(ch):
        return None
    p = _parts().get(ch)
    out = {"c": ch, "py": pinyin_of(ch), "meaning": word_ru(ch, lang), "level": level_of(ch),
           "writable": ch in stroke_chars(), "radical": None, "parts": [], "kind": "", "semantic": None, "phonetic": None,
           "assoc": _pick(_assoc().get(ch, {}), lang) or None, "words": []}
    if p:
        decomp, rad, kind, sem, pho = p[0], p[1], p[2], p[3], p[4]
        if rad and rad != ch:
            out["radical"] = {"c": rad, "m": meaning_of_part(rad, lang)}
        seen = []
        for c in decomp:
            if c not in IDS and c != ch and c not in seen:
                seen.append(c)
        out["parts"] = [{"c": c, "py": pinyin_of(c), "m": meaning_of_part(c, lang)} for c in seen]
        out["kind"] = kind or ""
        if kind == "pictophonetic":
            if sem:
                out["semantic"] = {"c": sem, "m": meaning_of_part(sem, lang)}
            if pho:
                out["phonetic"] = {"c": pho, "py": pinyin_of(pho)}
        if kind in ("ideographic", "pictographic") and lang == "en" and p[6]:
            out["hint"] = p[6]
    ws = []
    for w in C.WORDS:
        if len(w["zh"]) > 1 and ch in w["zh"] and w.get("scheme") == "3.0" and w["hsk"] and w["hsk"] <= 3:
            ws.append({"zh": w["zh"], "py": w["py"], "m": C.meaning(w, lang)})
            if len(ws) >= 5:
                break
    out["words"] = ws
    return out


# ── проверка тонов голосом (версия 26): кто видит кнопку 🎤 ──
def _cfg_init():
    with db._conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS hanzi_cfg (k TEXT PRIMARY KEY, v TEXT)")


def tones_mode():
    """'pilot' (по умолчанию): кнопка видна только владельцу; 'all': всем."""
    try:
        _cfg_init()
        with db._conn() as c:
            r = c.execute("SELECT v FROM hanzi_cfg WHERE k='tones'").fetchone()
        return r[0] if r else "pilot"
    except Exception:
        logging.exception("tones_mode")
        return "pilot"


def tones_set(v):
    _cfg_init()
    with db._conn() as c:
        c.execute("INSERT OR REPLACE INTO hanzi_cfg (k, v) VALUES ('tones', ?)", (v,))


def tones_for(uid, owner_id):
    return bool(uid) and (uid == owner_id or tones_mode() == "all")
