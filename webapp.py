"""
Mini App «Чайная лавка 清越»: сайт, который открывается внутри Telegram, и его API.
Работает в том же процессе, что и бот, и использует ту же базу, поэтому жизни, монеты, рейтинг и ники общие.

Безопасность:
  · каждый запрос подписан Telegram (initData); подпись проверяется токеном бота, подделать её нельзя;
  · в рейтинге и ленте отдаются только ники, настоящие имена не уходят с сервера никому, кроме самого игрока.
"""
import hashlib
import hmac
import html
import json
import logging
import os
import random
import re
import threading
import time
from datetime import datetime, timedelta
from urllib.parse import parse_qsl, quote

from flask import Flask, jsonify, request, send_from_directory

import db
import practice
import quest
from texts import T, t

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(HERE, "webapp_static")
INIT_MAX_AGE = 24 * 3600
CHANNEL_URL = "https://t.me/qing_laoshi"
INSTAGRAM_URL = "https://instagram.com/lllaziza_r"
LANGS = ("ru", "uz", "en", "zh")

ORDERS = {}                 # uid → текущий заказ в Чайной лавке {order, seq, answered, queue, gap, recent, ts}
_LOCK = threading.Lock()


# ─── проверка подписи Telegram ────────────────────────────────────────────────

def verify_init_data(init_data, token, max_age=INIT_MAX_AGE, now=None):
    """Проверка initData по инструкции Telegram: секрет = HMAC_SHA256("WebAppData", токен бота),
    подпись = HMAC_SHA256(секрет, строка из отсортированных пар key=value, без hash, через \\n).
    Возвращает словарь пользователя или None."""
    if not init_data or not token:
        return None
    try:
        pairs = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
    except ValueError:
        return None
    got = pairs.pop("hash", None)
    if not got:
        return None
    check = "\n".join(f"{k}={pairs[k]}" for k in sorted(pairs))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    want = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(want, got):
        return None
    try:
        age = (now or time.time()) - int(pairs.get("auth_date", "0"))
    except ValueError:
        return None
    if age > max_age or age < -300:
        return None
    try:
        user = json.loads(pairs.get("user", ""))
    except ValueError:
        return None
    return user if isinstance(user, dict) and isinstance(user.get("id"), int) else None


# ─── вспомогательное ──────────────────────────────────────────────────────────

_ALLOWED = ("b", "i", "code")


def safe_html(text):
    """Тексты правил приходят в разметке Telegram: оставляем только <b>, <i>, <code>, остальное экранируем."""
    s = html.escape(text, quote=False)
    for tag in _ALLOWED:
        s = s.replace(f"&lt;{tag}&gt;", f"<{tag}>").replace(f"&lt;/{tag}&gt;", f"</{tag}>")
    return s.replace("\n", "<br>")


def now_tz():
    return datetime.now(db.TZ)


def first_name_tokens(u, tg):
    return [*(u.get("name") or "").replace(",", " ").split(), u.get("username") or "",
            tg.get("first_name") or "", tg.get("last_name") or "", tg.get("username") or ""]


