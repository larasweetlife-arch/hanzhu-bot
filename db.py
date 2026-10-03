"""
汉助 HanZhu — база данных (SQLite, встроена в Python, ничего ставить не нужно).
"""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Узбекистан живёт по UTC+5 круглый год, перехода на летнее время нет.
TZ = timezone(timedelta(hours=5))
# На хостинге DATA_DIR указывает на постоянный том (например /data).
# Дома переменной нет, и база лежит рядом с кодом.
DATA_DIR = Path(os.environ.get("DATA_DIR") or Path(__file__).parent)
DB_PATH = DATA_DIR / "hanzhu.db"


def today():
    return datetime.now(TZ).strftime("%Y-%m-%d")


@contextmanager
def _conn():
    c = sqlite3.connect(DB_PATH, timeout=10)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with _conn() as c:
        c.execute("PRAGMA journal_mode=WAL")
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, name TEXT, username TEXT,
            lang TEXT DEFAULT 'ru', level TEXT, source TEXT,
            is_student INTEGER DEFAULT 0, zoom_link TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            date TEXT NOT NULL, topic TEXT
        );
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            date TEXT NOT NULL, lessons INTEGER NOT NULL, note TEXT
        );
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            date TEXT NOT NULL, title TEXT, score REAL NOT NULL, max_score REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            weekday INTEGER NOT NULL, time TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sent (
            user_id INTEGER NOT NULL, key TEXT NOT NULL,
            PRIMARY KEY (user_id, key)
        );
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            lesson TEXT NOT NULL, status TEXT NOT NULL, reason TEXT, date TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, kind TEXT, date TEXT
        );
        CREATE TABLE IF NOT EXISTS stickers (
            name TEXT PRIMARY KEY, file_id TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS inbox (
            owner_msg_id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL
        );
        """)
        # миграция для базы, созданной прошлой версией
        cols = {r["name"] for r in c.execute("PRAGMA table_info(users)")}
        if "zoom_link" not in cols:
            c.execute("ALTER TABLE users ADD COLUMN zoom_link TEXT")


# ─── ПОЛЬЗОВАТЕЛИ ─────────────────────────────────────────────────────────────

def get_user(uid):
    with _conn() as c:
        r = c.execute("SELECT * FROM users WHERE user_id=?", (uid,)).fetchone()
        return dict(r) if r else None


def save_user(uid, **fields):
    with _conn() as c:
        exists = c.execute("SELECT 1 FROM users WHERE user_id=?", (uid,)).fetchone()
        if exists:
            if fields:
                sets = ", ".join(f"{k}=?" for k in fields)
                c.execute(f"UPDATE users SET {sets} WHERE user_id=?", (*fields.values(), uid))
        else:
            fields.setdefault("created_at", datetime.now(TZ).isoformat(timespec="seconds"))
            cols = ", ".join(["user_id", *fields])
            marks = ", ".join("?" * (len(fields) + 1))
            c.execute(f"INSERT INTO users ({cols}) VALUES ({marks})", (uid, *fields.values()))


def all_users():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM users ORDER BY created_at DESC")]


def students():
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM users WHERE is_student=1 ORDER BY name")]


def users_since(date):
    with _conn() as c:
        return c.execute("SELECT COUNT(*) FROM users WHERE substr(created_at,1,10)>=?",
                         (date,)).fetchone()[0]


# ─── УРОКИ, ОПЛАТА ────────────────────────────────────────────────────────────

def add_lesson(uid, topic=None, date=None):
    with _conn() as c:
        c.execute("INSERT INTO lessons (user_id, date, topic) VALUES (?,?,?)",
                  (uid, date or today(), topic))


def add_payment(uid, lessons, note=None, date=None):
    with _conn() as c:
        c.execute("INSERT INTO payments (user_id, date, lessons, note) VALUES (?,?,?,?)",
                  (uid, date or today(), lessons, note))


def balance(uid):
    """(проведено, оплачено, остаток)"""
    with _conn() as c:
        done = c.execute("SELECT COUNT(*) FROM lessons WHERE user_id=?", (uid,)).fetchone()[0]
        paid = c.execute("SELECT COALESCE(SUM(lessons),0) FROM payments WHERE user_id=?",
                         (uid,)).fetchone()[0]
    return done, paid, paid - done


def last_lessons(uid, limit=3):
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM lessons WHERE user_id=? ORDER BY date DESC, id DESC LIMIT ?",
            (uid, limit))]


def undo_last_lesson(uid):
    with _conn() as c:
        row = c.execute("SELECT id FROM lessons WHERE user_id=? ORDER BY id DESC LIMIT 1",
                        (uid,)).fetchone()
        if not row:
            return False
        c.execute("DELETE FROM lessons WHERE id=?", (row["id"],))
        return True


def lessons_count_since(date):
    with _conn() as c:
        return c.execute("SELECT COUNT(*) FROM lessons WHERE date>=?", (date,)).fetchone()[0]


# ─── ТЕСТЫ ────────────────────────────────────────────────────────────────────

def add_test(uid, title, score, max_score, date=None):
    with _conn() as c:
        c.execute("INSERT INTO tests (user_id, date, title, score, max_score) VALUES (?,?,?,?,?)",
                  (uid, date or today(), title, score, max_score))


def tests(uid):
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM tests WHERE user_id=? ORDER BY date, id", (uid,))]


def progress(uid):
    t = tests(uid)
    if not t:
        return None
    first = t[0]["score"] / t[0]["max_score"] * 100
    last = t[-1]["score"] / t[-1]["max_score"] * 100
    return {"first": first, "last": last, "delta": last - first, "count": len(t)}


# ─── РАСПИСАНИЕ И НАПОМИНАНИЯ ─────────────────────────────────────────────────

def set_schedule(uid, slots):
    """slots — список (день_недели 0..6, 'ЧЧ:ММ'). Полностью заменяет прежнее."""
    with _conn() as c:
        c.execute("DELETE FROM schedule WHERE user_id=?", (uid,))
        c.executemany("INSERT INTO schedule (user_id, weekday, time) VALUES (?,?,?)",
                      [(uid, w, tm) for w, tm in slots])


def get_schedule(uid):
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT weekday, time FROM schedule WHERE user_id=? ORDER BY weekday, time", (uid,))]


def all_schedules():
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT s.user_id, s.weekday, s.time, u.name, u.lang, u.zoom_link "
            "FROM schedule s JOIN users u ON u.user_id=s.user_id WHERE u.is_student=1")]


def was_sent(uid, key):
    with _conn() as c:
        return c.execute("SELECT 1 FROM sent WHERE user_id=? AND key=?", (uid, key)).fetchone() is not None


def mark_sent(uid, key):
    with _conn() as c:
        c.execute("INSERT OR IGNORE INTO sent (user_id, key) VALUES (?,?)", (uid, key))


def save_attendance(uid, lesson, status, reason=None):
    with _conn() as c:
        c.execute("INSERT INTO attendance (user_id, lesson, status, reason, date) VALUES (?,?,?,?,?)",
                  (uid, lesson, status, reason, today()))


def absences_since(date):
    with _conn() as c:
        return c.execute("SELECT COUNT(*) FROM attendance WHERE status='no' AND date>=?",
                         (date,)).fetchone()[0]


# ─── СТАТИСТИКА И ВОПРОСЫ ─────────────────────────────────────────────────────

def log_event(uid, kind):
    with _conn() as c:
        c.execute("INSERT INTO events (user_id, kind, date) VALUES (?,?,?)", (uid, kind, today()))


def top_events_since(date, limit=3):
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT kind, COUNT(*) AS n FROM events WHERE date>=? "
            "GROUP BY kind ORDER BY n DESC LIMIT ?", (date, limit))]


def save_inbox(owner_msg_id, uid):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO inbox (owner_msg_id, user_id) VALUES (?,?)",
                  (owner_msg_id, uid))


def inbox_user(owner_msg_id):
    with _conn() as c:
        r = c.execute("SELECT user_id FROM inbox WHERE owner_msg_id=?", (owner_msg_id,)).fetchone()
        return r["user_id"] if r else None


# ─── РЕЗЕРВНАЯ КОПИЯ ──────────────────────────────────────────────────────────

def make_backup(dest):
    """Целостная копия базы. Простое копирование файла может потерять свежие записи,
    потому что часть данных лежит во временном журнале (WAL), этот способ их учитывает."""
    with _conn() as src:
        dst = sqlite3.connect(dest)
        try:
            src.backup(dst)
        finally:
            dst.close()


# ─── СТИКЕРЫ ──────────────────────────────────────────────────────────────────

def set_sticker(name, file_id):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO stickers (name, file_id) VALUES (?,?)", (name, file_id))


def get_sticker(name):
    with _conn() as c:
        r = c.execute("SELECT file_id FROM stickers WHERE name=?", (name,)).fetchone()
        return r["file_id"] if r else None


def sticker_names():
    with _conn() as c:
        return {r["name"] for r in c.execute("SELECT name FROM stickers")}


# ─── УДАЛЕНИЕ ДАННЫХ ──────────────────────────────────────────────────────────

def delete_user(uid):
    """Стирает всё, что бот знает об этом человеке. Данные других людей не трогает."""
    with _conn() as c:
        for table in ("lessons", "payments", "tests", "schedule", "attendance", "events", "sent"):
            c.execute(f"DELETE FROM {table} WHERE user_id=?", (uid,))
        c.execute("DELETE FROM inbox WHERE user_id=?", (uid,))
        c.execute("DELETE FROM users WHERE user_id=?", (uid,))


# ─── КОПИЯ ДАННЫХ ЧЕЛОВЕКА ────────────────────────────────────────────────────

def export_user(uid):
    """Всё, что бот хранит об одном человеке. Данные других людей сюда не попадают."""
    u = get_user(uid)
    if not u:
        return None
    with _conn() as c:
        def rows(sql):
            return [dict(r) for r in c.execute(sql, (uid,))]
        usage = {r["kind"]: r["n"] for r in c.execute(
            "SELECT kind, COUNT(*) AS n FROM events WHERE user_id=? GROUP BY kind", (uid,))}
        return {
            "profile": u,
            "lessons": rows("SELECT date, topic FROM lessons WHERE user_id=? ORDER BY date, id"),
            "payments": rows("SELECT date, lessons, note FROM payments WHERE user_id=? ORDER BY date, id"),
            "tests": rows("SELECT date, title, score, max_score FROM tests WHERE user_id=? ORDER BY date, id"),
            "schedule": rows("SELECT weekday, time FROM schedule WHERE user_id=? ORDER BY weekday, time"),
            "attendance": rows("SELECT lesson, status, reason, date FROM attendance WHERE user_id=? ORDER BY id"),
            "button_usage": usage,
        }
