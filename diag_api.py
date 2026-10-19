import sys, json, time
sys.argv=["x"]
exec(open("../mock9.py").read().split("U = 7001")[0].replace('sys.path.insert(0, ".")','sys.path.insert(0, ".")'))
rules = sorted({(r.rule, tuple(sorted(r.methods - {"HEAD","OPTIONS"}))) for r in app.url_map.iter_rules() if not r.rule.startswith("/static")})
print(len(rules), "маршрутов")
import db
db.save_user(7100, name="API", lang="ru", level="HSK2", username="api")
bad = []
payloads = [{}, {"scene": None}, {"scene": 5, "idx": "x", "a": []}, {"item": "x" * 5000}, {"hero": 1, "gender": None}, [], "str", {"a": {"b": {}}}]
for rule, methods in rules:
    path = rule
    import re
    path = re.sub(r"<[^>]+>", "x", path)
    for m in methods:
        for pl in payloads if m == "POST" else [None]:
            try:
                if m == "GET":
                    r = cl.get(path, headers={"X-Init-Data": init(7100, "ru")})
                else:
                    r = cl.post(path, data=json.dumps(pl), content_type="application/json", headers={"X-Init-Data": init(7100, "ru")})
            except Exception as e:
                bad.append((m, path, repr(pl)[:40], "EXC " + repr(e)[:80])); continue
            if r.status_code >= 500:
                bad.append((m, path, repr(pl)[:40], r.status_code))
print("ОШИБОК 5xx/исключений:", len(bad))
seen=set()
for b in bad:
    k=(b[0],b[1],str(b[3]))
    if k in seen: continue
    seen.add(k); print("-", b)
