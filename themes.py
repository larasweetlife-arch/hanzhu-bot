"""
Оформления профиля (версия 12).

· Недельные: приз победителю рейтинга (раньше был авторский урок). Действуют до конца следующей недели,
  когда подводят новые итоги. Каждую неделю своё оформление, подряд два раза одно и то же не выпадет.
· Магазинные: покупаются за игровые монеты или за звёзды Telegram, остаются навсегда.
· Монеты можно докупить за звёзды (пакеты PACKS). В рейтинг идут только заработанные в игре очки,
  купленные монеты на рейтинг не влияют.

Сами цвета лежат здесь, в CATALOG; сайт получает их через /api/themes и применяет как CSS-переменные.
"""
import hashlib
import hmac
import threading
from datetime import date, datetime, timedelta

import db

OWNER_ID = [0]
TOKEN = [""]
_LOCK = threading.RLock()

QUEST_WIN_MIN = 60          # минимум очков за неделю в рейтинге игры, чтобы получить оформление

# цена оформлений из магазина: (монеты, звёзды)
# курс игры (с версии 17): 1 монета = 1 ⭐, как у нарядов и жизней. Монетную цену игрок набирает игрой, звёздную платит сразу
TIERS = {"rare": (300, 300), "epic": (500, 500), "legendary": (980, 980)}
# пакеты монет за звёзды: id → (монеты, звёзды), с небольшой скидкой за большой пакет
PACKS = {"pack100": (100, 100), "pack270": (270, 250), "pack560": (560, 500)}


def _t(id_, kind, emoji, scheme, ru, uz, en, zh, c, qbg, tier=None):
    """c — цвета: bg bg2 card ink mute jade jade2 mist seal gold onjade; line и shadow считаются сами."""
    keys = ("bg", "bg2", "card", "ink", "mute", "jade", "jade2", "mist", "seal", "gold", "onjade")
    vars_ = dict(zip(keys, c.split()))
    dark = scheme == "dark"
    vars_["line"] = "rgba(255,255,255,.16)" if dark else "rgba(30,30,30,.13)"
    vars_["shadow"] = "0 8px 26px rgba(0,0,0,.45)" if dark else "0 8px 26px rgba(40,30,20,.12)"
    vars_["ok"] = vars_["jade"]
    vars_["ok-bg"] = vars_["mist"]
    vars_["bad-bg"] = "rgba(255,90,90,.18)" if dark else "#f6dcd8"
    return {"id": id_, "kind": kind, "emoji": emoji, "scheme": scheme, "tier": tier,
            "name": {"ru": ru, "uz": uz, "en": en, "zh": zh}, "vars": vars_, "bg": qbg}


