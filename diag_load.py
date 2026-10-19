import sys, time, random
sys.argv=["x"]
import diag_smoke as D
import bot, db, quest
from datetime import datetime, timedelta
random.seed(1)
N=3000
today=datetime.now(db.TZ).date()
with db._conn() as c:
    for u in range(10000, 10000+N):
        c.execute("INSERT OR IGNORE INTO users (user_id,name,username,lang,level,source,created_at,is_student) VALUES (?,?,?,?,?,?,?,0)", (u,f"N{u}",f"u{u}",random.choice(["ru","uz","en","zh"]),"hsk1","t",today.isoformat()))
    kinds=["word","quiz","cards","tea","texts","fact","quest"]
    rows=[(random.randrange(10000,10000+N), random.choice(kinds), (today-timedelta(days=random.randrange(60))).isoformat()) for _ in range(300000)]
    c.executemany("INSERT INTO events (user_id,kind,date) VALUES (?,?,?)", rows)
    c.executemany("INSERT OR IGNORE INTO quest_score (user_id,day,pts) VALUES (?,?,?)", [(random.randrange(10000,10000+N),(today-timedelta(days=random.randrange(30))).isoformat(),random.randrange(5,90)) for _ in range(60000)])
print("данные готовы")
db.init()
def timeit(label, fn, n=5):
    t=time.time()
    for _ in range(n): fn()
    print(f"{label:35} {1000*(time.time()-t)/n:7.1f} мс")
uid=10001
timeit("db.stats-подобный запрос", lambda: bot.db.get_user(uid))
D.mkuser(uid,"ru")
for lb in ("📊 Мой прогресс","🏆 Рейтинг недели"):
    pass
def press(txt): D.run(D.msg_update(uid, txt, "ru"), txt)
for lb in sorted(bot.menu_labels("ru")):
    t=time.time(); D.CALLS.clear(); press(lb); dt=time.time()-t
    if dt>0.15: print(f"МЕДЛЕННО {dt*1000:.0f} мс  {lb}")
print("меню прогнано")

D.mkuser(1,"ru")
with db._conn() as c:
    c.execute("UPDATE users SET is_student=1 WHERE user_id BETWEEN 10000 AND 10040")
for cd in ("a:stats","a:students","a:sched","a:alumni","a:groups","a:hw","a:invite"):
    t=time.time(); D.run(D.cb_update(1, cd, "ru"), cd); print(f"{cd:12} {1000*(time.time()-t):6.0f} мс")
for cmd in ("/stats","/admin","/students","/start"):
    t=time.time(); D.run(D.msg_update(1, cmd, "ru"), cmd); print(f"{cmd:12} {1000*(time.time()-t):6.0f} мс")
import bot as B
for f in ("send_weekly","send_digest"):
    t=time.time(); getattr(B,f)(datetime.now(db.TZ)); print(f"{f:12} {1000*(time.time()-t):6.0f} мс")
print("PROBLEMS", D.PROBLEMS[:5])
