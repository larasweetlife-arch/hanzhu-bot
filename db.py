"""
汉助 HanZhu — база данных (SQLite, встроена в Python, ничего ставить не нужно).
"""
import json
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
            is_student INTEGER DEFAULT 0, zoom_link TEXT, created_at TEXT, adult_ok INTEGER DEFAULT 0
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
        CREATE TABLE IF NOT EXISTS seen (
            user_id INTEGER NOT NULL, kind TEXT NOT NULL, key TEXT NOT NULL,
            PRIMARY KEY (user_id, kind, key)
        );
        CREATE TABLE IF NOT EXISTS missing (
            query TEXT PRIMARY KEY, n INTEGER NOT NULL, last_date TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS stickers (
            name TEXT PRIMARY KEY, file_id TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS inbox (
            owner_msg_id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS cards (
            user_id INTEGER NOT NULL, zh TEXT NOT NULL, box INTEGER NOT NULL DEFAULT 0, due TEXT NOT NULL,
            PRIMARY KEY (user_id, zh)
        );
        CREATE TABLE IF NOT EXISTS game (
            user_id INTEGER PRIMARY KEY, coins INTEGER NOT NULL DEFAULT 0, served INTEGER NOT NULL DEFAULT 0,
            streak INTEGER NOT NULL DEFAULT 0, lives INTEGER NOT NULL DEFAULT 5, lives_date TEXT, bonus_lives INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS referrals (
            friend_id INTEGER PRIMARY KEY, referrer_id INTEGER NOT NULL, date TEXT NOT NULL,
            trial INTEGER NOT NULL DEFAULT 0, paid INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS homework (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, text TEXT NOT NULL,
            due TEXT, done INTEGER NOT NULL DEFAULT 0, created TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            orig TEXT NOT NULL, new TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending'
        );
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            rating INTEGER, text TEXT, public INTEGER NOT NULL DEFAULT 0, date TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS marathon (
            user_id INTEGER NOT NULL, level INTEGER NOT NULL, done INTEGER NOT NULL DEFAULT 0,
            correct INTEGER NOT NULL DEFAULT 0, seen TEXT NOT NULL DEFAULT '[]', wrong TEXT NOT NULL DEFAULT '[]',
            started TEXT, finished TEXT, PRIMARY KEY (user_id, level)
        );
        CREATE TABLE IF NOT EXISTS study_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS grp_members (
            group_id INTEGER NOT NULL, user_id INTEGER NOT NULL, PRIMARY KEY (group_id, user_id)
        );
        CREATE TABLE IF NOT EXISTS hw_subs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, hw_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
            files INTEGER NOT NULL DEFAULT 0, date TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'new'
        );
        CREATE TABLE IF NOT EXISTS tea_score (
            user_id INTEGER NOT NULL, day TEXT NOT NULL, points INTEGER NOT NULL DEFAULT 0,
            correct INTEGER NOT NULL DEFAULT 0, wrong INTEGER NOT NULL DEFAULT 0, last_at TEXT,
            PRIMARY KEY (user_id, day)
        );
        CREATE TABLE IF NOT EXISTS board (
            user_id INTEGER PRIMARY KEY, joined INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, kind TEXT NOT NULL,
            text TEXT NOT NULL, created TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS discounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, friend_id INTEGER,
            status TEXT NOT NULL DEFAULT 'queued', start TEXT, end TEXT, created TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS parents (
            parent_id INTEGER NOT NULL, child_id INTEGER NOT NULL, created TEXT NOT NULL,
            PRIMARY KEY (parent_id, child_id)
        );
        CREATE TABLE IF NOT EXISTS par_codes (
            code TEXT PRIMARY KEY, child_id INTEGER NOT NULL, created TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS lx_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, created TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'new'
        );
        CREATE TABLE IF NOT EXISTS feed (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, kind TEXT NOT NULL,
            data TEXT, ts TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS gifts (
            user_id INTEGER NOT NULL, day TEXT NOT NULL, kind TEXT, amount INTEGER,
            PRIMARY KEY (user_id, day)
        );
        CREATE TABLE IF NOT EXISTS kpi (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, date TEXT NOT NULL, note TEXT
        );
        """)
        # миграция для базы, созданной прошлой версией
        cols = {r["name"] for r in c.execute("PRAGMA table_info(users)")}
        if "zoom_link" not in cols:
            c.execute("ALTER TABLE users ADD COLUMN zoom_link TEXT")
        if "adult_ok" not in cols:      # 1 = подтвердил 16+, -1 = раздел закрыт преподавателем, 0 = не подтверждал
            c.execute("ALTER TABLE users ADD COLUMN adult_ok INTEGER DEFAULT 0")
        bcols = {r["name"] for r in c.execute("PRAGMA table_info(board)")}
        if "nick" not in bcols:
            c.execute("ALTER TABLE board ADD COLUMN nick TEXT")
            c.execute("ALTER TABLE board ADD COLUMN nick_date TEXT")
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS board_nick ON board(nick COLLATE NOCASE)")
        gcols = {r["name"] for r in c.execute("PRAGMA table_info(game)")}
        if "pro_until" not in gcols:
            c.execute("ALTER TABLE game ADD COLUMN pro_until TEXT")
        # скидки версии 9 (по одной записи на друга в списке подарков) переезжают в очередь скидочных месяцев
        old = c.execute("SELECT id, user_id, created FROM rewards WHERE kind='discount' AND done=0").fetchall()
        for r in old:
            c.execute("INSERT INTO discounts (user_id, friend_id, status, created) VALUES (?,?,?,?)",
                      (r["user_id"], 0, "queued", r["created"]))
            c.execute("UPDATE rewards SET done=1 WHERE id=?", (r["id"],))


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


def alumni():
    """Бывшие ученики: не числятся учениками, но есть история уроков или оплат."""
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM users WHERE is_student=0 AND (user_id IN (SELECT user_id FROM lessons) "
            "OR user_id IN (SELECT user_id FROM payments)) ORDER BY name")]


def all_schedules():
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT s.user_id, s.weekday, s.time, u.name, u.lang, u.zoom_link "
            "FROM schedule s JOIN users u ON u.user_id=s.user_id WHERE u.is_student=1")]


# ─── МАРАФОН ВИКТОРИНЫ ────────────────────────────────────────────────────────

def _marathon_row(r):
    d = dict(r)
    d["seen"], d["wrong"] = json.loads(d["seen"] or "[]"), json.loads(d["wrong"] or "[]")
    return d


def marathon_get(uid, level):
    with _conn() as c:
        r = c.execute("SELECT * FROM marathon WHERE user_id=? AND level=?", (uid, level)).fetchone()
        return _marathon_row(r) if r else None


def marathon_start(uid, level):
    """Начинает уровень заново (старый прогресс стирается)."""
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO marathon (user_id, level, started) VALUES (?,?,?)", (uid, level, today()))


def marathon_save(uid, level, **f):
    for k in ("seen", "wrong"):
        if k in f:
            f[k] = json.dumps(f[k], ensure_ascii=False)
    sets = ", ".join(f"{k}=?" for k in f)
    with _conn() as c:
        c.execute(f"UPDATE marathon SET {sets} WHERE user_id=? AND level=?", (*f.values(), uid, level))


def marathon_all(uid):
    with _conn() as c:
        return [_marathon_row(r) for r in c.execute("SELECT * FROM marathon WHERE user_id=? ORDER BY level", (uid,))]


# ─── ГРУППЫ УЧЕНИКОВ ──────────────────────────────────────────────────────────

def group_add(name):
    with _conn() as c:
        return c.execute("INSERT INTO study_groups (name) VALUES (?)", (name,)).lastrowid


def group_list():
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT g.id, g.name, (SELECT COUNT(*) FROM grp_members m JOIN users u ON u.user_id=m.user_id "
            "WHERE m.group_id=g.id AND u.is_student=1) AS n FROM study_groups g ORDER BY g.name")]


def group_get(gid):
    with _conn() as c:
        r = c.execute("SELECT * FROM study_groups WHERE id=?", (gid,)).fetchone()
        return dict(r) if r else None


def group_members(gid, students_only=True):
    with _conn() as c:
        sql = ("SELECT u.user_id, u.name FROM grp_members m JOIN users u ON u.user_id=m.user_id WHERE m.group_id=?"
               + (" AND u.is_student=1" if students_only else "") + " ORDER BY u.name")
        return [dict(r) for r in c.execute(sql, (gid,))]


def group_set_members(gid, uids):
    with _conn() as c:
        c.execute("DELETE FROM grp_members WHERE group_id=?", (gid,))
        c.executemany("INSERT OR IGNORE INTO grp_members (group_id, user_id) VALUES (?,?)", [(gid, u) for u in uids])


def group_delete(gid):
    with _conn() as c:
        c.execute("DELETE FROM grp_members WHERE group_id=?", (gid,))
        c.execute("DELETE FROM study_groups WHERE id=?", (gid,))


# ─── СДАЧА ДОМАШКИ ────────────────────────────────────────────────────────────

def sub_add(hw_id, uid, files):
    with _conn() as c:
        return c.execute("INSERT INTO hw_subs (hw_id, user_id, files, date) VALUES (?,?,?,?)",
                         (hw_id, uid, files, today())).lastrowid


def sub_get(sid):
    with _conn() as c:
        r = c.execute("SELECT * FROM hw_subs WHERE id=?", (sid,)).fetchone()
        return dict(r) if r else None


def sub_set(sid, status):
    with _conn() as c:
        c.execute("UPDATE hw_subs SET status=? WHERE id=?", (status, sid))


# ─── РЕЙТИНГ НЕДЕЛИ И ПОДАРКИ ─────────────────────────────────────────────────

def score_add(uid, points, correct, wrong, cap):
    """Записывает очки дня (не больше cap в день). Возвращает, сколько очков реально засчитано."""
    day, now = today(), datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S")
    with _conn() as c:
        r = c.execute("SELECT points FROM tea_score WHERE user_id=? AND day=?", (uid, day)).fetchone()
        have = r["points"] if r else 0
        add = max(0, min(points, cap - have))
        if r:
            c.execute("UPDATE tea_score SET points=points+?, correct=correct+?, wrong=wrong+?, last_at=CASE WHEN ?>0 THEN ? ELSE last_at END "
                      "WHERE user_id=? AND day=?", (add, correct, wrong, add, now, uid, day))
        else:
            c.execute("INSERT INTO tea_score (user_id, day, points, correct, wrong, last_at) VALUES (?,?,?,?,?,?)",
                      (uid, day, add, correct, wrong, now if add else None))
        return add


def score_week(start, end):
    """Очки за неделю [start, end] (даты YYYY-MM-DD) по каждому игроку."""
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT user_id, SUM(points) AS points, SUM(correct) AS correct, SUM(wrong) AS wrong, MAX(last_at) AS last_at "
            "FROM tea_score WHERE day>=? AND day<=? GROUP BY user_id", (start, end))]


def board_set(uid, joined):
    with _conn() as c:
        c.execute("INSERT INTO board (user_id, joined) VALUES (?,?) ON CONFLICT(user_id) DO UPDATE SET joined=excluded.joined",
                  (uid, 1 if joined else 0))


def board_joined(uid=None):
    with _conn() as c:
        if uid is not None:
            r = c.execute("SELECT joined FROM board WHERE user_id=?", (uid,)).fetchone()
            return bool(r and r["joined"])
        return {r["user_id"] for r in c.execute("SELECT user_id FROM board WHERE joined=1")}


def reward_add(uid, kind, text):
    with _conn() as c:
        return c.execute("INSERT INTO rewards (user_id, kind, text, created) VALUES (?,?,?,?)",
                         (uid, kind, text, today())).lastrowid


def rewards_open(uid=None):
    with _conn() as c:
        sql = ("SELECT r.*, u.name FROM rewards r LEFT JOIN users u ON u.user_id=r.user_id WHERE r.done=0"
               + (" AND r.user_id=?" if uid is not None else "") + " ORDER BY r.id")
        return [dict(r) for r in c.execute(sql, (uid,) if uid is not None else ())]


def reward_get(rid):
    with _conn() as c:
        r = c.execute("SELECT * FROM rewards WHERE id=?", (rid,)).fetchone()
        return dict(r) if r else None


def reward_done(rid):
    with _conn() as c:
        c.execute("UPDATE rewards SET done=1 WHERE id=?", (rid,))


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


def attendance_status(uid, lesson):
    """('yes'|'no', причина) последнего ответа ученика на это занятие или None."""
    with _conn() as c:
        r = c.execute("SELECT status, reason FROM attendance WHERE user_id=? AND lesson=? ORDER BY rowid DESC LIMIT 1",
                      (uid, lesson)).fetchone()
        return (r["status"], r["reason"]) if r else None


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
        for table in ("lessons", "payments", "tests", "schedule", "attendance", "events", "sent", "seen",
                      "cards", "game", "homework", "moves", "reviews", "kpi", "marathon", "hw_subs", "grp_members", "tea_score", "board", "rewards", "discounts", "lx_requests", "feed", "gifts"):
            c.execute(f"DELETE FROM {table} WHERE user_id=?", (uid,))
        c.execute("DELETE FROM parents WHERE parent_id=? OR child_id=?", (uid, uid))
        c.execute("DELETE FROM par_codes WHERE child_id=?", (uid,))
        c.execute("DELETE FROM inbox WHERE user_id=?", (uid,))
        c.execute("DELETE FROM referrals WHERE friend_id=? OR referrer_id=?", (uid, uid))
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
            "homework": rows("SELECT text, due, done, created FROM homework WHERE user_id=? ORDER BY id"),
            "reviews": rows("SELECT rating, text, public, date FROM reviews WHERE user_id=? ORDER BY id"),
            "kpi_notes": rows("SELECT date, note FROM kpi WHERE user_id=? ORDER BY id"),
            "flashcards": rows("SELECT zh, box, due FROM cards WHERE user_id=? ORDER BY zh"),
            "game": rows("SELECT coins, served FROM game WHERE user_id=?"),
            "tea_score": rows("SELECT day, points, correct, wrong FROM tea_score WHERE user_id=? ORDER BY day"),
            "weekly_rating": rows("SELECT joined, nick FROM board WHERE user_id=?"),
            "discount_months": rows("SELECT status, start, end, created FROM discounts WHERE user_id=? ORDER BY id"),
            "daily_gifts": rows("SELECT day, kind, amount FROM gifts WHERE user_id=? ORDER BY day"),
            "linked_parents": rows("SELECT created FROM parents WHERE child_id=?"),
            "rewards": rows("SELECT kind, text, created, done FROM rewards WHERE user_id=? ORDER BY id"),
            "marathon": rows("SELECT level, done, correct, started, finished FROM marathon WHERE user_id=? ORDER BY level"),
            "homework_submissions": rows("SELECT hw_id, files, date, status FROM hw_subs WHERE user_id=? ORDER BY id"),
            "button_usage": usage,
            "already_shown": {k: [r["key"] for r in c.execute(
                "SELECT key FROM seen WHERE user_id=? AND kind=?", (uid, k))]
                for k in ("word", "chengyu", "fact")},
        }


# ─── ЧТО УЖЕ ПОКАЗЫВАЛИ (чтобы не повторяться) ────────────────────────────────

def seen_keys(uid, kind):
    with _conn() as c:
        return {r["key"] for r in c.execute("SELECT key FROM seen WHERE user_id=? AND kind=?", (uid, kind))}


def mark_seen(uid, kind, key):
    with _conn() as c:
        c.execute("INSERT OR IGNORE INTO seen (user_id, kind, key) VALUES (?,?,?)", (uid, kind, key))


def reset_seen(uid, kind):
    with _conn() as c:
        c.execute("DELETE FROM seen WHERE user_id=? AND kind=?", (uid, kind))


# ─── СЛОВА, КОТОРЫХ НЕ НАШЛОСЬ ────────────────────────────────────────────────

def log_missing(query):
    q = " ".join(query.lower().split())[:60]
    if not q:
        return
    with _conn() as c:
        c.execute("INSERT INTO missing (query, n, last_date) VALUES (?,1,?) "
                  "ON CONFLICT(query) DO UPDATE SET n=n+1, last_date=excluded.last_date", (q, today()))


def top_missing(since=None, limit=20):
    with _conn() as c:
        if since:
            rows = c.execute("SELECT query, n FROM missing WHERE last_date>=? ORDER BY n DESC, query LIMIT ?", (since, limit))
        else:
            rows = c.execute("SELECT query, n FROM missing ORDER BY n DESC, query LIMIT ?", (limit,))
        return [dict(r) for r in rows]


# ─── ФЛЕШ-КАРТОЧКИ ────────────────────────────────────────────────────────────

def card_add(uid, zh):
    with _conn() as c:
        c.execute("INSERT OR IGNORE INTO cards (user_id, zh, box, due) VALUES (?,?,0,?)", (uid, zh, today()))


def card_have(uid):
    with _conn() as c:
        return {r["zh"] for r in c.execute("SELECT zh FROM cards WHERE user_id=?", (uid,))}


def cards_due(uid, limit=20):
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT zh, box FROM cards WHERE user_id=? AND due<=? ORDER BY due, box LIMIT ?",
            (uid, today(), limit))]


def card_set(uid, zh, box, due):
    with _conn() as c:
        c.execute("UPDATE cards SET box=?, due=? WHERE user_id=? AND zh=?", (box, due, uid, zh))


def card_stats(uid):
    """(всего, к повторению сегодня, выучено: ящик 4 и выше)"""
    with _conn() as c:
        total = c.execute("SELECT COUNT(*) FROM cards WHERE user_id=?", (uid,)).fetchone()[0]
        due = c.execute("SELECT COUNT(*) FROM cards WHERE user_id=? AND due<=?", (uid, today())).fetchone()[0]
        known = c.execute("SELECT COUNT(*) FROM cards WHERE user_id=? AND box>=4", (uid,)).fetchone()[0]
    return total, due, known


# ─── ЧАЙНАЯ ЛАВКА ─────────────────────────────────────────────────────────────

PRO_MULT = 3        # «расширенная практика»: жизней в день в 3 раза больше


def pro_active(g):
    return bool(g.get("pro_until")) and g["pro_until"] >= today()


def game_get(uid, lives_per_day=5):
    """Состояние игры; жизни обновляются раз в день. Бонусные жизни (за друзей) сгорают вместе с днём.
    При включённой расширенной практике (pro_until) жизней в день в PRO_MULT раза больше."""
    with _conn() as c:
        r = c.execute("SELECT * FROM game WHERE user_id=?", (uid,)).fetchone()
        if not r:
            c.execute("INSERT INTO game (user_id, lives, lives_date) VALUES (?,?,?)", (uid, lives_per_day, today()))
            r = c.execute("SELECT * FROM game WHERE user_id=?", (uid,)).fetchone()
        g = dict(r)
        if g["lives_date"] != today():
            per_day = lives_per_day * (PRO_MULT if pro_active(g) else 1)
            g["lives"], g["bonus_lives"], g["lives_date"] = per_day, 0, today()
            c.execute("UPDATE game SET lives=?, bonus_lives=0, lives_date=? WHERE user_id=?",
                      (g["lives"], g["lives_date"], uid))
        return g


def game_save(uid, **fields):
    sets = ", ".join(f"{k}=?" for k in fields)
    with _conn() as c:
        c.execute(f"UPDATE game SET {sets} WHERE user_id=?", (*fields.values(), uid))


def game_set_pro(uid, days, lives_per_day=5):
    """Включает расширенную практику на days дней (продлевает, если уже включена) и сразу добавляет жизни на сегодня."""
    g = game_get(uid, lives_per_day)
    base = datetime.strptime(max(g["pro_until"] or today(), today()), "%Y-%m-%d")
    until = (base + timedelta(days=days)).strftime("%Y-%m-%d")
    game_save(uid, pro_until=until, lives=g["lives"] + lives_per_day * (PRO_MULT - 1))
    return until


def game_add_lives(uid, n, lives_per_day=5):
    g = game_get(uid, lives_per_day)
    game_save(uid, lives=g["lives"] + n)


# ─── РЕФЕРАЛЫ ─────────────────────────────────────────────────────────────────

def referral_add(friend, referrer):
    """True, если записали (друг новый, сам себя пригласить нельзя, второй раз тоже)."""
    if friend == referrer:
        return False
    with _conn() as c:
        if c.execute("SELECT 1 FROM referrals WHERE friend_id=?", (friend,)).fetchone():
            return False
        c.execute("INSERT INTO referrals (friend_id, referrer_id, date) VALUES (?,?,?)", (friend, referrer, today()))
    return True


def referral_of(friend):
    with _conn() as c:
        r = c.execute("SELECT * FROM referrals WHERE friend_id=?", (friend,)).fetchone()
        return dict(r) if r else None


def referral_mark(friend, field):
    """field: 'trial' или 'paid'. True, если отметка поставлена впервые."""
    assert field in ("trial", "paid")
    with _conn() as c:
        r = c.execute(f"SELECT {field} FROM referrals WHERE friend_id=?", (friend,)).fetchone()
        if not r or r[0]:
            return False
        c.execute(f"UPDATE referrals SET {field}=1 WHERE friend_id=?", (friend,))
        return True


def referral_stats(referrer):
    with _conn() as c:
        r = c.execute("SELECT COUNT(*), COALESCE(SUM(trial),0), COALESCE(SUM(paid),0) FROM referrals "
                      "WHERE referrer_id=?", (referrer,)).fetchone()
    return {"joined": r[0], "trial": r[1], "paid": r[2]}


def payments_count(uid):
    with _conn() as c:
        return c.execute("SELECT COUNT(*) FROM payments WHERE user_id=?", (uid,)).fetchone()[0]


# ─── ДОМАШНИЕ ЗАДАНИЯ ─────────────────────────────────────────────────────────

def hw_add(uid, text, due):
    with _conn() as c:
        cur = c.execute("INSERT INTO homework (user_id, text, due, created) VALUES (?,?,?,?)",
                        (uid, text, due or None, today()))
        return cur.lastrowid


def hw_open(uid):
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM homework WHERE user_id=? AND done=0 ORDER BY COALESCE(due,'9999'), id", (uid,))]


def hw_get(hid):
    with _conn() as c:
        r = c.execute("SELECT * FROM homework WHERE id=?", (hid,)).fetchone()
        return dict(r) if r else None


def hw_done(hid):
    with _conn() as c:
        c.execute("UPDATE homework SET done=1 WHERE id=?", (hid,))


def hw_reopen(hid):
    with _conn() as c:
        c.execute("UPDATE homework SET done=0 WHERE id=?", (hid,))


def hw_all_open():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM homework WHERE done=0")]


# ─── ПЕРЕНОС УРОКОВ ───────────────────────────────────────────────────────────

def move_add(uid, orig, new):
    with _conn() as c:
        cur = c.execute("INSERT INTO moves (user_id, orig, new) VALUES (?,?,?)", (uid, orig, new))
        return cur.lastrowid


def move_get(mid):
    with _conn() as c:
        r = c.execute("SELECT * FROM moves WHERE id=?", (mid,)).fetchone()
        return dict(r) if r else None


def move_set(mid, status):
    with _conn() as c:
        c.execute("UPDATE moves SET status=? WHERE id=?", (status, mid))


def moves_ok():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM moves WHERE status='ok'")]


# ─── ОТЗЫВЫ, KPI, ОТЧЁТЫ ──────────────────────────────────────────────────────

def review_add(uid, rating, text, public):
    with _conn() as c:
        c.execute("INSERT INTO reviews (user_id, rating, text, public, date) VALUES (?,?,?,?,?)",
                  (uid, rating, text, 1 if public else 0, today()))


def kpi_add(uid, note):
    with _conn() as c:
        c.execute("INSERT INTO kpi (user_id, date, note) VALUES (?,?,?)", (uid, today(), note))


def first_lesson_date(uid):
    with _conn() as c:
        r = c.execute("SELECT MIN(date) FROM lessons WHERE user_id=?", (uid,)).fetchone()
        return r[0] if r else None


def absences_detail(date):
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT u.name, a.lesson, a.reason FROM attendance a JOIN users u ON u.user_id=a.user_id "
            "WHERE a.status='no' AND a.date>=? ORDER BY a.date", (date,))]


def month_rows(ym):
    """Строки для CSV за месяц 'YYYY-MM': уроки и оплаты всех учеников."""
    with _conn() as c:
        out = []
        for r in c.execute("SELECT l.date, u.name, l.topic FROM lessons l JOIN users u ON u.user_id=l.user_id "
                           "WHERE substr(l.date,1,7)=? ORDER BY l.date, l.id", (ym,)):
            out.append((r["date"], r["name"] or "", "урок", "1", r["topic"] or ""))
        for r in c.execute("SELECT p.date, u.name, p.lessons, p.note FROM payments p JOIN users u ON u.user_id=p.user_id "
                           "WHERE substr(p.date,1,7)=? ORDER BY p.date, p.id", (ym,)):
            out.append((r["date"], r["name"] or "", "оплата", str(r["lessons"]), r["note"] or ""))
        return sorted(out)


# ─── ОЧЕРЕДЬ СКИДОЧНЫХ МЕСЯЦЕВ ЗА ДРУЗЕЙ ──────────────────────────────────────
# Каждый друг, начавший заниматься, даёт пригласившей один скидочный месяц (30%). Скидки не суммируются:
# месяцы идут по очереди, каждый действует 30 дней с того дня, когда его применили к оплате.

DISCOUNT_DAYS = 30


def discount_queue_add(uid, friend_id=0):
    with _conn() as c:
        return c.execute("INSERT INTO discounts (user_id, friend_id, status, created) VALUES (?,?, 'queued', ?)",
                         (uid, friend_id, today())).lastrowid


def discount_state(uid):
    """{'active': запись или None, 'queued': сколько ждёт} (истёкшие активные помечаются used)."""
    with _conn() as c:
        c.execute("UPDATE discounts SET status='used' WHERE user_id=? AND status='active' AND end<?", (uid, today()))
        act = c.execute("SELECT * FROM discounts WHERE user_id=? AND status='active' ORDER BY id LIMIT 1", (uid,)).fetchone()
        q = c.execute("SELECT COUNT(*) FROM discounts WHERE user_id=? AND status='queued'", (uid,)).fetchone()[0]
        return {"active": dict(act) if act else None, "queued": q}


def discount_activate(uid):
    """Берёт следующий месяц из очереди и запускает его на 30 дней. None, если очередь пуста или месяц уже идёт."""
    st = discount_state(uid)
    if st["active"] or not st["queued"]:
        return None
    start = datetime.strptime(today(), "%Y-%m-%d")
    end = (start + timedelta(days=DISCOUNT_DAYS - 1)).strftime("%Y-%m-%d")
    with _conn() as c:
        row = c.execute("SELECT id FROM discounts WHERE user_id=? AND status='queued' ORDER BY id LIMIT 1", (uid,)).fetchone()
        c.execute("UPDATE discounts SET status='active', start=?, end=? WHERE id=?", (today(), end, row["id"]))
        return dict(c.execute("SELECT * FROM discounts WHERE id=?", (row["id"],)).fetchone())


def discount_all_queued():
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT d.user_id, u.name, COUNT(*) AS n FROM discounts d LEFT JOIN users u ON u.user_id=d.user_id "
            "WHERE d.status='queued' GROUP BY d.user_id ORDER BY u.name")]


# ─── НИКИ В РЕЙТИНГЕ ──────────────────────────────────────────────────────────

def nick_get(uid):
    with _conn() as c:
        r = c.execute("SELECT nick, nick_date FROM board WHERE user_id=?", (uid,)).fetchone()
        return (r["nick"], r["nick_date"]) if r else (None, None)


def nick_taken(nick, except_uid=None):
    with _conn() as c:
        r = c.execute("SELECT user_id FROM board WHERE nick=? COLLATE NOCASE", (nick,)).fetchone()
        return bool(r and r["user_id"] != except_uid)


def nick_set(uid, nick):
    """True, если ник сохранён (False: занят)."""
    with _conn() as c:
        try:
            c.execute("INSERT INTO board (user_id, joined, nick, nick_date) VALUES (?,1,?,?) "
                      "ON CONFLICT(user_id) DO UPDATE SET nick=excluded.nick, nick_date=excluded.nick_date, joined=1",
                      (uid, nick, today()))
        except sqlite3.IntegrityError:
            return False
    return True


def nick_clear(uid):
    with _conn() as c:
        c.execute("UPDATE board SET nick=NULL, nick_date=NULL WHERE user_id=?", (uid,))


def nick_map(uids=None):
    """{user_id: ник} для всех, у кого ник задан."""
    with _conn() as c:
        return {r["user_id"]: r["nick"] for r in c.execute("SELECT user_id, nick FROM board WHERE nick IS NOT NULL")
                if uids is None or r["user_id"] in uids}


def board_members():
    """Все вступившие в рейтинг с настоящими именами: видит только владелец."""
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT b.user_id, b.nick, u.name, u.username FROM board b LEFT JOIN users u ON u.user_id=b.user_id "
            "WHERE b.joined=1 ORDER BY b.nick COLLATE NOCASE")]


# ─── РОДИТЕЛИ (недельная сводка) ──────────────────────────────────────────────

def par_code_new(child_id):
    import secrets
    code = secrets.token_urlsafe(6).replace("-", "x").replace("_", "y")
    with _conn() as c:
        c.execute("INSERT INTO par_codes (code, child_id, created) VALUES (?,?,?)", (code, child_id, today()))
    return code


def par_code_child(code):
    with _conn() as c:
        r = c.execute("SELECT child_id FROM par_codes WHERE code=?", (code,)).fetchone()
        return r["child_id"] if r else None


def parent_link(parent_id, child_id):
    with _conn() as c:
        c.execute("INSERT OR IGNORE INTO parents (parent_id, child_id, created) VALUES (?,?,?)",
                  (parent_id, child_id, today()))


def parent_unlink(parent_id, child_id=None):
    with _conn() as c:
        if child_id is None:
            c.execute("DELETE FROM parents WHERE parent_id=?", (parent_id,))
        else:
            c.execute("DELETE FROM parents WHERE parent_id=? AND child_id=?", (parent_id, child_id))
            if not c.execute("SELECT 1 FROM parents WHERE child_id=?", (child_id,)).fetchone():
                pass


def parents_of(child_id):
    with _conn() as c:
        return [r["parent_id"] for r in c.execute("SELECT parent_id FROM parents WHERE child_id=?", (child_id,))]


def children_of(parent_id):
    with _conn() as c:
        return [r["child_id"] for r in c.execute("SELECT child_id FROM parents WHERE parent_id=?", (parent_id,))]


def all_parent_links():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT parent_id, child_id FROM parents ORDER BY child_id")]


# ─── ПРОДЛЕНИЕ ПРАКТИКИ (оплата не через Stars) ───────────────────────────────

def lx_open(uid):
    """Новая заявка на продление; если открытая уже есть, возвращает её (id, False)."""
    with _conn() as c:
        r = c.execute("SELECT id FROM lx_requests WHERE user_id=? AND status='new' ORDER BY id DESC LIMIT 1", (uid,)).fetchone()
        if r:
            return r["id"], False
        return c.execute("INSERT INTO lx_requests (user_id, created) VALUES (?,?)", (uid, today())).lastrowid, True


def lx_get(rid):
    with _conn() as c:
        r = c.execute("SELECT * FROM lx_requests WHERE id=?", (rid,)).fetchone()
        return dict(r) if r else None


def lx_set(rid, status):
    with _conn() as c:
        c.execute("UPDATE lx_requests SET status=? WHERE id=?", (status, rid))


# ─── ЛЕНТА, ПОДАРОЧНЫЕ КОРОБКИ, СТАТИСТИКА ДЛЯ MINI APP ───────────────────────

def feed_add(uid, kind, data=""):
    with _conn() as c:
        c.execute("INSERT INTO feed (user_id, kind, data, ts) VALUES (?,?,?,?)",
                  (uid, kind, data, datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S")))
        c.execute("DELETE FROM feed WHERE id < (SELECT MAX(id) FROM feed) - 500")


def feed_recent(limit=30):
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM feed ORDER BY id DESC LIMIT ?", (limit * 3,))]


def gift_today(uid):
    with _conn() as c:
        r = c.execute("SELECT * FROM gifts WHERE user_id=? AND day=?", (uid, today())).fetchone()
        return dict(r) if r else None


def gift_save(uid, kind, amount):
    with _conn() as c:
        try:
            c.execute("INSERT INTO gifts (user_id, day, kind, amount) VALUES (?,?,?,?)", (uid, today(), kind, amount))
        except sqlite3.IntegrityError:
            return False
    return True


def gift_streak(uid):
    """Сколько дней подряд (включая сегодня или вчера) открывались коробки."""
    with _conn() as c:
        days = {r["day"] for r in c.execute("SELECT day FROM gifts WHERE user_id=?", (uid,))}
    d, n = datetime.strptime(today(), "%Y-%m-%d"), 0
    if d.strftime("%Y-%m-%d") not in days:
        d -= timedelta(days=1)
    while d.strftime("%Y-%m-%d") in days:
        n += 1
        d -= timedelta(days=1)
    return n


def score_totals(uid):
    """Итого очков, верных, ошибок, активных дней и последние 14 дней (для профиля Mini App)."""
    with _conn() as c:
        r = c.execute("SELECT COALESCE(SUM(points),0), COALESCE(SUM(correct),0), COALESCE(SUM(wrong),0), COUNT(*) "
                      "FROM tea_score WHERE user_id=? AND (correct>0 OR wrong>0)", (uid,)).fetchone()
        days = [x["day"] for x in c.execute("SELECT day FROM tea_score WHERE user_id=? AND (correct>0 OR wrong>0) ORDER BY day DESC", (uid,))]
    return {"points": r[0], "correct": r[1], "wrong": r[2], "days": r[3], "day_list": days}


def play_streak(uid):
    days = set(score_totals(uid)["day_list"])
    d, n = datetime.strptime(today(), "%Y-%m-%d"), 0
    if d.strftime("%Y-%m-%d") not in days:
        d -= timedelta(days=1)
    while d.strftime("%Y-%m-%d") in days:
        n += 1
        d -= timedelta(days=1)
    return n


def month_score(ym):
    """Очки по игрокам за месяц YYYY-MM (сезон)."""
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT user_id, SUM(points) AS points, SUM(correct) AS correct, SUM(wrong) AS wrong, MAX(last_at) AS last_at, COUNT(*) AS days "
            "FROM tea_score WHERE substr(day,1,7)=? GROUP BY user_id", (ym,))]


def total_score_rows():
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT t.user_id, SUM(t.points) AS points, SUM(t.correct) AS correct, SUM(t.wrong) AS wrong, MAX(t.last_at) AS last_at "
            "FROM tea_score t GROUP BY t.user_id")]


def coins_rows():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT user_id, coins, served, streak FROM game")]


# ─── ДАННЫЕ ДЛЯ НЕДЕЛЬНОЙ СВОДКИ РОДИТЕЛЯМ ────────────────────────────────────

def lessons_between(uid, start, end):
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT date, topic FROM lessons WHERE user_id=? AND date>=? AND date<=? ORDER BY date, id",
                                           (uid, start, end))]


def tests_between(uid, start, end):
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM tests WHERE user_id=? AND date>=? AND date<=? ORDER BY date, id",
                                           (uid, start, end))]


def absences_between(uid, start, end):
    with _conn() as c:
        return c.execute("SELECT COUNT(*) FROM attendance WHERE user_id=? AND status='no' AND date>=? AND date<=?",
                         (uid, start, end)).fetchone()[0]


def hw_stats(uid, start, end):
    """(задано за неделю, сдано из них, просрочено среди открытых)"""
    with _conn() as c:
        given = c.execute("SELECT COUNT(*) FROM homework WHERE user_id=? AND created>=? AND created<=?", (uid, start, end)).fetchone()[0]
        done = c.execute("SELECT COUNT(*) FROM homework WHERE user_id=? AND created>=? AND created<=? AND done=1", (uid, start, end)).fetchone()[0]
        late = c.execute("SELECT COUNT(*) FROM homework WHERE user_id=? AND done=0 AND due IS NOT NULL AND due!='' AND due<?",
                         (uid, today())).fetchone()[0]
    return given, done, late


def score_between(uid, start, end):
    with _conn() as c:
        r = c.execute("SELECT COALESCE(SUM(points),0), COALESCE(SUM(correct),0), COALESCE(SUM(wrong),0), COUNT(*) FROM tea_score "
                      "WHERE user_id=? AND day>=? AND day<=? AND (correct>0 OR wrong>0)", (uid, start, end)).fetchone()
        return {"points": r[0], "correct": r[1], "wrong": r[2], "days": r[3]}
