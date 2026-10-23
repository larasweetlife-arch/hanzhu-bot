"""
Объявления (версия 24).

  · Лазиза: /ad → текст → предпросмотр → аудитория → «Отправить». Бесплатно.
  · Остальные (в том числе репетиторы): /ad → текст → предпросмотр → аудитория → оплата звёздами →
    объявление уходит Лазизе на одобрение. Одобрила → рассылка, отклонила → звёзды возвращаются сами.
  · На всех объявлениях пометка «Реклама» на языке получателя. Человеку не больше AD_WEEK_MAX объявлений
    за 7 дней (по умолчанию 5), чтобы не надоедать.
  · Цены (звёзды), настраиваются переменными окружения без новой версии:
      AD_PRICE_STARS      — одна группа (ученики / не ученики / один язык), по умолчанию 300
      AD_PRICE_ALL_STARS  — все пользователи, по умолчанию 450
      AD_PRO_DISCOUNT     — скидка репетиторам на «Про», %, по умолчанию 30
      AD_WEEK_MAX         — сколько объявлений на человека за 7 дней, по умолчанию 5
Тексты для рекламодателей — texts_v15.py (4 языка), для Лазизы — здесь, по-русски.
"""
import html
import logging
import os
import threading
import time
from datetime import datetime, timedelta

from telebot import types

import booking
import db
import tutors
from texts_v15 import AD

esc = lambda s: html.escape(str(s), quote=False)
ctx = {}
FLOW = {}                                   # {uid: {"step": "text"|"pick"|"confirm", "text": ..., "aud": ...}}
_SENDING = threading.Lock()

TEXT_MIN, TEXT_MAX = 10, 700
LANGS = {"ru": "По-русски", "uz": "O'zbekcha", "en": "English", "zh": "中文"}


def _int_env(name, default):
    try:
        return int(os.getenv(name, "") or default)
    except ValueError:
        return default


def price_group():
    return _int_env("AD_PRICE_STARS", 300)


def price_all():
    return _int_env("AD_PRICE_ALL_STARS", 450)


def pro_discount():
    return max(0, min(90, _int_env("AD_PRO_DISCOUNT", 30)))


def week_max():
    return max(1, _int_env("AD_WEEK_MAX", 5))


def A(lang, key, **kw):
    s = AD.get(lang, AD["ru"]).get(key)
    if s is None:
        s = AD["ru"][key]
    kw.setdefault("max", TEXT_MAX)
    kw.setdefault("min", TEXT_MIN)
    return s.format(**kw) if kw else s