CATALOG = [
    # ── недельные (приз победителям): 12 штук, на каждую неделю своё ──
    _t("sakura", "weekly", "🌸", "dark", "Ночная сакура", "Tungi sakura", "Midnight Sakura", "夜樱",
       "#1a1020 #241530 #2c1a3a #f7e8f1 #b69cb0 #ff8fb8 #c45a8e #3d2250 #ff6b9a #ffd1a1 #2a1030",
       "radial-gradient(circle at 12% 8%, rgba(255,143,184,.28), transparent 42%), radial-gradient(circle at 92% 28%, rgba(196,90,142,.24), transparent 46%), linear-gradient(#1a1020, #241530)"),
    _t("jadedragon", "weekly", "🐉", "dark", "Нефритовый дракон", "Yashma ajdar", "Jade Dragon", "青龙",
       "#07201a #0b2c24 #103629 #e9f5ec #86b3a1 #4de3a6 #1fa77a #174a3a #ffb23e #ffd36a #05261c",
       "radial-gradient(circle at 85% 6%, rgba(77,227,166,.25), transparent 44%), radial-gradient(circle at 10% 70%, rgba(255,211,106,.12), transparent 40%), linear-gradient(#07201a, #0b2c24)"),
    _t("lanterns", "weekly", "🏮", "dark", "Праздник фонарей", "Chiroqlar bayrami", "Lantern Festival", "灯会",
       "#2a0a0a #3a1010 #4a1614 #ffeccb #d9a98a #ffb340 #ff7a2f #6b2018 #ff4d3d #ffd24a #2a0a0a",
       "radial-gradient(circle at 20% 12%, rgba(255,179,64,.30), transparent 38%), radial-gradient(circle at 80% 40%, rgba(255,77,61,.22), transparent 44%), linear-gradient(#2a0a0a, #3a1010)"),
    _t("ink", "weekly", "🖌", "light", "Тушь и горы", "Siyoh va tog'lar", "Ink & Mountains", "水墨",
       "#efede6 #e2dfd5 #faf9f5 #1c1c1c #6b6b66 #2b2b2b #6d6d68 #e3e1d8 #c8281e #9a8a5a #faf9f5",
       "linear-gradient(180deg, rgba(60,60,60,.10), transparent 30%), radial-gradient(ellipse at 70% 100%, rgba(40,40,40,.18), transparent 55%), #efede6"),
    _t("teasea", "weekly", "🍵", "light", "Чайное море", "Choy dengizi", "Sea of Tea", "茶海",
       "#e4f4f1 #d1ece7 #f6fcfb #0f3a38 #4d7e7a #0f8f8a #4ec3bc #cdeeea #e8715d #e0a93b #f6fcfb",
       "radial-gradient(circle at 15% 5%, rgba(78,195,188,.35), transparent 45%), radial-gradient(circle at 90% 60%, rgba(15,143,138,.18), transparent 50%), #e4f4f1"),
    _t("panda", "weekly", "🐼", "light", "Бамбуковая панда", "Bambuk panda", "Bamboo Panda", "熊猫",
       "#f4f4f2 #e7e8e4 #ffffff #141414 #666666 #2e7d4f #7fbf8f #e3efe5 #d9423a #b99b49 #ffffff",
       "repeating-linear-gradient(90deg, rgba(46,125,79,.07) 0 14px, transparent 14px 46px), linear-gradient(#f4f4f2, #e7e8e4)"),
    _t("moonrabbit", "weekly", "🐇", "dark", "Лунный кролик", "Oy quyoni", "Moon Rabbit", "月兔",
       "#0d1530 #131d40 #1a2650 #eaf0ff #9aa9d6 #b9c8ff #7b8fe0 #25346b #ff8fa3 #ffe9a8 #0d1530",
       "radial-gradient(circle at 82% 8%, rgba(255,233,168,.30), transparent 22%), radial-gradient(circle at 20% 90%, rgba(123,143,224,.22), transparent 46%), linear-gradient(#0d1530, #131d40)"),
    _t("peony", "weekly", "🌺", "light", "Пион", "Pion", "Peony", "牡丹",
       "#fdeef3 #f9dbe6 #fff8fb #4a1530 #9a5a78 #d6336c #f783ac #fbd6e4 #c2255c #e5a53a #ffffff",
       "radial-gradient(circle at 90% 6%, rgba(247,131,172,.40), transparent 40%), radial-gradient(circle at 8% 60%, rgba(214,51,108,.14), transparent 46%), #fdeef3"),
    _t("imperial", "weekly", "👑", "dark", "Императорское золото", "Imperator oltini", "Imperial Gold", "金龙",
       "#2b0b12 #3a0f19 #4a1520 #fbeab8 #cfa77a #f2c14e #c9902a #5a1c28 #ff5a4d #ffd86b #2b0b12",
       "radial-gradient(circle at 50% -10%, rgba(242,193,78,.35), transparent 50%), linear-gradient(#2b0b12, #3a0f19)"),
    _t("bamboorain", "weekly", "🎋", "light", "Бамбуковый дождь", "Bambuk yomg'iri", "Bamboo Rain", "竹雨",
       "#eaf6e4 #d9eccf #f7fcf3 #17361a #5b805c #3a9d3f #8bd18b #d2ecc9 #e07a3c #c9a43a #f7fcf3",
       "repeating-linear-gradient(100deg, rgba(58,157,63,.08) 0 2px, transparent 2px 22px), linear-gradient(#eaf6e4, #d9eccf)"),
    _t("aurora", "weekly", "🌌", "dark", "Северное сияние", "Shimoliy yog'du", "Aurora", "极光",
       "#07121f #0b1d33 #10283f #e6fbff #8fc0cc #5cf2c9 #38a8e8 #153b52 #b388ff #b8f5a0 #06202a",
       "radial-gradient(ellipse at 20% 0%, rgba(92,242,201,.34), transparent 55%), radial-gradient(ellipse at 80% 10%, rgba(179,136,255,.30), transparent 55%), linear-gradient(#07121f, #0b1d33)"),
    _t("neon", "weekly", "🌃", "dark", "Неоновый Шанхай", "Neon Shanxay", "Neon Shanghai", "霓虹上海",
       "#0b0716 #140b26 #1b1033 #f1e9ff #a795d1 #00e5ff #ff2bd6 #2a1650 #ff2bd6 #ffe600 #0b0716",
       "radial-gradient(circle at 10% 0%, rgba(255,43,214,.30), transparent 40%), radial-gradient(circle at 95% 25%, rgba(0,229,255,.26), transparent 42%), linear-gradient(#0b0716, #140b26)"),
    # ── из магазина ──
    _t("matcha", "shop", "🍃", "light", "Матча-латте", "Matcha latte", "Matcha Latte", "抹茶拿铁",
       "#f1f0e0 #e6e6cf #fbfbf1 #2d3a22 #75835f #7a9b3d #b5cd7a #e4eac9 #b5651d #c8a24a #fbfbf1",
       "radial-gradient(circle at 80% 8%, rgba(181,205,122,.45), transparent 46%), radial-gradient(circle at 5% 70%, rgba(122,155,61,.15), transparent 44%), #f1f0e0", "rare"),
    _t("sunset", "shop", "🌅", "light", "Закат над Хуанхэ", "Xuanxe ustida quyosh botishi", "Yellow River Sunset", "黄河落日",
       "#fff1df #ffe0c2 #fffaf3 #4a2410 #a0693f #e0662b #f2a65a #ffe3c8 #c23b5b #e8a317 #fffaf3",
       "linear-gradient(180deg, rgba(194,59,91,.20), rgba(242,166,90,.18) 40%, transparent 70%), #fff1df", "rare"),
    _t("porcelain", "shop", "🏺", "light", "Бело-голубой фарфор", "Ko'k-oq chinni", "Blue & White Porcelain", "青花瓷",
       "#f2f6fc #e1eaf7 #ffffff #12306b #5d74a6 #1f4fb5 #6c93de #dbe6f8 #c0392b #b79b4e #ffffff",
       "radial-gradient(circle at 50% 120%, rgba(31,79,181,.18), transparent 60%), radial-gradient(circle at 100% 0%, rgba(108,147,222,.28), transparent 40%), #f2f6fc", "rare"),
    _t("silkroad", "shop", "✨", "dark", "Звёздный Шёлковый путь", "Yulduzli Ipak yo'li", "Starry Silk Road", "丝路星空",
       "#0e0f2b #15173d #1c1f4d #f3efe0 #aeb0d9 #f5c15a #8e7de0 #2b2e6a #ff7a59 #ffd98a #0e0f2b",
       "radial-gradient(circle at 20% 15%, rgba(255,217,138,.9) 0 1px, transparent 2px), radial-gradient(circle at 70% 30%, rgba(255,217,138,.8) 0 1px, transparent 2px), radial-gradient(circle at 40% 75%, rgba(243,239,224,.8) 0 1px, transparent 2px), radial-gradient(circle at 88% 80%, rgba(243,239,224,.7) 0 1px, transparent 2px), radial-gradient(ellipse at 50% 0%, rgba(142,125,224,.35), transparent 60%), linear-gradient(#0e0f2b, #15173d)", "epic"),
    _t("boba", "shop", "🧋", "light", "Жемчужный милк-ти", "Marvarid sutli choy", "Bubble Tea", "珍珠奶茶",
       "#f6e9df #ecd6c6 #fff8f2 #4a2e22 #9a7662 #a8683f #d7a07a #f1dccd #e56b8b #d8a24a #fff8f2",
       "radial-gradient(circle, rgba(74,46,34,.13) 0 5px, transparent 6px) 0 0 / 38px 38px, radial-gradient(circle at 90% 5%, rgba(229,107,139,.25), transparent 40%), #f6e9df", "epic"),
    _t("dragongate", "shop", "🐲", "dark", "Врата дракона", "Ajdar darvozasi", "Dragon Gate", "龙门",
       "#05060a #0b0d14 #12151f #f5ecd2 #a7a08a #ffcc4d #ff8a3d #1d2230 #ff4d4d #ffe08a #05060a",
       "radial-gradient(circle at 50% -5%, rgba(255,204,77,.38), transparent 46%), radial-gradient(circle at 0% 100%, rgba(255,138,61,.20), transparent 46%), linear-gradient(#05060a, #0b0d14)", "legendary"),
]
BY_ID = {x["id"]: x for x in CATALOG}
WEEKLY = [x["id"] for x in CATALOG if x["kind"] == "weekly"]
SHOP = [x["id"] for x in CATALOG if x["kind"] == "shop"]


