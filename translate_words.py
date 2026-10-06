"""
Перевод слов из автоматического списка на русский и узбекский через Claude API.

Запуск (Windows, командная строка, в папке с ботом):
    set ANTHROPIC_API_KEY=ваш_ключ
    python translate_words.py --dry-run          сначала только посчитает, сколько слов и примерно сколько токенов
    python translate_words.py                    переведёт всё, что ещё не переведено
    python translate_words.py --limit 200        только 200 слов (для пробы)
    python translate_words.py --level 6          только слова HSK 6

Результат дописывается в content_translations_auto.txt. Скрипт можно остановить и запустить снова:
уже переведённое он пропустит. Загрузи получившийся файл на GitHub, и бот его подхватит.
Ключ API никуда не записывается. Не вставляй его в чат и не загружай на GitHub.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = Path(__file__).parent
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
BATCH = int(os.environ.get("BATCH", "40"))
OUT = BASE / "content_translations_auto.txt"
HEADER = ("# Автоматические переводы слов (русский, узбекский). Сделаны через Claude API скриптом translate_words.py.\n"
          "# Не проверены носителем. Формат: иероглифы | по-русски | по-узбекски | пиньинь (необязательно).\n")

CYR = re.compile(r"[а-яёА-ЯЁ]")
HAN = re.compile(r"[\u4e00-\u9fff]")
LAT = re.compile(r"[A-Za-z]")

SYSTEM = (
    "Ты опытный лексикограф китайского языка для русскоязычных и узбекоязычных учащихся. "
    "Для каждого слова дай краткий словарный перевод на русский и на узбекский (латиницей). "
    "Правила: 1-4 значения через точку с запятой, самые употребительные первыми, без примеров и пояснений. "
    "Английское значение в данных может быть редким или неточным: переводи то значение, которое слово чаще всего "
    "имеет в современном китайском и в экзамене HSK. Для счётных слов пиши «сч. сл. для ...», для частиц и междометий "
    "указывай функцию. В узбекском языке используй латиницу и апостроф для oʻ и gʻ (пиши o' и g'). "
    "Верни ТОЛЬКО JSON-массив вида [{\"i\": 1, \"ru\": \"...\", \"uz\": \"...\"}] без какого-либо другого текста."
)


def read_table(name, nfields):
    path = BASE / name
    rows = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                p = [x.strip() for x in line.split("|")]
                if len(p) >= nfields:
                    rows.append(p)
    return rows


def already_covered():
    """Слова, которые переводить не нужно: у них есть русский перевод в других файлах."""
    zh = set()
    for name, n in (("content_words.txt", 6), ("content_hsk30.txt", 5), ("content_hsk5.txt", 5),
                    ("content_translations.txt", 3), ("content_translations_auto.txt", 3)):
        zh.update(p[0] for p in read_table(name, n))
    return zh


def load_pending(level=None):
    done = already_covered()
    pending = []
    for p in read_table("content_hsk.txt", 4):          # иероглифы | пиньинь | уровень | английский
        zh, py, lv, en = p[0], p[1], p[2], p[3]
        if zh in done or (level is not None and lv != str(level)):
            continue
        pending.append({"zh": zh, "py": py, "level": lv, "en": en})
    return pending


def make_prompt(batch):
    items = [{"i": k + 1, "zh": w["zh"], "pinyin": w["py"], "english": w["en"]} for k, w in enumerate(batch)]
    return "Переведи слова:\n" + json.dumps(items, ensure_ascii=False)


def call_api(prompt, key):
    """Один запрос к API. Возвращает текст ответа. Заменяется в проверках заглушкой."""
    body = json.dumps({"model": MODEL, "max_tokens": 4096, "system": SYSTEM,
                       "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body, method="POST", headers={
        "content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
    return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")


def call_with_retry(prompt, key, tries=5, sleep=time.sleep):
    for attempt in range(tries):
        try:
            return call_api(prompt, key)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise SystemExit("Ключ API не подошёл (ошибка %d). Проверь ANTHROPIC_API_KEY." % e.code)
            if e.code not in (408, 429, 500, 502, 503, 529) or attempt == tries - 1:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == tries - 1:
                raise
        sleep(5 * 2 ** attempt)                          # ждём дольше с каждой попыткой


def valid_ru(s):
    return bool(s) and CYR.search(s) and len(s) <= 160 and "|" not in s and "\n" not in s


def valid_uz(s):
    return bool(s) and LAT.search(s) and not CYR.search(s) and not HAN.search(s) and len(s) <= 160 and "|" not in s and "\n" not in s


def parse_response(text, batch):
    """Достаёт из ответа JSON-массив и оставляет только проверенные переводы: {иероглифы: (ru, uz)}."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end < 0:
        return {}
    try:
        arr = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return {}
    out = {}
    for it in arr:
        try:
            w = batch[int(it["i"]) - 1]
        except (KeyError, ValueError, IndexError, TypeError):
            continue
        ru, uz = str(it.get("ru", "")).strip(), str(it.get("uz", "")).strip()
        if valid_ru(ru) and valid_uz(uz):
            out[w["zh"]] = (ru, uz)
    return out


def append_results(results):
    if not results:
        return                                           # нечего писать: не создаём файл с одной шапкой
    new_file = not OUT.exists()
    with open(OUT, "a", encoding="utf-8") as f:
        if new_file:
            f.write(HEADER)
        for zh, (ru, uz) in results.items():
            f.write(f"{zh} | {ru} | {uz}\n")


def run(limit=None, level=None, dry=False, key=None, sleep=time.sleep, log=print):
    pending = load_pending(level)
    if limit:
        pending = pending[:limit]
    chars = sum(len(w["zh"]) + len(w["py"]) + len(w["en"]) + 30 for w in pending)
    log(f"К переводу: {len(pending)} слов, {-(-len(pending) // BATCH)} запросов по {BATCH}.")
    log(f"Примерно {chars // 3 + 400 * (-(-len(pending) // BATCH))} входных и {len(pending) * 28} выходных токенов. "
        f"Модель: {MODEL}. Цену смотри на странице тарифов Anthropic.")
    if dry or not pending:
        return {"requested": len(pending), "saved": 0}
    if not key:
        raise SystemExit("Не задан ключ. В командной строке: set ANTHROPIC_API_KEY=твой_ключ")
    saved = 0
    for b in range(0, len(pending), BATCH):
        batch = pending[b:b + BATCH]
        got = {}
        for attempt in range(3):                         # если ответ пришёл не в том формате, пробуем ещё раз
            text = call_with_retry(make_prompt(batch), key, sleep=sleep)
            got = parse_response(text, batch)
            if len(got) >= len(batch) * 0.8:
                break
        append_results(got)
        saved += len(got)
        log(f"  {min(b + BATCH, len(pending))}/{len(pending)}: сохранено {len(got)} из {len(batch)}")
    return {"requested": len(pending), "saved": saved}


def main(argv):
    limit = level = None
    if "--limit" in argv:
        limit = int(argv[argv.index("--limit") + 1])
    if "--level" in argv:
        level = int(argv[argv.index("--level") + 1])
    r = run(limit=limit, level=level, dry="--dry-run" in argv, key=os.environ.get("ANTHROPIC_API_KEY", "").strip())
    if "--dry-run" not in argv:
        print(f"Готово: сохранено {r['saved']} из {r['requested']}. Не вошедшее можно перезапустить: скрипт продолжит с места остановки.")


if __name__ == "__main__":
    main(sys.argv[1:])
