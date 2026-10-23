"""Согласие в мини-аппе (v31). Тексты лежат в content_consent.txt (ru, uz, en, zh).
Если меняешь текст по существу, увеличь CONSENT_VERSION: тогда все увидят экран согласия заново."""
import os
import re

CONSENT_VERSION = 1
LANGS = ("ru", "uz", "en", "zh")
_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content_consent.txt")
_BLOCKS = None


def _load():
    global _BLOCKS
    if _BLOCKS is not None:
        return _BLOCKS
    out, cur = {}, None
    try:
        with open(_FILE, encoding="utf-8") as f:
            for line in f.read().splitlines():
                m = re.match(r"^## (\w+)\s*$", line)
                if m:
                    cur = m.group(1)
                    out[cur] = []
                    continue
                if cur is None or not line.strip() or line.startswith("# ") and cur is None:
                    continue
                if line.startswith("# "):
                    out[cur].append({"t": "h", "x": line[2:].strip()})
                elif line.startswith("· "):
                    out[cur].append({"t": "li", "x": line[2:].strip()})
                else:
                    out[cur].append({"t": "p", "x": line.strip()})
    except OSError:
        out = {}
    _BLOCKS = out
    return out


def blocks(lang):
    b = _load()
    return b.get(lang) or b.get("ru") or []
