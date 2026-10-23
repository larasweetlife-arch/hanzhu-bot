/* Практика фонетики (v27): «услышь и выбери тон» и «скажи» с проверкой голосом. Теория лежит в меню бота. */
(function () {
  "use strict";
  const Q = () => window.QY;
  const T = {
    ru: { title: "Фонетика: тренировка", sub: "Тоны на слух и голосом", back: "Назад", hear: "Услышь и выбери тон", hear_sub: "10 слогов. Слушай и выбирай, какой тон прозвучал. Без штрафов.",
      say: "Скажи сам(а)", say_sub: "8 слогов. Послушай образец и повтори, приложение покажет линию голоса.", q: "Слог {n} из {m}", listen: "Послушать", pick: "Какой это тон?",
      right: "Верно!", wrong: "Не совсем. Это {n}-й тон.", next: "Дальше", result: "Результат", done: "Готово!", score: "Верно: {n} из {m}", again: "Ещё раз", menu: "К тренировкам",
      loading: "Загрузка…", offline: "Не удалось загрузить. Проверь интернет и попробуй ещё раз.", tone: "Тон {n}", t1: "ровный", t2: "вверх", t3: "вниз-вверх", t4: "вниз",
      praise: ["Отличный слух!", "Хороший результат!", "Уже неплохо, ухо привыкает!", "Первый шаг сделан, ухо привыкает с практикой."], say_note: "Скажи слог и посмотри на линию. Это подсказка, а не оценка." },
    uz: { title: "Fonetika: mashq", sub: "Ohanglarni quloq va ovoz bilan", back: "Orqaga", hear: "Eshiting va ohangni tanlang", hear_sub: "10 ta bo‘g‘in. Tinglang va qaysi ohang bo‘lganini tanlang. Jarimasiz.",
      say: "O‘zingiz ayting", say_sub: "8 ta bo‘g‘in. Namunani tinglab, takrorlang, ilova ovoz chizig‘ini ko‘rsatadi.", q: "{m} dan {n}-bo‘g‘in", listen: "Tinglash", pick: "Bu qaysi ohang?",
      right: "To‘g‘ri!", wrong: "Unchalik emas. Bu {n}-ohang.", next: "Keyingisi", result: "Natija", done: "Tayyor!", score: "To‘g‘ri: {m} dan {n}", again: "Yana bir bor", menu: "Mashqlarga",
      loading: "Yuklanmoqda…", offline: "Yuklab bo‘lmadi. Internetni tekshirib, qayta urinib ko‘ring.", tone: "{n}-ohang", t1: "tekis", t2: "yuqoriga", t3: "pastga-yuqoriga", t4: "pastga",
      praise: ["Ajoyib eshitish!", "Yaxshi natija!", "Yomon emas, quloq o‘rganyapti!", "Birinchi qadam qo‘yildi, quloq mashq bilan o‘rganadi."], say_note: "Bo‘g‘inni ayting va chiziqni ko‘ring. Bu maslahat, baho emas." },
    en: { title: "Phonetics practice", sub: "Tones by ear and by voice", back: "Back", hear: "Listen and pick the tone", hear_sub: "10 syllables. Listen and choose which tone you heard. No penalties.",
      say: "Say it yourself", say_sub: "8 syllables. Listen to the sample and repeat; the app shows your voice line.", q: "Syllable {n} of {m}", listen: "Listen", pick: "Which tone is it?",
      right: "Correct!", wrong: "Not quite. It is tone {n}.", next: "Next", result: "Result", done: "Done!", score: "Correct: {n} of {m}", again: "Again", menu: "Back to practice",
      loading: "Loading…", offline: "Could not load. Check your connection and try again.", tone: "Tone {n}", t1: "level", t2: "rising", t3: "dip-rise", t4: "falling",
      praise: ["Excellent ear!", "Good result!", "Not bad, your ear is getting used to it!", "First step done; your ear improves with practice."], say_note: "Say the syllable and look at the line. It is a hint, not a grade." },
    zh: { title: "语音练习", sub: "用耳朵和声音练声调", back: "返回", hear: "听音选声调", hear_sub: "10 个音节。听一听，选出是第几声。不扣分。",
      say: "自己说", say_sub: "8 个音节。听示范后跟读，应用会显示你的声音曲线。", q: "第 {n} / {m} 个音节", listen: "听", pick: "这是第几声？",
      right: "正确！", wrong: "不太对，这是第{n}声。", next: "下一个", result: "查看结果", done: "完成！", score: "答对：{n} / {m}", again: "再来一次", menu: "回到练习",
      loading: "加载中…", offline: "加载失败，请检查网络后重试。", tone: "第{n}声", t1: "平", t2: "升", t3: "降升", t4: "降",
      praise: ["耳朵真灵！", "成绩不错！", "还不错，耳朵正在适应！", "迈出了第一步，多练耳朵会越来越灵。"], say_note: "说出音节，看看曲线。这只是提示，不是打分。" },
  };
  const tx = (k, v) => {
    const d = T[Q().S.lang] || T.ru; let s = d[k] !== undefined ? d[k] : T.ru[k];
    if (v && typeof s === "string") s = s.replace(/\{(\w+)\}/g, (_, x) => (v[x] !== undefined ? v[x] : ""));
    return s;
  };
  const MARK = { 1: "ˉ", 2: "ˊ", 3: "ˇ", 4: "ˋ" }, ARROW = { 1: "→", 2: "↗", 3: "↘↗", 4: "↘" };
  const st = { mode: null, items: null, i: 0, score: 0, picked: null, tones: false, loading: false, err: false };

  async function load(mode) {
    st.loading = true; st.err = false; st.items = null; st.mode = mode; st.i = 0; st.score = 0; st.picked = null; Q().render();
    try { const j = await Q().api("/api/phon/quiz", { mode }); st.items = j.items; st.tones = !!j.tones; } catch (e) { st.err = true; }
    st.loading = false; Q().render();
    if (st.items && mode === "hear") setTimeout(() => Q().speak(st.items[0].c), 150);
  }
  function entryCard() {
    const { h, S, render, haptic } = Q();
    return h("button", { class: "card qrate", onclick: () => { S.playSub = "phon"; st.mode = null; haptic(); render(); window.scrollTo(0, 0); } },
      h("div", { class: "row" }, h("span", { class: "em" }, "🎧"), h("div", { style: "flex:1;text-align:left" }, h("b", {}, tx("title")), h("div", { class: "muted" }, tx("sub")))));
  }
  function backBtn(label, fn) { return Q().h("button", { class: "linkbtn", style: "margin-bottom:10px", onclick: fn }, "← " + label); }
  function view() {
    const { h, S, render } = Q();
    if (!st.mode) {
      return h("div", {}, backBtn(tx("back"), () => { S.playSub = null; render(); window.scrollTo(0, 0); }),
        h("div", { class: "card hero" }, h("h2", {}, "🎧 " + tx("title")), h("div", { style: "margin-top:4px;opacity:.9" }, tx("sub"))),
        h("button", { class: "card qrate", onclick: () => load("hear") }, h("div", { class: "row" }, h("span", { class: "em" }, "👂"), h("div", { style: "flex:1;text-align:left" }, h("b", {}, tx("hear")), h("div", { class: "muted" }, tx("hear_sub"))))),
        h("button", { class: "card qrate", onclick: () => load("say") }, h("div", { class: "row" }, h("span", { class: "em" }, "🎤"), h("div", { style: "flex:1;text-align:left" }, h("b", {}, tx("say")), h("div", { class: "muted" }, tx("say_sub"))))));
    }
    const top = backBtn(tx("menu"), () => { st.mode = null; try { Q().stopSpeak(); window.TONES && window.TONES.stop(); } catch (e) { /* ок */ } render(); window.scrollTo(0, 0); });
    if (st.loading || st.err || !st.items) {
      return h("div", {}, top, h("div", { class: "hz-msg" }, st.err ? [tx("offline"), h("br"), h("button", { class: "btn line sm", onclick: () => load(st.mode) }, "↻")] : tx("loading")));
    }
    if (st.i >= st.items.length) return resultView(top);
    return st.mode === "hear" ? hearView(top) : sayView(top);
  }
  function head(top) {
    const { h } = Q(); const n = st.items.length;
    return [top, h("div", { class: "ph-prog" }, h("i", { style: `width:${Math.round((st.i / n) * 100)}%` })), h("div", { class: "hz-hint", style: "margin:6px 0 0" }, tx("q", { n: st.i + 1, m: n }))];
  }
  function hearView(top) {
    const { h, speak, haptic, render } = Q(); const it = st.items[st.i], answered = st.picked !== null;
    const opts = [1, 2, 3, 4].map((n) => {
      let cls = "ph-opt";
      if (answered) { if (n === it.tone) cls += " right"; else if (n === st.picked) cls += " wrong"; }
      return h("button", { class: cls, disabled: answered, onclick: () => {
        st.picked = n; if (n === it.tone) { st.score++; haptic("ok"); } else haptic("bad"); render();
      } }, h("b", {}, n + " " + MARK[n]), h("span", {}, ARROW[n]), h("small", {}, tx("t" + n)));
    });
    const out = [...head(top), h("div", { class: "ph-stage" }, h("button", { class: "ph-play", "aria-label": tx("listen"), onclick: () => speak(it.c) }, "🔊"), h("div", { class: "hz-note" }, tx("listen"))),
      h("div", { class: "hz-note", style: "text-align:center;margin:0 0 8px" }, tx("pick")), h("div", { class: "ph-opts" }, opts)];
    if (answered) {
      const ok = st.picked === it.tone;
      out.push(h("div", { class: "ph-reveal " + (ok ? "ok" : "bad") }, h("div", { class: "zh ph-big" }, it.c), h("div", {}, h("b", {}, it.py), " · " + tx("tone", { n: it.tone })), h("div", { class: "hz-tverdict " + (ok ? "ok" : "bad") }, ok ? tx("right") : tx("wrong", { n: it.tone }))),
        h("button", { class: "btn primary", style: "margin-top:12px", onclick: () => { st.i++; st.picked = null; render(); window.scrollTo(0, 0); if (st.i < st.items.length) setTimeout(() => speak(st.items[st.i].c), 150); } }, st.i + 1 >= st.items.length ? tx("result") : tx("next")));
    }
    return h("div", {}, out);
  }
  function sayView(top) {
    const { h, render } = Q(); const it = st.items[st.i];
    const out = [...head(top), h("div", { class: "ph-stage" }, h("div", { class: "zh ph-huge" }, it.c), h("div", { class: "hz-py" }, it.py), h("div", { class: "hz-badge" }, tx("tone", { n: it.tone }) + " " + ARROW[it.tone]))];
    if (st.tones && window.HZ && window.HZ.tonePanel && window.TONES) out.push(window.HZ.tonePanel({ c: it.c, py: it.py }, it.tone));
    out.push(h("div", { class: "hz-note", style: "text-align:center" }, tx("say_note")),
      h("button", { class: "btn primary", style: "margin-top:12px", onclick: () => { try { Q().stopSpeak(); window.TONES && window.TONES.stop(); } catch (e) { /* ок */ } st.i++; render(); window.scrollTo(0, 0); } }, st.i + 1 >= st.items.length ? tx("result") : tx("next")));
    return h("div", {}, out);
  }
  function resultView(top) {
    const { h, render, confetti } = Q(); const n = st.items.length, hear = st.mode === "hear";
    const pr = tx("praise"); const msg = !hear ? tx("done") : st.score >= n - 1 ? pr[0] : st.score >= n * 0.7 ? pr[1] : st.score >= n * 0.4 ? pr[2] : pr[3];
    if (hear && st.score >= n - 1) setTimeout(confetti, 200);
    return h("div", {}, top, h("div", { class: "card", style: "text-align:center" }, h("div", { style: "font-size:44px" }, hear ? "👂" : "🎤"), h("h3", {}, tx("done")),
      hear ? h("div", { class: "ph-score" }, tx("score", { n: st.score, m: n })) : null, h("div", { class: "muted", style: "margin-top:6px" }, msg),
      h("button", { class: "btn primary", style: "margin-top:14px", onclick: () => load(st.mode) }, tx("again"))));
  }
  window.PH = { entryCard, view, open() { const { S, render } = Q(); S.tab = "play"; S.playSub = "phon"; st.mode = null; render(); } };
})();
