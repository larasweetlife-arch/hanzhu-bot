/* Шкафчик (v29, темы v32): каталог слов по ящичкам HSK и по темам, поиск, статусы, карточка слова и «Знаю это слово». */
(function () {
  "use strict";
  const Q = () => window.QY;
  const T = {
    ru: { m_lv: "По уровням", m_tp: "По темам", tshelf: "Все темы", topic: "Тема", fam: "Люди и семья", body: "Тело и здоровье", food: "Еда и напитки", home: "Дом и вещи", shop: "Одежда и покупки", city: "Город и транспорт", trip: "Путешествия и страны", nature: "Природа и погода", time: "Время и числа", work: "Учёба и работа", fun: "Досуг, спорт и культура", mind: "Чувства и общение", gen: "Общие слова", slang: "Сленг",
      title: "Шкафчик", ph: "Иероглиф, пиньинь или перевод", all: "Все", learn: "Учу", known: "Помню", due: "Повторить", st_new: "Новое", st_learn: "Учу", st_due: "Повторить", st_known: "Помню",
      of: "{a} из {b}", shelf: "Все ящички", more: "Показать ещё", shown: "Показано {a} из {b}", none: "Ничего не найдено", empty: "Здесь пока пусто",
      empty_learn: "Слова из карточек, которые ты ещё учишь, появятся здесь.", empty_known: "Выученные слова появятся здесь.", empty_due: "На сегодня повторять нечего.",
      level: "HSK {n}", level7: "HSK 7–9", part: "часть {n}", nolevel: "Без уровня", listen: "Послушать", know: "Знаю это слово", knew: "Отмечено: слово теперь в «Помню»", write: "Написать",
      examples: "Примеры", note: "Перевода на твой язык пока нет: показан {l}.", load: "Загрузка…", err: "Не удалось загрузить. Проверь интернет и попробуй ещё раз.", close: "Закрыть" },
    uz: { m_lv: "Darajalar bo‘yicha", m_tp: "Mavzular bo‘yicha", tshelf: "Barcha mavzular", topic: "Mavzu", fam: "Oila va odamlar", body: "Tana va salomatlik", food: "Taom va ichimliklar", home: "Uy va buyumlar", shop: "Kiyim va xaridlar", city: "Shahar va transport", trip: "Sayohat va mamlakatlar", nature: "Tabiat va ob-havo", time: "Vaqt va sonlar", work: "O‘qish va ish", fun: "Dam olish, sport, madaniyat", mind: "His-tuyg‘u va muloqot", gen: "Umumiy so‘zlar", slang: "Slang",
      title: "Javon", ph: "Ieroglif, pinyin yoki tarjima", all: "Hammasi", learn: "O‘rganyapman", known: "Eslab qoldim", due: "Takrorlash", st_new: "Yangi", st_learn: "O‘rganyapman", st_due: "Takrorlash", st_known: "Eslab qoldim",
      of: "{b} dan {a}", shelf: "Barcha tortmalar", more: "Yana ko‘rsatish", shown: "{b} dan {a} ko‘rsatildi", none: "Hech narsa topilmadi", empty: "Bu yerda hozircha bo‘sh",
      empty_learn: "Kartochkalardagi hali o‘rganayotgan so‘zlaringiz shu yerda ko‘rinadi.", empty_known: "O‘rganilgan so‘zlar shu yerda ko‘rinadi.", empty_due: "Bugun takrorlaydigan so‘z yo‘q.",
      level: "HSK {n}", level7: "HSK 7–9", part: "{n}-qism", nolevel: "Darajasiz", listen: "Tinglash", know: "Bu so‘zni bilaman", knew: "Belgilandi: so‘z endi «Eslab qoldim»da", write: "Yozish",
      examples: "Misollar", note: "Sizning tilingizda tarjima hali yo‘q: {l} ko‘rsatildi.", load: "Yuklanmoqda…", err: "Yuklab bo‘lmadi. Internetni tekshirib, qayta urinib ko‘ring.", close: "Yopish" },
    en: { m_lv: "By level", m_tp: "By topic", tshelf: "All topics", topic: "Topic", fam: "People & family", body: "Body & health", food: "Food & drinks", home: "Home & things", shop: "Clothes & shopping", city: "City & transport", trip: "Travel & countries", nature: "Nature & weather", time: "Time & numbers", work: "Study & work", fun: "Leisure, sport & culture", mind: "Feelings & talk", gen: "General words", slang: "Slang",
      title: "Locker", ph: "Character, pinyin or translation", all: "All", learn: "Learning", known: "Known", due: "Review", st_new: "New", st_learn: "Learning", st_due: "Review", st_known: "Known",
      of: "{a} of {b}", shelf: "All drawers", more: "Show more", shown: "Showing {a} of {b}", none: "Nothing found", empty: "Nothing here yet",
      empty_learn: "Words from your cards that you are still learning will appear here.", empty_known: "Words you have learned will appear here.", empty_due: "Nothing to review today.",
      level: "HSK {n}", level7: "HSK 7–9", part: "part {n}", nolevel: "No level", listen: "Listen", know: "I know this word", knew: "Marked: the word is now in “Known”", write: "Write",
      examples: "Examples", note: "No translation in your language yet: showing {l}.", load: "Loading…", err: "Could not load. Check your connection and try again.", close: "Close" },
    zh: { m_lv: "按等级", m_tp: "按主题", tshelf: "全部主题", topic: "主题", fam: "人物与家庭", body: "身体与健康", food: "饮食", home: "家与物品", shop: "服装与购物", city: "城市与交通", trip: "旅行与国家", nature: "自然与天气", time: "时间与数字", work: "学习与工作", fun: "休闲、运动与文化", mind: "情感与交流", gen: "常用词", slang: "网络流行语",
      title: "柜子", ph: "汉字、拼音或释义", all: "全部", learn: "在学", known: "记住了", due: "待复习", st_new: "新词", st_learn: "在学", st_due: "待复习", st_known: "记住了",
      of: "{a} / {b}", shelf: "全部抽屉", more: "显示更多", shown: "已显示 {a} / {b}", none: "没有找到", empty: "这里还没有内容",
      empty_learn: "卡片中还在学的词会出现在这里。", empty_known: "已记住的词会出现在这里。", empty_due: "今天没有要复习的词。",
      level: "HSK {n}", level7: "HSK 7–9", part: "第{n}部分", nolevel: "未分级", listen: "听", know: "我认识这个词", knew: "已标记：这个词现在是“记住了”", write: "书写",
      examples: "例句", note: "暂无你的语言的释义，显示的是 {l}。", load: "加载中…", err: "加载失败，请检查网络后重试。", close: "关闭" },
  };
  const tx = (k, v) => {
    const d = T[Q().S.lang] || T.ru; let s = d[k] !== undefined ? d[k] : T.ru[k];
    if (v && typeof s === "string") s = s.replace(/\{(\w+)\}/g, (_, x) => (v[x] !== undefined ? v[x] : ""));
    return s;
  };
  const LANG = { EN: { ru: "английский", uz: "inglizcha", en: "English", zh: "英语" }, RU: { ru: "русский", uz: "ruscha", en: "Russian", zh: "俄语" } };
  const GLYPH = { 1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 0: "其" };
  const TGLYPH = { fam: "家", body: "身", food: "食", home: "居", shop: "买", city: "城", trip: "游", nature: "天", time: "时", work: "学", fun: "乐", mind: "心", gen: "通", slang: "梗" };
  const st = { mode: "lv", data: null, flt: "all", q: "", drawer: null, items: null, total: 0, next: null, busy: false, err: false, seq: 0, box: null, timer: null };

  const isT = (id) => String(id || "").indexOf("t:") === 0;
  const tName = (id) => tx(String(id).replace(/^t:/, ""));
  function dName(d) {
    if (d.topic) return tName(d.id);
    if (d.level === 0) return tx("nolevel");
    if (d.level === 7) return tx("level7") + (d.parts > 1 ? " · " + tx("part", { n: d.part }) : "");
    return tx("level", { n: d.level });
  }

  async function loadShelf() {
    try { st.data = await Q().api("/api/locker", {}); st.err = false; } catch (e) { st.err = true; }
    paint();
  }
  // запрос списка: заново (reset) или следующая порция
  async function fetchList(reset) {
    const { api } = Q();
    const my = ++st.seq;
    if (reset) { st.items = null; st.next = null; st.total = 0; }
    st.busy = true; st.err = false; paint();
    try {
      const j = await api("/api/locker/list", { drawer: st.drawer || "", flt: st.flt, q: st.q, offset: reset ? 0 : (st.next || 0) });
      if (my !== st.seq) return;
      st.items = (reset ? [] : st.items || []).concat(j.items); st.total = j.total; st.next = j.next;
    } catch (e) { if (my !== st.seq) return; st.err = true; }
    st.busy = false; paint();
  }
  const listMode = () => !!(st.q.trim() || st.drawer || st.flt !== "all");
  function refresh() { if (listMode()) fetchList(true); else { st.items = null; paint(); } loadShelfQuiet(); }
  async function loadShelfQuiet() { try { st.data = await Q().api("/api/locker", {}); paint(); } catch (e) { /* ок */ } }

  function chips() {
    const { h } = Q(); const c = (st.data && st.data.counts) || {};
    const one = (id, label, n) => h("button", { class: st.flt === id ? "on" : "", onclick: () => { st.flt = id; refresh(); } }, label + (n ? " · " + n : ""));
    return h("div", { class: "seg lk-chips" }, one("all", tx("all"), 0), one("learn", tx("learn"), c.learn), one("known", tx("known"), c.known), one("due", tx("due"), c.due));
  }
  function modeSw() {
    const { h } = Q();
    if (!st.data || !(st.data.topics || []).length) return null;
    const one = (id, label) => h("button", { class: st.mode === id ? "on" : "", onclick: () => { if (st.mode === id) return; st.mode = id; st.drawer = null; refresh(); window.scrollTo(0, 0); } }, label);
    return h("div", { class: "seg lk-mode" }, one("lv", tx("m_lv")), one("tp", tx("m_tp")));
  }
  function shelf() {
    const { h } = Q();
    if (st.mode === "tp" && st.data && (st.data.topics || []).length) {
      return h("div", { class: "lk-shelf lk-tshelf" }, st.data.topics.map((t) =>
        h("button", { class: "lk-drawer lk-topic", onclick: () => { Q().haptic(); st.drawer = "t:" + t.id; fetchList(true); window.scrollTo(0, 0); } },
          h("span", { class: "lk-knob", "aria-hidden": "true" }), h("span", { class: "zh lk-gl" }, TGLYPH[t.id] || "题"),
          h("span", { class: "lk-dn" }, tName(t.id)), h("span", { class: "lk-dp" }, "\u00a0"), h("span", { class: "lk-dc" }, tx("of", { a: t.known, b: t.total })))));
    }
    if (!st.data) return h("div", { class: "hz-msg" }, st.err ? [tx("err"), h("br"), h("button", { class: "btn line sm", onclick: loadShelf }, "↻")] : tx("load"));
    return h("div", { class: "lk-shelf" }, st.data.drawers.map((d) =>
      h("button", { class: "lk-drawer", onclick: () => { Q().haptic(); st.drawer = d.id; fetchList(true); window.scrollTo(0, 0); } },
        h("span", { class: "lk-knob", "aria-hidden": "true" }), h("span", { class: "zh lk-gl" }, GLYPH[d.level] || "柜"),
        h("span", { class: "lk-dn" }, d.level === 7 ? tx("level7") : dName(d)), h("span", { class: "lk-dp" }, d.level === 7 && d.parts > 1 ? tx("part", { n: d.part }) : "\u00a0"), h("span", { class: "lk-dc" }, tx("of", { a: d.known, b: d.total })))));
  }
  function row(w) {
    const { h } = Q();
    return h("button", { class: "lk-row", onclick: () => openWord(w.zh) },
      h("span", { class: "zh lk-zh" }, w.zh),
      h("span", { class: "lk-mid" }, h("span", { class: "lk-tr" }, w.tr || "—", w.tag ? h("i", { class: "lk-tag" }, w.tag) : null), h("span", { class: "lk-py" }, w.py)),
      h("span", { class: "lk-st s-" + w.st }, tx("st_" + w.st)));
  }
  function list() {
    const { h } = Q();
    if (st.err && !st.items) return h("div", { class: "hz-msg" }, tx("err"), h("br"), h("button", { class: "btn line sm", onclick: () => fetchList(true) }, "↻"));
    if (!st.items) return h("div", { class: "hz-msg" }, tx("load"));
    if (!st.items.length) {
      const m = st.q.trim() ? tx("none") : (st.flt === "all" ? tx("empty") : tx("empty_" + st.flt));
      return h("div", { class: "hz-msg" }, m);
    }
    return h("div", {}, h("div", { class: "card lk-list" }, st.items.map(row)),
      h("div", { class: "muted lk-foot" }, tx("shown", { a: st.items.length, b: st.total })),
      st.next != null ? h("button", { class: "btn line", style: "width:100%;margin-top:8px", disabled: st.busy ? "" : null, onclick: () => fetchList(false) }, tx("more")) : null);
  }
  function drawerHead() {
    const { h } = Q();
    let d = null;
    if (st.data && st.drawer) {
      if (isT(st.drawer)) { const t = (st.data.topics || []).find((x) => "t:" + x.id === st.drawer); d = t ? { id: st.drawer, topic: 1, known: t.known, total: t.total } : null; }
      else d = st.data.drawers.find((x) => x.id === st.drawer);
    }
    if (!d) return null;
    return h("div", { class: "lk-head" }, h("button", { class: "linkbtn", onclick: () => { st.drawer = null; refresh(); window.scrollTo(0, 0); } }, "← " + tx(d.topic ? "tshelf" : "shelf")),
      h("div", {}, h("b", {}, dName(d)), h("span", { class: "muted" }, " · " + tx("of", { a: d.known, b: d.total }))));
  }
  function paint() {
    if (!st.box || !st.box.isConnected) return;
    const { h } = Q();
    st.box.replaceChildren(...[modeSw(), chips(), drawerHead(), listMode() ? list() : shelf()].filter(Boolean));
  }

  async function openWord(zh) {
    const { h, api, sheet, speak, toast, haptic } = Q();
    let w;
    try { w = await api("/api/locker/word", { zh }); } catch (e) { toast(tx("err")); return; }
    const bg = sheet(null);
    const box = bg.firstChild;
    function build() {
      const note = w.tag ? h("div", { class: "muted lk-note" }, tx("note", { l: (LANG[w.tag] || {})[Q().S.lang] || w.tag })) : null;
      const meta = [w.hsk ? (w.hsk === 7 ? tx("level7") : tx("level", { n: w.hsk })) : tx("nolevel"), w.topic ? tName(w.topic) : "", w.pos].filter(Boolean).join(" · ");
      box.replaceChildren(...[
        h("div", { class: "lk-wc" },
          h("div", { class: "zh lk-big" }, w.zh), h("div", { class: "lk-wpy" }, w.py),
          h("span", { class: "lk-st s-" + w.st }, tx("st_" + w.st)),
          h("div", { class: "lk-wtr" }, w.tr || "—", w.tag ? h("i", { class: "lk-tag" }, w.tag) : null), note,
          h("div", { class: "muted", style: "margin-top:4px" }, meta)),
        w.examples && w.examples.length ? h("div", { class: "lk-ex" }, h("b", {}, tx("examples")), w.examples.map((e) => h("div", {}, e))) : null,
        h("div", { class: "lk-btns" },
          h("button", { class: "btn line", onclick: () => speak(w.zh) }, "🔊 " + tx("listen")),
          w.chars && w.chars.length ? h("button", { class: "btn line", onclick: () => { bg.remove(); try { Q().stopSpeak(); } catch (e) { /* ок */ } window.HZ && window.HZ.open(w.zh); } }, "✍️ " + tx("write")) : null),
        w.st !== "known" ? h("button", { class: "btn jade", style: "width:100%;margin-top:10px", onclick: async () => {
          try { await api("/api/locker/know", { zh: w.zh }); } catch (e) { toast(tx("err")); return; }
          haptic(); toast(tx("knew")); bg.remove(); refresh();
        } }, "✓ " + tx("know")) : null,
        h("button", { class: "linkbtn", style: "width:100%;margin-top:12px", onclick: () => { try { Q().stopSpeak(); } catch (e) { /* ок */ } bg.remove(); } }, tx("close"))].filter(Boolean));
    }
    build();
  }

  function view() {
    const { h } = Q();
    const inp = h("input", { type: "search", class: "lk-search", placeholder: tx("ph"), value: st.q, "aria-label": tx("ph"), autocomplete: "off", enterkeyhint: "search" });
    inp.addEventListener("input", () => { st.q = inp.value; clearTimeout(st.timer); st.timer = setTimeout(() => { if (st.q.trim()) st.drawer = null; refresh(); }, 280); });
    st.box = h("div", {});
    const root = h("div", {}, h("h2", { class: "pg-title" }, tx("title")), h("div", { class: "lk-sw" }, inp), st.box);
    if (!st.data) loadShelf(); else paint();
    if (listMode() && !st.items) fetchList(true);
    setTimeout(paint, 0);
    return root;
  }
  window.LK = { view, openWord };
})();
