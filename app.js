/* 清越 · Чайная лавка: интерфейс Mini App. Без внешних библиотек. */
(() => {
  "use strict";
  const tg = window.Telegram && window.Telegram.WebApp;
  const LANGS = [["ru", "RU", "Русский"], ["uz", "UZ", "O'zbekcha"], ["en", "EN", "English"], ["zh", "中", "中文"]];
  const LOCALES = { ru: "ru-RU", uz: "uz-UZ", en: "en-GB", zh: "zh-CN" };
  const S = { me: null, lang: "ru", tab: "quest", game: null, board: { tab: "week", data: null }, docs: null, pop: false };
  const app = document.getElementById("app");

  // ── утилиты ──
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* без хранилища работаем так же */ } },
  };
  function tr(key, vars) {
    const d = window.I18N[S.lang] || {};
    let v = d[key] !== undefined ? d[key] : window.I18N.ru[key];
    if (typeof v === "string" && vars) v = v.replace(/\{(\w+)\}/g, (_, k) => (vars[k] !== undefined ? vars[k] : ""));
    return v;
  }
  function h(tag, props, ...kids) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(props || {})) {
      if (v === false || v == null) continue;
      if (k === "class") el.className = v;
      else if (k === "html") el.innerHTML = v;
      else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v === true ? "" : v);
    }
    for (const kid of kids.flat()) {
      if (kid == null || kid === false) continue;
      el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
    }
    return el;
  }
  const svg = (inner, vb = "0 0 24 24") => { const d = document.createElement("div"); d.innerHTML = `<svg viewBox="${vb}">${inner}</svg>`; return d.firstChild; };
  const haptic = (kind) => { try { const hf = tg && tg.HapticFeedback; if (!hf) return; kind === "ok" || kind === "bad" ? hf.notificationOccurred(kind === "ok" ? "success" : "error") : hf.impactOccurred("light"); } catch (e) { /* не страшно */ } };
  const openLink = (url) => { try { tg && tg.openLink ? tg.openLink(url) : window.open(url, "_blank"); } catch (e) { window.open(url, "_blank"); } };
  const openTg = (url) => { try { tg && tg.openTelegramLink ? tg.openTelegramLink(url) : window.open(url, "_blank"); } catch (e) { window.open(url, "_blank"); } };
  const fmtDate = (iso) => new Date(iso + "T00:00:00").toLocaleDateString(LOCALES[S.lang], { day: "numeric", month: "short" });

  function toast(msg) {
    document.querySelectorAll(".toast").forEach((n) => n.remove());
    const n = h("div", { class: "toast" }, msg);
    document.body.append(n);
    setTimeout(() => n.remove(), 2600);
  }
  function sheet(content) {
    const bg = h("div", { class: "sheetbg", onclick: (e) => { if (e.target === bg) bg.remove(); } }, h("div", { class: "sheet" }, content));
    document.body.append(bg);
    return bg;
  }
  function confetti() {
    const wrap = h("div", { class: "confetti" });
    const colors = ["#c5413a", "#c79a3b", "#2c6c5b", "#f3eee1", "#5fa08b"];
    for (let i = 0; i < 46; i++) {
      const p = h("i");
      p.style.left = Math.random() * 100 + "%";
      p.style.background = colors[i % colors.length];
      p.style.animationDuration = 1.6 + Math.random() * 1.6 + "s";
      p.style.animationDelay = Math.random() * 0.4 + "s";
      wrap.append(p);
    }
    document.body.append(wrap);
    setTimeout(() => wrap.remove(), 3600);
  }

  async function api(path, body) {
    const r = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json", "X-Init-Data": (tg && tg.initData) || "" }, body: JSON.stringify(body || {}) });
    if (r.status === 401) { const e = new Error("auth"); e.auth = true; throw e; }
    const j = await r.json().catch(() => ({}));
    if (r.status === 409) { j.stale = true; return j; }
    if (!r.ok) throw new Error("http " + r.status);
    return j;
  }
  async function safe(fn) { try { return await fn(); } catch (e) { if (e.auth) return showNoTg(); toast(tr("err")); } }

  // ── оформление ──
  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    store.set("qy_theme", theme);
    try { if (tg) { tg.setHeaderColor(theme === "dark" ? "#0f1915" : "#f3eee1"); tg.setBackgroundColor(theme === "dark" ? "#0f1915" : "#f3eee1"); } } catch (e) { /* старые версии Telegram */ }
  }
  function initTheme() {
    const saved = store.get("qy_theme");
    const sys = (tg && tg.colorScheme) || (window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    applyTheme(saved || sys);
  }
  const curTheme = () => document.documentElement.dataset.theme;

  const MASCOT = `<svg class="mascot" viewBox="0 0 120 120" aria-hidden="true">
    <g class="steam" fill="none" stroke="#fffcf4" stroke-width="3" stroke-linecap="round" opacity=".8"><path d="M44 34 C38 24 50 20 44 8"/><path d="M60 32 C54 22 66 18 60 6"/><path d="M76 34 C70 24 82 20 76 8"/></g>
    <ellipse cx="60" cy="108" rx="38" ry="6" fill="#d9cdb0" opacity=".9"/>
    <path d="M98 60 C116 58 116 84 94 86" fill="none" stroke="#fffcf4" stroke-width="6" stroke-linecap="round"/>
    <path d="M20 54 H100 C100 88 84 106 60 106 C36 106 20 88 20 54 Z" fill="#fffcf4"/>
    <path d="M20 54 H100 C100 60 99 66 97 71 C80 66 40 66 23 71 C21 66 20 60 20 54 Z" fill="#e9e2cf"/>
    <ellipse cx="60" cy="54" rx="40" ry="9" fill="#8db39a"/><ellipse cx="60" cy="53" rx="34" ry="6" fill="#a8caa5"/>
    <path d="M56 50 C60 44 70 44 74 49 C68 52 60 52 56 50 Z" fill="#2c6c5b"/>
    <circle cx="46" cy="80" r="4" fill="#22302b"/><circle cx="74" cy="80" r="4" fill="#22302b"/>
    <circle cx="46" cy="79" r="1.3" fill="#fff"/><circle cx="74" cy="79" r="1.3" fill="#fff"/>
    <circle cx="38" cy="88" r="5" fill="#f2a79d" opacity=".7"/><circle cx="82" cy="88" r="5" fill="#f2a79d" opacity=".7"/>
    <path d="M54 88 Q60 94 66 88" fill="none" stroke="#22302b" stroke-width="3" stroke-linecap="round"/></svg>`;
  const BOX = `<svg class="box" viewBox="0 0 64 64" aria-hidden="true"><rect x="8" y="26" width="48" height="32" rx="6" fill="#c5413a"/><rect x="5" y="18" width="54" height="13" rx="5" fill="#d9574d"/>
    <rect x="28" y="18" width="8" height="40" fill="#e9c96d"/><path d="M32 18 C20 4 8 14 22 18 Z M32 18 C44 4 56 14 42 18 Z" fill="#e9c96d"/></svg>`;
  const ICONS = {
    quest: '<path d="M4 18c3-1 4-5 8-5s5 4 8 3"/><circle cx="6" cy="7" r="2.4"/><path d="M6 9.4V13M15 4l5 2-5 2z"/><path d="M15 4v8"/>',
    play: '<path d="M5 9h12v4a6 6 0 0 1-12 0V9z"/><path d="M17 10h2a2 2 0 0 1 0 4h-2"/><path d="M8 4c-1 1 1 2 0 3M12 4c-1 1 1 2 0 3"/>',
    top: '<path d="M8 4h8v5a4 4 0 0 1-8 0V4z"/><path d="M8 6H5a3 3 0 0 0 3 4M16 6h3a3 3 0 0 1-3 4"/><path d="M12 13v4M8 20h8M10 17h4"/>',
    me: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    about: '<path d="M12 21c-6-3-8-8-6-14 4 0 7 1 8 4 1 3 0 7-2 10z"/><path d="M12 21c0-5 2-8 5-10"/>',
  };

  // ── каркас ──
  function render() {
    if (!S.me) return;
    document.documentElement.lang = S.lang;
    app.replaceChildren(top(), h("div", { class: "view", id: "view" }, view()), tabbar());
  }
  function top() {
    const cur = LANGS.find((l) => l[0] === S.lang);
    const bar = h("div", { class: "top" },
      h("div", { class: "seal sm" }, "清越"),
      h("div", { class: "ttl" }, tr("app")),
      h("button", { class: "iconbtn", "aria-label": "theme", onclick: () => { applyTheme(curTheme() === "dark" ? "light" : "dark"); render(); } }, curTheme() === "dark" ? "☀️" : "🌙"),
      h("button", { class: "langbtn", onclick: (e) => { e.stopPropagation(); S.pop = !S.pop; render(); } }, cur[1]));
    if (S.pop) {
      bar.append(h("div", { class: "pop" }, LANGS.map(([c, , name]) => h("button", { class: c === S.lang ? "on" : "", onclick: () => setLang(c) }, name))));
    }
    return bar;
  }
  function tabbar() {
    const tabs = [["quest", "tab_quest"], ["play", "tab_play"], ["top", "tab_top"], ["me", "tab_me"], ["about", "tab_about"]];
    return h("div", { class: "tabbar" }, h("div", { class: "in" }, tabs.map(([id, key]) =>
      h("button", { class: "tab" + (S.tab === id ? " on" : ""), onclick: () => go(id) }, svg(ICONS[id]), h("span", {}, tr(key))))));
  }
  function go(tab) {
    haptic();
    S.tab = tab; S.pop = false;
    if (tab === "top") { loadBoard(S.board.tab); }
    if (tab === "quest" && window.QUEST) window.QUEST.enter();
    render(); window.scrollTo(0, 0);
  }
  function view() {
    return { quest: () => window.QUEST.view(), play: viewPlay, top: viewTop, me: viewMe, about: viewAbout }[S.tab]();
  }
  document.addEventListener("click", () => { if (S.pop) { S.pop = false; render(); } });

  async function setLang(code) {
    S.lang = code; S.pop = false;
    render();
    await safe(async () => { await api("/api/lang", { lang: code }); await reloadMe(); S.docs = null; if (S.tab === "top") loadBoard(S.board.tab); render(); });
  }
  async function reloadMe() { S.me = await api("/api/me"); S.lang = S.me.lang; }

  // ── вкладка «Играть» ──
  function cupsRow(m) {
    if (m.lives_max > 8) return null;
    return h("div", { class: "cups" }, Array.from({ length: m.lives_max }, (_, i) => h("i", { class: i < m.lives ? "" : "off" })));
  }
  function statTiles(m) {
    return h("div", { class: "stats" },
      h("div", { class: "stat" }, h("b", {}, m.lives_max > 8 ? `${m.lives}/${m.lives_max}` : m.lives), cupsRow(m) || null, h("span", {}, tr("lives"))),
      h("div", { class: "stat" }, h("b", {}, "🪙 " + m.coins), h("span", {}, tr("coins"))),
      h("div", { class: "stat" }, h("b", {}, "🔥 " + m.streak), h("span", {}, tr("streak"))));
  }
  function viewPlay() {
    if (S.game) return viewGame();
    const m = S.me, r = m.rank;
    const nm = m.nick || null;
    const pct = r.to ? Math.min(100, Math.round(((m.served - r.from) / (r.to - r.from)) * 100)) : 100;
    const nextTitle = r.to ? tr("title" + (r.level + 1)) : "";
    const hero = h("div", { class: "card hero" },
      h("div", { class: "row" }, h("div", { html: MASCOT }),
        h("div", {}, h("h2", {}, nm ? tr("hello", { n: nm }) : tr("hello_anon")), h("div", { class: "rank" }, r.emoji + " " + r.title))),
      h("div", { class: "bar" }, h("i", { style: `width:${pct}%` })),
      h("div", { class: "small" }, r.to ? tr("to_next", { t: nextTitle, n: r.to - m.served }) : tr("max_rank")),
      h("button", { class: "btn primary", onclick: startGame }, "🍵 " + (m.lives > 0 ? tr("start") : tr("start"))));
    const out = [hero, statTiles(m), giftCard(m), inviteCard(m)];
    if (m.pro_until) out.splice(2, 0, h("div", { class: "card" }, h("b", {}, "✨ " + tr("ext_active", { d: fmtDate(m.pro_until) }))));
    out.push(h("details", {}, h("summary", {}, tr("how_title")), h("div", { class: "body" }, h("ol", {}, tr("how").map((s) => h("li", {}, s))))));
    return h("div", {}, out);
  }
  function giftCard(m) {
    const g = m.gift, ready = !g.opened;
    const filled = ready ? g.streak % 7 : ((g.streak - 1) % 7) + 1;
    const chain = h("div", { class: "chain" }, Array.from({ length: 7 }, (_, i) => {
      const on = i < filled;
      const cls = on ? "on" : ready && i === filled ? "today" : "";
      return h("i", { class: cls + (i === 6 && !on ? " x2" : "") }, i === 6 ? tr("gift_double") : on ? "✓" : String(i + 1));
    }));
    let sub = tr("gift_sub");
    if (g.opened) sub = giftText(g.kind, g.amount);
    return h("div", { class: "card" },
      h("div", { class: "gift" + (ready ? " ready" : "") }, h("div", { html: BOX }),
        h("div", { style: "flex:1" }, h("h3", {}, tr("gift_title")), h("div", { class: "muted" }, sub))),
      chain,
      h("button", { class: "btn jade sm", style: "margin-top:12px", disabled: !ready, onclick: openGift }, ready ? "🎁 " + tr("gift_open") : "✓ " + tr("gift_done")));
  }
  function giftText(kind, n) {
    return kind === "coins" ? tr("gift_coins", { n }) : kind === "lives" ? tr("gift_lives", { n }) : tr("gift_word");
  }
  async function openGift() {
    haptic();
    await safe(async () => {
      const r = await api("/api/gift");
      await reloadMe();
      render();
      if (r.already) return;
      confetti(); haptic("ok");
      const body = h("div", { class: "reward" });
      if (r.kind === "word" && r.word) {
        body.append(h("div", { class: "zh" }, r.word.zh), h("div", { class: "py" }, r.word.py), h("div", { style: "margin-top:6px;font-weight:700" }, r.word.meaning),
          h("p", { class: "muted" }, tr("gift_word_hint")));
      } else {
        body.append(h("div", { class: "big" }, r.kind === "coins" ? "🪙" : "🍵"), h("h2", { style: "margin-top:10px" }, giftText(r.kind, r.amount)));
      }
      const bg = sheet([h("h3", { style: "text-align:center" }, "🎁 " + tr("gift_title")), body, h("button", { class: "btn jade", style: "margin-top:14px", onclick: () => bg.remove() }, "OK")]);
    });
  }
  function inviteCard(m) {
    const i = m.invite;
    if (!i.link) return h("div");
    const card = h("div", { class: "card" }, h("h3", {}, "🤝 " + tr("invite_title")), h("div", { class: "muted" }, tr("invite_sub")));
    card.append(h("div", { class: "muted", style: "margin-top:8px" }, tr("invite_stats", { j: i.joined, t: i.trial, p: i.paid })));
    if (i.disc_until) card.append(h("div", { style: "margin-top:6px;font-weight:700;color:var(--jade)" }, "💸 " + tr("invite_disc_on", { d: fmtDate(i.disc_until) })));
    if (i.disc_queue) card.append(h("div", { style: "margin-top:6px;font-weight:700;color:var(--jade)" }, "⏭ " + tr("invite_disc", { n: i.disc_queue })));
    card.append(h("div", { class: "row2", style: "margin-top:12px" },
      h("button", { class: "btn line sm", onclick: async () => { try { await navigator.clipboard.writeText(i.link); toast(tr("copied")); } catch (e) { toast(i.link); } } }, tr("invite_copy")),
      h("button", { class: "btn jade sm", onclick: () => openTg("https://t.me/share/url?url=" + encodeURIComponent(i.link) + "&text=" + encodeURIComponent(tr("share_text"))) }, tr("invite_share"))));
    return card;
  }

  // ── игра ──
  async function startGame() { haptic(); S.game = { loading: true }; render(); await nextOrder(); }
  async function nextOrder() {
    await safe(async () => {
      const r = await api("/api/tea/next");
      S.game = r.closed ? { closed: true } : { order: r, answered: false, pick: null, result: null };
      if (r.closed) { S.me.lives = 0; }
      render(); window.scrollTo(0, 0);
    });
  }
  function leaveGame() { S.game = null; safe(async () => { await reloadMe(); render(); }); }
  function speak(zh) { try { const u = new SpeechSynthesisUtterance(zh); u.lang = "zh-CN"; u.rate = 0.85; speechSynthesis.cancel(); speechSynthesis.speak(u); } catch (e) { /* нет озвучки: ничего страшного */ } }
  async function pick(i) {
    const g = S.game;
    if (!g || !g.order || g.answered) return;
    g.answered = true; g.pick = i; render();
    await safe(async () => {
      const r = await api("/api/tea/answer", { seq: g.order.seq, choice: i });
      if (r.stale || r.error) { return nextOrder(); }
      g.result = r;
      Object.assign(S.me, { coins: r.coins, served: r.served, streak: r.streak, lives: r.lives });
      haptic(r.ok ? "ok" : "bad");
      render();
      if (r.ok && r.gain) { const t = document.querySelector(".ticket"); if (t) t.append(h("div", { class: "coinpop" }, "+" + r.gain)); }
      if (r.levelup) { confetti(); const bg = sheet([h("div", { class: "reward" }, h("div", { class: "big" }, r.levelup.emoji), h("h2", { style: "margin-top:10px" }, tr("levelup", { t: r.levelup.title }))), h("button", { class: "btn jade", style: "margin-top:14px", onclick: () => bg.remove() }, "OK")]); }
    });
  }
  function viewGame() {
    const g = S.game, m = S.me;
    const bar = h("div", { class: "gamebar" }, h("button", { class: "iconbtn x", onclick: leaveGame, "aria-label": tr("close") }, "✕"),
      h("div", { class: "grow" }, h("b", {}, "🍵 " + (m.lives_max > 8 ? `${m.lives}/${m.lives_max}` : "×" + m.lives)), "  ", h("b", {}, "🪙 " + m.coins), "  ", h("b", {}, "🔥 " + m.streak)));
    if (g.loading) return h("div", {}, bar);
    if (g.closed) return h("div", {}, bar, closedCard());
    const o = g.order, res = g.result;
    const opts = h("div", { class: "opts" }, o.options.map((text, i) => {
      let cls = "opt";
      if (res) { if (i === res.right_index) cls += " ok"; else if (i === g.pick) cls += " bad"; else cls += " dim"; }
      return h("button", { class: cls, disabled: g.answered, onclick: () => pick(i) }, text);
    }));
    const ticket = h("div", { class: "ticket" },
      h("div", { class: "no" }, h("span", {}, tr("order", { n: o.seq })), h("span", {}, "清越")),
      h("div", { class: "zh" }, o.zh), h("div", { class: "py" }, o.py),
      h("button", { class: "speak", onclick: () => speak(o.zh) }, "🔊 " + tr("listen")), opts,
      h("div", { class: "verdict " + (res ? (res.ok ? "ok" : "bad") : "") }, res ? (res.ok ? "✓ " + tr("right") : tr("wrong", { r: res.right })) : ""));
    const out = [bar, ticket];
    if (res) out.push(res.closed ? h("button", { class: "btn jade", style: "margin-top:14px", onclick: () => { S.game = { closed: true }; render(); } }, tr("next"))
      : h("button", { class: "btn primary", style: "margin-top:14px", onclick: nextOrder }, tr("next") + " →"));
    return h("div", {}, out);
  }
  function closedCard() {
    const m = S.me, p = m.pay;
    const card = h("div", { class: "card", style: "text-align:center" }, h("div", { style: "font-size:48px" }, "🏮"), h("h2", {}, tr("closed_title")),
      h("div", { class: "muted", style: "margin-top:6px" }, tr("closed_sub", { n: m.lives_max })));
    const out = [card];
    if (!m.pro_until) {
      const ext = h("div", { class: "card" }, h("h3", {}, "💳 " + tr("ext_title")), h("div", { class: "muted" }, tr("ext_sub", { pro: p.pro_lives, d: p.days })));
      if (p.on) {
        if (p.price) ext.append(h("div", { style: "margin-top:10px" }, h("b", {}, tr("ext_price") + ": "), p.price));
        if (p.info) ext.append(h("div", { style: "margin-top:8px;white-space:pre-wrap" }, h("b", {}, tr("ext_how") + ":\n"), p.info));
        const row = h("div", { style: "margin-top:12px;display:grid;gap:8px" });
        if (/^https?:/i.test(p.url)) row.append(h("button", { class: "btn line sm", onclick: () => openLink(p.url) }, tr("ext_pay")));
        row.append(h("button", { class: "btn jade sm", onclick: () => safe(async () => { await api("/api/pay/paid"); toast(tr("ext_sent")); }) }, tr("ext_paid")));
        ext.append(row);
      } else {
        ext.append(h("button", { class: "btn jade sm", style: "margin-top:12px", onclick: () => safe(async () => { await api("/api/pay/ask"); toast(tr("ext_asked")); }) }, tr("ext_ask")));
      }
      ext.append(h("div", { class: "muted", style: "margin-top:10px" }, tr("ext_or")));
      out.push(ext);
    }
    out.push(inviteCard(m));
    return h("div", {}, out);
  }

  // ── рейтинг ──
  async function loadBoard(tab) {
    S.board.tab = tab; S.board.data = null; render();
    await safe(async () => { S.board.data = await api("/api/board", { tab }); render(); });
  }
  function medal(p) { return p === 1 ? "🥇" : p === 2 ? "🥈" : p === 3 ? "🥉" : p; }
  function viewTop() {
    const m = S.me, w = m.week;
    const out = [h("div", { class: "card hero" }, h("h2", {}, "🏆 " + tr("top_title")), h("div", { style: "margin-top:4px;opacity:.85" }, tr("week_range", { a: fmtDate(w.start), b: fmtDate(w.end) }) + " · " + tr("days_left", { n: w.days_left })),
      h("div", { style: "margin-top:10px;font-size:14px;opacity:.9" }, tr("prize", { m: w.min })))];
    if (!m.joined) {
      out.push(h("div", { class: "card" }, h("h3", {}, tr("join_cta")), h("div", { class: "muted" }, tr("join_sub")),
        h("button", { class: "btn primary", style: "margin-top:12px", onclick: joinFlow }, "✅ " + tr("join_cta"))));
    } else if (w.place) {
      out.push(h("div", { class: "card", style: "text-align:center" }, h("b", {}, tr("your_place", { p: w.place })), " · ", h("b", {}, w.points + " " + tr("points"))));
    }
    const tabs = [["week", "t_week"], ["coins", "t_coins"], ["streak", "t_streak"], ["feed", "t_feed"], ["results", "t_results"]];
    out.push(h("div", { class: "seg", style: "margin-top:14px" }, tabs.map(([id, key]) => h("button", { class: S.board.tab === id ? "on" : "", onclick: () => loadBoard(id) }, tr(key)))));
    out.push(boardBody());
    return h("div", {}, out);
  }
  function relTime(ts) {
    const d = new Date(ts + "+05:00"), mins = Math.max(1, Math.round((Date.now() - d.getTime()) / 60000));
    return mins < 60 ? mins + " " + tr("ago_min") : mins < 1440 ? Math.round(mins / 60) + " " + tr("ago_hr") : Math.round(mins / 1440) + " " + tr("ago_day");
  }
  function boardBody() {
    const d = S.board.data;
    if (!d) return h("div", { class: "muted", style: "text-align:center;padding:24px" }, "…");
    if (!d.rows.length) return h("div", { class: "card muted", style: "text-align:center" }, tr("empty"));
    if (d.tab === "feed") {
      return h("div", { class: "list" }, d.rows.map((e) => {
        const text = e.kind === "levelup" ? tr("ev_levelup", { t: tr("title" + String(e.data).replace("title", "")) }) : e.kind === "marathon" ? tr("ev_marathon", { n: e.data }) : tr("ev_win", { d: e.data });
        const icon = e.kind === "levelup" ? "🍵" : e.kind === "marathon" ? "🏃" : "🥇";
        return h("div", { class: "li feed" + (e.me ? " me" : "") }, h("div", { class: "pl" }, icon), h("div", { class: "nm" }, h("b", {}, e.nick), " " + text), h("time", {}, relTime(e.ts)));
      }));
    }
    if (d.tab === "results") {
      return h("div", { class: "list res" }, d.rows.map((r) => h("div", { class: "card", style: "margin-top:10px" },
        h("h4", {}, tr("week_range", { a: fmtDate(r.start), b: fmtDate(r.end) }) + " · " + (r.prize ? "🎁 " + tr("prize_given") : tr("prize_none"))),
        r.top.map((x, i) => h("div", { class: "li" + (x.me ? " me" : ""), style: "margin-top:6px" }, h("div", { class: "pl" }, medal(i + 1)), h("div", { class: "nm" }, x.nick), h("div", { class: "vl" }, x.points, " ", h("small", {}, tr("points"))))))));
    }
    const unit = d.tab === "coins" ? "🪙" : d.tab === "streak" ? tr("days_unit") : tr("points");
    return h("div", { class: "list" }, d.rows.map((r) => h("div", { class: "li" + (r.me ? " me" : "") }, h("div", { class: "pl" }, medal(r.place)), h("div", { class: "nm" }, r.nick + (r.me ? " · " + tr("you") : "")), h("div", { class: "vl" }, r.value, " ", h("small", {}, unit)))));
  }
  function joinFlow() { S.me.nick ? setJoined(true) : nickSheet(true); }
  async function setJoined(v) {
    await safe(async () => {
      const r = await api("/api/board/join", { joined: v });
      if (r.need_nick) return nickSheet(true);
      await reloadMe(); if (S.tab === "top") await loadBoard(S.board.tab); render();
    });
  }
  function nickSheet(thenJoin) {
    const L = S.me.limits;
    const input = h("input", { maxlength: L.nick_max, placeholder: tr("nick_ph"), autocomplete: "off", autocapitalize: "off", spellcheck: "false" });
    input.value = S.me.nick || "";
    const err = h("div", { class: "err" });
    const bg = sheet([h("h3", {}, tr("nick_title")), h("div", { class: "muted", style: "margin-top:6px" }, tr("nick_hint", { a: L.nick_min, b: L.nick_max })), input, err,
      h("div", { class: "row2", style: "margin-top:8px" }, h("button", { class: "btn line", onclick: () => bg.remove() }, tr("cancel")),
        h("button", { class: "btn jade", onclick: async () => {
          err.textContent = "";
          await safe(async () => {
            const r = await api("/api/nick", { nick: input.value });
            if (!r.ok) { err.textContent = r.err || tr("err"); return; }
            bg.remove(); toast(tr("nick_saved"));
            if (thenJoin) await api("/api/board/join", { joined: true });
            await reloadMe(); if (S.tab === "top") await loadBoard(S.board.tab); render();
          });
        } }, tr("save")))]);
    setTimeout(() => input.focus(), 150);
  }

  // ── профиль ──
  const BADGE_ICON = { first: "☕", served25: "🍃", served100: "💯", streak3: "🔥", streak7: "🗓️", gift7: "🎁", marathon: "🏃", marathon3: "🏅", friend: "🤝", ranked: "🏆", winner: "🥇", sharp: "🎯" };
  function viewMe() {
    const m = S.me, s = m.season;
    const month = new Date(s.ym + "-01T00:00:00").toLocaleDateString(LOCALES[S.lang], { month: "long", year: "numeric" });
    const out = [h("div", { class: "pf" }, h("div", { class: "avatar" }, m.nick ? [...m.nick][0].toUpperCase() : "茶"),
      h("div", {}, h("div", { class: "muted" }, tr("me_nick")), h("h2", {}, m.nick || "—"), h("div", { class: "rank", style: "background:var(--mist);color:var(--jade);margin-top:6px" }, m.rank.emoji + " " + m.rank.title)))];
    const acc = s.correct + s.wrong ? Math.round((s.correct * 100) / (s.correct + s.wrong)) : 0;
    out.push(h("div", { class: "card" }, h("h3", {}, "🗓 " + tr("season") + " · " + month),
      h("div", { class: "sgrid" }, [[s.points, "s_points"], [acc + "%", "s_acc"], [s.days, "s_days"], [m.play_streak, "streak"]].map(([v, k]) => h("div", {}, h("b", {}, v), h("span", {}, tr(k)))))));
    out.push(statTiles(m));
    const bs = m.badges, ids = Object.keys(bs);
    out.push(h("div", { class: "card" }, h("h3", {}, "🏵 " + tr("badges") + " · " + ids.filter((k) => bs[k]).length + "/" + ids.length),
      h("div", { class: "grid3", style: "margin-top:10px" }, ids.map((k) => { const [n, d] = tr("b_" + k); return h("div", { class: "badge" + (bs[k] ? "" : " lock") }, h("div", { class: "em" }, BADGE_ICON[k]), h("b", {}, n), h("span", {}, d)); }))));
    const sw = h("div", { class: "switch" + (m.joined ? " on" : ""), role: "switch", "aria-checked": String(m.joined), onclick: () => (m.nick ? setJoined(!m.joined) : (toast(tr("visible_need")), nickSheet(true))) });
    out.push(h("div", { class: "card" }, h("h3", {}, "⚙️ " + tr("settings")),
      h("div", { class: "setting" }, h("div", { class: "tx" }, h("b", {}, tr("visible")), h("span", { class: "muted" }, tr("visible_sub"))), sw),
      h("div", { class: "setting" }, h("div", { class: "tx" }, h("b", {}, tr("me_nick") + ": " + (m.nick || "—")), m.nick && !m.can_change_nick ? h("span", { class: "muted" }, tr("nick_wait")) : null),
        h("button", { class: "btn line sm", style: "width:auto", disabled: !!(m.nick && !m.can_change_nick), onclick: () => nickSheet(false) }, m.nick ? tr("change_nick") : tr("nick_title"))),
      h("div", { class: "setting", style: "display:block" }, h("b", {}, tr("lang")), h("div", { class: "seg fill", style: "margin-top:6px" }, LANGS.map(([c, , n]) => h("button", { class: c === S.lang ? "on" : "", onclick: () => setLang(c) }, n)))),
      h("div", { class: "setting", style: "display:block" }, h("b", {}, tr("theme")), h("div", { class: "seg fill", style: "margin-top:6px" },
        h("button", { class: curTheme() === "light" ? "on" : "", onclick: () => { applyTheme("light"); render(); } }, "☀️ " + tr("theme_light")),
        h("button", { class: curTheme() === "dark" ? "on" : "", onclick: () => { applyTheme("dark"); render(); } }, "🌙 " + tr("theme_dark"))))));
    out.push(supportCard());
    return h("div", {}, out);
  }
  function supportCard() {
    return h("button", { class: "card qsupport", onclick: () => window.QUEST.openSupport() }, h("span", { class: "em" }, "💝"), h("div", { style: "text-align:left" }, h("b", {}, tr("q_support")), h("div", { class: "muted" }, tr("q_support_sub"))));
  }

  // ── о проекте ──
  function lazyDoc(key, label) {
    const body = h("div", { class: "body" }, "…");
    const d = h("details", {}, h("summary", {}, label), body);
    d.addEventListener("toggle", async () => {
      if (!d.open) return;
      await safe(async () => { if (!S.docs) S.docs = await api("/api/docs"); body.innerHTML = S.docs[key]; });
    });
    return d;
  }
  function viewAbout() {
    const m = S.me;
    const creator = h("div", { class: "card creator" }, h("div", { class: "photo" }, h("img", { src: "/static/lara.jpg", alt: tr("creator"), loading: "lazy" })),
      h("h2", {}, tr("creator")), h("div", { class: "role" }, tr("role")), h("p", {}, tr("bio")),
      h("div", { class: "chips" },
        h("button", { class: "chip", onclick: () => openLink(m.links.instagram) }, h("div", { class: "ic ig" }, "IG"), h("div", {}, h("small", {}, tr("insta")), h("b", {}, "@lllaziza_r"))),
        h("button", { class: "chip", onclick: () => openTg(m.links.channel) }, h("div", { class: "ic tg" }, "TG"), h("div", {}, h("small", {}, tr("channel")), h("b", {}, tr("channel_name"))))));
    const why = h("div", { class: "card" }, h("h3", {}, "🍃 " + tr("why_title")), h("p", { style: "margin:8px 0 0" }, tr("why")));
    const how = h("details", {}, h("summary", {}, tr("howto")), h("div", { class: "body" }, h("ol", {}, tr("how").map((s) => h("li", {}, s)))));
    return h("div", {}, creator, why, supportCard(), how, lazyDoc("rules", tr("rules")), lazyDoc("privacy", tr("privacy")), h("div", { class: "foot" }, tr("version")));
  }

  window.QY = { h, tr, api, safe, toast, sheet, haptic, confetti, openTg, openLink, render, S };

  // ── запуск ──
  function showNoTg() {
    document.getElementById("splash").classList.add("off");
    app.replaceChildren(h("div", { class: "notg" }, h("div", { class: "seal", style: "margin:0 auto 18px" }, "清\n越"), h("h2", {}, tr("app")), h("p", { class: "muted" }, tr("open_tg"))));
  }
  async function boot() {
    initTheme();
    try { if (tg) { tg.ready(); tg.expand(); if (tg.disableVerticalSwipes) tg.disableVerticalSwipes(); } } catch (e) { /* ок */ }
    const code = ((tg && tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.language_code) || "ru").slice(0, 2);
    S.lang = window.I18N[code] ? code : "ru";
    const want = new URLSearchParams(location.search).get("tab");
    if (want && ["quest", "play", "top", "me", "about"].includes(want)) S.tab = want;
    document.getElementById("splashName").textContent = tr("app");
    if (!tg || !tg.initData) { return showNoTg(); }
    const started = Date.now();
    try {
      await reloadMe();
    } catch (e) { return e.auth ? showNoTg() : (document.getElementById("splashSub").textContent = tr("err")); }
    const wait = Math.max(0, 1000 - (Date.now() - started));
    setTimeout(() => { render(); document.getElementById("splash").classList.add("off"); }, wait);
  }
  boot();
})();
