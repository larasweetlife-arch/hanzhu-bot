import sys
sys.argv=["x"]
import diag_smoke as D
import bot, db, content as C
D.mkuser(9401,"ru")
print("слов", len(C.WORDS), "чэнъюй", len(C.CHENGYU), "фактов", len(C.FACTS), "текстов", len(C.TEXTS), "адалт", len(C.ADULT), "грамматика", sum(len(v) for v in C.GRAMMAR.values()))
orig_pick = bot.pick
state = {"i": 0}
def fake_pick(uid, kind, items, key, **kw):
    return items[state["i"] % len(items)]
bot.pick = fake_pick
import time
t0=time.time()
for lang in ("ru","uz","en","zh"):
    db.save_user(9401, lang=lang)
    for name, items, fn in (("word", C.WORDS, bot.send_word), ("chengyu", C.CHENGYU, bot.send_chengyu), ("fact", C.FACTS, bot.send_fact)):
        step = max(1, len(items)//2500)       # до 2500 элементов на вид
        for i in range(0, len(items), step):
            state["i"] = i
            D.CUR["where"] = f"[{lang}] {name} #{i}"
            try: fn(9401)
            except Exception as e: D.PROBLEMS.append(("исключение", D.CUR["where"], repr(e)[:100]))
    for lvl, models in C.GRAMMAR.items():
        for idx in range(len(models)):
            D.CUR["where"] = f"[{lang}] grammar {lvl}:{idx}"
            txt, kb = bot.grammar_view(lang, lvl, idx)
            D.PROBLEMS += [("текст > 4096", D.CUR["where"], str(len(txt)))] if len(txt) > 4096 else []
            e = D.check_html(txt)
            if e: D.PROBLEMS.append(("битый HTML", D.CUR["where"], e))
    for kind in ("adapted", "classic"):
        lvls = sorted({y["level"] for y in C.TEXTS if y["kind"] == kind}) or [0]
        for lvl in lvls:
            items = bot.texts_list(kind, lvl)
            for idx in range(len(items)):
                D.CUR["where"] = f"[{lang}] text {kind} {lvl}:{idx}"
                txt, kb, x = bot.text_view(lang, kind, lvl, idx)
                lim = 1024 if (x.get("image") and len(txt) <= 1000) else 4096
                if len(txt) > 4096: D.PROBLEMS.append(("текст > 4096", D.CUR["where"], str(len(txt))))
                e = D.check_html(txt)
                if e: D.PROBLEMS.append(("битый HTML", D.CUR["where"], e))
    for i in range(len(C.ADULT)):
        state["i"] = i
        D.CUR["where"] = f"[{lang}] adult {i}"
        try:
            txt, kb = bot.adult_item_view(lang, 9401)
        except Exception as e:
            D.PROBLEMS.append(("исключение", D.CUR["where"], repr(e)[:100])); continue
        e = D.check_html(txt)
        if e: D.PROBLEMS.append(("битый HTML", D.CUR["where"], e))
print("время", round(time.time()-t0,1), "с")
import collections
agg = collections.OrderedDict()
for k, w, d in D.PROBLEMS: agg.setdefault((k, d), []).append(w)
print("ПРОБЛЕМ:", len(agg))
for (k, d), ws in list(agg.items())[:25]: print("-", k, d, "|", ws[0], f"(+{len(ws)-1})" if len(ws)>1 else "")