def price(theme_id):
    x = BY_ID.get(theme_id)
    return TIERS[x["tier"]] if x and x["kind"] == "shop" else None


def configure(owner_id, token):
    OWNER_ID[0] = int(owner_id or 0)
    TOKEN[0] = token or ""


# ─── база ─────────────────────────────────────────────────────────────────────

def init_db():
    with db._conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS theme_owned (
            user_id INTEGER NOT NULL, theme_id TEXT NOT NULL, src TEXT, expires TEXT, granted TEXT,
            PRIMARY KEY (user_id, theme_id)
        );
        CREATE TABLE IF NOT EXISTS theme_equip (user_id INTEGER PRIMARY KEY, theme_id TEXT);
        CREATE TABLE IF NOT EXISTS weekly_win (
            week_start TEXT NOT NULL, kind TEXT NOT NULL, user_id INTEGER NOT NULL, theme_id TEXT, pts INTEGER DEFAULT 0,
            notified INTEGER DEFAULT 0, PRIMARY KEY (week_start, kind)
        );
        CREATE TABLE IF NOT EXISTS weekly_closed (week_start TEXT PRIMARY KEY);
        """)


def _today():
    return db.today()


def grant(uid, theme_id, src, expires=None, conn=None):
    """Выдаёт оформление. -> False, если такое уже есть навсегда. conn: если вызывающий уже держит транзакцию, пишем в ней же."""
    if theme_id not in BY_ID:
        return False

    def go(c):
        cur = c.execute("SELECT expires FROM theme_owned WHERE user_id=? AND theme_id=?", (uid, theme_id)).fetchone()
        if cur and cur[0] is None and expires is None:
            return False
        c.execute("INSERT OR REPLACE INTO theme_owned (user_id, theme_id, src, expires, granted) VALUES (?,?,?,?,?)",
                  (uid, theme_id, src, expires, _today()))
        return True
    if conn is not None:
        return go(conn)
    with _LOCK, db._conn() as c:
        return go(c)


def owned(uid, conn=None):
    """{theme_id: {src, expires}} только действующие."""
    q = "SELECT theme_id, src, expires FROM theme_owned WHERE user_id=? AND (expires IS NULL OR expires>=?)"
    if conn is not None:
        rows = conn.execute(q, (uid, _today())).fetchall()
    else:
        with db._conn() as c:
            rows = c.execute(q, (uid, _today())).fetchall()
    return {r[0]: {"src": r[1], "expires": r[2]} for r in rows}


def has(uid, theme_id, conn=None):
    return theme_id in owned(uid, conn)


def equipped(uid):
    """Надетое оформление, если оно ещё действует."""
    with db._conn() as c:
        r = c.execute("SELECT theme_id FROM theme_equip WHERE user_id=?", (uid,)).fetchone()
    tid = r[0] if r else None
    return tid if tid and has(uid, tid) else None


def equip(uid, theme_id):
    """theme_id=None снимает оформление. -> True/False."""
    if theme_id is not None and not has(uid, theme_id):
        return False
    with db._conn() as c:
        if theme_id is None:
            c.execute("DELETE FROM theme_equip WHERE user_id=?", (uid,))
        else:
            c.execute("INSERT OR REPLACE INTO theme_equip (user_id, theme_id) VALUES (?,?)", (uid, theme_id))
    return True


def wins(uid):
    with db._conn() as c:
        rows = c.execute("SELECT kind, COUNT(*) FROM weekly_win WHERE user_id=? GROUP BY kind", (uid,)).fetchall()
    d = {r[0]: r[1] for r in rows}
    return {"word": d.get("word", 0), "quest": d.get("quest", 0), "total": sum(d.values())}


def ref(uid):
    """Безликая подпись игрока для публичных списков: по ней можно открыть профиль, но не узнать Telegram-аккаунт."""
    return hmac.new((TOKEN[0] or "x").encode(), f"ref:{uid}".encode(), hashlib.sha256).hexdigest()[:12]


def uid_from_ref(r, candidates):
    for uid in candidates:
        if hmac.compare_digest(ref(uid), r or ""):
            return uid
    return None


# ─── еженедельные итоги ───────────────────────────────────────────────────────

def weekly_theme_id(week_start, kind):
    """Оформление недели: у соседних недель оно разное, у двух рейтингов одной недели тоже."""
    d = date.fromisoformat(week_start) if isinstance(week_start, str) else week_start
    n = (d - date(2024, 1, 1)).days // 7
    return WEEKLY[(5 * n + (0 if kind == "word" else 6)) % len(WEEKLY)]


def quest_ranked(start, end, exclude=()):
    """Рейтинг игры за неделю: список {user_id, pts}. Скрытые игроки в рейтинге не участвуют."""
    ex = {int(x) for x in exclude if x}
    with db._conn() as c:
        rows = c.execute(
            "SELECT s.user_id AS uid, SUM(s.pts) AS pts, "
            "(SELECT COUNT(*) FROM quest_prog p WHERE p.user_id=s.user_id) AS scenes "
            "FROM quest_score s JOIN quest_char ch ON ch.user_id=s.user_id "
            "WHERE s.day>=? AND s.day<=? AND ch.hide=0 GROUP BY s.user_id HAVING pts>0 "
            "ORDER BY pts DESC, scenes DESC, s.user_id ASC", (start, end)).fetchall()
    return [{"user_id": r[0], "pts": r[1]} for r in rows if r[0] not in ex]


def close_week(prev_monday, word_ranked, quest_rows, word_min):
    """Подводит итоги недели prev_monday (понедельник). Идемпотентно. -> список новых победителей."""
    ws = prev_monday.isoformat() if hasattr(prev_monday, "isoformat") else str(prev_monday)
    with _LOCK, db._conn() as c:
        if c.execute("SELECT 1 FROM weekly_closed WHERE week_start=?", (ws,)).fetchone():
            return []
        c.execute("INSERT INTO weekly_closed (week_start) VALUES (?)", (ws,))
    d = date.fromisoformat(ws)
    expires = (d + timedelta(days=13)).isoformat()      # до воскресенья следующей недели включительно
    out = []
    for kind, top, need in (("word", word_ranked[0] if word_ranked else None, word_min),
                            ("quest", quest_rows[0] if quest_rows else None, QUEST_WIN_MIN)):
        if not top:
            continue
        pts = top.get("points", top.get("pts", 0))
        if pts < need:
            continue
        tid = weekly_theme_id(ws, kind)
        with _LOCK, db._conn() as c:
            c.execute("INSERT OR REPLACE INTO weekly_win (week_start, kind, user_id, theme_id, pts, notified) VALUES (?,?,?,?,?,0)",
                      (ws, kind, top["user_id"], tid, pts))
        grant(top["user_id"], tid, "win", expires)
        # победитель сразу надевает новое оформление; вручную можно сменить на любое своё
        equip(top["user_id"], tid)
        out.append({"kind": kind, "user_id": top["user_id"], "theme_id": tid, "pts": pts, "expires": expires, "week_start": ws})
    return out


def mark_notified(week_start, kind):
    with db._conn() as c:
        c.execute("UPDATE weekly_win SET notified=1 WHERE week_start=? AND kind=?", (week_start, kind))


# ─── что отдаём сайту ─────────────────────────────────────────────────────────

def public_item(x, lang):
    name = x["name"].get(lang) or x["name"]["en"]
    p = price(x["id"])
    return {"id": x["id"], "kind": x["kind"], "emoji": x["emoji"], "scheme": x["scheme"], "tier": x["tier"], "name": name,
            "vars": x["vars"], "bg": x["bg"], "coins": p[0] if p else None, "stars": p[1] if p else None}


def view(uid, lang):
    """Каталог, что есть у игрока, что надето, пакеты монет."""
    mine = owned(uid)
    eq = equipped(uid)
    return {"catalog": [public_item(x, lang) for x in CATALOG],
            "owned": mine, "equipped": eq,
            "packs": [{"id": k, "coins": v[0], "stars": v[1]} for k, v in PACKS.items()],
            "wins": wins(uid)}


def public_theme(uid):
    """Надетое оформление игрока для публичных списков (id или None)."""
    return equipped(uid)
