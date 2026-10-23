/* Прогресс (v30): «Мой путь» (этапы HSK), «Достижения», «Настройки обучения». */
(function () {
  "use strict";
  const Q = () => window.QY;
  const T = {
    ru: { path: "Мой путь", path_hint: "Этап пройден, когда все слова уровня в «Помню».", now: "Сейчас", done: "Пройден", of: "{a} из {b}", level: "HSK {n}", level7: "HSK 7–9",
      ach: "Достижения", ach_sub: "Получено {a} из {b}", set: "Настройки обучения", set_sub: "Уровень, цель дня, сообщения 茶茶", back: "Прогресс",
      se_level: "Мой уровень", se_goal: "Цель дня", se_goal_sub: "Верных ответов в тренировке слов за день", se_chacha: "Сообщения от 茶茶", se_lang: "Язык", saved: "Сохранено", err: "Не удалось. Попробуй ещё раз.", load: "Загрузка…" },
    uz: { path: "Mening yo‘lim", path_hint: "Daraja so‘zlarining hammasi «Eslab qoldim»da bo‘lsa, bosqich o‘tilgan hisoblanadi.", now: "Hozir", done: "O‘tilgan", of: "{b} dan {a}", level: "HSK {n}", level7: "HSK 7–9",
      ach: "Yutuqlar", ach_sub: "{b} dan {a} olingan", set: "O‘rganish sozlamalari", set_sub: "Daraja, kun maqsadi, 茶茶 xabarlari", back: "Natija",
      se_level: "Mening darajam", se_goal: "Kun maqsadi", se_goal_sub: "So‘z mashqida kuniga to‘g‘ri javoblar soni", se_chacha: "茶茶 xabarlari", se_lang: "Til", saved: "Saqlandi", err: "Bo‘lmadi. Qayta urinib ko‘ring.", load: "Yuklanmoqda…" },
    en: { path: "My path", path_hint: "A stage is complete when all words of the level are in “Known”.", now: "Now", done: "Complete", of: "{a} of {b}", level: "HSK {n}", level7: "HSK 7–9",
      ach: "Achievements", ach_sub: "Earned {a} of {b}", set: "Learning settings", set_sub: "Level, daily goal, 茶茶 messages", back: "Progress",
      se_level: "My level", se_goal: "Daily goal", se_goal_sub: "Correct answers in word practice per day", se_chacha: "Messages from 茶茶", se_lang: "Language", saved: "Saved", err: "Failed. Please try again.", load: "Loading…" },
    zh: { path: "我的进阶", path_hint: "某一等级的所有词都是“记住了”时，该阶段完成。", now: "当前", done: "已完成", of: "{a} / {b}", level: "HSK {n}", level7: "HSK 7–9",
      ach: "成就", ach_sub: "已获得 {a} / {b}", set: "学习设置", set_sub: "水平、每日目标、茶茶消息", back: "进度",
      se_level: "我的水平", se_goal: "每日目标", se_goal_sub: "每天单词练习中的答对数", se_chacha: "茶茶的消息", se_lang: "语言", saved: "已保存", err: "失败，请重试。", load: "加载中…" },
  };
  const tx = (k, v) => {
    const d = T[Q().S.lang] || T.ru; let s = d[k] !== undefined ? d[k] : T.ru[k];
    if (v && typeof s === "string") s = s.replace(/\{(\w+)\}/g, (_, x) => (v[x] !== undefined ? v[x] : ""));
    return s;
  };
  // значки за этапы: тексты кладём в общий словарь, как у остальных значков
  const SB = {
    ru: (n) => [`Этап ${n}`, `Все слова ${n} в «Помню»`], uz: (n) => [`${n} bosqichi`, `${n} so‘zlarining hammasi «Eslab qoldim»da`],
    en: (n) => [`${n} stage`, `All ${n} words are in “Known”`], zh: (n) => [`${n} 阶段`, `${n} 的所有词都是“记住了”`],
  };
  for (const l of Object.keys(SB)) for (let n = 1; n <= 7; n++) window.I18N[l]["b_s_hsk" + n] = SB[l](n === 7 ? "HSK 7–9" : "HSK " + n);
  const STAGE_ICON = { s_hsk1: "🌱", s_hsk2: "🌿", s_hsk3: "🌳", s_hsk4: "🏔️", s_hsk5: "🏯", s_hsk6: "🐉", s_hsk7: "🌟" };
  const GL = { 1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七" };
  const P = { path: null, at: 0, busy: false, set: null, setBusy: false, err: false };
  const lvName = (n) => (n === 7 ? tx("level7") : tx("level", { n }));

  async function loadPath() {
    const { api, S, render } = Q();
    if (P.busy) return;
    P.busy = true;
    try { P.path = await api("/api/stages", {}); P.at = Date.now(); } catch (e) { /* покажем «…» */ }
    P.busy = false;
    if (S.tab === "progress" && !S.sub) render();
  }
  function path() {
    const { h } = Q();
    if (!P.busy && (!P.path || Date.now() - P.at > 15000)) loadPath();
    const rows = P.path ? P.path.stages.map((s) => {
      const cur = P.path.current === s.level, pct = s.total ? Math.floor((s.known * 100) / s.total) : 0;
      return h("div", { class: "pg-st" + (s.done ? " done" : "") + (cur ? " cur" : "") },
        h("span", { class: "zh pg-n" }, s.done ? "✓" : GL[s.level]),
        h("div", { class: "pg-b" }, h("div", { class: "pg-t" }, h("b", {}, lvName(s.level)), s.done ? h("i", {}, tx("done")) : cur ? h("i", {}, tx("now")) : null),
          h("div", { class: "pg-bar" }, h("span", { style: "width:" + pct + "%" })), h("div", { class: "muted pg-c" }, tx("of", { a: s.known, b: s.total }))));
    }) : [h("div", { class: "muted", style: "margin-top:8px" }, "…")];
    return h("div", { class: "card" }, h("h3", {}, "🧭 " + tx("path")), h("div", { class: "muted", style: "margin-top:2px" }, tx("path_hint")), h("div", { class: "pg-list" }, rows));
  }

  // ── достижения ──
  function badgeIds(bs) {
    const icons = Q().badgeIcons;
    return Object.keys(Object.assign({}, icons, STAGE_ICON)).filter((k) => k in bs);
  }
  function achCount() {
    const bs = (Q().S.me && Q().S.me.badges) || {}, ids = badgeIds(bs);
    return [ids.filter((k) => bs[k]).length, ids.length];
  }
  function entry(emoji, title, sub, onclick) {
    const { h, haptic } = Q();
    return h("button", { class: "card qrate", onclick: () => { haptic(); onclick(); } },
      h("div", { class: "row" }, h("span", { class: "em" }, emoji), h("div", { style: "flex:1;text-align:left" }, h("b", {}, title), h("div", { class: "muted" }, sub))));
  }
  function entries() {
    const { S, render } = Q(); const [a, b] = achCount();
    return [entry("🏵", tx("ach"), tx("ach_sub", { a, b }), () => { S.sub = "ach"; render(); window.scrollTo(0, 0); }),
      entry("🎛", tx("set"), tx("set_sub"), () => { S.sub = "set"; P.set = null; P.err = false; render(); window.scrollTo(0, 0); loadSet(); })];
  }
  function back() {
    const { h, S, render } = Q();
    return h("button", { class: "linkbtn", style: "margin-bottom:10px", onclick: () => { S.sub = null; render(); window.scrollTo(0, 0); } }, "← " + tx("back"));
  }
  function ach() {
    const { h, S } = Q(); const icons = Object.assign({}, Q().badgeIcons, STAGE_ICON);
    const bs = (S.me && S.me.badges) || {}, all = badgeIds(bs);
    const ids = all.filter((k) => k in STAGE_ICON).concat(all.filter((k) => !(k in STAGE_ICON)));
    const [a, b] = achCount();
    return h("div", {}, back(), h("div", { class: "card", style: "margin-top:0" }, h("h3", {}, "🏵 " + tx("ach") + " · " + a + "/" + b),
      h("div", { class: "grid3", style: "margin-top:10px" }, ids.map((k) => { const [n, d] = Q().tr("b_" + k); return h("div", { class: "badge" + (bs[k] ? "" : " lock") }, h("div", { class: "em" }, icons[k]), h("b", {}, n), h("span", {}, d)); }))));
  }

  // ── настройки обучения ──
  async function loadSet() {
    const { api, S, render } = Q();
    if (P.setBusy) return;
    P.setBusy = true; P.err = false;
    try { P.set = await api("/api/settings", {}); } catch (e) { P.err = true; }
    P.setBusy = false;
    if (S.tab === "progress" && S.sub === "set") render();
  }
  async function save(k, v) {
    const { api, toast, render, haptic, S } = Q();
    haptic();
    try { P.set = await api("/api/settings/set", { k, v }); toast(tx("saved")); } catch (e) { toast(tx("err")); }
    if (S.tab === "progress" && S.sub === "set") render();
  }
  function set() {
    const { h, S } = Q(); const d = P.set;
    if (!d) return h("div", {}, back(), h("div", { class: "hz-msg" }, P.err ? [tx("err"), h("br"), h("button", { class: "btn line sm", onclick: () => { P.err = false; Q().render(); loadSet(); } }, "↻")] : tx("load")));
    const chip = (on, label, fn) => h("button", { class: on ? "on" : "", onclick: fn }, label);
    return h("div", {}, back(),
      h("div", { class: "card", style: "margin-top:0" }, h("b", {}, tx("se_level")), h("div", { class: "seg pg-wrap", style: "margin-top:8px" }, d.levels.map((l, i) => chip(d.level === i, l, () => save("level", i))))),
      h("div", { class: "card" }, h("b", {}, tx("se_goal")), h("div", { class: "muted" }, tx("se_goal_sub")), h("div", { class: "seg fill", style: "margin-top:8px" }, d.goals.map((g) => chip(d.goal === g, String(g), () => save("goal", g))))),
      h("div", { class: "card" }, h("b", {}, "💬 " + tx("se_chacha")), h("div", { class: "seg pg-wrap", style: "margin-top:8px" }, d.freqs.map((f) => chip(d.freq === f.n, f.label, () => save("freq", f.n))))),
      h("div", { class: "card" }, h("b", {}, tx("se_lang")), h("div", { class: "seg fill", style: "margin-top:8px" }, Q().LANGS.map(([c, , n]) => chip(c === S.lang, n, async () => { await Q().setLang(c); P.set = null; loadSet(); })))));
  }
  window.PG = { path, entries, ach, set, achCount };
})();
