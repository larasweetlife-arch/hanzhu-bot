# -*- coding: utf-8 -*-
"""Строит из ch1_src.py: ch1.json (для игры) и ch1_review.md (для проверки Ларой).
Пиньинь = pypinyin + ручные исключения + правила 不/一 + эрхуа + апостроф."""
import json, random, re, sys, unicodedata
from pypinyin import pinyin, Style
import ch1_src as S

PUNCT = "，。！？、：；"
# ручные исключения (слово → слоги). Всё, что pypinyin читает неверно/не по учебнику.
FIX = {
    "谢谢": ["xiè", "xie"], "走得": ["zǒu", "de"], "玩得": ["wán", "de"],
    "照片": ["zhào", "piàn"], "了不起": ["liǎo", "bu", "qǐ"], "笑一笑": ["xiào", "yi", "xiào"],
    "便宜": ["pián", "yi"], "怎么样": ["zěn", "me", "yàng"], "师傅": ["shī", "fu"],
    "阿姨": ["ā", "yí"], "休息": ["xiū", "xi"], "意思": ["yì", "si"], "名字": ["míng", "zi"],
    "客气": ["kè", "qi"], "不客气": ["bú", "kè", "qi"], "学生": ["xué", "sheng"],
    "什么": ["shén", "me"], "护照": ["hù", "zhào"], "没问题": ["méi", "wèn", "tí"],
    "东西": ["dōng", "xi"], "喜欢": ["xǐ", "huan"], "我们": ["wǒ", "men"], "你们": ["nǐ", "men"],
    "你们": ["nǐ", "men"], "朋友": ["péng", "you"], "台阶": ["tái", "jiē"], "慢慢": ["màn", "màn"],
    "包子": ["bāo", "zi"], "饺子": ["jiǎo", "zi"], "地方": ["dì", "fang"], "晚安": ["wǎn", "ān"],
    "听说": ["tīng", "shuō"], "好汉": ["hǎo", "hàn"], "先": ["xiān"], "那边": ["nà", "bian"],
    "前面": ["qián", "mian"], "路上": ["lù", "shang"], "上来": ["shàng", "lái"],
    "担心": ["dān", "xīn"], "出发": ["chū", "fā"], "欢迎": ["huān", "yíng"],
    "光临": ["guāng", "lín"], "预订": ["yù", "dìng"], "一直": ["yì", "zhí"],
    "然后": ["rán", "hòu"], "年轻": ["nián", "qīng"], "快": ["kuài"], "两": ["liǎng"],
    "长城": ["cháng", "chéng"], "长": ["cháng"], "还": ["hái"], "会": ["huì"],
    "的": ["de"], "了": ["le"], "吗": ["ma"], "吧": ["ba"], "啊": ["a"], "呢": ["ne"],
    "得": ["de"], "着": ["zhe"], "辣的": ["là", "de"],
}
CAP_ALWAYS = set()
FIX.update({"哇": ["wā"], "对不起": ["duì", "bu", "qǐ"], "上来": ["shàng", "lai"]})
PY_STR = {"不客气": "bú kèqi", "你好": "nǐ hǎo", "笑一笑": "xiào yi xiào", "不到": "bú dào", "十二点": "shí'èr diǎn"}
SPACED = {"七点", "九点", "九点半", "十二点", "三点", "八点"}


def strip_tone(s):
    d = unicodedata.normalize("NFD", s)
    d = "".join(c for c in d if c not in "̄́̌̀")
    return unicodedata.normalize("NFC", d)


MARKS = {"̄": 1, "́": 2, "̌": 3, "̀": 4}
TONE_CH = {1: "̄", 2: "́", 3: "̌", 4: "̀"}


def tone_of(syl):
    for c in unicodedata.normalize("NFD", syl):
        if c in MARKS:
            return MARKS[c]
    return 5


def set_tone(syl, t):
    base = strip_tone(syl)
    if t == 5:
        return base
    low = base.lower()
    idx = None
    for ch in "ae":
        if ch in low:
            idx = low.index(ch)
            break
    if idx is None and "ou" in low:
        idx = low.index("o")
    if idx is None:
        for i in range(len(low) - 1, -1, -1):
            if low[i] in "aeiouü":
                idx = i
                break
    if idx is None:
        return base
    return unicodedata.normalize("NFC", base[:idx + 1] + TONE_CH[t] + base[idx + 1:])


def join_syl(sylls):
    out = ""
    for s in sylls:
        if out and s[0] in "aoeāáǎàōóǒòēéěè":
            out += "'"
        out += s
    return out