def init_db():
    with db._conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, text TEXT NOT NULL, aud TEXT NOT NULL,
            price INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL, charge_id TEXT, created TEXT,
            sent_ok INTEGER DEFAULT 0, sent_fail INTEGER DEFAULT 0, sent_at TEXT
        );
        CREATE TABLE IF NOT EXISTS ad_log (
            user_id INTEGER NOT NULL, ad_id INTEGER NOT NULL, ts TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS ix_adlog_u ON ad_log(user_id, ts);
        """)


def _one(sql, args=()):
    return tutors._one(sql, args)


def _all(sql, args=()):
    return tutors._all(sql, args)


def _run(sql, args=()):
    return tutors._run(sql, args)


def is_owner(uid):
    return bool(ctx.get("owner_id")) and uid == ctx["owner_id"]


# ─── ЦЕНА И АУДИТОРИЯ ─────────────────────────────────────────────────────────

def is_pro_tutor(uid):
    tc = booking.teacher_of_user(uid)
    return bool(tc) and not tutors.is_owner_tc(tc) and tutors.eff_tier(tc) >= 3


def price_for(uid, aud):
    """(цена, процент скидки). У Лазизы всегда 0."""
    if is_owner(uid):
        return 0, 0
    base = price_all() if aud == "all" else price_group()
    pct = pro_discount() if is_pro_tutor(uid) else 0
    return max(1, round(base * (100 - pct) / 100)), pct


def aud_name(lang, aud):
    if aud in LANGS:
        return LANGS[aud]
    return A(lang, "a_" + aud)


def recipients(aud, exclude=()):
    """Кому можно отправить сейчас: зарегистрированные, не исчерпавшие недельный лимит, не отправитель и не владелица."""
    since = (datetime.now(db.TZ) - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    with db._conn() as c:
        used = {r[0]: r[1] for r in c.execute("SELECT user_id, COUNT(*) FROM ad_log WHERE ts>=? GROUP BY user_id", (since,))}
        rows = [dict(r) for r in c.execute("SELECT user_id, lang, is_student FROM users WHERE level IS NOT NULL")]
    skip = set(exclude) | {ctx.get("owner_id")}
    out = []
    for u in rows:
        if u["user_id"] in skip or used.get(u["user_id"], 0) >= week_max():
            continue
        if aud == "stu" and not u["is_student"]:
            continue
        if aud == "non" and u["is_student"]:
            continue
        if aud in LANGS and (u["lang"] or "ru") != aud:
            continue
        out.append(u)
    return out


def counts(exclude=()):
    return {a: len(recipients(a, exclude)) for a in ("all", "stu", "non", "ru", "uz", "en", "zh")}


# ─── ОФОРМЛЕНИЕ ───────────────────────────────────────────────────────────────

def render(text, lang, advertiser=None, raw_html=False):
    body = text if raw_html else esc(text)
    out = f"📢 <i>{A(lang, 'label')}</i>\n\n{body}"
    if advertiser:
        out += f"\n\n<i>{esc(advertiser)}</i>"
    return out


def advertiser_line(uid):
    u = db.get_user(uid) or {}
    if u.get("username"):
        return "@" + u["username"]
    return u.get("name") or ""


def bot_():
    return ctx["bot"]


def say(uid, text, kb=None):
    return bot_().send_message(uid, text, reply_markup=kb, disable_web_page_preview=True)


# ─── ДИАЛОГ ───────────────────────────────────────────────────────────────────

def cmd_ad(m):
    uid = m.from_user.id
    lang = ctx["lang_of"](uid)
    u = db.get_user(uid)
    if not (u and u.get("level")):
        return
    if not is_owner(uid) and not ctx["stars_on"]:
        return say(uid, A(lang, "nostars"))
    FLOW[uid] = {"step": "text"}
    if is_owner(uid):
        return say(uid, "📢 Пришли текст объявления (от 10 до 700 знаков). Можно с <b>жирным</b> и <i>курсивом</i> (HTML-теги). "
                        "Потом покажу, как оно будет выглядеть. Отмена: /menu.")
    say(uid, A(lang, "ask"))


def on_text(m, txt):
    """Из bot.on_text. True — сообщение обработано здесь."""
    uid = m.from_user.id
    d = FLOW.get(uid)
    if not d or d["step"] != "text":
        return False
    if tutors._is_menu(txt, uid):
        FLOW.pop(uid, None)
        return False
    lang = ctx["lang_of"](uid)
    if len(txt) < TEXT_MIN:
        say(uid, A(lang, "short"))
        return True
    if len(txt) > TEXT_MAX:
        say(uid, A(lang, "long"))
        return True
    owner = is_owner(uid)
    try:                                                        # предпросмотр: у владелицы разрешён HTML, остальным текст экранируется
        say(uid, A(lang, "head") if not owner else "Так увидят объявление:")
        say(uid, render(txt, lang, None if owner else advertiser_line(uid), raw_html=owner))
    except Exception as e:
        logging.info("предпросмотр объявления не вышел: %s", e)
        say(uid, "Не получилось показать: проверь HTML-теги в тексте и пришли его ещё раз." if owner else A(lang, "bad"))
        return True
    d.update(step="pick", text=txt)
    cn = counts(exclude=(uid,))
    rows = []
    for a in ("all", "stu", "non", "ru", "uz", "en", "zh"):
        if cn[a]:
            rows.append((f"{aud_name(lang, a)} · {cn[a]}", f"ax:a:{a}"))
    if not rows:
        FLOW.pop(uid, None)
        say(uid, A(lang, "zero"))
        return True
    kb = booking.ikb([[r] for r in rows] + [[(A(lang, "cancel"), "ax:x")]])
    say(uid, A(lang, "pick") if not owner else "Кому отправить?", kb)
    return True


def cb(c):
    p = c.data.split(":")
    act = p[1]
    uid = c.from_user.id
    bot = bot_()
    try:
        bot.answer_callback_query(c.id)
    except Exception:
        pass
    lang = ctx["lang_of"](uid)
    try:
        if act == "x":
            FLOW.pop(uid, None)
            return say(uid, A(lang, "cancelled"))
        if act == "a":
            return pick(uid, lang, p[2])
        if act == "go":
            return confirm(uid, lang)
        if act in ("ok", "no"):
            return decide(c, int(p[2]), act == "ok")
    except Exception:
        logging.exception("объявления: ошибка в кнопке %s", c.data)


def pick(uid, lang, aud):
    d = FLOW.get(uid)
    if not d or d.get("step") not in ("pick", "confirm") or not d.get("text"):
        return
    n = len(recipients(aud, exclude=(uid,)))
    if not n:
        return say(uid, A(lang, "zero"))
    d.update(step="confirm", aud=aud)
    if is_owner(uid):
        return say(uid, f"Аудитория: <b>{esc(aud_name('ru', aud))}</b>, получат примерно {n} чел. (у кого не исчерпан лимит {week_max()} объявлений за 7 дней).",
                   booking.ikb([[(f"✅ Отправить {n} чел.", "ax:go")], [("❌ Отмена", "ax:x")]]))
    price, pct = price_for(uid, aud)
    disc = A(lang, "disc", pct=pct) if pct else ""
    say(uid, A(lang, "price", aud=esc(aud_name(lang, aud)), n=n, price=price, disc=disc),
        booking.ikb([[(A(lang, "pay", price=price), "ax:go")], [(A(lang, "cancel"), "ax:x")]]))


def confirm(uid, lang):
    d = FLOW.get(uid)
    if not d or d.get("step") != "confirm" or not d.get("aud"):
        return
    if is_owner(uid):
        FLOW.pop(uid, None)
        ad_id = _run("INSERT INTO ads (user_id, text, aud, price, status, created) VALUES (?,?,?,?,?,?)",
                     (uid, d["text"], d["aud"], 0, "approved", tutors.now_s()))
        say(uid, "Отправляю…")
        return start_send(ad_id, raw_html=True)
    if not ctx["stars_on"]:
        return say(uid, A(lang, "nostars"))
    price, _ = price_for(uid, d["aud"])
    ad_id = _run("INSERT INTO ads (user_id, text, aud, price, status, created) VALUES (?,?,?,?,?,?)",
                 (uid, d["text"], d["aud"], price, "invoiced", tutors.now_s()))
    FLOW.pop(uid, None)
    try:
        bot_().send_invoice(uid, title=A(lang, "inv_title"), description=A(lang, "inv_desc"), invoice_payload=f"ax:{ad_id}",
                            provider_token="", currency="XTR", prices=[types.LabeledPrice(label=A(lang, "inv_title"), amount=price)])
    except Exception as e:
        logging.warning("счёт за объявление не отправился: %s", e)
        _run("UPDATE ads SET status='failed' WHERE id=?", (ad_id,))
        say(uid, A(lang, "bad"))


# ─── ОПЛАТА ───────────────────────────────────────────────────────────────────

def precheck(q):
    """pre_checkout_query для payload «ax:ID»: объявление есть, ждёт оплаты, сумма верная, платит автор."""
    try:
        ad = _one("SELECT * FROM ads WHERE id=?", (int(q.invoice_payload[3:]),))
    except (ValueError, TypeError):
        return False
    return bool(ad) and ad["status"] == "invoiced" and ad["user_id"] == q.from_user.id and ad["price"] == q.total_amount


def on_paid(uid, stars, charge, payload):
    """successful_payment для «ax:ID»: объявление идёт Лазизе на одобрение."""
    lang = ctx["lang_of"](uid)
    try:
        ad_id = int(payload[3:])
    except ValueError:
        ad_id = None
    ad = _one("SELECT * FROM ads WHERE id=?", (ad_id,)) if ad_id else None
    if not ad or ad["user_id"] != uid or ad["status"] not in ("invoiced", "failed"):
        ctx["notify_owner"](f"⚠️ Пришла оплата {stars} ⭐ за объявление, но запись не найдена или уже обработана. "
                            f"Человек: {esc(advertiser_line(uid))}. Номер операции: <code>{esc(charge)}</code>. Команда: /refund {esc(charge)}")
        return
    _run("UPDATE ads SET status='paid', charge_id=? WHERE id=?", (charge, ad_id))
    say(uid, A(lang, "paid"))
    n = len(recipients(ad["aud"], exclude=(uid,)))
    ctx["notify_owner"](
        f"📢 <b>Платное объявление на проверку</b> (№{ad_id})\nОт: {esc(advertiser_line(uid))}\n"
        f"Аудитория: {esc(aud_name('ru', ad['aud']))}, дойдёт примерно до {n} чел.\nОплачено: {stars} ⭐\n\n"
        f"{render(ad['text'], 'ru', advertiser_line(uid))}",
        reply_markup=booking.ikb([[("✅ Отправить", f"ax:ok:{ad_id}")], [("❌ Отклонить и вернуть звёзды", f"ax:no:{ad_id}")]]))


def decide(c, ad_id, ok):
    if not is_owner(c.from_user.id):
        return
    ad = _one("SELECT * FROM ads WHERE id=?", (ad_id,))
    if not ad or ad["status"] != "paid":
        return say(c.from_user.id, "Это объявление уже обработано.")
    if ok:
        _run("UPDATE ads SET status='approved' WHERE id=?", (ad_id,))
        say(c.from_user.id, f"Отправляю объявление №{ad_id}…")
        return start_send(ad_id, raw_html=False)
    lang = ctx["lang_of"](ad["user_id"])
    try:
        ctx["bot"].refund_star_payment(ad["user_id"], ad["charge_id"])
    except Exception as e:
        logging.warning("возврат за объявление не вышел: %s", e)
        return say(c.from_user.id, f"Не получилось вернуть звёзды автоматически: {esc(e)}\nНомер операции: <code>{esc(ad['charge_id'])}</code>, команда /refund.")
    _run("UPDATE ads SET status='rejected' WHERE id=?", (ad_id,))
    say(c.from_user.id, f"↩️ Объявление №{ad_id} отклонено, звёзды возвращены.")
    try:
        say(ad["user_id"], A(lang, "rejected", stars=ad["price"]))
    except Exception:
        pass


# ─── РАССЫЛКА ─────────────────────────────────────────────────────────────────

def start_send(ad_id, raw_html):
    threading.Thread(target=send_ad, args=(ad_id, raw_html), daemon=True).start()


def send_ad(ad_id, raw_html=False):
    """Рассылка в фоне, около 15 сообщений в секунду. Лимит Telegram ~30 в секунду."""
    with _SENDING:                                   # две рассылки подряд не идут одновременно
        ad = _one("SELECT * FROM ads WHERE id=?", (ad_id,))
        if not ad or ad["status"] != "approved":
            return
        adv = None if is_owner(ad["user_id"]) else advertiser_line(ad["user_id"])
        ok = fail = 0
        for u in recipients(ad["aud"], exclude=(ad["user_id"],)):
            lang = u["lang"] if u["lang"] in LANGS else "ru"
            try:
                ctx["bot"].send_message(u["user_id"], render(ad["text"], lang, adv, raw_html=raw_html), disable_web_page_preview=True)
                _run("INSERT INTO ad_log (user_id, ad_id, ts) VALUES (?,?,?)",
                     (u["user_id"], ad_id, datetime.now(db.TZ).strftime("%Y-%m-%d %H:%M:%S")))
                ok += 1
            except Exception as e:
                fail += 1
                if "429" in str(e):
                    time.sleep(3)
            time.sleep(0.06)
        _run("UPDATE ads SET status='sent', sent_ok=?, sent_fail=?, sent_at=? WHERE id=?", (ok, fail, tutors.now_s(), ad_id))
        ctx["notify_owner"](f"📢 Объявление №{ad_id} разослано: дошло <b>{ok}</b>, не дошло {fail} (закрыли бота).")
        if not is_owner(ad["user_id"]):
            try:
                say(ad["user_id"], A(ctx["lang_of"](ad["user_id"]), "sent", n=ok))
            except Exception:
                pass


def report(m):
    """/ads — владелице: последние объявления и цены."""
    if not is_owner(m.from_user.id):
        return
    rows = _all("SELECT * FROM ads WHERE status IN ('sent','paid','rejected') ORDER BY id DESC LIMIT 10")
    lines = [f"📢 <b>Объявления</b>\nЦены: группа {price_group()} ⭐, все {price_all()} ⭐, скидка Про {pro_discount()}%. "
             f"Лимит: {week_max()} на человека за 7 дней.\nНовое объявление: /ad"]
    names = {"sent": "разослано", "paid": "ждёт проверки", "rejected": "отклонено"}
    for r in rows:
        lines.append(f"· №{r['id']} {names.get(r['status'], r['status'])}, {esc(aud_name('ru', r['aud']))}, "
                     f"{r['price']} ⭐" + (f", дошло {r['sent_ok']}" if r['status'] == "sent" else "") + f", {esc(advertiser_line(r['user_id']))}")
    say(m.from_user.id, "\n".join(lines))


def register(bot, owner_id, lang_of, notify_owner, stars_on):
    ctx.update(bot=bot, owner_id=owner_id, lang_of=lang_of, notify_owner=notify_owner, stars_on=stars_on)
    init_db()
    bot.message_handler(commands=["ad"])(cmd_ad)
    bot.message_handler(commands=["ads"])(report)
    bot.callback_query_handler(func=lambda c: c.data.startswith("ax:"))(cb)
