"""
Озвучка китайского на сервере (версия 12).

Раньше игра просила голос у самого телефона (speechSynthesis). Если на телефоне нет китайского голоса,
кнопка 🔊 нажимается, а звука нет. Теперь звук делает сервер и отдаёт обычный mp3: он играет на любом телефоне.

Двигатели по очереди:
  1) edge-tts (нейросетевой голос Microsoft, пакет edge-tts);
  2) Google Translate TTS (без пакетов, обычный HTTPS-запрос).
Готовые файлы кладутся в DATA_DIR/tts, поэтому каждая фраза генерируется один раз.
"""
import asyncio
import hashlib
import json
import logging
import os
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path

DATA_DIR = Path(os.environ.get("DATA_DIR") or Path(__file__).parent)
CACHE = DATA_DIR / "tts"
VOICE = os.environ.get("TTS_VOICE", "zh-CN-XiaoxiaoNeural").strip()
RATE = os.environ.get("TTS_RATE", "-15%").strip()          # чуть медленнее обычного, чтобы учеба шла легче
MAX_FILES = 6000
MAX_LEN = 120
_SEM = threading.Semaphore(3)                              # не больше трёх одновременных запросов к внешним сервисам
_LOCKS = {}
_LOCKS_GUARD = threading.Lock()
_ENGINE_BAD = {}                                           # имя двигателя → [подряд ошибок, до какого времени не трогать]
_FAIL_UNTIL = [0.0]                                        # если оба двигателя упали, 5 минут не долбим их
_USER_GEN = {}                                             # uid → времена последних новых генераций (защита от злоупотреблений)

# проверяется в тестах: можно подменить двигатели
ENGINES = []


def key(text):
    return hashlib.sha1((VOICE + "|" + RATE + "|" + text).encode("utf-8")).hexdigest()


def path_for(text):
    return CACHE / (key(text) + ".mp3")


def valid_text(text):
    """Только короткий текст, в котором есть китайские иероглифы."""
    if not text or len(text) > MAX_LEN:
        return False
    return any("一" <= ch <= "鿿" for ch in text)


def cached(text):
    p = path_for(text)
    return p if p.is_file() and p.stat().st_size > 300 else None


def _edge(text, out):
    import edge_tts

    async def go():
        await asyncio.wait_for(edge_tts.Communicate(text, VOICE, rate=RATE).save(str(out)), 25)
    asyncio.run(go())


def _google(text, out):
    url = ("https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=zh-CN&ttsspeed=0.8&q="
           + urllib.parse.quote(text))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    out.write_bytes(data)


def _engines():
    return ENGINES or [("edge-tts", _edge), ("google", _google)]


def generate(text):
    """Путь к mp3 или None. Блокирует поток на время генерации, поэтому вызывать из рабочего потока сервера."""
    p = cached(text)
    if p:
        return p
    if not valid_text(text) or time.time() < _FAIL_UNTIL[0]:
        return None
    CACHE.mkdir(parents=True, exist_ok=True)
    k = key(text)
    with _LOCKS_GUARD:
        lock = _LOCKS.setdefault(k, threading.Lock())
    with lock:                                            # две одинаковые просьбы одновременно: вторая ждёт первую
        p = cached(text)
        if p:
            return p
        if sum(1 for _ in CACHE.glob("*.mp3")) >= MAX_FILES:
            logging.warning("озвучка: кэш переполнен (%s файлов)", MAX_FILES)
            return None
        tmp = CACHE / (k + ".part")
        with _SEM:
            for name, fn in _engines():
                bad = _ENGINE_BAD.get(name, [0, 0.0])
                if bad[0] >= 3 and time.time() < bad[1]:
                    continue                                  # двигатель три раза подряд упал: 10 минут его не мучаем
                try:
                    tmp.unlink(missing_ok=True)
                    fn(text, tmp)
                    if tmp.is_file() and tmp.stat().st_size > 300:
                        _ENGINE_BAD[name] = [0, 0.0]
                        tmp.replace(path_for(text))
                        logging.info("озвучка: %s → %s", text[:20], name)
                        return path_for(text)
                except Exception as e:
                    logging.warning("озвучка: %s не сработал (%s: %s)", name, type(e).__name__, str(e)[:120])
                    _ENGINE_BAD[name] = [bad[0] + 1, time.time() + 600]
                finally:
                    tmp.unlink(missing_ok=True)
        _FAIL_UNTIL[0] = time.time() + 300
        logging.error("озвучка: не получилось ни одним способом, пауза 5 минут")
        return None


def allow_user(uid, limit=20, per=60):
    """Новых генераций на человека не больше limit в минуту (повторы из кэша не считаются)."""
    now = time.time()
    xs = [x for x in _USER_GEN.get(uid, []) if now - x < per]
    if len(xs) >= limit:
        _USER_GEN[uid] = xs
        return False
    xs.append(now)
    _USER_GEN[uid] = xs
    return True


# ─── заранее готовим всё, что звучит в игре ──────────────────────────────────

def phrases_from(data):
    """Все китайские фразы из файлов глав: реплики, задания, отдельные слова. Реплики с именем героя пропускаем."""
    out = set()

    def walk(x):
        if isinstance(x, list):
            if x and all(isinstance(e, dict) and ("h" in e or "x" in e or "name" in e) for e in x):
                if not any(e.get("name") for e in x):
                    s = "".join(e.get("h") or e.get("x") or "" for e in x)
                    if valid_text(s):
                        out.add(s)
            for e in x:
                walk(e)
        elif isinstance(x, dict):
            h = x.get("h")
            if isinstance(h, str) and valid_text(h):
                out.add(h)
            for v in x.values():
                walk(v)
    walk(data)
    return out


def prewarm(folder, delay=45, gap=1.5):
    """Фоном, не спеша. Если два раза подряд не вышло, останавливаемся."""
    def run():
        time.sleep(delay)
        phrases = set()
        for f in sorted(Path(folder).glob("*.json")):
            try:
                phrases |= phrases_from(json.loads(f.read_text(encoding="utf-8")))
            except Exception as e:
                logging.warning("озвучка: не прочитала %s: %s", f.name, e)
        todo = sorted(p for p in phrases if not cached(p))
        logging.info("озвучка: готовых фраз %s, надо сделать %s", len(phrases) - len(todo), len(todo))
        bad = 0
        for p in todo:
            if generate(p):
                bad = 0
            else:
                bad += 1
                if bad >= 2:
                    logging.warning("озвучка: останавливаю подготовку, сервисы недоступны")
                    return
            time.sleep(gap)
        logging.info("озвучка: подготовка закончена")
    threading.Thread(target=run, daemon=True, name="tts-prewarm").start()
