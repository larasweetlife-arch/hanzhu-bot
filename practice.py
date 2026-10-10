"""
Практика: викторина, флеш-карточки и «Чайная лавка».
Здесь только логика (без Telegram), чтобы её можно было проверить отдельно.
Кнопки и сообщения лежат в bot.py, тексты в texts_practice.py.
"""
import random
import re
from datetime import datetime, timedelta

import content as C

LIVES_PER_DAY = 5
QUIZ_LEN = 5
BOX_DAYS = [0, 1, 3, 7, 14, 30]          # через сколько дней карточка вернётся, по ящикам 0..5
NEW_PER_SESSION = 5

# ─── ВИКТОРИНА ────────────────────────────────────────────────────────────────


def short_meaning(item, lang, limit=38):
    m = (C.meaning(item, lang) or "").strip()
    m = re.split(r"\s*[;/]\s*", m)[0] if len(m) > limit else m
    return m if len(m) <= limit else m[:limit - 1].rstrip() + "…"


def _pool(lang, level):
    """Слова, у которых есть значение на языке человека, около его уровня."""
    own = [w for w in C.WORDS if C.meaning_lang(w, lang) == lang or (lang == "uz" and C.meaning_lang(w, lang) == "ru")]
    lo, hi = max(1, level - 1), max(2, level + 1)
    near = [w for w in own if lo <= w["hsk"] <= hi]
    return near if len(near) >= 20 else (own if len(own) >= 20 else C.WORDS)


def make_question(lang, level, rng=random, exclude=()):
    pool = _pool(lang, level)
    for _ in range(50):
        w = rng.choice(pool)
        if w["zh"] in exclude:
            continue
        right = short_meaning(w, lang)
        if not right:
            continue
        wrong, tries = [], 0
        while len(wrong) < 3 and tries < 200:
            tries += 1
            d = rng.choice(pool)
            m = short_meaning(d, lang)
            if d["zh"] != w["zh"] and m and m != right and m not in wrong:
                wrong.append(m)
        if len(wrong) < 3:
            continue
        options = wrong + [right]
        rng.shuffle(options)
        return {"zh": w["zh"], "py": w["py"], "hsk": w["hsk"], "options": options,
                "answer": options.index(right), "right": right}
    return None


# ─── МАРАФОН: 100 вопросов на HSK 1–3, 150 на HSK 4–6 ─────────────────────────

MARATHON_LEN = {1: 100, 2: 100, 3: 100, 4: 150, 5: 150, 6: 150}


def marathon_pool(lang, level):
    """Слова ровно этого уровня, у которых есть значение на языке человека.
    ru → русское, en/zh → английское, uz → узбекское, а если узбекских слов уровня мало, то русское."""
    base = [w for w in C.WORDS if w["hsk"] == level]
    if lang == "uz":
        uz = [w for w in base if C.meaning_lang(w, "uz") == "uz" and short_meaning(w, "uz")]
        if len(uz) >= MARATHON_LEN.get(level, 100):
            return uz
    want = "ru" if lang in ("ru", "uz") else "en"
    return [w for w in base if C.meaning_lang(w, lang) == want and short_meaning(w, lang)]


def marathon_question(lang, level, seen, rng=random, pool=None):
    """Вопрос без повторов (seen — уже заданные иероглифы). None, если слова уровня закончились."""
    pool = pool if pool is not None else marathon_pool(lang, level)
    taken = set(seen)
    fresh = [w for w in pool if w["zh"] not in taken]
    if not fresh:
        return None
    for _ in range(30):
        w = rng.choice(fresh)
        right = short_meaning(w, lang)
        wrong, tries = [], 0
        while len(wrong) < 3 and tries < 300:
            tries += 1
            m = short_meaning(rng.choice(pool), lang)
            if m and m != right and m not in wrong:
                wrong.append(m)
        if len(wrong) == 3:
            options = wrong + [right]
            rng.shuffle(options)
            return {"zh": w["zh"], "py": w["py"], "hsk": level, "options": options,
                    "answer": options.index(right), "right": right}
    return None


def marathon_title(correct, total):
    pct = correct * 100 // max(total, 1)
    return "hi" if pct >= 90 else "mid" if pct >= 70 else "low"


# ─── РЕЙТИНГ НЕДЕЛИ ───────────────────────────────────────────────────────────

