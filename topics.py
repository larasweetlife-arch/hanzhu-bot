"""Темы слов (v32). Какое слово к какой теме относится, лежит в content_topics.txt:
разделы `## код — название`, в строке слова важна только часть до первой « | » (иероглиф).
Названия тем на четырёх языках лежат в webapp_static/locker.js. Порядок тем = порядок разделов в файле.
Одно слово = одна тема (если слово записано дважды, берётся первая запись)."""
import os
import re

_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content_topics.txt")
_CACHE = None


def load():
    """[(код, [иероглифы])]; пустые разделы и неизвестные слова отсеивает вызывающий."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    out, seen, cur = [], set(), None
    try:
        with open(_FILE, encoding="utf-8") as f:
            for line in f.read().splitlines():
                m = re.match(r"^##\s*([a-z0-9_]+)\b", line)
                if m:
                    cur = (m.group(1), [])
                    out.append(cur)
                    continue
                s = line.strip()
                if not s or s.startswith("#") or cur is None:
                    continue
                zh = s.split("|", 1)[0].strip()
                if zh and zh not in seen:
                    seen.add(zh)
                    cur[1].append(zh)
    except OSError:
        out = []
    _CACHE = out
    return out
