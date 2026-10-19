"""Диагностика Mini App: открываем в мобильном браузере, жмём каждую видимую кнопку (на свежей загрузке),
ловим ошибки JS, упавшие запросы к API и кнопки, после нажатия на которые ничего не меняется."""
import sys, hashlib
exec(open("shoot_q.py").read())
import time as _t

def mkuser(uid, name, lang, done, coins=0, lives=5, gender="m", skin=0):
    db.save_user(uid, name=name, lang=lang, level="HSK2", username=f"u{uid}")
    quest.char_save(uid, name, gender, skin, 0, 0)
    with db._conn() as c:
        for i in range(done):
            c.execute("INSERT OR IGNORE INTO quest_prog (user_id, scene_id, done_day) VALUES (?,?,?)", (uid, f"s{i+1}", "2026-10-01"))
        c.execute("UPDATE quest_char SET coins=?, lives=?, lives_ts=? WHERE user_id=?", (coins, lives, _t.time()-600, uid))
        c.execute("INSERT OR IGNORE INTO quest_score (user_id, day, pts) VALUES (?,?,?)", (uid, db.today(), 10*done+7))
mkuser(201, "Лина", "ru", 0)
mkuser(202, "Aziz", "uz", 10, 130, 3, "m", 2)
mkuser(203, "Mei", "en", 18, 220, 5, "f", 1)

PROBLEMS = []
SKIP = ("quest-btn-pay", )

def snapshot(page):
    return hashlib.md5(page.evaluate("document.body.innerHTML").encode()).hexdigest()

def crawl(p, uid, lang, url_suffix=""):
    br = p.chromium.launch()
    ctx = br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
    def fresh():
        page = ctx.new_page(); errs = []
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e)))
        page.on("response", lambda r: errs.append(f"HTTP {r.status} {r.url[-60:]}") if r.status >= 400 and "/api/" in r.url else None)
        page.route("**/telegram.org/**", lambda r: r.fulfill(content_type="application/javascript", body=STUB % (json.dumps(sign(uid, lc=lang)), lang, "light")))
        page.route("**/fonts.googleapis.com/**", lambda r: r.abort())
        page.goto("http://127.0.0.1:8766/" + url_suffix)
        page.wait_for_timeout(1400)
        return page, errs
    page, errs = fresh()
    sel = "button:visible, [role=button]:visible, .tab:visible, nav a:visible, .qnode:visible, .qbtn:visible, .opt:visible"
    n = page.locator(sel).count()
    labels = []
    for i in range(n):
        try:
            labels.append(page.locator(sel).nth(i).inner_text(timeout=500).strip().replace("\n", " ")[:40] or f"#{i}")
        except Exception:
            labels.append(f"#{i}")
    if errs:
        PROBLEMS.append((f"[{lang}] загрузка {url_suffix}", errs[:3]))
    page.close()
    print(f"[{lang} u{uid} {url_suffix or '/'}] кнопок: {n}")
    for i in range(min(n, 45)):
        page, errs = fresh()
        try:
            loc = page.locator(sel).nth(i)
            before = snapshot(page)
            loc.click(timeout=2500)
            page.wait_for_timeout(700)
            after = snapshot(page)
            if before == after and not page.evaluate("window.__opened||window.__inv||''"):
                PROBLEMS.append((f"[{lang}] кнопка «{labels[i]}» ничего не изменила", []))
            if errs:
                PROBLEMS.append((f"[{lang}] после «{labels[i]}»", errs[:3]))
        except Exception as e:
            PROBLEMS.append((f"[{lang}] кнопку «{labels[i]}» не удалось нажать", [str(e)[:120]]))
        page.close()
    br.close()

with sync_playwright() as p:
    crawl(p, 201, "ru")
    crawl(p, 201, "ru", "?tab=quest")
    crawl(p, 202, "uz", "?tab=quest")
    crawl(p, 203, "en")
    crawl(p, 203, "en", "?tab=quest")
print("\n=== ПРОБЛЕМЫ Mini App ===", len(PROBLEMS))
seen = set()
for w, e in PROBLEMS:
    k = (w, tuple(e))
    if k in seen: continue
    seen.add(k)
    print("-", w, e)