BOARD_DAILY_CAP = 60        # больше стольких очков в день не засчитывается: выигрывает регулярность, а не марафон в одну ночь
BOARD_MIN_POINTS = 30       # минимум очков за неделю, чтобы получить приз
BOARD_TOP = 10


def week_bounds(day):
    """Понедельник и воскресенье недели, в которую попадает день (date) → строки YYYY-MM-DD."""
    monday = day - timedelta(days=day.weekday())
    return monday.strftime("%Y-%m-%d"), (monday + timedelta(days=6)).strftime("%Y-%m-%d")


def rank(rows, joined, exclude=()):
    """Таблица недели: только вступившие в рейтинг. Очки ↓, точность ↓, кто набрал раньше ↑."""
    out = []
    for r in rows:
        if r["user_id"] in joined and r["user_id"] not in exclude and (r["points"] or 0) > 0:
            total = (r["correct"] or 0) + (r["wrong"] or 0)
            out.append({**r, "acc": (r["correct"] or 0) / total if total else 0.0})
    out.sort(key=lambda r: (-r["points"], -r["acc"], r["last_at"] or ""))
    return out


def nick(name):
    """Что видят другие: только первое слово имени, до 14 знаков."""
    w = (name or "").split()
    return (w[0] if w else "—")[:14]


# ─── ФЛЕШ-КАРТОЧКИ ────────────────────────────────────────────────────────────

def next_due(box, today):
    """Дата следующего показа карточки из ящика box."""
    box = max(0, min(box, len(BOX_DAYS) - 1))
    return (datetime.strptime(today, "%Y-%m-%d") + timedelta(days=BOX_DAYS[box])).strftime("%Y-%m-%d")


def grade(box, known):
    """Знаю → ящик выше (но не выше последнего), не знаю → снова в ящик 0."""
    return min(box + 1, len(BOX_DAYS) - 1) if known else 0


def new_cards(lang, level, have, n=NEW_PER_SESSION, rng=random):
    """Новые слова для колоды: около уровня, ещё не в колоде."""
    pool = [w for w in _pool(lang, level) if w["zh"] not in have]
    rng.shuffle(pool)
    return pool[:n]


def word_by_zh(zh):
    for w in C.WORDS:
        if w["zh"] == zh:
            return w
    return None


# ─── ЧАЙНАЯ ЛАВКА ─────────────────────────────────────────────────────────────
# Всё содержимое своё: слова общеупотребительные, фразы составлены для бота.

TEAS = [
    {"zh": "绿茶", "py": "lǜchá", "ru": "зелёный чай", "uz": "yashil choy", "en": "green tea"},
    {"zh": "红茶", "py": "hóngchá", "ru": "красный (чёрный) чай", "uz": "qora choy", "en": "black tea"},
    {"zh": "乌龙茶", "py": "wūlóngchá", "ru": "улун", "uz": "ulun choyi", "en": "oolong tea"},
    {"zh": "普洱茶", "py": "pǔ'ěrchá", "ru": "пуэр", "uz": "puer choyi", "en": "pu-erh tea"},
    {"zh": "茉莉花茶", "py": "mòlìhuāchá", "ru": "жасминовый чай", "uz": "yasmin choyi", "en": "jasmine tea"},
    {"zh": "白茶", "py": "báichá", "ru": "белый чай", "uz": "oq choy", "en": "white tea"},
    {"zh": "菊花茶", "py": "júhuāchá", "ru": "хризантемовый чай", "uz": "xrizantema choyi", "en": "chrysanthemum tea"},
]
WARE = [
    {"zh": "茶壶", "py": "cháhú", "ru": "чайник", "uz": "choynak", "en": "teapot"},
    {"zh": "茶杯", "py": "chábēi", "ru": "чашка для чая", "uz": "choy piyolasi", "en": "teacup"},
    {"zh": "盖碗", "py": "gàiwǎn", "ru": "гайвань", "uz": "gaywan", "en": "gaiwan"},
    {"zh": "茶盘", "py": "chápán", "ru": "чайный поднос", "uz": "choy laganbari", "en": "tea tray"},
]
ADDS = [
    {"zh": "糖", "py": "táng", "ru": "сахар", "uz": "shakar", "en": "sugar"},
    {"zh": "蜂蜜", "py": "fēngmì", "ru": "мёд", "uz": "asal", "en": "honey"},
    {"zh": "牛奶", "py": "niúnǎi", "ru": "молоко", "uz": "sut", "en": "milk"},
    {"zh": "柠檬", "py": "níngméng", "ru": "лимон", "uz": "limon", "en": "lemon"},
    {"zh": "冰", "py": "bīng", "ru": "лёд", "uz": "muz", "en": "ice"},
    {"zh": "热水", "py": "rèshuǐ", "ru": "горячая вода", "uz": "issiq suv", "en": "hot water"},
]
TEMPLATES = {
    "tea": ("你好！我要一杯{zh}。", "Nǐ hǎo! Wǒ yào yì bēi {py}.", TEAS),
    "ware": ("请给我{zh}。", "Qǐng gěi wǒ {py}.", WARE),
    "add": ("我的茶要加{zh}。", "Wǒ de chá yào jiā {py}.", ADDS),
}
TITLES = [(0, "🥢", "title0"), (10, "🍃", "title1"), (30, "🏮", "title2"), (80, "🍵", "title3"), (200, "🏆", "title4")]