def token_syllables(h):
    """слоги токена: (список, зафиксирован ли вручную)"""
    if h in FIX:
        return list(FIX[h]), True
    res = pinyin(h, style=Style.TONE)
    sylls = [x[0] for x in res]
    # эрхуа: ...儿 в конце многосложного слова → r к предыдущему слогу
    if len(h) > 1 and h.endswith("儿") and len(sylls) >= 2:
        sylls = sylls[:-2] + [sylls[-2] + "r"]
        hs = h
    chars = [c for c in h if "\u4e00" <= c <= "\u9fff"]
    if len(sylls) != len(chars) and not h.endswith("儿"):
        print("MISMATCH", h, sylls)
    return sylls, False


def parse_line(zh):
    """→ список элементов: {'h','p'} | {'x'} | {'name':True}"""
    items = []
    for raw in zh.split("|"):
        raw = raw.strip()
        cap = raw.startswith("^")
        if cap:
            raw = raw[1:]
        trail = ""
        while raw and raw[-1] in PUNCT:
            trail = raw[-1] + trail
            raw = raw[:-1]
        if raw == "{name}":
            items.append({"name": True})
        elif raw:
            items.append({"h": raw, "cap": cap})
        for p in trail:
            items.append({"x": p})
    return items


def render(items):
    """проставить пиньинь + сандхи через границы слов"""
    flat = []  # (item_idx, syl_idx)
    for i, it in enumerate(items):
        if "h" in it:
            sylls, fixed = token_syllables(it["h"])
            it["_s"] = sylls
            it["_fixed"] = fixed
            # соответствие слог ↔ иероглиф (для 不/一); эрхуа сдвигает, поэтому только при равной длине
            it["_chars"] = list(it["h"]) if len(it["h"]) == len(sylls) else [None] * len(sylls)
            for j in range(len(sylls)):
                flat.append((i, j))
    for k, (i, j) in enumerate(flat):
        it = items[i]
        if it["_fixed"]:
            continue
        ch = it["_chars"][j]
        if ch not in ("不", "一"):
            continue
        # следующий слог
        nxt = None
        if k + 1 < len(flat):
            ni, nj = flat[k + 1]
            # если между ними знак препинания — не меняем
            between = items[i + 1:ni]
            if not any("x" in b for b in between):
                nxt = items[ni]["_s"][nj]
        if nxt is None:
            continue
        t = tone_of(nxt)
        if ch == "不":
            it["_s"][j] = "bú" if t == 4 else "bù"
        else:
            it["_s"][j] = "yí" if t == 4 else ("yì" if t in (1, 2, 3) else "yī")
    out = []
    for it in items:
        if "h" in it:
            p = PY_STR.get(it["h"]) or (" ".join(it["_s"]) if it["h"] in SPACED else join_syl(it["_s"]))
            if it["cap"]:
                p = p[0].upper() + p[1:]
            out.append({"h": it["h"], "p": p})
        elif "name" in it:
            out.append({"name": True})
        else:
            out.append(it)
    return out


ASCII = {"，": ",", "。": ".", "！": "!", "？": "?", "、": ","}


def plain_pinyin(items):
    s = ""
    for it in items:
        if "p" in it:
            s += (" " if s else "") + it["p"]
        elif "name" in it:
            s += (" " if s else "") + "{name}"
        else:
            s += ASCII.get(it["x"], it["x"])
    import re as _re
    if not any("x" in it for it in items):
        return s
    s = _re.sub(r"(^|[.!?] )([a-zāáǎàēéěèīíǐìōóǒòūúǔùüǖǘǚǜ])", lambda m: m.group(1) + m.group(2).upper(), s)
    return s


def plain_hanzi(items):
    return "".join(it.get("h", "") or ("{name}" if it.get("name") else it.get("x", "")) for it in items)


def tone_variants(h):
    sylls, _ = token_syllables(h)
    sylls = [s for s in FIX.get(h, sylls)]
    correct = join_syl(sylls)
    rng = random.Random(h)
    variants = set()
    tries = 0
    while len(variants) < 3 and tries < 200:
        tries += 1
        new = list(sylls)
        n = rng.choice([1, len(sylls)]) if len(sylls) > 1 else 1
        for idx in rng.sample(range(len(sylls)), n):
            new[idx] = set_tone(sylls[idx], rng.choice([1, 2, 3, 4, 5]))
        v = join_syl(new)
        if v != correct:
            variants.add(v)
    return correct, sorted(variants)


