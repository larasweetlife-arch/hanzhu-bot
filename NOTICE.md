# Источники

**Словарь перевода** построен на CC-CEDICT: свободный китайско-английский словарь,
поддерживается сообществом, публикуется MDBG.
Лицензия: Creative Commons Attribution-ShareAlike 4.0 International
https://creativecommons.org/licenses/by-sa/4.0/
Основа: CEDICT, Copyright (C) 1997, 1998 Paul Andrew Denisowski.
Файл `cedict.txt.gz` взят из пакета pycccedict без изменений.

**Список слов HSK** (`content_hsk.txt`) собран из проекта complete-hsk-vocabulary
(Yanis Zafirópulos), лицензия MIT: https://github.com/drkameleon/complete-hsk-vocabulary
Значения слов в нём происходят из CC-CEDICT (лицензия выше).

**БКРС** (https://bkrs.info) бот не использует как источник данных: только даёт ссылку на сайт.

**Твои учебные материалы** (`content_hsk30.txt`, `content_hsk5.txt`, `content_grammar.txt`) разобраны из файлов,
которые прислала Лазиза: списки слов HSK 3.0 уровней 1–4, таблица слов HSK 2.0 (на ней указан сайт myhsk.org)
и документы с грамматикой (ссылаются на официальную программу HSK, 2025). **Прежде чем выкладывать их в
публичный репозиторий, проверь права на эти материалы.** Если репозиторий публичный, файлы видны всем.

**Тексты** (`content_texts.txt`): адаптированные написаны для этого бота. Стихи Ли Бо, Мэн Хаожаня и Ван Чжихуаня
относятся к общественному достоянию, перевод на русский авторский.

**Список слов HSK 3.0** (`content_hsk30.txt`): иероглифы, пиньинь, части речи и уровни взяты из официального «新版HSK考试大纲» (Chinese Testing International, 2025). Английские значения адаптированы из CC-CEDICT (лицензия CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/). Русские значения: из списков автора проекта.

**Каллиграфия** (`webapp_static/hz/`, `hanzi-writer.min.js`, `hanzi_parts.json`):
- Порядок и форма черт: пакет hanzi-writer-data 2.0.1 (https://github.com/chanind/hanzi-writer-data), основан на проекте Make Me a Hanzi (https://github.com/skishore/makemeahanzi). Графика получена из шрифтов Arphic PL KaitiM GB и Arphic PL UKai и распространяется по **Arphic Public License** (текст в `webapp_static/hz/ARPHICPL.TXT`, не удалять). Мы изменили только упаковку: данные разных иероглифов собраны в 16 файлов, лишние поля убраны (23.10.2026). Эти данные остаются свободно доступными.
- Разбор иероглифов на части (`hanzi_parts.json`): из файла dictionary.txt проекта Make Me a Hanzi, лицензия **LGPL-3.0 или новее** (`webapp_static/hz/COPYING-makemeahanzi.txt`). Мы взяли только подмножество для иероглифов HSK 3.0 уровней 1–2.
- Библиотека **Hanzi Writer** 3.7.3, лицензия **MIT** (`webapp_static/hz/LICENSE-hanzi-writer.txt`), https://hanziwriter.org
- Русские значения частей иероглифов (`content_hanzi_ru.txt`) написаны для проекта и не сверялись с носителем языка.