def tea_meaning(item, lang):
    return item.get(lang) or item.get("ru") if lang != "zh" else item["en"]


def tea_title(served):
    cur = TITLES[0]
    for row in TITLES:
        if served >= row[0]:
            cur = row
    return cur


def make_order(lang, rng=random, avoid=()):
    kind = rng.choice(list(TEMPLATES))
    zh_t, py_t, items = TEMPLATES[kind]
    cand = [i for i in items if i["zh"] not in avoid] or items
    item = rng.choice(cand)
    others = [i for i in items if i is not item]
    rng.shuffle(others)
    choices = [item] + others[:3]
    rng.shuffle(choices)
    return {"kind": kind, "zh": zh_t.format(zh=item["zh"]), "py": py_t.format(py=item["py"]),
            "item": item["zh"], "options": [tea_meaning(c, lang) for c in choices],
            "answer": choices.index(item), "right": tea_meaning(item, lang)}


def order_for_item(lang, zh, rng=random):
    """Тот же вопрос про слово из очереди повторов."""
    for kind, (zh_t, py_t, items) in TEMPLATES.items():
        for item in items:
            if item["zh"] == zh:
                others = [i for i in items if i is not item]
                rng.shuffle(others)
                choices = [item] + others[:3]
                rng.shuffle(choices)
                return {"kind": kind, "zh": zh_t.format(zh=item["zh"]), "py": py_t.format(py=item["py"]),
                        "item": zh, "options": [tea_meaning(c, lang) for c in choices],
                        "answer": choices.index(item), "right": tea_meaning(item, lang)}
    return None


# ─── РАЗБОР ВРЕМЕНИ ДЛЯ ПЕРЕНОСА УРОКА ────────────────────────────────────────

_ABBR = {"пн": 0, "вт": 1, "ср": 2, "чт": 3, "пт": 4, "сб": 5, "вс": 6}
_FULL = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]


def parse_when(text, now):
    """'чт 17:30' → ближайший четверг в 17:30; '15.10 17:30' → эта дата. Не поняла → None.
    Всегда в будущем и не дальше 30 дней."""
    s = " ".join(text.lower().replace(",", " ").split())
    m = re.fullmatch(r"(\d{1,2})\.(\d{1,2})(?:\.(\d{2,4}))?\s+(\d{1,2})[:.](\d{2})", s)
    if m:
        d, mo, y, h, mi = m.groups()
        year = int(y) + (2000 if y and len(y) == 2 else 0) if y else now.year
        try:
            dt = datetime(year, int(mo), int(d), int(h), int(mi), tzinfo=now.tzinfo)
        except ValueError:
            return None
        if not y and dt < now:
            try:
                dt = dt.replace(year=year + 1)
            except ValueError:
                return None
    else:
        m = re.fullmatch(r"([а-я]{2,})\.?\s+(\d{1,2})[:.](\d{2})", s)
        if not m:
            return None
        word, h, mi = m.group(1), int(m.group(2)), int(m.group(3))
        wd = _ABBR.get(word)
        if wd is None and len(word) >= 3:
            wd = next((i for i, n in enumerate(_FULL) if n.startswith(word)), None)
        if wd is None or h > 23 or mi > 59:
            return None
        for off in range(0, 8):
            day = (now + timedelta(days=off)).date()
            if day.weekday() == wd:
                dt = datetime(day.year, day.month, day.day, h, mi, tzinfo=now.tzinfo)
                if dt > now:
                    break
        else:
            return None
    if dt <= now or dt > now + timedelta(days=30):
        return None
    return dt