def build():
    data = {"chapter": S.CHAPTER, "cast": S.CAST, "scenes": []}
    review_tokens = {}
    for sc in S.SCENES:
        out = {k: sc[k] for k in ("id", "title_ru", "bg", "cast", "obstacle_ru", "culture_ru") if k in sc}
        out["boss"] = bool(sc.get("boss"))
        out["title"] = render(parse_line(sc["title"]))
        lines = []
        for who, zh, ru in sc["dialogue"]:
            its = render(parse_line(zh))
            lines.append({"who": who, "zh": its, "ru": ru})
            for it in its:
                if "h" in it:
                    review_tokens.setdefault(it["h"], it["p"])
        out["dialogue"] = lines
        tasks = []
        for t in sc["tasks"]:
            d = {"t": t["t"]}
            if t["t"] == "rp":
                d["who"] = t["who"]
                d["npc"] = render(parse_line(t["npc"]))
                d["opts"] = [render(parse_line(o)) for o in t["opts"]]
                d["ok"] = t["ok"]
            elif t["t"] == "hz":
                d["emoji"] = t["emoji"]
                d["opts"] = []
                for o in t["opts"]:
                    r = render(parse_line(o))
                    d["opts"].append(r)
                d["ok"] = t["ok"]
            elif t["t"] == "tn":
                correct, vars_ = tone_variants(t["w"])
                d["h"] = t["w"]
                d["correct"] = correct
                d["wrong"] = vars_
            elif t["t"] == "od":
                d["words"] = [x for x in render(parse_line("|".join(t["words"]))) if "h" in x]
                d["end"] = t["end"]
                d["hint_ru"] = t["hint_ru"]
            elif t["t"] == "mt":
                d["pairs"] = []
                for h, x in t["pairs"]:
                    r = render(parse_line(h))[0]
                    d["pairs"].append({"h": r["h"], "p": r["p"], "x": x})
            elif t["t"] == "tr":
                d["zh"] = render(parse_line(t["zh"]))
                d["opts_ru"] = t["opts_ru"]
                d["ok"] = 0
            for key in ("npc", "zh"):
                for it in d.get(key, []) if isinstance(d.get(key), list) else []:
                    if "h" in it:
                        review_tokens.setdefault(it["h"], it["p"])
            for lst in d.get("opts", []):
                if isinstance(lst, list):
                    for it in lst:
                        if "h" in it:
                            review_tokens.setdefault(it["h"], it["p"])
            tasks.append(d)
        out["tasks"] = tasks
        data["scenes"].append(out)
    return data, review_tokens


TYPE_RU = {"rp": "Ответь собеседнику", "hz": "Найди иероглиф", "tn": "Выбери тоны",
           "od": "Собери предложение", "mt": "Найди пары", "tr": "Выбери перевод"}


def md(data):
    L = []
    c = data["chapter"]
    L.append(f"# {c['title_zh']} · {c['title_ru']}")
    L.append("")
    L.append(f"Город: {c['city_ru']} · Уровень: {c['level']} · Цель: {c['goal_ru']}")
    L.append(f"{c['next_ru']}")
    L.append("")
    L.append("**Как читать.** В игре весь текст на китайском: иероглифы + пиньинь над каждым словом. "
             "Русский перевод открывается по нажатию на реплику. `{name}` — ник героя. "
             "✅ — правильный ответ.")
    L.append("")
    total = 0
    for i, sc in enumerate(data["scenes"], 1):
        L.append(f"## Сцена {i}. {plain_hanzi(sc['title'])} ({plain_pinyin(sc['title'])}) · {sc['title_ru']}")
        L.append(f"*Фон:* {sc['bg']}. *Персонажи:* " + ", ".join(
            f"{data['cast'][w]['zh']} ({data['cast'][w]['py']})" for w in sc['cast']) + ".")
        L.append(f"*Препятствие:* {sc['obstacle_ru']}.")
        L.append("")
        L.append("| Кто | 汉字 | Pinyin | Перевод |")
        L.append("|---|---|---|---|")
        for ln in sc["dialogue"]:
            who = data["cast"][ln["who"]]
            nm = "Герой" if ln["who"] == "me" else f"{who['zh']}"
            L.append(f"| {nm} | {plain_hanzi(ln['zh'])} | {plain_pinyin(ln['zh'])} | {ln['ru']} |")
        L.append("")
        L.append(f"*Заметка о культуре:* {sc['culture_ru']}")
        L.append("")
        L.append("**Задания**")
        L.append("")
        for k, t in enumerate(sc["tasks"], 1):
            total += 1
            head = f"{k}. *{TYPE_RU[t['t']]}*: "
            if t["t"] == "rp":
                L.append(head + f"{data['cast'][t['who']]['zh']} говорит «{plain_hanzi(t['npc'])}» ({plain_pinyin(t['npc'])})")
                for j, o in enumerate(t["opts"]):
                    L.append(f"   - {'✅ ' if j == t['ok'] else ''}{plain_hanzi(o)} ({plain_pinyin(o)})")
            elif t["t"] == "hz":
                L.append(head + f"картинка {t['emoji']}, выбрать иероглиф")
                for j, o in enumerate(t["opts"]):
                    L.append(f"   - {'✅ ' if j == t['ok'] else ''}{plain_hanzi(o)} ({plain_pinyin(o)})")
            elif t["t"] == "tn":
                L.append(head + f"слово {t['h']}, выбрать правильное чтение")
                L.append(f"   - ✅ {t['correct']}")
                for w in t["wrong"]:
                    L.append(f"   - {w}")
            elif t["t"] == "od":
                ws = " · ".join(f"{plain_hanzi([w])} ({w['p']})" for w in t["words"])
                L.append(head + f"слова перемешаны ({t['hint_ru']}). Правильный порядок: {ws} {t['end']}")
            elif t["t"] == "mt":
                L.append(head + "соединить: " + "; ".join(f"{p['h']} ({p['p']}) ↔ {p['x']}" for p in t["pairs"]))
            elif t["t"] == "tr":
                L.append(head + f"{plain_hanzi(t['zh'])} ({plain_pinyin(t['zh'])})")
                for j, o in enumerate(t["opts_ru"]):
                    L.append(f"   - {'✅ ' if j == 0 else ''}{o}")
        L.append("")
    L.append(f"**Итого:** {len(data['scenes'])} сцен, {total} заданий.")
    return "\n".join(L)


