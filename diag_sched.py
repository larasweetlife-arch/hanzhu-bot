import sys, os, logging, io
sys.argv=["x"]
import diag_smoke as D
import bot, db, scheduler
from datetime import datetime, timedelta
logs = io.StringIO(); h = logging.StreamHandler(logs); h.setLevel(logging.WARNING); logging.getLogger().addHandler(h)
now0 = datetime.now(db.TZ)
for uid, lang in ((9301,"ru"),(9302,"uz"),(9303,"en"),(9304,"zh")):
    D.mkuser(uid, lang); db.save_user(uid, is_student=1, zoom_link='https://zoom.example/x')
    db.set_schedule(uid, [(w, "18:00") for w in range(7)])
    db.hw_add(uid, "Выучить 10 слов", (now0.date()).isoformat())
    db.hw_add(uid, "Старая домашка", (now0 - timedelta(days=3)).date().isoformat())
    db.game_save(uid, coins=50, served=12, streak=3) if hasattr(db, "game_save") else None
    db.score_add(uid, 5, 1, 0, 100)
    db.board_set(uid, True)
    db.nick_set(uid, f"Игрок{uid}") if hasattr(db, "nick_set") else None
errs = 0
t = now0.replace(hour=7, minute=0, second=0, microsecond=0)
for step in range(0, 8*24*4):       # неделя шагом 15 минут: напоминания, домашки, KPI, рейтинг, недельный отчёт
    now = t + timedelta(minutes=15*step)
    D.CUR["where"] = f"планировщик {now:%a %H:%M}"
    try:
        scheduler.tick(now, bot.send_reminder, bot.send_weekly, bot.send_digest, (bot.hw_hook, bot.kpi_hook, bot.board_hook, bot.parent_hook, bot.booking.hook))
    except Exception as e:
        errs += 1; D.PROBLEMS.append(("исключение планировщика", D.CUR["where"], repr(e)))
print("API-вызовов:", len(D.CALLS))
kinds = {}
for m, p in D.CALLS: kinds[m] = kinds.get(m, 0) + 1
print(kinds)
print("PROBLEMS:", D.PROBLEMS[:10])
print("LOG WARNINGS:\n" + "\n".join(sorted(set(logs.getvalue().splitlines()))[:15]))
import collections
c = collections.Counter()
for m, p in D.CALLS:
    c[(p.get("chat_id"), (p.get("text") or p.get("caption") or "")[:40].replace("\n"," "))] += 1
for k, v in sorted(c.items(), key=lambda x: str(x[0])): print(v, k)
