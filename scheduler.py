"""
Расписание и напоминания. Вся логика «кому и когда писать» здесь,
отправка сообщений — в bot.py. Так её можно проверить без Telegram.
"""
import re
import time
import logging
from datetime import datetime, timedelta, time as dtime

import db

_ABBR = {"пн": 0, "вт": 1, "ср": 2, "чт": 3, "пт": 4, "сб": 5, "вс": 6}
_FULL = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]


def parse_schedule(text):
    """'пн 18:00, ср 18:00' -> [(0,'18:00'), (2,'18:00')]. Ошибка формата -> ValueError."""
    slots = []
    for part in re.split(r"[,\n;]+", text):
        part = part.strip().lower()
        if not part:
            continue
        m = re.fullmatch(r"([а-я]{2,})\.?\s+(\d{1,2})[:.](\d{2})", part)
        if not m:
            raise ValueError(part)
        word, h, mi = m.group(1), int(m.group(2)), int(m.group(3))
        wd = _ABBR.get(word)
        if wd is None and len(word) >= 3:
            wd = next((i for i, n in enumerate(_FULL) if n.startswith(word)), None)
        if wd is None or h > 23 or mi > 59:
            raise ValueError(part)
        slot = (wd, f"{h:02d}:{mi:02d}")
        if slot not in slots:
            slots.append(slot)
    if not slots:
        raise ValueError("пусто")
    return sorted(slots)


def due(now, slots):
    """Какие напоминания пора отправить прямо сейчас.
    24h — за сутки (окно 2 часа), 1h — за час (окно 30 минут)."""
    out = []
    for offset in range(0, 3):
        day = now.date() + timedelta(days=offset)
        for s in slots:
            if s["weekday"] != day.weekday():
                continue
            h, m = map(int, s["time"].split(":"))
            lesson = datetime.combine(day, dtime(h, m), tzinfo=db.TZ)
            if lesson - timedelta(hours=24) <= now < lesson - timedelta(hours=22):
                out.append(("24h", s, lesson))
            if lesson - timedelta(hours=1) <= now < lesson - timedelta(minutes=30):
                out.append(("1h", s, lesson))
    return out


def tick(now, send_reminder, send_weekly):
    for kind, slot, lesson in due(now, db.all_schedules()):
        key = f"{kind}:{lesson.strftime('%Y-%m-%dT%H:%M')}"
        if db.was_sent(slot["user_id"], key):
            continue
        db.mark_sent(slot["user_id"], key)   # сперва отмечаем, чтобы не слать дважды
        try:
            send_reminder(kind, slot, lesson)
        except Exception as e:
            logging.warning("не удалось отправить напоминание %s: %s", key, e)

    # воскресенье после 20:00 — недельный отчёт владельцу
    if now.weekday() == 6 and now.hour >= 20:
        key = f"weekly:{now.date().isoformat()}"
        if not db.was_sent(0, key):
            db.mark_sent(0, key)
            try:
                send_weekly(now)
            except Exception as e:
                logging.warning("не удалось отправить отчёт: %s", e)


def loop(send_reminder, send_weekly, interval=60):
    while True:
        try:
            tick(datetime.now(db.TZ), send_reminder, send_weekly)
        except Exception:
            logging.exception("ошибка в планировщике")
        time.sleep(interval)
