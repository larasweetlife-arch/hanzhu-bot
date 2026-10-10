/* 清越 · «Путешествие с Чачей»: экраны игры (создание героя, карта, сцены, задания, магазин).
   Все правила и проверка ответов на сервере; здесь только показ. Связь с app.js через window.QY. */
(() => {
  "use strict";
  const Y = () => window.QY;
  const A = () => window.QART;
  const Q = { st: null, scene: null, loadedAt: 0, busy: false, mood: "smile", nextLifeAt: 0, draft: null, board: {} };
  const ICONS = ["✈️", "🚕", "🏨", "🥟", "🚇", "🚆", "⛰️", "🏯"];
  const TASK_KEY = { tr: "q_t_tr", hz: "q_t_hz", tn: "q_t_tn", od: "q_t_od", mt: "q_t_mt", rp: "q_t_rp" };

  const h = (...a) => Y().h(...a);
  const tr = (k, v) => Y().tr(k, v);
  const S = () => Y().S;
  const tlang = () => (S().lang === "zh" ? "en" : S().lang);       // на каком языке показывать перевод
  const html = (s) => { const d = document.createElement("div"); d.innerHTML = s; return d.firstElementChild; };
  const heroName = () => (Q.st && Q.st.char && Q.st.char.hero) || "";
  const loc = (o) => (o ? (o[tlang()] || o.en || o.ru || "") : "");
  const fillName = (s) => String(s || "").replace(/\{name\}/g, heroName());
  const plain = (toks) => toks.map((t) => (t.h ? t.h : t.name ? heroName() : t.x || "")).join("");
  const mmss = (sec) => { sec = Math.max(0, Math.round(sec)); const m = Math.floor(sec / 60), s = sec % 60; return m >= 60 ? `${Math.floor(m / 60)}:${String(m % 60).padStart(2, "0")}:${String(s).padStart(2, "0")}` : `${m}:${String(s).padStart(2, "0")}`; };

  // ── иероглифы с пиньинем над словами ──
  function ruby(tokens, o) {
    o = o || {};
    const box = h("span", { class: "zhl" + (o.cls ? " " + o.cls : "") });
    for (const t of tokens) {
      if (t.name) box.append(h("span", { class: "nm" }, heroName()));
      else if (t.h) box.append(o.nopy ? h("span", { class: "hz" }, t.h) : h("ruby", {}, t.h, h("rt", {}, t.p)));
      else box.append(h("span", { class: "pn" }, t.x || ""));
    }
    return box;
  }
  function speak(toks) { try { const u = new SpeechSynthesisUtterance(plain(toks)); u.lang = "zh-CN"; u.rate = 0.85; speechSynthesis.cancel(); speechSynthesis.speak(u); } catch (e) { /* озвучки нет: не страшно */ } }

  // ── загрузка состояния ──
  async function load(force) {
    if (Q.busy) return;
    if (!force && Q.st && Date.now() - Q.loadedAt < 15000) return;
    Q.busy = true;
    try {
      Q.st = await Y().api("/api/quest/state");
      Q.loadedAt = Date.now();
      Q.nextLifeAt = Q.st.next_life_in ? Date.now() + Q.st.next_life_in * 1000 : 0;
    } catch (e) { if (e.auth) Y().safe(() => { throw e; }); else Y().toast(tr("err")); }
    Q.busy = false;
    if (S().tab === "quest" && !Q.scene) Y().render();
  }
  const reload = () => load(true);

  // обновление таймеров раз в секунду
  setInterval(() => {
    const now = Date.now();
    document.querySelectorAll(".qtick").forEach((el) => { const left = Math.max(0, Math.round((Q.nextLifeAt - now) / 1000)); el.textContent = left ? tr("q_life_in", { t: mmss(left) }) : tr("q_life_full"); });
    if (Q.st && Q.nextLifeAt && now > Q.nextLifeAt + 800 && !Q.busy) { Q.nextLifeAt = 0; reload(); }
  }, 1000);

  // ───────────────────────── герой ─────────────────────────
  function preview(ch, mood) { return h("div", { class: "qprev", html: A().figure("me", ch, mood || "smile") }); }

  function skinChips(draft, owned, onPick) {
    return h("div", { class: "qskins" }, A().SKINS.map((sk, i) => {
      const have = owned.includes(i);
      const ch = Object.assign({}, draft, { skin: i });
      return h("button", { class: "qskin" + (draft.skin === i ? " on" : "") + (have ? "" : " lock"), onclick: () => onPick(i, have) },
        h("div", { class: "av", html: A().avatar(ch) }), h("span", {}, tr("q_sk" + i)), have ? null : h("em", {}, "🔒 " + Q.st.shop.items.skin.coins));
    }));
  }

  // выбор цвета волос и причёски (бесплатно)
  function lookPick(d, redraw) {
    const A_ = A(), n = 3;
    return h("div", { class: "qlook" },
      h("h3", { style: "margin-top:14px" }, tr("q_hair")),
      h("div", { class: "qhairs" }, A_.HAIRS.map((c, i) => h("button", { class: "qhair" + ((d.hair || 0) === i ? " on" : ""), style: `--hc:${c}`, "aria-label": "hair " + (i + 1), onclick: () => { d.hair = i; redraw(); } }))),
      h("h3", { style: "margin-top:14px" }, tr("q_hstyle")),
      h("div", { class: "qhst" }, Array.from({ length: n }, (_, i) => h("button", { class: "qhs" + ((d.hstyle || 0) === i ? " on" : ""), onclick: () => { d.hstyle = i; redraw(); } },
        h("div", { class: "av", html: A_.figure("me", Object.assign({}, d, { hstyle: i }), "smile").replace('viewBox="0 0 120 190"', 'viewBox="4 0 112 112"') })))));
  }

  function creatorView() {
    const st = Q.st;
    const d = Q.draft = Q.draft || { gender: "f", skin: 0, hero: "", hair: 0, hstyle: 0 };
    const owned = st.shop.free;
    const input = h("input", { maxlength: 16, placeholder: tr("q_name_ph"), autocomplete: "off", spellcheck: "false", value: d.hero, oninput: (e) => { d.hero = e.target.value; } });
    const err = h("div", { class: "err" });
    const wrap = h("div", { class: "qcreate" },
      h("div", { class: "card hero qhero" }, h("div", { class: "qcha", html: A().chacha("happy") }),
        h("h2", {}, tr("q_create_title")), h("div", { style: "opacity:.9;margin-top:6px" }, tr("q_create_sub"))),
      h("div", { class: "card" },
        preview(d),
        h("div", { class: "seg fill", style: "margin-top:6px" }, [["f", "q_girl"], ["m", "q_boy"]].map(([g, k]) => h("button", { class: d.gender === g ? "on" : "", onclick: () => { d.gender = g; Y().render(); } }, tr(k)))),
        h("h3", { style: "margin-top:14px" }, tr("q_name")), input, err,
        lookPick(d, () => Y().render()),
        h("h3", { style: "margin-top:14px" }, tr("q_outfit")),
        skinChips(d, owned, (i, have) => { if (!have) return Y().toast(tr("q_locked_skin", { n: Q.st.shop.items.skin.coins })); d.skin = i; Y().render(); }),
        h("button", { class: "btn primary", style: "margin-top:16px", onclick: async () => {
          if ((d.hero || "").trim().length < 2) { err.textContent = tr("q_name_err"); return; }
          await Y().safe(async () => {
            const r = await Y().api("/api/quest/char", { hero: d.hero, gender: d.gender, skin: d.skin, hair: d.hair || 0, hstyle: d.hstyle || 0 });
            if (!r.ok) { err.textContent = tr("q_name_err"); return; }
            Q.draft = null; await reload(); Y().haptic("ok"); Y().render();
          });
        } }, "🍵 " + tr("q_go"))));
    return wrap;
  }

  // ───────────────────────── значки: фонарик (жизнь), монета ─────────────────────────
  const LAN = `<svg viewBox="0 0 24 32" aria-hidden="true"><rect x="9" y="0" width="6" height="3" rx="1" fill="#e0b24a"/><ellipse cx="12" cy="16" rx="10" ry="12" fill="#c0302a" stroke="#e0b24a" stroke-width="1.3"/><path d="M12 4v24M6.5 6c-2.5 6-2.5 14 0 20M17.5 6c2.5 6 2.5 14 0 20" stroke="#8f1d16" stroke-width="1" fill="none"/><rect x="8" y="27" width="8" height="3" rx="1" fill="#e0b24a"/><path d="M12 30v2" stroke="#e0b24a" stroke-width="1.4"/></svg>`;
  const COIN = `<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="9" fill="#e0b24a" stroke="#a87a1c" stroke-width="1.2"/><circle cx="10" cy="10" r="7" fill="none" stroke="#f6d676" stroke-width=".8"/><rect x="6.6" y="6.6" width="6.8" height="6.8" rx=".6" fill="#7a1812"/></svg>`;
  const NUM = ["一", "二", "三", "四", "五", "六", "七", "八"];
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const coinI = () => h("span", { class: "qcn", html: COIN });

  // ───────────────────────── главная: карта ─────────────────────────
  function hearts(n, max) { return h("span", { class: "qhearts", "aria-label": `${n}/${max}` }, Array.from({ length: max }, (_, i) => h("i", { class: "qlan" + (i < n ? "" : " off"), html: LAN }))); }

  function homeView() {
    const st = Q.st, ch = st.char, c = st.constants, ch1 = st.chapters[0];
    const out = [];
    out.push(h("div", { class: "card hero qhero" },
      h("div", { class: "row" },
        h("div", { class: "qme", html: A().avatar(ch) }),
        h("div", { style: "flex:1;min-width:0" }, h("h2", {}, ch.hero), h("div", { class: "rank" }, "🗺 " + tr("q_chapter", { n: 1 }) + " · " + loc(ch1.city)),
          h("div", { style: "margin-top:6px;font-size:13px;opacity:.9" }, tr("q_level") + ": " + ch1.level))),
      h("div", { class: "qstat" },
        h("div", {}, hearts(st.lives, c.lives_max), h("small", { class: "qtick" }, st.lives >= c.lives_max ? tr("q_life_full") : tr("q_life_in", { t: mmss(st.next_life_in) }))),
        h("div", { class: "qcoin" }, h("b", {}, "🪙 " + st.coins), h("small", {}, tr("q_coins")))),
      h("div", { class: "row2", style: "margin-top:14px" },
        h("button", { class: "btn line sm qonhero", onclick: shopSheet }, "🛍 " + tr("q_shop")),
        h("button", { class: "btn line sm qonhero", onclick: wardrobeSheet }, "👘 " + tr("q_wardrobe")))));

    const t = st.today;
    if (!t.chapter_done) {
      if (t.free_left) out.push(h("div", { class: "card qtoday" }, h("div", { class: "em" }, "🍵"), h("div", {}, h("b", {}, tr("q_today_free")), h("div", { class: "muted" }, tr("q_howmuch", { a: c.task_coins, b: c.scene_bonus })))));
      else if (t.extra) out.push(h("div", { class: "card qtoday" }, h("div", { class: "em" }, "🎟"), h("div", {}, h("b", {}, tr("q_continue_today")), h("div", { class: "muted" }, tr("q_continue_sub")))));
      else out.push(h("div", { class: "card qtoday done" }, h("div", { class: "em" }, "🌙"), h("div", { style: "flex:1" }, h("b", {}, tr("q_today_done")),
        h("button", { class: "btn jade sm", style: "margin-top:10px", onclick: () => extraSheet() }, "▶ " + tr("q_continue_today") + " · ⭐ " + st.shop.items.extra.stars))));
    }

    out.push(mapView());
    const pc = prizeCard(); if (pc) out.push(pc);
    out.push(ratingCard());
    out.push(h("div", { class: "card qsoon" }, [["q_ch2", "🏯"], ["q_ch3", "🐼"]].map(([k, e]) => h("div", { class: "it" }, h("span", {}, e), h("div", {}, h("b", {}, tr(k)), h("small", {}, tr("q_soon")))))));
    out.push(h("button", { class: "card qsupport", onclick: openSupport }, h("span", { class: "em" }, "💝"), h("div", { style: "text-align:left" }, h("b", {}, tr("q_support")), h("div", { class: "muted" }, tr("q_support_sub")))));
    return h("div", {}, out);
  }

  // карта главы: дорога слева направо (Пекин → Великая стена), прокручивается пальцем
  function mapView() {
    const st = Q.st, n = st.scenes.length, H = 250, STEP = 150, W = Math.max(Math.min(window.innerWidth, 560) - 32, 80 + n * STEP);
    const xs = (i) => 76 + i * ((W - 152) / Math.max(1, n - 1));
    const ys = (i) => 104 + Math.sin(i * 1.3 + .4) * 34;
    let d = `M ${xs(0) - 70} ${ys(0) + 10} L ${xs(0)} ${ys(0)}`;
    for (let i = 1; i < n; i++) { const x0 = xs(i - 1), x1 = xs(i), mx = (x0 + x1) / 2; d += ` C ${mx} ${ys(i - 1)}, ${mx} ${ys(i)}, ${x1} ${ys(i)}`; }
    const doneN = st.scenes.filter((s) => s.status === "done").length;
    const cur = Math.max(0, st.scenes.findIndex((s) => s.status === "current"));
    const box = h("div", { class: "qmap", style: `width:${W}px;height:${H}px` });
    box.append(html(window.QWORLD.mapArt(W, H)));
    box.append(html(`<svg class="qpath" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><path d="${d}" fill="none" stroke="rgba(90,17,13,.28)" stroke-width="11" stroke-linecap="round"/><path d="${d}" fill="none" stroke="#e0b24a" stroke-width="4" stroke-dasharray="3 10" stroke-linecap="round"/></svg>`));
    st.scenes.forEach((s, i) => {
      const node = h("button", { class: "qnode " + s.status + (s.boss ? " boss" : ""), style: `left:${xs(i) - 29}px;top:${ys(i) - 29}px`, "aria-label": loc(s.title_tr), onclick: () => tapScene(s) },
        h("span", {}, s.status === "locked" ? "🔒" : ICONS[i] || "📍"), s.status === "done" ? h("em", {}, "✓") : null);
      const label = h("div", { class: "qlabel " + s.status, style: `top:${ys(i) + 36}px;left:${xs(i) - 62}px;width:124px` },
        h("small", {}, tr("q_scene_n", { n: s.n })), ruby(s.title), h("div", { class: "tl" }, loc(s.title_tr)),
        s.status === "current" && s.progress ? h("div", { class: "pg" }, s.progress + "/" + s.tasks) : null);
      box.append(node, label);
      if (s.status === "current") box.append(h("div", { class: "qwho", style: `left:${xs(i) - 19}px;top:${ys(i) - 76}px`, html: A().avatar(st.char) }));
    });
    const sc = h("div", { class: "qmapscroll" }, box);
    setTimeout(() => { if (sc.isConnected) sc.scrollLeft = Math.max(0, xs(cur) - sc.clientWidth / 2); }, 30);
    return h("div", { class: "card qmapcard" },
      h("div", { style: "display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px" }, h("h3", {}, loc(st.chapters[0].title)), h("span", { class: "muted" }, `${doneN}/${n}`)),
      h("div", { class: "muted", style: "margin:-2px 0 10px" }, tr("q_goal") + ": " + loc(st.chapters[0].goal)), sc);
  }

  function prizeCard() {
    const pz = Q.st.prize;
    if (!pz || !pz.on) return null;
    const sub = pz.won ? tr("q_prize_won") : pz.entered ? tr("q_prize_in", { n: pz.count }) : tr("q_prize_sub");
    return h("div", { class: "card qprize" + (pz.won ? " won" : pz.entered ? " in" : "") }, h("div", { class: "em" }, "🎁"),
      h("div", { style: "flex:1;min-width:0" }, h("b", {}, tr("q_prize_title")), h("div", { class: "muted" }, sub),
        pz.winner ? h("div", { class: "muted", style: "margin-top:4px" }, "🏆 " + tr("q_prize_winner", { name: pz.winner })) : null));
  }

  // ── рейтинг ──
  async function loadBoard(tab, force) {
    const b = Q.board[tab];
    if (b && !force && Date.now() - b.at < 30000) return b;
    try { const r = await Y().api("/api/quest/board", { tab }); r.at = Date.now(); Q.board[tab] = r; } catch (e) { return null; }
    if (S().tab === "quest" && !Q.scene && !document.querySelector(".sheetbg")) Y().render();
    return Q.board[tab];
  }
  const MEDAL = ["🥇", "🥈", "🥉"];
  function boardRows(b) {
    if (!b.rows.length) return [h("div", { class: "muted", style: "text-align:center;padding:18px 0" }, tr("q_rate_empty"))];
    return b.rows.map((r) => h("div", { class: "qrow" + (r.me ? " me" : "") },
      h("span", { class: "pl" }, MEDAL[r.place - 1] || r.place),
      h("span", { class: "av", html: A().avatar({ gender: r.gender, skin: r.skin, hero: r.hero }) }),
      h("span", { class: "nm" }, r.hero, h("small", {}, `${tr("q_rate_scenes", { n: r.scenes })}`)),
      h("b", { class: "pt" }, r.pts)));
  }
  function ratingCard() {
    const b = Q.board.week, top = b && b.rows.slice(0, 3);
    const me = b && b.me;
    const sub = !b ? "…" : me && me.place ? tr("q_rate_you", { p: me.place, pts: me.pts }) : me && me.hidden ? tr("q_rate_hidden") : tr("q_rate_none");
    return h("button", { class: "card qrate", onclick: ratingSheet },
      h("div", { class: "row" }, h("span", { class: "em" }, "🏆"), h("div", { style: "flex:1;text-align:left" }, h("b", {}, tr("q_rating")), h("div", { class: "muted" }, sub))),
      top && top.length ? h("div", { class: "qtop3" }, top.map((r) => h("span", { class: r.me ? "me" : "" }, MEDAL[r.place - 1] + " " + r.hero + " · " + r.pts))) : null);
  }
  function ratingSheet() {
    closeSheets();
    let tab = "week";
    const wrap = h("div", {});
    const draw = (b) => {
      const me = b && b.me;
      const hidden = !!Q.st.hide;
      wrap.replaceChildren(...[h("h3", {}, "🏆 " + tr("q_rating")),
        h("div", { class: "seg fill", style: "margin:8px 0" }, [["week", "q_rate_week"], ["all", "q_rate_all"]].map(([k, t]) => h("button", { class: tab === k ? "on" : "", onclick: () => { tab = k; fetch_(); } }, tr(t)))),
        b ? h("div", { class: "qrows" }, boardRows(b)) : h("div", { class: "muted", style: "text-align:center;padding:20px" }, "…"),
        b && me && me.place && !b.rows.some((r) => r.me) ? h("div", { class: "qrow me" }, h("span", { class: "pl" }, me.place), h("span", { class: "nm" }, heroName()), h("b", { class: "pt" }, me.pts)) : null,
        h("div", { class: "muted", style: "font-size:12.5px;margin-top:10px" }, tr("q_rate_note")),
        h("button", { class: "linkbtn", style: "margin-top:10px", onclick: async () => { await Y().safe(async () => { await Y().api("/api/quest/hide", { hide: !hidden }); Q.st.hide = !hidden; Q.board = {}; Y().toast(tr("q_bought")); fetch_(true); }); } }, hidden ? "👁 " + tr("q_rate_show") : "🙈 " + tr("q_rate_hide"))].filter(Boolean));
    };
    const fetch_ = async (force) => { draw(Q.board[tab]); const b = await loadBoard(tab, force !== false); draw(b); };
    Y().sheet(wrap); fetch_(true);
  }

  function tapScene(s) {
    Y().haptic();
    if (s.status === "locked") return Y().toast(tr("q_locked"));
    if (s.status === "done") {
      const bg = Y().sheet([h("h3", {}, loc(s.title_tr)), ruby(s.title), h("p", { class: "muted" }, tr("q_replay")),
        h("div", { class: "row2" }, h("button", { class: "btn line", onclick: () => bg.remove() }, tr("cancel")), h("button", { class: "btn jade", onclick: () => { bg.remove(); openScene(s.id); } }, "↻ " + tr("q_play")))]);
      return;
    }
    openScene(s.id);
  }

  async function openScene(id) {
    await Y().safe(async () => {
      const r = await Y().api("/api/quest/scene", { scene: id });
      if (!r.ok) {
        if (r.err === "extra") return extraSheet(id);
        if (r.err === "locked") return Y().toast(tr("q_locked"));
        return Y().toast(tr("err"));
      }
      Q.scene = { p: r, phase: r.idx > 0 ? "task" : "dlg", li: 0, showTr: false, task: r.task, idx: r.idx, fb: null, mt: { sel: null, done: (r.task && r.task.matched) || [] }, od: { bank: null, ans: [] }, wrong: [], res: null, lock: false, anim: false };
      Q.mood = "smile";
      mountScene();
    });
  }

  // ───────────────────────── сцена: мир 16:9 ─────────────────────────
  let root = null, G = null;

  function enterFull() {
    const tg = window.Telegram && window.Telegram.WebApp;
    try { if (tg) { if (tg.expand) tg.expand(); if (tg.isVersionAtLeast && tg.isVersionAtLeast("8.0") && tg.requestFullscreen && !tg.isFullscreen) { tg.requestFullscreen(); G.fs = true; } if (tg.disableVerticalSwipes) tg.disableVerticalSwipes(); } } catch (e) { /* не страшно */ }
    try { if (screen.orientation && screen.orientation.lock) screen.orientation.lock("landscape").then(() => { G.locked = true; }).catch(() => {}); } catch (e) { /* не страшно */ }
  }
  function leaveFull() {
    const tg = window.Telegram && window.Telegram.WebApp;
    try { if (G && G.fs && tg && tg.exitFullscreen) tg.exitFullscreen(); } catch (e) { /* ok */ }
    try { if (G && G.locked && screen.orientation && screen.orientation.unlock) screen.orientation.unlock(); } catch (e) { /* ok */ }
  }

  // Вписываем сцену 16:9 в экран. Если телефон держат вертикально и повернуть нельзя, поворачиваем картинку сами.
  function fit() {
    if (!G) return;
    const iw = window.innerWidth, ih = window.innerHeight;
    const coarse = window.matchMedia && matchMedia("(pointer: coarse)").matches;
    const rot = ih > iw * 1.05 && coarse;
    const W = rot ? ih : iw, H = rot ? iw : ih;
    const sw = Math.min(W, (H * 16) / 9), sh = (sw * 9) / 16;
    G.rot.style.width = W + "px"; G.rot.style.height = H + "px";
    G.rot.style.transform = rot ? `translateX(${iw}px) rotate(90deg)` : "none";
    G.qg.style.width = sw + "px"; G.qg.style.height = sh + "px"; G.qg.style.setProperty("--u", sw / 100 + "px");
    if (rot && !G.rotHint) { G.rotHint = h("div", { class: "qrotate" }, "↻ " + tr("q_rotate")); G.qg.append(G.rotHint); }
    if (!rot && G.rotHint) { G.rotHint.remove(); G.rotHint = null; }
  }

  const camX = (u, f) => `translateX(calc(var(--u) * ${-(u * f).toFixed(2)}))`;
  function setCam(u, anim) {
    G.cam = u;
    [["far", 0.12], ["mid", 0.42], ["near", 1], ["fg", 1.3]].forEach(([k, f]) => { const el = G[k]; if (!el) return; el.classList.toggle("pan", !!anim); el.style.transform = camX(u, f); });
  }
  async function walkTo(u) {
    G.hero.classList.add("walk"); void G.near.offsetWidth; setCam(u, true);
    await wait(1950);
    G.hero.classList.remove("walk");
    [G.far, G.mid, G.near, G.fg].forEach((e) => e && e.classList.remove("pan"));
  }
  function setMood(m) { Q.mood = m; if (G && G.cc) G.cc.innerHTML = A().figure("cc", Q.st.char, m); }
  function pop(text, bad) { if (!G) return; const el = h("div", { class: "qpop" + (bad ? " bad" : "") }, text); G.qg.append(el); setTimeout(() => el.remove(), 1400); }
  function fx(el, cls, ms) { el.classList.remove(cls); void el.offsetWidth; el.classList.add(cls); setTimeout(() => el.classList.remove(cls), ms); }

  // ── живость: передний план, падающие листья, свет, монеты, искры ──
  const LEAF = { airport: ["#e8b53c", "#f3d06a", "#d99a2b"], road: ["#e8b53c", "#f3d06a", "#d99a2b"], hotel: ["#e8b53c", "#f08a5d", "#d9632f"], food: ["#e8b53c", "#f08a5d", "#f3d06a"], mountain: ["#e8b53c", "#8fc35f", "#d9632f"], wall: ["#e0a53a", "#d9632f", "#f3d06a"] };
  function ambient(pal) {
    const th = pal.theme || "airport";
    const back = h("div", { class: "qamb back" }, h("div", { class: "qgrade g-" + th }));
    const front = h("div", { class: "qamb" });
    if (pal.indoor) {
      for (let i = 0; i < 18; i++) front.append(h("i", { class: "qmote", style: `left:${(i * 37) % 100}%;top:${(i * 53) % 90}%;--d:${6 + (i % 5)}s;--dl:-${(i * 1.3).toFixed(1)}s;--s:${0.5 + (i % 3) * 0.3}` }));
    } else {
      back.append(h("div", { class: "qrays" }));
      const cols = LEAF[th] || LEAF.airport;
      for (let i = 0; i < 14; i++) front.append(h("i", { class: "qleaf", style: `left:${(i * 29 + 7) % 100}%;--d:${9 + (i % 6) * 1.6}s;--dl:-${(i * 1.7).toFixed(1)}s;--s:${(1 + (i % 4) * 0.35).toFixed(2)};--sw:${(i % 2 ? 1 : -1) * (3 + (i % 4))}u;background:${cols[i % cols.length]}` }));
    }
    front.append(h("div", { class: "qvig" }));
    return { back, front };
  }
  // передний план: большие бумажные фонари, которые едут быстрее мира (глубина)
  function fgLayer(n) {
    const screens = Math.ceil(1.3 * (n + 1)) + 2, Wd = 1600;
    let s = "";
    for (let k = 0, x = 420; x < screens * Wd; k++, x += 900 + ((k * 7) % 5) * 70) {
      const y = 175 + ((k * 37) % 70), sc = 3 + ((k * 3) % 5) * 0.14;
      s += `<path d="M${x} -10 V${y - 30 * sc}" stroke="#4a2f18" stroke-width="5"/>${A().lantern(x, y, sc)}`;
      if (k % 2 === 0) s += `<path d="M${x + 150} -10 V${y + 40 - 30 * sc * 0.7}" stroke="#4a2f18" stroke-width="4"/>${A().lantern(x + 150, y + 90, sc * 0.7)}`;
    }
    return { screens, html: `<svg class="qw-svg" viewBox="0 0 ${screens * Wd} 900" preserveAspectRatio="none" aria-hidden="true">${s}</svg>` };
  }
  function rel(el) { let x = 0, y = 0; while (el && el !== G.qg) { x += el.offsetLeft; y += el.offsetTop; el = el.offsetParent; } return { x, y }; }
  const U = () => parseFloat(G.qg.style.getPropertyValue("--u")) || 6;
  // монеты летят из героя в счётчик
  function coinFly(n) {
    const chip = G.hud.querySelector(".qchip:last-child .qcn"); if (!chip) return;
    const to = rel(chip), u = U(), fx0 = u * 14, fy0 = G.qg.clientHeight - u * 24;
    for (let i = 0; i < n; i++) {
      const c = h("span", { class: "qcoinfly", html: COIN, style: `left:${fx0 - u * 1.5}px;top:${fy0}px` });
      G.qg.append(c);
      const dx = to.x - fx0 + u * 1.2, dy = to.y - fy0;
      c.animate([{ transform: "translate(0,0) scale(.5)", opacity: 0 }, { transform: `translate(${dx * 0.25}px,${-u * 6 - i * u * 0.6}px) scale(1.1)`, opacity: 1, offset: 0.3 }, { transform: `translate(${dx}px,${dy}px) scale(.8)`, opacity: 1 }],
        { duration: 950 + i * 70, delay: i * 80, easing: "cubic-bezier(.35,.05,.3,1)", fill: "both" }).onfinish = () => { c.remove(); const ch = G && G.hud.querySelector(".qchip:last-child"); if (ch) fx(ch, "bump", 300); };
    }
  }
  // искры и пыль у препятствия
  function burst(kind) {
    const u = U(), cx = 33, cy = kind === "dust" ? 49 : 34;
    const n = kind === "dust" ? 6 : 12;
    for (let i = 0; i < n; i++) {
      const a = kind === "dust" ? Math.PI * (0.1 + (i / n) * 0.8) * -1 : (i / n) * Math.PI * 2, r = kind === "dust" ? 5 + (i % 3) * 2 : 7 + (i % 3) * 3;
      const e = h("i", { class: kind === "dust" ? "qdust" : "qspark", style: `left:${cx}%;top:${(cy / 56.25) * 100}%;--dx:${(Math.cos(a) * r).toFixed(1)}u;--dy:${(Math.sin(a) * r).toFixed(1)}u` });
      G.qg.append(e); setTimeout(() => e.remove(), 1000);
    }
  }
  function sceneBanner() {
    const sc = Q.scene, s = Q.st.scenes.find((x) => x.id === sc.p.id), n = s ? s.n : "";
    const b = h("div", { class: "qbanner" }, h("small", {}, n ? tr("q_scene_n", { n }) : ""), ruby(sc.p.title, { cls: "big" }), h("small", {}, loc(sc.p.title_tr)));
    G.qg.append(b); setTimeout(() => b.remove(), 2600);
  }

  function mountScene() {
    closeSheets();
    const sc = Q.scene, p = sc.p, ch = Q.st.char;
    if (root) root.remove();
    root = h("div", { id: "qs" }); document.body.append(root); document.body.classList.add("qs-open");
    const w = window.QWORLD.build(p.id, p.total);
    G = { w, cam: 0 };
    G.rot = h("div", { class: "qrot" });
    G.qg = h("div", { class: "qg noanim" });
    const lay = (cls, n, inner) => h("div", { class: "qlay " + cls, style: `width:calc(var(--u) * ${n * 100})`, html: inner });
    G.sky = lay("sky", 1, w.sky); G.far = lay("far", w.farS, w.far); G.mid = lay("mid", w.midS, w.mid); G.near = lay("near", w.screens, w.near);
    G.obs = Array.from(G.near.querySelectorAll(".qob"));
    G.hero = h("div", { class: "qgh hidden" }, h("div", { class: "bob" }, h("div", { class: "hop", html: A().figure("me", ch, "smile") })));
    G.cc = h("div", { class: "qcc", html: A().figure("cc", ch, "smile") });
    G.df = h("div", { class: "qdf" });
    G.obt = h("div", { class: "qobt", style: "display:none" });
    G.hud = h("div", { class: "qhud" });
    G.slot = h("div", { class: "qslot" });
    const pal = w.pal || {};
    if (!pal.indoor) { const f = fgLayer(p.total); G.fg = lay("fg", f.screens, f.html); }
    const amb = ambient(pal);
    G.qg.append(G.sky, G.far, G.mid, G.near, amb.back, G.df, G.hero, G.cc);
    if (G.fg) G.qg.append(G.fg);
    G.qg.append(amb.front, G.obt, G.hud, G.slot);
    G.rot.append(G.qg); root.append(G.rot);
    setCam(0, false);
    enterFull(); fit();
    G.onResize = () => fit();
    window.addEventListener("resize", G.onResize); window.addEventListener("orientationchange", G.onResize);
    renderHud();
    sceneBanner();
    if (sc.phase === "dlg") showDialogue();
    else placeTasks();
    setTimeout(() => G && G.qg.classList.remove("noanim"), 80);
  }
  function closeScene() {
    if (!root) return;
    window.removeEventListener("resize", G.onResize); window.removeEventListener("orientationchange", G.onResize);
    leaveFull();
    root.remove(); root = null; G = null;
    document.body.classList.remove("qs-open");
    Q.scene = null; speechSynthesisCancel();
    reload().then(() => Y().render());
  }
  async function closeSceneThen(fn) {
    if (root) { window.removeEventListener("resize", G.onResize); window.removeEventListener("orientationchange", G.onResize); leaveFull(); root.remove(); root = null; G = null; }
    document.body.classList.remove("qs-open"); Q.scene = null;
    await reload(); Y().render(); fn();
  }
  function speechSynthesisCancel() { try { speechSynthesis.cancel(); } catch (e) { /* нет озвучки */ } }

  function renderHud() {
    if (!G) return;
    const sc = Q.scene, st = Q.st;
    G.hud.replaceChildren(
      h("button", { class: "qbtn round l", "aria-label": tr("q_close"), onclick: closeScene }, "✕"),
      h("div", { class: "qplaque" }, ruby(sc.p.title, { cls: "sm" })),
      sc.p.replay ? h("span", { class: "qchip" }, "↻") : h("button", { class: "qchip", onclick: () => outSheet(true) }, hearts(st.lives, st.constants.lives_max)),
      h("span", { class: "qchip" }, coinI(), h("b", {}, String(st.coins))));
  }
  const updateHud = renderHud;

  // ── диалог: персонажи по пояс над свитком ──
  function showDialogue() {
    const sc = Q.scene, p = sc.p, ln = p.dialogue[sc.li], speaker = ln.who;
    G.hero.classList.add("hidden"); G.cc.style.display = "none"; G.obt.style.display = "none";
    const ids = ["me"].concat(Object.keys(p.cast || {}).filter((k) => k !== "me"));
    const others = ids.slice(1), n = others.length;
    G.df.replaceChildren(...ids.map((id, i) => {
      const x = i === 0 ? 14 : n === 1 ? 66 : 38 + (i - 1) * (50 / (n - 1));
      const mood = id === speaker ? "open" : "smile";
      return h("div", { class: "qf" + (id === speaker ? " talk" : " dim"), "data-who": id, style: `left:${x}%`, html: A().figure(id, Q.st.char, mood) });
    }));
    winDlg(sc.li === 0 || !G.slot.firstChild);
  }
  function winDlg(fresh) {
    const sc = Q.scene, p = sc.p, ln = p.dialogue[sc.li], last = sc.li === p.dialogue.length - 1;
    const who = ln.who, c = p.cast[who] || {};
    const name = who === "me" ? heroName() : c.zh, sub = who === "me" ? "" : c.py;
    const tl = fillName(loc(ln.tr));
    const win = h("div", { class: "qwin dlg" + (fresh ? " in" : "") },
      h("i", { class: "roll l" }), h("i", { class: "roll r" }),
      h("div", { class: "np" + (who === "me" ? " me" : "") }, h("b", {}, name), sub ? h("small", {}, sub) : null, h("small", {}, loc(c.role) || tr("q_dlg"))),
      h("div", { class: "qdl-body", onclick: () => { sc.showTr = !sc.showTr; Y().haptic(); winDlg(false); } },
        h("div", { class: "tx" }, ruby(ln.zh, { cls: "big" }), sc.showTr ? h("div", { class: "trl" }, tl) : h("div", { class: "taphint" }, "👆 " + tr("q_tap_tr"))),
        h("div", { class: "qdl-ctl", onclick: (e) => e.stopPropagation() },
          h("button", { class: "qbtn y sm", "aria-label": tr("q_hear"), onclick: () => speak(ln.zh) }, "🔊"),
          h("div", { class: "qdl-dots" }, p.dialogue.map((_, i) => h("i", { class: i === sc.li ? "on" : i < sc.li ? "past" : "" }))),
          h("button", { class: "qbtn sm", onclick: () => { Y().haptic(); sc.showTr = false; if (last) startTasks(); else { sc.li++; showDialogue(); } } }, last ? tr("q_to_tasks") + " →" : tr("q_next") + " ▶"))));
    G.slot.replaceChildren(win);
  }

  // из диалога выходим на улицу: герой идёт к первому препятствию
  async function startTasks() {
    const sc = Q.scene; sc.phase = "task"; sc.anim = true;
    G.slot.replaceChildren(); G.df.replaceChildren();
    G.hero.classList.remove("hidden"); G.cc.style.display = "";
    setMood("smile");
    await walkTo(100 * (sc.idx + 1));
    if (Q.scene !== sc) return;
    sc.anim = false; showObstacleHint(); winTask(true);
  }
  // продолжаем с середины: сразу ставим камеру и открываем пройденные препятствия
  function placeTasks() {
    const sc = Q.scene;
    G.hero.classList.remove("hidden"); G.cc.style.display = "";
    G.obs.forEach((o, i) => o.classList.toggle("open", i < sc.idx));
    setCam(100 * (sc.idx + 1), false);
    if (sc.phase === "done") return;
    showObstacleHint(); winTask(true);
  }
  function showObstacleHint() {
    const sc = Q.scene;
    if (sc.idx === 0 && !sc.p.replay && sc.p.obstacle) { G.obt.style.display = ""; G.obt.replaceChildren(h("b", {}, "🚧 " + tr("q_obstacle") + ": "), loc(sc.p.obstacle)); }
    else G.obt.style.display = "none";
  }

  // ── окно задания ──
  function winTask(fresh) {
    const sc = Q.scene;
    if (!G || sc.phase !== "task") return;
    const p = sc.p, t = sc.task;
    if (!t) return;
    const old = G.slot.querySelector(".qwin-body"), top = old ? old.scrollTop : 0;
    const fbk = sc.fb ? h("span", { class: "fb " + (sc.fb.ok ? "ok" : "bad") }, sc.fb.text) : tr(TASK_KEY[t.t]);
    const seals = h("div", { class: "qseals", "aria-label": tr("q_task_n", { a: sc.idx + 1, b: p.total }) }, Array.from({ length: p.total }, (_, i) => h("i", { class: "qseal" + (i < sc.idx ? " done" : i === sc.idx ? " now" : "") }, NUM[i] || String(i + 1))));
    let body;
    switch (t.t) {
      case "rp": body = rpBody(t); break;
      case "hz": body = hzBody(t); break;
      case "tn": body = tnBody(t); break;
      case "od": body = odBody(t); break;
      case "mt": body = mtBody(t); break;
      default: body = trBody(t);
    }
    const win = h("div", { class: "qwin task" + (fresh ? " in" : "") },
      h("div", { class: "qwin-bar" }, h("button", { class: "linkb", onclick: dlgSheet }, "📖 " + tr("q_dlg")), h("div", { class: "t" }, fbk), seals),
      h("div", { class: "qwin-body" }, body));
    G.slot.replaceChildren(win);
    if (!fresh) win.querySelector(".qwin-body").scrollTop = top;
  }
  const rerender = () => winTask(false);

  // общий обработчик ответа
  async function submit(a, after) {
    const sc = Q.scene;
    if (sc.lock || sc.anim) return;
    sc.lock = true;
    let r;
    try { r = await Y().api("/api/quest/answer", { scene: sc.p.id, idx: sc.idx, a }); }
    catch (e) { sc.lock = false; return Y().toast(tr("err")); }
    sc.lock = false;
    if (Q.scene !== sc) return;
    if (r.err === "sync") return openSceneAgain();
    if (r.err) return Y().toast(tr("err"));
    Q.st.lives = r.lives; Q.st.coins = r.coins;
    if (r.next_life_in) Q.nextLifeAt = Date.now() + r.next_life_in * 1000;
    updateHud();
    if (r.out && !r.ok && !sc.p.replay && r.lives <= 0) {
      Y().haptic("bad"); if (after) after(r); wrongFx();
      sc.fb = { ok: false, text: tr("q_out_title") }; rerender();
      await wait(600); if (Q.scene !== sc) return;
      sc.fb = null; rerender(); outSheet();
      return;
    }
    if (!r.ok) {
      Y().haptic("bad"); if (after) after(r); wrongFx();
      sc.fb = { ok: false, text: "✗ " + tr("q_wrong") }; rerender();
      await wait(1100); if (Q.scene !== sc) return;
      sc.fb = null; setMood("smile"); rerender();
      return;
    }
    if (after) after(r);
    if (!r.done) { Y().haptic("ok"); rerender(); return; }          // верная пара, задание ещё не закончено
    Y().haptic("ok");
    await advance(r);
  }
  function wrongFx() {
    setMood("sad");
    fx(G.hero, "bonk", 520);
    const ob = G.obs[Q.scene.idx]; if (ob) { ob.classList.remove("shake"); void ob.getBoundingClientRect(); ob.classList.add("shake"); setTimeout(() => ob.classList.remove("shake"), 520); }
    G.hud.querySelectorAll(".qchip").forEach((c) => fx(c, "hit", 520));
  }
  // верный ответ: препятствие открывается, герой идёт дальше (или прыгает через ящики)
  async function advance(r) {
    const sc = Q.scene; sc.anim = true;
    const i = sc.idx, ob = G.obs[i], kind = G.w.kinds[i % G.w.kinds.length];
    setMood("happy"); sc.fb = { ok: true, text: "✓ " + tr("q_correct") }; rerender();
    if (r.gain) { pop("+" + r.gain); coinFly(Math.min(8, Math.max(2, Math.round(r.gain / 4)))); }
    burst("spark");
    await wait(550); if (Q.scene !== sc) return;
    if (kind === "crates") fx(G.hero, "hop", 820); else if (ob) ob.classList.add("open");
    burst("dust");
    G.obt.style.display = "none";
    await wait(900); if (Q.scene !== sc) return;
    G.slot.replaceChildren(); sc.fb = null; setMood("smile");
    if (r.scene_done) {
      await walkTo(100 * (sc.p.total + 1)); if (Q.scene !== sc) return;
      fx(G.hero, "cheer", 1400); setMood("happy"); Y().confetti();
      await wait(1200); if (Q.scene !== sc) return;
      sc.res = r; sc.phase = "done"; sc.anim = false;
      finale();
      return;
    }
    sc.idx = r.idx; sc.task = r.task; sc.mt = { sel: null, done: [] }; sc.od = { bank: null, ans: [] }; sc.wrong = []; sc.p.idx = sc.idx;
    await walkTo(100 * (sc.idx + 1)); if (Q.scene !== sc) return;
    sc.anim = false; winTask(true);
  }
  async function openSceneAgain() {
    const sc = Q.scene, id = sc.p.id;
    const r = await Y().api("/api/quest/scene", { scene: id });
    if (!r.ok) return closeScene();
    Object.assign(sc, { p: r, idx: r.idx, task: r.task, mt: { sel: null, done: (r.task && r.task.matched) || [] }, od: { bank: null, ans: [] }, wrong: [], fb: null, anim: false });
    G.obs.forEach((o, i) => o.classList.toggle("open", i < sc.idx));
    setCam(100 * (sc.idx + 1), false);
    winTask(true);
  }

  // ── тела заданий ──
  function choice(t, render) {
    const sc = Q.scene;
    return h("div", { class: "opts" }, t.opts.map((o) => {
      const bad = sc.wrong.includes(o.id);
      return h("button", { class: "opt" + (bad ? " bad" : ""), "data-id": o.id, disabled: bad || sc.lock || sc.anim || !!sc.fb, onclick: () => submit(o.id, (r) => { if (!r.ok) sc.wrong.push(o.id); }) }, render(o));
    }));
  }
  function rpBody(t) {
    const p = Q.scene.p, w = t.who, c = p.cast[w] || {};
    return h("div", {},
      h("div", { class: "ask" }, h("div", { class: "who", html: A().avatarOf(w, Q.st.char) }), h("div", { class: "bubble sm" }, h("small", {}, (c.zh || "") + (c.py ? " · " + c.py : "")), ruby(t.npc, { cls: "big" }),
        h("button", { class: "iconbtn mini", onclick: () => speak(t.npc) }, "🔊"))),
      choice(t, (o) => ruby(o.zh, { cls: "optz" })));
  }
  function hzBody(t) {
    return h("div", {}, h("div", { class: "emo" }, t.emoji), h("div", { class: "opts grid2" }, t.opts.map((o) => {
      const sc = Q.scene, bad = sc.wrong.includes(o.id);
      return h("button", { class: "opt hzo" + (bad ? " bad" : ""), "data-id": o.id, disabled: bad || sc.lock || sc.anim || !!sc.fb, onclick: () => submit(o.id, (r) => { if (!r.ok) sc.wrong.push(o.id); }) }, ruby(o.zh, { cls: "xl" }));
    })));
  }
  function tnBody(t) {
    return h("div", {}, h("div", { class: "bigzh" }, t.h, h("button", { class: "iconbtn mini", style: "top:20%", onclick: () => speak([{ h: t.h }]) }, "🔊")), choice(t, (o) => h("span", { class: "py2" }, o.p)));
  }
  function trBody(t) {
    return h("div", {}, h("div", { class: "bubble sm solo" }, ruby(t.zh, { cls: "big" }), h("button", { class: "iconbtn mini", onclick: () => speak(t.zh) }, "🔊")),
      choice(t, (o) => h("span", {}, fillName(loc(o.tr)))));
  }
  function odBody(t) {
    const sc = Q.scene, od = sc.od;
    if (!od.bank) od.bank = t.words.map((w) => w.id);
    const byId = Object.fromEntries(t.words.map((w) => [w.id, w]));
    const chip = (id, onclick) => h("button", { class: "chip3", "data-id": id, onclick }, ruby([{ h: byId[id].h, p: byId[id].p }]));
    const ans = h("div", { class: "odans" + (od.ans.length ? "" : " empty") },
      od.ans.map((id) => chip(id, () => { od.ans = od.ans.filter((x) => x !== id); od.bank.push(id); rerender(); })),
      od.ans.length ? h("span", { class: "pn big" }, t.end) : h("span", { class: "muted" }, "…"));
    const bank = h("div", { class: "odbank" }, od.bank.map((id) => chip(id, () => { od.bank = od.bank.filter((x) => x !== id); od.ans.push(id); Y().haptic(); rerender(); })));
    return h("div", {},
      h("div", { class: "hintbox" }, "💡 " + fillName(loc(t.hint))),
      ans, bank,
      h("button", { class: "qbtn g btn-check", disabled: od.bank.length > 0 || sc.lock || sc.anim || !!sc.fb, onclick: () => submit(od.ans.slice(), (r) => { if (!r.ok) { od.bank = od.bank.concat(od.ans); od.ans = []; } }) }, "✓ " + tr("q_check")));
  }
  function mtBody(t) {
    const sc = Q.scene, mt = sc.mt;
    const pick = (side, id) => {
      if (sc.lock || sc.anim || sc.fb) return;
      if (side === "l") { mt.sel = mt.sel === id ? null : id; Y().haptic(); return rerender(); }
      if (mt.sel == null) { Y().toast("👈"); return; }
      const l = mt.sel;
      submit({ l, r: id }, (r) => { if (r.ok) { mt.done = r.matched; mt.sel = null; } else { mt.sel = null; } });
    };
    return h("div", { class: "mt" },
      h("div", { class: "col" }, t.left.map((o) => h("button", { "data-id": o.id, class: "mtc" + (mt.done.includes(o.id) ? " ok" : "") + (mt.sel === o.id ? " sel" : ""), disabled: mt.done.includes(o.id), onclick: () => pick("l", o.id) }, ruby([{ h: o.h, p: o.p }])))),
      h("div", { class: "col" }, t.right.map((o) => h("button", { "data-id": o.id, class: "mtc r" + (mt.done.includes(o.id) ? " ok" : ""), disabled: mt.done.includes(o.id), onclick: () => pick("r", o.id) }, o.x))));
  }

  function dlgSheet() {
    const p = Q.scene.p;
    const list = h("div", { class: "dlglist" }, p.dialogue.map((ln) => {
      const c = p.cast[ln.who] || {}; const row = h("div", { class: "dl" + (ln.who === "me" ? " me" : "") }, h("small", {}, ln.who === "me" ? heroName() : c.zh), ruby(ln.zh), h("div", { class: "trl", style: "display:none" }, fillName(loc(ln.tr))));
      row.addEventListener("click", () => { const x = row.querySelector(".trl"); x.style.display = x.style.display === "none" ? "block" : "none"; });
      return row;
    }));
    sheet([h("div", { class: "muted", style: "margin:4px 0 10px" }, tr("q_tap_tr")), list], { title: tr("q_dlg") });
  }

  // ── конец сцены: окно-итог по центру ──
  function finale() {
    const sc = Q.scene, r = sc.res || {};
    const nx = r.next_scene;
    const acts = [];
    if (nx && !r.replay) {
      if (r.can_continue) acts.push(h("button", { class: "qbtn", onclick: () => { const id = nx; closeSceneThen(() => openScene(id)); } }, tr("q_next_scene") + " →"));
      else acts.push(h("button", { class: "qbtn g", onclick: () => { const id = nx; closeSceneThen(() => extraSheet(id)); } }, "▶ " + tr("q_continue_today")));
    }
    acts.push(h("button", { class: "qbtn l", onclick: closeScene }, tr("q_back_map")));
    const body = h("div", { class: "qfn" },
      h("div", { class: "cha", html: A().chacha("happy") }),
      h("div", {},
        h("h2", {}, r.replay ? tr("q_replay_done") : r.chapter_done ? tr("q_chapter_done") : tr("q_done_title")),
        r.chapter_done ? h("p", { class: "muted" }, tr("q_chapter_done_sub")) : null,
        !r.replay ? h("div", { class: "earn" }, h("span", {}, coinI(), " " + tr("q_earned", { n: r.earned || 0 }).replace("🪙", "").trim()), r.mistakes ? h("small", {}, tr("q_mist", { n: r.mistakes })) : null) : null,
        r.prize_new ? h("div", { class: "prz" }, "🎁 " + tr("q_prize_new")) : null,
        h("div", { class: "culture" }, h("b", {}, "🏮 " + tr("q_culture")), h("p", {}, loc(sc.p.culture))),
        nx && !r.replay && !r.can_continue ? h("div", { class: "muted", style: "margin:2px 0 8px" }, tr("q_tomorrow")) : null,
        h("div", { class: "acts" }, acts)));
    const win = h("div", { class: "qwin m wide in" }, h("div", { class: "qwin-bar" }, h("div", { class: "t" }, "到了！  ·  " + tr("q_done_title"))), h("div", { class: "qwin-body" }, body));
    G.qg.append(h("div", { class: "qmodal" }, win));
  }

  // ───────────────────────── жизни, магазин, оплата ─────────────────────────
  // В игре окна показываются внутри сцены (чтобы поворачивались вместе с ней), на карте это обычные листы.
  function sheet(content, o) {
    o = o || {};
    if (!G) return Y().sheet([o.title ? h("h3", {}, o.title) : null, content]);
    const win = h("div", { class: "qwin m in" + (o.wide ? " wide" : "") },
      h("div", { class: "qwin-bar" }, h("div", { class: "t" }, o.title || ""), h("button", { class: "qx", onclick: () => bg.remove() }, "✕")),
      h("div", { class: "qwin-body" }, content));
    const bg = h("div", { class: "qmodal", onclick: (e) => { if (e.target === bg) bg.remove(); } }, win);
    G.qg.append(bg);
    return bg;
  }
  const closeSheets = () => document.querySelectorAll(".sheetbg,.qmodal").forEach((n) => { if (!n.classList.contains("qfinal")) n.remove(); });

  const priceRow = (item, onDone) => {
    const st = Q.st, it = st.shop.items[item] || st.shop.items.skin;
    const row = h("div", { class: "prow" });
    row.append(h("button", { class: "btn jade sm", onclick: () => buyCoins(item, onDone) }, `🪙 ${it.coins}`));
    if (st.stars_on) row.append(h("button", { class: "btn star sm", onclick: () => buyStars(item, onDone) }, `⭐ ${it.stars}`));
    return row;
  };

  async function buyCoins(item, done) {
    await Y().safe(async () => {
      const r = await Y().api("/api/quest/buy", { item });
      if (r.err === "poor") return Y().toast(tr("q_poor", { n: r.need }));
      if (r.err === "full") return Y().toast(tr("q_full"));
      if (r.err === "owned") return Y().toast(tr("q_owned"));
      if (!r.ok) return Y().toast(tr("err"));
      Y().haptic("ok"); Y().toast(tr("q_bought")); await reload(); if (done) done(); refreshAll();
    });
  }
  async function buyStars(item, done) {
    await Y().safe(async () => {
      const r = await Y().api("/api/quest/invoice", { item });
      if (!r.ok) return Y().toast(tr("q_pay_fail"));
      const finish = async () => {
        Y().toast(tr("q_pay_wait"));
        for (let i = 0; i < 10; i++) {
          await new Promise((res) => setTimeout(res, 1200));
          const p = await Y().api("/api/quest/paid", { nonce: r.nonce }).catch(() => ({}));
          if (p.paid) { await reload(); Y().toast(tr("q_pay_ok")); Y().confetti(); if (done) done(); refreshAll(); return; }
        }
        Y().toast(tr("q_pay_slow")); reload().then(refreshAll);
      };
      const tg = window.Telegram && window.Telegram.WebApp;
      if (tg && tg.openInvoice) tg.openInvoice(r.link, (status) => { if (status === "paid") finish(); else if (status === "cancelled") Y().toast(tr("q_pay_cancel")); else if (status === "failed") Y().toast(tr("q_pay_fail")); });
      else { Y().openTg(r.link); finish(); }
    });
  }
  function refreshAll() {
    if (root && Q.scene) { updateHud(); if (Q.scene.phase === "task" && !Q.scene.anim) winTask(false); } else Y().render();
  }

  // нет жизней
  function outSheet(manual) {
    const st = Q.st, c = st.constants;
    if (manual && st.lives >= c.lives_max) return Y().toast(tr("q_life_full"));
    closeSheets();
    const left = st.today.revives_left;
    const body = [h("div", { style: "text-align:center" }, h("div", { class: "qem" }, st.lives <= 0 ? "🫖" : "🏮"), h("h3", {}, st.lives <= 0 ? tr("q_out_title") : tr("q_lives")),
      hearts(st.lives, c.lives_max), h("div", { class: "muted qtick", style: "margin-top:6px" }, tr("q_life_in", { t: mmss(Math.max(0, (Q.nextLifeAt - Date.now()) / 1000)) })))];
    body.push(h("div", { class: "qopt" }, h("div", { class: "tx" }, h("b", {}, "🔁 " + tr("q_cards")), h("small", {}, tr("q_cards_sub", { n: left }))),
      h("button", { class: "btn jade sm", disabled: !left || st.lives >= c.lives_max, onclick: () => { closeSheets(); cardsSheet(); } }, "▶")));
    body.push(h("div", { class: "qopt" }, h("div", { class: "tx" }, h("b", {}, "🏮 " + tr("q_life")), h("small", {}, "+1")), priceRow("life", () => closeSheets())));
    body.push(h("div", { class: "qopt" }, h("div", { class: "tx" }, h("b", {}, "🏮🏮 " + tr("q_refill")), h("small", {}, `+${c.lives_max}`)), priceRow("refill", () => closeSheets())));
    if (st.stars_on) body.push(h("div", { class: "muted", style: "font-size:12.5px;margin-top:8px" }, tr("q_stars_note")));
    sheet(body, { title: tr("q_lives") });
  }

  // «повтори карточки»
  async function cardsSheet() {
    await Y().safe(async () => {
      const r = await Y().api("/api/quest/cards");
      if (!r.ok) return Y().toast(tr("err"));
      const c = Q.st.constants; const t0 = Date.now();
      const claim = h("button", { class: "btn primary block", disabled: true }, "⏳");
      const bg = sheet([h("div", { class: "muted", style: "margin:4px 0 10px" }, tr("q_cards_hint")),
        h("div", { class: "dlglist" }, r.cards.map((cd) => { const row = h("div", { class: "dl" }, ruby(cd.zh), h("div", { class: "trl", style: "display:none" }, fillName(loc(cd.tr)))); row.addEventListener("click", () => { const x = row.querySelector(".trl"); x.style.display = x.style.display === "none" ? "block" : "none"; }); return row; })), claim], { title: "🔁 " + tr("q_cards") });
      const tick = setInterval(() => {
        if (!document.body.contains(claim)) return clearInterval(tick);
        const left = Math.ceil(c.cards_min - (Date.now() - t0) / 1000);
        if (left > 0) { claim.textContent = "⏳ " + left; return; }
        clearInterval(tick); claim.disabled = false; claim.textContent = "🏮 " + tr("q_claim");
        claim.onclick = async () => {
          claim.disabled = true;
          await Y().safe(async () => {
            const k = await Y().api("/api/quest/cards/claim");
            if (k.err === "fast") return Y().toast(tr("q_cards_fast"));
            if (!k.ok) { bg.remove(); return Y().toast(k.err === "full" ? tr("q_full") : tr("err")); }
            Q.st.lives = k.lives; Q.nextLifeAt = k.next_life_in ? Date.now() + k.next_life_in * 1000 : 0; Q.st.today.revives_left = k.revives_left;
            bg.remove(); Y().haptic("ok"); Y().toast(tr("q_got_life")); refreshAll();
          });
        };
      }, 500);
    });
  }

  // магазин (с карты)
  function shopSheet() {
    closeSheets();
    const st = Q.st, c = st.constants;
    const body = [h("h3", {}, "🛍 " + tr("q_shop_title")), h("div", { class: "muted" }, "🪙 " + st.coins + " · " + tr("q_howmuch", { a: c.task_coins, b: c.scene_bonus }))];
    body.push(h("div", { class: "qopt" }, h("div", { class: "tx" }, h("b", {}, "🎟 " + tr("q_extra")), h("small", {}, tr("q_extra_sub"))), priceRow("extra", () => closeSheets())));
    body.push(h("div", { class: "qopt" }, h("div", { class: "tx" }, h("b", {}, "🏮 " + tr("q_life")), h("small", {}, "+1")), priceRow("life", () => closeSheets())));
    body.push(h("div", { class: "qopt" }, h("div", { class: "tx" }, h("b", {}, "🏮🏮 " + tr("q_refill")), h("small", {}, `+${c.lives_max}`)), priceRow("refill", () => closeSheets())));
    if (st.stars_on) body.push(h("div", { class: "muted", style: "font-size:12.5px;margin-top:10px" }, tr("q_stars_note")));
    body.push(h("button", { class: "btn line sm", style: "margin-top:14px", onclick: () => { closeSheets(); wardrobeSheet(); } }, "👘 " + tr("q_wardrobe")));
    Y().sheet(body);
  }
  function extraSheet(nextId) {
    closeSheets();
    const st = Q.st;
    const body = [h("div", { style: "text-align:center" }, h("div", { class: "qem" }, "🎟"), h("h3", {}, tr("q_continue_today")), h("div", { class: "muted" }, tr("q_continue_sub"))),
      h("div", { class: "qopt" }, h("div", { class: "tx" }, h("b", {}, tr("q_extra")), h("small", {}, "🪙 " + st.coins)), priceRow("extra", async () => { closeSheets(); if (nextId) openScene(nextId); else { await reload(); Y().render(); } }))];
    if (st.stars_on) body.push(h("div", { class: "muted", style: "font-size:12.5px;margin-top:8px" }, tr("q_stars_note")));
    body.push(h("button", { class: "btn line sm", style: "margin-top:12px", onclick: closeSheets }, tr("close")));
    sheet(body);
  }

  // гардероб и редактирование героя
  function wardrobeSheet() {
    closeSheets();
    const st = Q.st, ch = st.char, d = { gender: ch.gender, skin: ch.skin, hero: ch.hero, hair: ch.hair || 0, hstyle: ch.hstyle || 0 };
    const wrap = h("div", {});
    const draw = () => {
      const have = st.char.owned.includes(d.skin);
      const input = h("input", { maxlength: 16, value: d.hero, oninput: (e) => { d.hero = e.target.value; } });
      wrap.replaceChildren(h("h3", {}, "👘 " + tr("q_ward_title")), preview(d),
        h("div", { class: "seg fill" }, [["f", "q_girl"], ["m", "q_boy"]].map(([g, k]) => h("button", { class: d.gender === g ? "on" : "", onclick: () => { d.gender = g; draw(); } }, tr(k)))),
        input,
        lookPick(d, draw),
        skinChips(d, st.char.owned, (i) => { d.skin = i; draw(); }),
        have
          ? h("button", { class: "btn jade", style: "margin-top:14px", onclick: save }, "✓ " + tr("q_save"))
          : h("div", { style: "margin-top:14px" }, h("div", { class: "muted", style: "margin-bottom:6px" }, tr("q_locked_skin", { n: st.shop.items.skin.coins })), priceRow("skin" + d.skin, () => { closeSheets(); })));
    };
    const save = async () => {
      await Y().safe(async () => {
        const r = await Y().api("/api/quest/char", { hero: d.hero, gender: d.gender, skin: d.skin, hair: d.hair || 0, hstyle: d.hstyle || 0 });
        if (!r.ok) return Y().toast(tr("q_name_err"));
        closeSheets(); await reload(); Y().toast(tr("q_bought")); refreshAll();
      });
    };
    draw(); Y().sheet(wrap);
  }
  function openSupport() {
    const link = Y().S.me && Y().S.me.invite && Y().S.me.invite.link;
    const bot = link ? link.split("?")[0] : "";
    Y().sheet([h("div", { style: "text-align:center" }, h("div", { class: "qem" }, "💝"), h("h3", {}, tr("q_donate_title")), h("p", { class: "muted" }, tr("q_donate_text"))),
      bot ? h("button", { class: "btn jade", onclick: () => { closeSheets(); Y().openTg(bot + "?start=donate"); } }, tr("q_donate_open")) : null]);
  }

  // ───────────────────────── вход ─────────────────────────
  function view() {
    if (!Q.st) { load(); return h("div", { class: "muted", style: "text-align:center;padding:40px" }, "…"); }
    if (!Q.st.char) return creatorView();
    return homeView();
  }
  function enter() { load(false); loadBoard("week", false); }

  window.QUEST = { view, enter, reload, openSupport };
})();