def create_app(deps):
    app = Flask(__name__, static_folder=None)
    OWNER = deps.get("owner_id") or 0
    TOKEN = deps["token"]
    PAY = deps.get("pay") or {}

    def lives_max(g):
        return practice.LIVES_PER_DAY * (db.PRO_MULT if db.pro_active(g) else 1)

    def authed():
        """(tg_user, lang, db_user) или None. Новому человеку заводим минимальную запись, чтобы хранить язык."""
        tg = verify_init_data(request.headers.get("X-Init-Data", ""), TOKEN)
        if not tg:
            return None
        uid = tg["id"]
        u = db.get_user(uid)
        if not u:
            code = (tg.get("language_code") or "")[:2].lower()
            db.save_user(uid, name=(tg.get("first_name") or "")[:60], username=tg.get("username"),
                         lang=code if code in LANGS else "ru")
            u = db.get_user(uid)
        lang = u.get("lang") if u.get("lang") in LANGS else "ru"
        return tg, lang, u

    def need_auth(fn):
        def wrapper(*a, **kw):
            r = authed()
            if not r:
                return jsonify({"error": "auth"}), 401
            return fn(r[0], r[1], r[2], *a, **kw)
        wrapper.__name__ = fn.__name__
        return wrapper

    # ── статические файлы ──
    @app.after_request
    def headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["Referrer-Policy"] = "no-referrer"
        if request.path.startswith("/api/"):
            resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.route("/")
    def index():
        resp = send_from_directory(STATIC, "index.html")
        resp.headers["Cache-Control"] = "no-cache"
        return resp

    @app.route("/static/<path:name>")
    def static_files(name):
        resp = send_from_directory(STATIC, name)
        resp.headers["Cache-Control"] = "public, max-age=3600"
        return resp

    @app.route("/healthz")
    def healthz():
        return "ok"

    # ── профиль ──
    def profile(tg, lang, u):
        uid = tg["id"]
        g = db.game_get(uid, practice.LIVES_PER_DAY)
        totals = db.score_totals(uid)
        start, end = practice.week_bounds(now_tz().date())
        ranked = practice.rank(db.score_week(start, end), db.board_joined(), exclude={OWNER})
        place = next((i + 1 for i, r in enumerate(ranked) if r["user_id"] == uid), None)
        week_pts = next((r["points"] for r in ranked if r["user_id"] == uid), 0)
        ym = now_tz().strftime("%Y-%m")
        season = next((r for r in db.month_score(ym) if r["user_id"] == uid), None) or {"points": 0, "correct": 0, "wrong": 0, "days": 0}
        nick, nick_date = db.nick_get(uid)
        joined = db.board_joined(uid)
        mar = db.marathon_all(uid)
        marathons = sum(1 for r in mar if r.get("finished"))
        rs = db.referral_stats(uid)
        wins = sum(1 for r in db.feed_recent(500) if r["user_id"] == uid and r["kind"] == "win")
        gstreak = db.gift_streak(uid)
        pstreak = db.play_streak(uid)
        stats = {"served": g["served"], "correct": totals["correct"], "wrong": totals["wrong"], "play_streak": pstreak,
                 "gift_streak": gstreak, "marathons": marathons, "friends": rs["joined"], "joined": joined, "wins": wins}
        th, emoji, tkey = practice.tea_title(g["served"])
        nxt = next((row[0] for row in practice.TITLES if row[0] > g["served"]), None)
        gift = db.gift_today(uid)
        link = ""
        name = deps["bot_username"]()
        if name:
            link = f"https://t.me/{name}?start=ref_{uid}"
        dq = db.discount_state(uid)
        acc = totals["correct"] * 100 // max(totals["correct"] + totals["wrong"], 1)
        can_change = True
        if nick and nick_date:
            can_change = datetime.strptime(nick_date, "%Y-%m-%d").date() + timedelta(days=practice.NICK_CHANGE_DAYS) <= now_tz().date()
        return {
            "lang": lang, "is_owner": bool(OWNER and uid == OWNER), "nick": nick, "can_change_nick": can_change,
            "joined": joined, "coins": g["coins"], "served": g["served"], "streak": g["streak"],
            "lives": g["lives"], "lives_max": lives_max(g), "pro_until": g.get("pro_until") if db.pro_active(g) else None,
            "rank": {"emoji": emoji, "key": tkey, "title": t(lang, tkey), "from": th, "to": nxt, "level": [r[0] for r in practice.TITLES].index(th)},
            "week": {"points": week_pts, "place": place, "start": start, "end": end,
                     "days_left": (datetime.strptime(end, "%Y-%m-%d").date() - now_tz().date()).days + 1,
                     "min": practice.BOARD_MIN_POINTS, "cap": practice.BOARD_DAILY_CAP},
            "season": {"ym": ym, "points": season["points"], "correct": season["correct"], "wrong": season["wrong"], "days": season["days"]},
            "acc": acc, "play_streak": pstreak, "badges": practice.badges(stats),
            "gift": {"opened": bool(gift), "kind": gift["kind"] if gift else None, "amount": gift["amount"] if gift else None,
                     "streak": gstreak},
            "invite": {"link": link, "joined": rs["joined"], "trial": rs["trial"], "paid": rs["paid"],
                       "disc_queue": dq["queued"], "disc_until": dq["active"]["end"] if dq["active"] else None},
            "pay": {"on": bool(PAY.get("info") or PAY.get("url")), "price": PAY.get("price") or "", "info": PAY.get("info") or "",
                    "url": PAY.get("url") or "", "days": PAY.get("days") or 30, "pro_lives": practice.LIVES_PER_DAY * db.PRO_MULT},
            "limits": {"nick_min": practice.NICK_MIN, "nick_max": practice.NICK_MAX},
            "links": {"instagram": INSTAGRAM_URL, "channel": CHANNEL_URL},
        }

    @app.route("/api/me", methods=["POST"])
    @need_auth
    def api_me(tg, lang, u):
        return jsonify(profile(tg, lang, u))

    @app.route("/api/lang", methods=["POST"])
    @need_auth
    def api_lang(tg, lang, u):
        new = (request.get_json(silent=True) or {}).get("lang")
        if new in LANGS:
            db.save_user(tg["id"], lang=new)
        return jsonify({"ok": new in LANGS})

    @app.route("/api/docs", methods=["POST"])
    @need_auth
    def api_docs(tg, lang, u):
        return jsonify({"rules": safe_html(t(lang, "rules", lives=practice.LIVES_PER_DAY, cap=practice.BOARD_DAILY_CAP,
                                              min=practice.BOARD_MIN_POINTS)),
                        "privacy": safe_html(t(lang, "privacy"))})

    # ── ник и участие в рейтинге ──
    @app.route("/api/nick", methods=["POST"])
    @need_auth
    def api_nick(tg, lang, u):
        uid = tg["id"]
        raw = (request.get_json(silent=True) or {}).get("nick", "")
        cur, since = db.nick_get(uid)
        if cur and since and datetime.strptime(since, "%Y-%m-%d").date() + timedelta(days=practice.NICK_CHANGE_DAYS) > now_tz().date():
            nxt = datetime.strptime(since, "%Y-%m-%d") + timedelta(days=practice.NICK_CHANGE_DAYS)
            return jsonify({"ok": False, "err": t(lang, "nk_wait", days=practice.NICK_CHANGE_DAYS, date=nxt.strftime("%d.%m.%Y"))})
        nick, err = practice.valid_nick(str(raw), first_name_tokens(u, tg))
        if err:
            return jsonify({"ok": False, "err": t(lang, err, min=practice.NICK_MIN, max=practice.NICK_MAX)})
        if db.nick_taken(nick, uid) or not db.nick_set(uid, nick):
            return jsonify({"ok": False, "err": t(lang, "nk_taken")})
        return jsonify({"ok": True, "nick": nick})

    @app.route("/api/board/join", methods=["POST"])
    @need_auth
    def api_join(tg, lang, u):
        uid = tg["id"]
        want = bool((request.get_json(silent=True) or {}).get("joined"))
        if want and not db.nick_get(uid)[0]:
            return jsonify({"ok": False, "need_nick": True})
        if OWNER and uid == OWNER:
            return jsonify({"ok": False})
        db.board_set(uid, want)
        return jsonify({"ok": True, "joined": want})

    # ── таблицы ──
    def pub(uid):
        return db.nick_get(uid)[0] or practice.anon_nick(uid)

    def board_rows(rows, me, value_key="points", extra=None):
        out = []
        for i, r in enumerate(rows[:20]):
            out.append({"place": i + 1, "nick": pub(r["user_id"]), "value": r[value_key], "me": r["user_id"] == me})
        return out

    @app.route("/api/board", methods=["POST"])
    @need_auth
    def api_board(tg, lang, u):
        me = tg["id"]
        tab = (request.get_json(silent=True) or {}).get("tab", "week")
        joined = db.board_joined() - {OWNER}
        today = now_tz().date()
        res = {"tab": tab, "rows": [], "me": None}
        if tab == "week":
            start, end = practice.week_bounds(today)
            ranked = practice.rank(db.score_week(start, end), joined)
            res["rows"] = board_rows(ranked, me)
            res["meta"] = {"start": start, "end": end}
        elif tab == "coins":
            rows = sorted([r for r in db.coins_rows() if r["user_id"] in joined and r["coins"] > 0],
                          key=lambda r: (-r["coins"], r["user_id"]))
            res["rows"] = board_rows(rows, me, "coins")
        elif tab == "streak":
            rows = [{"user_id": x, "n": db.play_streak(x)} for x in joined]
            rows = sorted([r for r in rows if r["n"] > 0], key=lambda r: (-r["n"], r["user_id"]))
            res["rows"] = board_rows(rows, me, "n")
        elif tab == "feed":
            ev = []
            for r in db.feed_recent(30):
                if r["user_id"] in joined:
                    ev.append({"nick": pub(r["user_id"]), "kind": r["kind"], "data": r["data"], "ts": r["ts"], "me": r["user_id"] == me})
            res["rows"] = ev[:30]
        elif tab == "results":
            out = []
            for k in range(1, 7):
                d = today - timedelta(days=7 * k)
                start, end = practice.week_bounds(d)
                ranked = practice.rank(db.score_week(start, end), joined)
                if ranked:
                    out.append({"start": start, "end": end, "top": [{"nick": pub(r["user_id"]), "points": r["points"], "me": r["user_id"] == me}
                                                                       for r in ranked[:3]],
                                "prize": ranked[0]["points"] >= practice.BOARD_MIN_POINTS})
            res["rows"] = out
        else:
            return jsonify({"error": "tab"}), 400
        if tab in ("week", "coins", "streak"):
            for r in res["rows"]:
                if r["me"]:
                    res["me"] = {"place": r["place"], "value": r["value"]}
        return jsonify(res)

    # ── Чайная лавка ──
    @app.route("/api/tea/next", methods=["POST"])
    @need_auth
    def api_tea_next(tg, lang, u):
        uid = tg["id"]
        with _LOCK:
            g = db.game_get(uid, practice.LIVES_PER_DAY)
            if g["lives"] <= 0:
                ORDERS.pop(uid, None)
                return jsonify({"closed": True, "lives": 0, "lives_max": lives_max(g)})
            sess = ORDERS.setdefault(uid, {"seq": 0, "queue": [], "gap": 0, "recent": [], "order": None, "answered": True})
            order = None
            if sess["queue"] and sess["gap"] >= 2:
                order = practice.order_for_item(lang, sess["queue"].pop(0))
                sess["gap"] = 0
            if not order:
                order = practice.make_order(lang, avoid=sess["recent"][-4:])
                sess["gap"] += 1
            sess["recent"].append(order["item"])
            sess["seq"] += 1
            sess.update(order=order, answered=False, ts=time.time())
            db.log_event(uid, "tea")
            return jsonify({"closed": False, "seq": sess["seq"], "zh": order["zh"], "py": order["py"],
                            "options": order["options"], "lives": g["lives"], "lives_max": lives_max(g)})

    @app.route("/api/tea/answer", methods=["POST"])
    @need_auth
    def api_tea_answer(tg, lang, u):
        uid = tg["id"]
        body = request.get_json(silent=True) or {}
        with _LOCK:
            sess = ORDERS.get(uid)
            try:
                seq, choice = int(body.get("seq")), int(body.get("choice"))
            except (TypeError, ValueError):
                return jsonify({"error": "bad"}), 400
            if not sess or sess["seq"] != seq or sess["answered"] or not (0 <= choice < 4):
                return jsonify({"error": "stale"}), 409
            sess["answered"] = True
            o = sess["order"]
            g = db.game_get(uid, practice.LIVES_PER_DAY)
            if g["lives"] <= 0:
                return jsonify({"error": "closed"}), 409
            ok = choice == o["answer"]
            before = practice.tea_title(g["served"])[0]
            res = {"ok": ok, "right": o["right"], "right_index": o["answer"], "gain": 0, "levelup": None}
            if ok:
                streak = g["streak"] + 1
                gain = 1 + (3 if streak % 5 == 0 else 0)
                served = g["served"] + 1
                db.game_save(uid, coins=g["coins"] + gain, served=served, streak=streak)
                db.score_add(uid, gain, 1, 0, practice.BOARD_DAILY_CAP)
                res.update(gain=gain, coins=g["coins"] + gain, served=served, streak=streak, lives=g["lives"])
                if practice.tea_title(served)[0] != before:
                    th, emoji, tkey = practice.tea_title(served)
                    res["levelup"] = {"emoji": emoji, "title": t(lang, tkey)}
                    db.feed_add(uid, "levelup", tkey)
            else:
                lives = max(0, g["lives"] - 1)
                db.game_save(uid, lives=lives, streak=0)
                db.score_add(uid, 0, 0, 1, practice.BOARD_DAILY_CAP)
                sess["queue"].append(o["item"])
                res.update(coins=g["coins"], served=g["served"], streak=0, lives=lives)
            res["lives_max"] = lives_max(g)
            res["closed"] = res["lives"] <= 0
            return jsonify(res)

    # ── подарочная коробка дня ──
    @app.route("/api/gift", methods=["POST"])
    @need_auth
    def api_gift(tg, lang, u):
        uid = tg["id"]
        with _LOCK:
            have = db.gift_today(uid)
            if have:
                return jsonify({"already": True, "kind": have["kind"], "amount": have["amount"]})
            streak_after = db.gift_streak(uid) + 1
            kind, n = practice.roll_gift(streak_after)
            if not db.gift_save(uid, kind, n):
                return jsonify({"already": True})
            res = {"already": False, "kind": kind, "amount": n, "streak": streak_after}
            g = db.game_get(uid, practice.LIVES_PER_DAY)
            if kind == "coins":
                db.game_save(uid, coins=g["coins"] + n)
            elif kind == "lives":
                db.game_save(uid, lives=g["lives"] + n)
            else:
                have_cards = db.card_have(uid)
                lvl = max(1, min(6, int(re.search(r"\d", u.get("level") or "1").group()) if re.search(r"\d", u.get("level") or "") else 1))
                fresh = practice.new_cards(lang, lvl, have_cards, n=1)
                if fresh:
                    w = fresh[0]
                    db.card_add(uid, w["zh"])
                    res["word"] = {"zh": w["zh"], "py": w["py"], "meaning": practice.short_meaning(w, lang, 60)}
                else:
                    res["kind"], res["amount"] = "coins", 5
                    db.game_save(uid, coins=g["coins"] + 5)
            return jsonify(res)

    # ── продление практики без Stars ──
    @app.route("/api/pay/paid", methods=["POST"])
    @need_auth
    def api_paid(tg, lang, u):
        uid = tg["id"]
        rid, new = db.lx_open(uid)
        if new:
            sent = deps["notify_owner"](
                f"💳 <b>{html.escape(u.get('name') or '?')}</b> (@{html.escape(u.get('username') or '—')}) нажал(а) «Я оплатил(а)» в Mini App: "
                f"расширенная практика на {PAY.get('days', 30)} дней" + (f", {html.escape(PAY.get('price'))}" if PAY.get("price") else "") +
                ".\nПроверь поступление и подтверди.",
                reply_markup=deps["ikb"]([[("✅ Оплата пришла", f"lx:ok:{rid}"), ("❌ Не нашла", f"lx:no:{rid}")]]))
            if sent:
                db.save_inbox(sent.message_id, uid)
        return jsonify({"ok": True, "dup": not new})

    @app.route("/api/pay/ask", methods=["POST"])
    @need_auth
    def api_pay_ask(tg, lang, u):
        """Способ оплаты не задан: просим преподавателя связаться с игроком."""
        uid = tg["id"]
        sent = deps["notify_owner"](f"💳 <b>{html.escape(u.get('name') or '?')}</b> (@{html.escape(u.get('username') or '—')}) хочет продлить практику (Mini App). "
                                    f"Задай PAY_INFO/PAY_URL, чтобы реквизиты показывались сами.\n\n<i>Ответь на это сообщение, и я перешлю ответ.</i>")
        if sent:
            db.save_inbox(sent.message_id, uid)
        return jsonify({"ok": True})

    # ── квест «Путешествие с Чачей» ──
    quest.init_db()
    STARS_ON = bool(deps.get("create_invoice"))
    DONATE = deps.get("donate") or {"on": False}

    def jbody():
        return request.get_json(silent=True) or {}

    @app.route("/api/quest/state", methods=["POST"])
    @need_auth
    def q_state(tg, lang, u):
        return jsonify(quest.state(tg["id"], STARS_ON, DONATE))

    @app.route("/api/quest/char", methods=["POST"])
    @need_auth
    def q_char(tg, lang, u):
        b = jbody()
        try:
            skin = int(b.get("skin", 0))
        except (TypeError, ValueError):
            skin = 0
        ch, err = quest.char_save(tg["id"], b.get("hero"), b.get("gender"), skin, b.get("hair", 0), b.get("hstyle", 0))
        if err:
            return jsonify({"ok": False, "err": err})
        return jsonify({"ok": True})

    @app.route("/api/quest/scene", methods=["POST"])
    @need_auth
    def q_scene(tg, lang, u):
        p, err = quest.start_scene(tg["id"], str(jbody().get("scene", "")))
        if err:
            return jsonify({"ok": False, "err": err})
        return jsonify({"ok": True, **p})

    @app.route("/api/quest/answer", methods=["POST"])
    @need_auth
    def q_answer(tg, lang, u):
        b = jbody()
        try:
            idx = int(b.get("idx"))
        except (TypeError, ValueError):
            return jsonify({"err": "bad"}), 400
        return jsonify(quest.answer(tg["id"], str(b.get("scene", "")), idx, b.get("a")))

    @app.route("/api/quest/cards", methods=["POST"])
    @need_auth
    def q_cards(tg, lang, u):
        cards, err = quest.cards_start(tg["id"])
        if err:
            return jsonify({"ok": False, "err": err})
        return jsonify({"ok": True, "cards": cards})

    @app.route("/api/quest/cards/claim", methods=["POST"])
    @need_auth
    def q_cards_claim(tg, lang, u):
        return jsonify(quest.cards_claim(tg["id"]))

    @app.route("/api/quest/buy", methods=["POST"])
    @need_auth
    def q_buy(tg, lang, u):
        return jsonify(quest.buy_coins(tg["id"], str(jbody().get("item", ""))))

    @app.route("/api/quest/invoice", methods=["POST"])
    @need_auth
    def q_invoice(tg, lang, u):
        """Ссылка на оплату Telegram Stars. Выдача наград — только в обработчике successful_payment бота."""
        if not STARS_ON:
            return jsonify({"ok": False, "err": "off"})
        uid = tg["id"]
        item = str(jbody().get("item", ""))
        p = quest.parse_item(item)
        if not p or not quest.char_get(uid):
            return jsonify({"ok": False, "err": "item"})
        nonce = "".join(random.choice("abcdefghjkmnpqrstuvwxyz23456789") for _ in range(10))
        title, desc = quest.item_text(lang, item)
        try:
            link = deps["create_invoice"](title[:32], desc[:250], quest.payload_for(uid, item, nonce), p[3])
        except Exception as e:
            logging.warning("не удалось создать счёт Stars: %s", e)
            return jsonify({"ok": False, "err": "fail"})
        return jsonify({"ok": True, "link": link, "nonce": nonce})

    @app.route("/api/quest/board", methods=["POST"])
    @need_auth
    def q_board(tg, lang, u):
        return jsonify(quest.board(tg["id"], str(jbody().get("tab", "week")), exclude=(OWNER,)))

    @app.route("/api/quest/hide", methods=["POST"])
    @need_auth
    def q_hide(tg, lang, u):
        quest.set_hide(tg["id"], bool(jbody().get("hide")))
        return jsonify({"ok": True})

    @app.route("/api/quest/paid", methods=["POST"])
    @need_auth
    def q_paid(tg, lang, u):
        return jsonify({"paid": quest.paid_state(tg["id"], str(jbody().get("nonce", "")))})

    return app


def serve(deps, port):
    app = create_app(deps)
    try:
        from waitress import serve as wserve
        wserve(app, host="0.0.0.0", port=port, threads=8, ident="qingyue")
    except ImportError:
        logging.warning("waitress не установлен: запускаю встроенный сервер Flask")
        app.run(host="0.0.0.0", port=port, threaded=True)
