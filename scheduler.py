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


def occurrences(now, slots, moves=(), days=3, start_offset=0):
    """Все занятия на ближайшие дни: [(datetime, slot)], с учётом подтверждённых переносов.
    slots — строки расписания (с user_id); moves — подтверждённые переносы {user_id, orig, new}."""
    moved_from = {(m["user_id"], m["orig"]) for m in moves}
    out = []
    for offset in range(start_offset, start_offset + days):
        day = now.date() + timedelta(days=offset)
        for s in slots:
            if s["weekday"] != day.weekday():
                continue
            h, mi = map(int, s["time"].split(":"))
            lesson = datetime.combine(day, dtime(h, mi), tzinfo=db.TZ)
            if (s["user_id"], lesson.strftime("%Y-%m-%dT%H:%M")) in moved_from:
                continue
            out.append((lesson, s))
    by_user = {}
    for s in slots:
        by_user.setdefault(s["user_id"], s)
    first_day = now.date() + timedelta(days=start_offset)
    last_day = first_day + timedelta(days=days)
    for m in moves:
        if (m["user_id"], m["new"]) in moved_from:      # этот перенос сам потом перенесли
            continue
        new = datetime.strptime(m["new"], "%Y-%m-%dT%H:%M").replace(tzinfo=db.TZ)
        if first_day <= new.date() < last_day:
            base = dict(by_user.get(m["user_id"]) or {})
            if not base:                                  # у ученика уже нет расписания: данные берём из профиля
                u = db.get_user(m["user_id"]) or {}
                base = {"user_id": m["user_id"], "name": u.get("name"), "lang": u.get("lang"),
                        "zoom_link": u.get("zoom_link")}
            base.update({"weekday": new.weekday(), "time": new.strftime("%H:%M"), "moved": True})
            out.append((new, base))
    return sorted(out, key=lambda x: x[0])


def due(now, slots, moves=()):
    """Какие напоминания пора отправить прямо сейчас.
    24h — за сутки (окно 2 часа), 1h — за час (окно 30 минут)."""
    out = []
    for lesson, s in occurrences(now, slots, moves, days=3):
        if lesson - timedelta(hours=24) <= now < lesson - timedelta(hours=22):
            out.append(("24h", s, lesson))
        if lesson - timedelta(hours=1) <= now < lesson - timedelta(minutes=30):
            out.append(("1h", s, lesson))
    return out


def tick(now, send_reminder, send_weekly, send_digest=None, hooks=()):
    for kind, slot, lesson in due(now, db.all_schedules(), db.moves_ok()):
        key = f"{kind}:{lesson.strftime('%Y-%m-%dT%H:%M')}"
        if db.was_sent(slot["user_id"], key):
            continue
        db.mark_sent(slot["user_id"], key)   # сперва отмечаем, чтобы не слать дважды
        try:
            send_reminder(kind, slot, lesson)
        except Exception as e:
            logging.warning("не удалось отправить напоминание %s: %s", key, e)

    # утренняя сводка: уроки на сегодня (с 8:00 до 13:00, один раз в день)
    if send_digest and 8 <= now.hour < 13:
        key = f"digest:{now.date().isoformat()}"
        if not db.was_sent(0, key):
            db.mark_sent(0, key)
            try:
                send_digest(now)
            except Exception as e:
                logging.warning("не удалось отправить сводку: %s", e)

    for hook in hooks:                       # дополнительные задачи: домашки, KPI и т. д.
        try:
            hook(now)
        except Exception:
            logging.exception("ошибка в задаче планировщика")

    # воскресенье после 20:00 — недельный отчёт владельцу
    if now.weekday() == 6 and now.hour >= 20:
        key = f"weekly:{now.date().isoformat()}"
        if not db.was_sent(0, key):
            db.mark_sent(0, key)
            try:
                send_weekly(now)
            except Exception as e:
                logging.warning("не удалось отправить отчёт: %s", e)


def loop(send_reminder, send_weekly, send_digest=None, hooks=(), interval=60):
    while True:
        try:
            tick(datetime.now(db.TZ), send_reminder, send_weekly, send_digest, hooks)
        except Exception:
            logging.exception("ошибка в планировщике")
        time.sleep(interval)