def parse_due(text, today):
    """Срок домашки: 'завтра', 'сегодня', '15.10', '-' (без срока). Возвращает 'YYYY-MM-DD', '' или None (не поняла)."""
    s = text.strip().lower()
    base = datetime.strptime(today, "%Y-%m-%d")
    if s in ("-", "нет", ""):
        return ""
    if s == "сегодня":
        return today
    if s == "завтра":
        return (base + timedelta(days=1)).strftime("%Y-%m-%d")
    if s == "послезавтра":
        return (base + timedelta(days=2)).strftime("%Y-%m-%d")
    m = re.fullmatch(r"(\d{1,2})\.(\d{1,2})", s)
    if m:
        try:
            dt = datetime(base.year, int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
        if dt < base:
            dt = dt.replace(year=base.year + 1)
        return dt.strftime("%Y-%m-%d")
    return None


# ─── НИКИ В РЕЙТИНГЕ (версия 10) ──────────────────────────────────────────────
# В таблице видны только ники. Кто за ником стоит, знает только владелица (команда /who).

NICK_MIN, NICK_MAX = 3, 16
NICK_CHANGE_DAYS = 7
_NICK_RE = re.compile(r"^[\w][\w .\-]*$", re.UNICODE)
_BAD_STEMS = ("хуй", "хуе", "пизд", "бляд", "блят", "ебан", "ебат", "ебл", "сука", "сучк", "мудак", "гандон", "залуп", "шлюх",
              "fuck", "shit", "bitch", "dick", "cunt", "nigg", "nazi", "hitler", "porn",
              "jalab", "qanjiq", "skay", "sikay", "ahmoq", "pidor", "пидор", "гитлер", "нацис", "порно", "секс")


def valid_nick(raw, real_names=()):
    """(ник, None) или (None, код_ошибки): nk_len, nk_chars, nk_bad, nk_name."""
    s = " ".join((raw or "").split())
    if not (NICK_MIN <= len(s) <= NICK_MAX):
        return None, "nk_len"
    if not _NICK_RE.match(s) or s.isdigit() or "t.me" in s.lower() or "http" in s.lower():
        return None, "nk_chars"
    low = s.lower().replace(" ", "").replace(".", "").replace("-", "").replace("_", "")
    if any(b in low for b in _BAD_STEMS):
        return None, "nk_bad"
    for n in real_names:
        n = (n or "").lower().strip()
        if len(n) >= 3 and (n in low or low in n):
            return None, "nk_name"
    return s, None


def anon_nick(uid):
    """Запасное имя для тех, кто вступил в рейтинг в версии 9 и ещё не выбрал ник."""
    return "Игрок-%03d" % (uid % 1000)


# ─── БЕЙДЖИ И ПОДАРОЧНЫЕ КОРОБКИ (Mini App) ───────────────────────────────────

BADGES = ["first", "served25", "served100", "streak3", "streak7", "gift7", "marathon", "marathon3", "friend", "ranked", "winner", "sharp"]


def badges(s):
    """s: словарь статистики → {id: получен ли}."""
    acc = s["correct"] / max(s["correct"] + s["wrong"], 1)
    return {
        "first": s["served"] >= 1, "served25": s["served"] >= 25, "served100": s["served"] >= 100,
        "streak3": s["play_streak"] >= 3, "streak7": s["play_streak"] >= 7, "gift7": s["gift_streak"] >= 7,
        "marathon": s["marathons"] >= 1, "marathon3": s["marathons"] >= 3, "friend": s["friends"] >= 1,
        "ranked": s["joined"], "winner": s["wins"] >= 1, "sharp": s["correct"] >= 50 and acc >= 0.9,
    }


def roll_gift(streak_after, rng=random):
    """Что лежит в коробке сегодня: ('coins', n) | ('lives', n) | ('word', 1). Каждый седьмой день подряд награда вдвое больше."""
    kind = rng.choices(["coins", "lives", "word"], weights=[60, 25, 15])[0]
    n = {"coins": rng.randint(3, 8), "lives": rng.randint(1, 2), "word": 1}[kind]
    if streak_after % 7 == 0 and kind != "word":
        n *= 2
    return kind, n
