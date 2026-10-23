/* Каллиграфия: карточка иероглифа с порядком черт и обводкой (Hanzi Writer, MIT).
   Данные черт: hz/s0..s15.json (Arphic Public License), разбор: /api/hanzi. Тексты на 4 языках лежат здесь же. */
(function () {
  "use strict";
  const Q = () => window.QY;
  const T = {
    ru: { title: "Каллиграфия", sub: "Порядок черт и обводка иероглифов", back: "Назад", close: "Закрыть", show: "Показать", write: "Писать", again: "Сначала",
      stroke: "Черта {n} из {m}", mistakes: "Ошибок: {n}", done: "Готово!", done0: "Готово, без ошибок!", done_n: "Готово. Ошибок: {n}", strict: "Строгость", free: "Свободно", normal: "Обычно", hard: "Строго",
      parts: "Из чего состоит", radical: "Ключ", phon: "Фонетик (подсказка к звучанию)", sem: "Смысл", assoc: "Ассоциация", words: "Слова с этим иероглифом", level: "Уровень HSK {n}",
      nodata: "Для этого иероглифа пока нет порядка черт.", offline: "Не удалось загрузить. Проверь интернет и попробуй ещё раз.", loading: "Загрузка…", lvl: "HSK {n}", hint: "Нажми на иероглиф в списке, чтобы потренироваться.", listen: "Послушать", tap: "Нажми на слово, чтобы послушать" },
    uz: { title: "Kalligrafiya", sub: "Chiziqlar tartibi va ustidan yozish", back: "Orqaga", close: "Yopish", show: "Ko‘rsatish", write: "Yozish", again: "Qaytadan",
      stroke: "{m} dan {n}-chiziq", mistakes: "Xatolar: {n}", done: "Tayyor!", done0: "Tayyor, xatosiz!", done_n: "Tayyor. Xatolar: {n}", strict: "Qat’iylik", free: "Erkin", normal: "Oddiy", hard: "Qat’iy",
      parts: "Nimadan tuzilgan", radical: "Kalit", phon: "Fonetik (talaffuz ishorasi)", sem: "Ma’no", assoc: "Assotsiatsiya", words: "Bu ieroglifli so‘zlar", level: "HSK {n}-daraja",
      nodata: "Bu ieroglif uchun chiziqlar tartibi hozircha yo‘q.", offline: "Yuklab bo‘lmadi. Internetni tekshirib, qayta urinib ko‘ring.", loading: "Yuklanmoqda…", lvl: "HSK {n}", hint: "Mashq qilish uchun ro‘yxatdan ieroglifni bosing.", listen: "Tinglash", tap: "Tinglash uchun so‘zni bosing" },
    en: { title: "Calligraphy", sub: "Stroke order and tracing", back: "Back", close: "Close", show: "Show me", write: "Write", again: "Restart",
      stroke: "Stroke {n} of {m}", mistakes: "Mistakes: {n}", done: "Done!", done0: "Done, no mistakes!", done_n: "Done. Mistakes: {n}", strict: "Strictness", free: "Relaxed", normal: "Normal", hard: "Strict",
      parts: "What it is made of", radical: "Radical", phon: "Phonetic (sound clue)", sem: "Meaning", assoc: "Mnemonic", words: "Words with this character", level: "HSK level {n}",
      nodata: "No stroke order for this character yet.", offline: "Could not load. Check your connection and try again.", loading: "Loading…", lvl: "HSK {n}", hint: "Tap a character to practise it.", listen: "Listen", tap: "Tap a word to hear it" },
    zh: { title: "书法", sub: "笔顺与描红", back: "返回", close: "关闭", show: "演示", write: "书写", again: "重来",
      stroke: "第 {n} 笔 / 共 {m} 笔", mistakes: "错误：{n}", done: "完成！", done0: "完成，没有错误！", done_n: "完成。错误：{n}", strict: "严格度", free: "宽松", normal: "普通", hard: "严格",
      parts: "字的构成", radical: "部首", phon: "声旁（读音线索）", sem: "义旁", assoc: "联想", words: "含此字的词", level: "HSK {n} 级",
      nodata: "这个字暂时没有笔顺数据。", offline: "加载失败，请检查网络后重试。", loading: "加载中…", lvl: "HSK {n}", hint: "点一个字开始练习。", listen: "朗读", tap: "点词语可朗读" },
  };
  const tx = (k, v) => {
    const d = T[Q().S.lang] || T.ru;
    let s = d[k] !== undefined ? d[k] : T.ru[k];
    if (v) s = s.replace(/\{(\w+)\}/g, (_, x) => (v[x] !== undefined ? v[x] : ""));
    return s;
  };
  const LEN = { free: [1.6, 1], normal: [1.0, 3], hard: [0.65, false] };
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* без хранилища тоже работаем */ } },
  };
  const css = (n, d) => (getComputedStyle(document.documentElement).getPropertyValue(n).trim() || d);

  // ── загрузка библиотеки и данных черт ──
  let libP = null;
  function loadLib() {
    if (window.HanziWriter) return Promise.resolve();
    if (!libP) libP = new Promise((ok, no) => {
      const s = document.createElement("script"); s.src = "/static/hanzi-writer.min.js";
      s.onload = ok; s.onerror = () => { libP = null; no(new Error("lib")); };
      document.head.append(s);
    });
    return libP;
  }
  const shards = {};
  function shard(n) {
    if (!shards[n]) shards[n] = fetch("/static/hz/s" + n + ".json").then((r) => { if (!r.ok) throw new Error("shard"); return r.json(); }).catch((e) => { delete shards[n]; throw e; });
    return shards[n];
  }
  const loader = (ch, ok, bad) => { shard(ch.codePointAt(0) % 16).then((d) => (d[ch] ? ok(d[ch]) : bad())).catch(bad); };

  // ── карточка ──
  let ov = null;
  function close() { if (ov) { try { window.QY.stopSpeak(); } catch (e) { /* ок */ } ov.remove(); ov = null; document.body.classList.remove("hz-lock"); } }

  async function open(chars) {
    const { h, api, safe, toast } = Q();
    const list = String(chars || "").split("").filter((c) => /[㐀-鿿]/.test(c)).slice(0, 6);
    if (!list.length) return;
    close();
    document.body.classList.add("hz-lock");
    const body = h("div", { class: "hz-body" }, h("div", { class: "hz-msg" }, tx("loading")));
    ov = h("div", { class: "hz-ov", role: "dialog" },
      h("div", { class: "hz-top" }, h("button", { class: "hz-x", "aria-label": tx("close"), onclick: close }, "✕")), body);
    document.body.append(ov);
    const mine = ov;
    let cards;
    try {
      const j = await api("/api/hanzi", { c: list.join("") });
      cards = j.cards;
    } catch (e) { if (ov === mine) body.replaceChildren(h("div", { class: "hz-msg" }, tx("offline"), h("br"), h("button", { class: "btn line sm", onclick: () => open(chars) }, "↻"))); return; }
    if (ov !== mine) return;
    let cur = 0;
    const tabs = h("div", { class: "hz-tabs" });
    const view = h("div", {});
    const drawTabs = () => {
      tabs.replaceChildren(...(cards.length > 1 ? cards.map((c, i) => h("button", { class: "hz-tab zh" + (i === cur ? " on" : ""), onclick: () => { cur = i; drawTabs(); drawCard(); } }, c.c)) : []));
    };
    const drawCard = () => { try { window.QY.stopSpeak(); } catch (e) { /* ок */ } view.replaceChildren(cardView(cards[cur], mine)); mine.scrollTop = 0; };
    body.replaceChildren(tabs, view);
    drawTabs(); drawCard();
  }

  function sec(title, ...kids) { const { h } = Q(); return h("div", { class: "hz-sec" }, h("h4", {}, title), ...kids); }

  function cardView(c, owner) {
    const { h, speak, haptic, confetti } = Q();
    const wrap = h("div", {});
    const head = h("div", { class: "hz-head" },
      h("div", { class: "hz-py" }, c.py || "·", " ", h("button", { class: "hz-say", "aria-label": tx("listen"), onclick: () => speak(c.c) }, "🔊")),
      h("div", { class: "hz-mean" }, c.meaning || ""),
      c.level ? h("span", { class: "hz-badge" }, tx("lvl", { n: c.level })) : null);
    wrap.append(head);
    if (!c.writable) { wrap.append(h("div", { class: "hz-msg" }, tx("nodata"))); appendInfo(wrap, c); return wrap; }

    const box = h("div", { class: "hz-box" }, h("div", { class: "hz-grid", "aria-hidden": "true" }));
    const status = h("div", { class: "hz-status", "aria-live": "polite" }, " ");
    const lvl = store.get("hz_strict") || "normal";
    let strict = LEN[lvl] ? lvl : "normal";
    let writer = null, mode = "idle", mistakes = 0, total = 0;

    const side = () => Math.max(220, Math.min(320, owner.clientWidth - 48 || 300));
    const btnShow = h("button", { class: "btn jade sm", onclick: () => run("show") }, "▶ " + tx("show"));
    const btnWrite = h("button", { class: "btn primary sm", onclick: () => run("write") }, "✍️ " + tx("write"));
    const btnAgain = h("button", { class: "btn line sm", onclick: () => run("reset") }, "↺ " + tx("again"));
    const chips = h("div", { class: "hz-chips" }, ["free", "normal", "hard"].map((k) => h("button", { class: "hz-chip" + (k === strict ? " on" : ""), onclick: (e) => {
      strict = k; store.set("hz_strict", k);
      chips.querySelectorAll(".hz-chip").forEach((n, i) => n.classList.toggle("on", ["free", "normal", "hard"][i] === k));
      if (mode === "write") run("write");
    } }, tx(k))));

    async function ensure() {
      if (writer) return writer;
      await loadLib();
      const s = side();
      box.style.width = s + "px"; box.style.height = s + "px";
      const holder = h("div", { class: "hz-canvas" }); box.append(holder);
      writer = window.HanziWriter.create(holder, c.c, {
        width: s, height: s, padding: 12, charDataLoader: loader,
        strokeColor: css("--ink", "#22302b"), radicalColor: css("--seal", "#c5413a"), outlineColor: css("--line", "rgba(0,0,0,.18)"),
        highlightColor: css("--jade", "#2c6c5b"), drawingColor: css("--jade", "#2c6c5b"), drawingWidth: 6,
        showOutline: true, showCharacter: true, strokeAnimationSpeed: 1.2, delayBetweenStrokes: 250, strokeFadeDuration: 250,
      });
      try { writer.getCharacterData().then((d) => { total = (d && d.strokes && d.strokes.length) || 0; }).catch(() => { /* число черт не обязательно */ }); } catch (e) { /* ок */ }
      return writer;
    }
    async function run(what) {
      try { await ensure(); } catch (e) { status.textContent = tx("offline"); return; }
      writer.cancelQuiz(); mistakes = 0;
      if (what === "show" || what === "reset") {
        mode = what === "show" ? "show" : "idle";
        writer.showCharacter(); writer.showOutline();
        status.textContent = " ";
        if (what === "show") writer.animateCharacter({ onComplete: () => { mode = "idle"; } });
        return;
      }
      mode = "write";
      writer.hideCharacter(); writer.showOutline();
      const cfg = LEN[strict];
      status.textContent = total ? tx("stroke", { n: 1, m: total }) : " ";
      writer.quiz({
        leniency: cfg[0], showHintAfterMisses: cfg[1], highlightOnComplete: true,
        onCorrectStroke: (d) => { haptic(); const m = d.strokeNum + 1 + d.strokesRemaining; status.textContent = tx("stroke", { n: Math.min(d.strokeNum + 2, m), m }); },
        onMistake: (d) => { mistakes = d.totalMistakes; haptic("bad"); status.textContent = tx("mistakes", { n: mistakes }); },
        onComplete: (d) => {
          mode = "idle"; const n = d.totalMistakes || 0;
          status.textContent = "🎉 " + (n === 0 ? tx("done0") : tx("done_n", { n }));
          if (n === 0) { haptic("ok"); confetti(); } else haptic("ok");
        },
      });
    }
    wrap.append(h("div", { class: "hz-stage" }, box), status, h("div", { class: "hz-btns" }, btnShow, btnWrite, btnAgain),
      h("div", { class: "hz-strict" }, h("span", {}, tx("strict")), chips));
    // порядок черт показываем сразу
    setTimeout(() => { if (owner.isConnected) run("show"); }, 250);
    appendInfo(wrap, c);
    return wrap;
  }

  function appendInfo(wrap, c) {
    const { h, speak } = Q();
    const cell = (p) => h("div", { class: "hz-part" }, h("span", { class: "zh hz-pc" }, p.c), h("div", {}, h("b", {}, p.py || "·"), h("small", {}, p.m || "")));
    if (c.radical || (c.parts && c.parts.length)) {
      const kids = [];
      if (c.radical) kids.push(h("div", { class: "hz-rad" }, h("b", {}, tx("radical") + ": "), h("span", { class: "zh hz-radc" }, c.radical.c), c.radical.m ? " " + c.radical.m : ""));
      if (c.parts && c.parts.length) kids.push(h("div", { class: "hz-parts" }, c.parts.map(cell)));
      if (c.kind === "pictophonetic" && (c.semantic || c.phonetic)) {
        const bits = [];
        if (c.semantic && !(c.radical && c.radical.c === c.semantic.c)) bits.push(tx("sem") + ": " + c.semantic.c + (c.semantic.m ? " (" + c.semantic.m + ")" : ""));
        if (c.phonetic) bits.push(tx("phon") + ": " + c.phonetic.c + (c.phonetic.py ? " (" + c.phonetic.py + ")" : ""));
        if (bits.length) kids.push(h("div", { class: "hz-note" }, bits.join(" · ")));
      }
      if (c.hint) kids.push(h("div", { class: "hz-note" }, c.hint));
      wrap.append(sec(tx("parts"), ...kids));
    }
    if (c.assoc) wrap.append(sec("💡 " + tx("assoc"), h("div", { class: "hz-assoc" }, c.assoc)));
    if (c.words && c.words.length) {
      wrap.append(sec(tx("words"), h("div", { class: "hz-note", style: "margin:-4px 0 8px" }, tx("tap")), h("div", { class: "hz-words" }, c.words.map((w) =>
        h("button", { class: "hz-word", onclick: () => speak(w.zh) }, h("span", { class: "zh" }, w.zh), h("span", { class: "hz-wt" }, h("small", {}, w.py), h("small", {}, w.m)))))));
    }
  }

  // ── список иероглифов ──
  const st = { levels: null, err: false, loading: false };
  function load() {
    if (st.levels || st.loading) return;
    st.loading = true;
    Q().api("/api/hanzi/list").then((j) => { st.levels = j.levels; }).catch(() => { st.err = true; }).finally(() => { st.loading = false; Q().render(); });
  }
  function listView() {
    const { h, S, render } = Q();
    load();
    const out = [h("button", { class: "linkbtn", style: "margin-bottom:10px", onclick: () => { S.playSub = null; render(); window.scrollTo(0, 0); } }, "← " + tx("back")),
      h("div", { class: "card hero" }, h("h2", {}, "✍️ " + tx("title")), h("div", { style: "margin-top:4px;opacity:.9" }, tx("sub")))];
    if (st.levels) {
      out.push(h("div", { class: "hz-hint" }, tx("hint")));
      for (const L of st.levels) out.push(h("div", { class: "card" }, h("h3", {}, tx("level", { n: L.level }), " · ", L.chars.length),
        h("div", { class: "hz-list" }, L.chars.map((ch) => h("button", { class: "hz-cell zh", onclick: () => open(ch) }, ch)))));
    } else out.push(h("div", { class: "hz-msg" }, st.err ? [tx("offline"), h("br"), h("button", { class: "btn line sm", onclick: () => { st.err = false; load(); render(); } }, "↻")] : tx("loading")));
    return h("div", {}, out);
  }
  function entryCard() {
    const { h, S, render, haptic } = Q();
    return h("button", { class: "card qrate", onclick: () => { S.playSub = "hz"; haptic(); render(); window.scrollTo(0, 0); } },
      h("div", { class: "row" }, h("span", { class: "em" }, "✍️"), h("div", { style: "flex:1;text-align:left" }, h("b", {}, tx("title")), h("div", { class: "muted" }, tx("sub")))));
  }

  const CR = { ru: "Порядок черт: Make Me a Hanzi и hanzi-writer-data (Arphic Public License, LGPL), библиотека Hanzi Writer (MIT).", uz: "Chiziqlar tartibi: Make Me a Hanzi va hanzi-writer-data (Arphic Public License, LGPL), Hanzi Writer kutubxonasi (MIT).",
    en: "Stroke data: Make Me a Hanzi and hanzi-writer-data (Arphic Public License, LGPL); Hanzi Writer library (MIT).", zh: "笔顺数据：Make Me a Hanzi 与 hanzi-writer-data（Arphic Public License、LGPL）；Hanzi Writer 库（MIT）。" };
  const credit = () => Q().h("div", { class: "foot" }, CR[Q().S.lang] || CR.ru);
  window.HZ = { open, close, listView, entryCard, credit };
})();