if __name__ == "__main__":
    data, toks = build()
    json.dump(data, open("ch1_build.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open("ch1_review.md", "w", encoding="utf-8").write(md(data))
    # отчёт для ручной сверки: все токены + многозначные
    print("TOKENS", len(toks))
    for h, p in sorted(toks.items(), key=lambda x: x[0]):
        multi = ""
        try:
            hp = pinyin(h, style=Style.TONE, heteronym=True)
            if any(len(x) > 1 for x in hp):
                multi = "  ← многозначный: " + "/".join("|".join(x) for x in hp)
        except Exception:
            pass
        print(f"{h}\t{p}{multi}")


def doc_sections(data):
    """Секции для Claude Docs: список (имя, markdown)."""
    secs = []
    for i, sc in enumerate(data["scenes"], 1):
        L = []
        L.append(f"## Сцена {i}. {sc['title_ru']} · {plain_hanzi(sc['title'])} {plain_pinyin(sc['title'])}")
        cast = ", ".join(f"{data['cast'][w]['zh']} {data['cast'][w]['py']}" for w in sc["cast"])
        L.append(f"Фон: {sc['bg']}. Персонажи: {cast}. Препятствие: {sc['obstacle_ru']}.")
        L.append("")
        L.append("| Кто | 汉字 | Pinyin | Перевод |")
        L.append("| --- | --- | --- | --- |")
        for ln in sc["dialogue"]:
            who = data["cast"][ln["who"]]
            nm = "Герой" if ln["who"] == "me" else who["zh"]
            L.append(f"| {nm} | {plain_hanzi(ln['zh'])} | {plain_pinyin(ln['zh'])} | {ln['ru']} |")
        L.append("")
        L.append(f"Заметка о культуре: {sc['culture_ru']}")
        L.append("")
        L.append("Задания:")
        L.append("")
        for k, t in enumerate(sc["tasks"], 1):
            head = f"{k}. {TYPE_RU[t['t']]}: "
            if t["t"] == "rp":
                L.append(head + f"{data['cast'][t['who']]['zh']} говорит «{plain_hanzi(t['npc'])}» ({plain_pinyin(t['npc'])})")
                for j, o in enumerate(t["opts"]):
                    L.append(f"    - {'✅ ' if j == t['ok'] else ''}{plain_hanzi(o)} ({plain_pinyin(o)})")
            elif t["t"] == "hz":
                L.append(head + f"картинка {t['emoji']}, выбрать иероглиф")
                for j, o in enumerate(t["opts"]):
                    L.append(f"    - {'✅ ' if j == t['ok'] else ''}{plain_hanzi(o)} ({plain_pinyin(o)})")
            elif t["t"] == "tn":
                L.append(head + f"слово {t['h']}, выбрать правильное чтение")
                L.append(f"    - ✅ {t['correct']}")
                for w in t["wrong"]:
                    L.append(f"    - {w}")
            elif t["t"] == "od":
                ws = " · ".join(f"{plain_hanzi([w])} ({w['p']})" for w in t["words"])
                L.append(head + f"слова перемешаны ({t['hint_ru']}). Правильный порядок: {ws} {t['end']}")
            elif t["t"] == "mt":
                L.append(head + "соединить: " + "; ".join(f"{p['h']} ({p['p']}) ↔ {p['x']}" for p in t["pairs"]))
            elif t["t"] == "tr":
                L.append(head + f"{plain_hanzi(t['zh'])} ({plain_pinyin(t['zh'])})")
                for j, o in enumerate(t["opts_ru"]):
                    L.append(f"    - {'✅ ' if j == 0 else ''}{o}")
        secs.append((sc["id"], "\n".join(L)))
    return secs
