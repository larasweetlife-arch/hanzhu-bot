/* Оформления профиля и карточки игроков. Подключается после app.js. Цвета и цены приходят с сервера (/api/themes). */
(() => {
  "use strict";
  const Y = () => window.QY;
  const h = (...a) => Y().h(...a);
  const S = () => Y().S;
  const L = () => S().lang || "ru";

  const TT = {
    ru: {
      title: "Оформления", card_sub: "Цвета интерфейса, подсветка в рейтинге и карточка игрока", open: "Открыть", none: "Без оформления", worn: "Надето",
      wear: "Надеть", off: "Снять оформление", until: "до {d}", forever: "навсегда", mine: "Мои оформления", shop: "Магазин оформлений",
      weekly: "Награда недели", rare: "Редкое", epic: "Эпическое", legendary: "Легендарное", empty: "Пока нет ни одного. Победи в рейтинге недели или загляни в магазин ниже.",
      weekly_note: "Победители рейтингов недели получают особое оформление на неделю. Каждый раз оно новое.",
      packs: "Пополнить монеты", pack_note: "Купленные монеты в рейтинг не идут: очки считаются только по заработанному в игре.",
      need_hero: "Монеты и покупки живут в игре «Путешествие». Сначала создай героя на вкладке «Путь».",
      coins: "У тебя 🪙 {n}", bought: "Оформление куплено и надето", worn_ok: "Оформление надето", off_ok: "Оформление снято",
      wins: "Победы в рейтингах", wins_sub: "Тренировка слов: {a} · Путешествие: {b}", week: "Очки за неделю", total: "Очки всего", season: "Очки за месяц",
      scenes: "Пройдено сцен", streak: "Серия дней", theme: "Оформление", closed: "Карточка недоступна", crown: "Победитель недели", close: "Закрыть",
      you: "это ты", coin_hidden: "Монеты других игроков не показываются",
    },
    uz: {
      title: "Bezaklar", card_sub: "Interfeys ranglari, reytingda ajratilish va o'yinchi kartochkasi", open: "Ochish", none: "Bezaksiz", worn: "Kiyilgan",
      wear: "Kiyish", off: "Bezakni yechish", until: "{d} gacha", forever: "abadiy", mine: "Mening bezaklarim", shop: "Bezaklar do'koni",
      weekly: "Hafta sovg'asi", rare: "Noyob", epic: "Epik", legendary: "Afsonaviy", empty: "Hozircha yo'q. Hafta reytingida g'olib bo'ling yoki quyidagi do'konga qarang.",
      weekly_note: "Hafta reytingi g'oliblari bir haftaga maxsus bezak oladi. U har safar yangi bo'ladi.",
      packs: "Tangalarni to'ldirish", pack_note: "Sotib olingan tangalar reytingga kirmaydi: ochkolar faqat o'yinda topilganlar bo'yicha hisoblanadi.",
      need_hero: "Tangalar va xaridlar «Sayohat» o'yinida. Avval «Yo'l» sahifasida qahramon yarating.",
      coins: "Sizda 🪙 {n}", bought: "Bezak sotib olindi va kiyildi", worn_ok: "Bezak kiyildi", off_ok: "Bezak yechildi",
      wins: "Reytinglardagi g'alabalar", wins_sub: "So'z mashqi: {a} · Sayohat: {b}", week: "Hafta ochkolari", total: "Jami ochko", season: "Oy ochkolari",
      scenes: "O'tilgan sahnalar", streak: "Kunlar seriyasi", theme: "Bezak", closed: "Kartochka mavjud emas", crown: "Hafta g'olibi", close: "Yopish",
      you: "bu siz", coin_hidden: "Boshqa o'yinchilarning tangalari ko'rsatilmaydi",
    },
    en: {
      title: "Themes", card_sub: "Interface colours, a highlight in the rankings and your player card", open: "Open", none: "No theme", worn: "Worn",
      wear: "Wear", off: "Remove theme", until: "until {d}", forever: "forever", mine: "My themes", shop: "Theme shop",
      weekly: "Weekly prize", rare: "Rare", epic: "Epic", legendary: "Legendary", empty: "None yet. Win a weekly ranking or take a look at the shop below.",
      weekly_note: "Winners of the weekly rankings get a special theme for a week. It is new every time.",
      packs: "Top up coins", pack_note: "Purchased coins do not count towards the ranking: points come only from coins earned in the game.",
      need_hero: "Coins and purchases live in the Journey game. Create your hero on the “Journey” tab first.",
      coins: "You have 🪙 {n}", bought: "Theme bought and worn", worn_ok: "Theme worn", off_ok: "Theme removed",
      wins: "Ranking wins", wins_sub: "Word practice: {a} · Journey: {b}", week: "Points this week", total: "Total points", season: "Points this month",
      scenes: "Scenes completed", streak: "Day streak", theme: "Theme", closed: "Card unavailable", crown: "Weekly winner", close: "Close",
      you: "that's you", coin_hidden: "Other players' coins are never shown",
    },
    zh: {
      title: "主题", card_sub: "界面配色、排行榜高亮和玩家名片", open: "打开", none: "无主题", worn: "已穿戴",
      wear: "穿戴", off: "取消主题", until: "至 {d}", forever: "永久", mine: "我的主题", shop: "主题商店",
      weekly: "每周奖励", rare: "稀有", epic: "史诗", legendary: "传说", empty: "还没有。赢得每周排行榜，或去下面的商店看看。",
      weekly_note: "每周排行榜的冠军可获得为期一周的特别主题，每次都不同。",
      packs: "充值金币", pack_note: "购买的金币不计入排行榜：积分只按游戏中赚到的金币计算。",
      need_hero: "金币和购买都在“旅行”游戏里。请先在“旅行”页创建主角。",
      coins: "你有 🪙 {n}", bought: "主题已购买并穿戴", worn_ok: "主题已穿戴", off_ok: "主题已取消",
      wins: "夺冠次数", wins_sub: "单词练习：{a} · 旅行：{b}", week: "本周积分", total: "总积分", season: "本月积分",
      scenes: "已通关幕数", streak: "连续天数", theme: "主题", closed: "名片不可用", crown: "每周冠军", close: "关闭",
      you: "这是你", coin_hidden: "不会显示其他玩家的金币",
    },
  };
  const tt = (k, v) => {
    let s = (TT[L()] || TT.ru)[k];
    if (s === undefined) s = TT.ru[k] || k;
    return v ? s.replace(/\{(\w+)\}/g, (_, x) => (v[x] !== undefined ? v[x] : "")) : s;
  };

  const TH = { data: null, cat: {}, eq: null, userScheme: null, keys: [] };
  const root = document.documentElement;
  const tg = window.Telegram && window.Telegram.WebApp;

  const scope = (x) => Object.entries(x.vars).map(([k, v]) => `--${k}:${v}`).join(";") + `;--qbg:${x.bg}`;

  function clear() {
    TH.keys.forEach((k) => root.style.removeProperty(k));
    TH.keys = [];
    root.removeAttribute("data-qtheme");
  }
  function apply(id) {
    const x = id && TH.cat[id];
    TH.eq = x ? id : null;
    if (!x) {
      const had = TH.keys.length > 0;
      clear();
      if (had && TH.userScheme) { root.dataset.theme = TH.userScheme; }
      TH.userScheme = null;
      return;
    }
    if (!TH.userScheme) TH.userScheme = root.dataset.theme;
    clear();
    root.setAttribute("data-qtheme", id);
    for (const [k, v] of Object.entries(x.vars)) { root.style.setProperty("--" + k, v); TH.keys.push("--" + k); }
    root.style.setProperty("--qbg", x.bg); TH.keys.push("--qbg");
    root.dataset.theme = x.scheme;
    try { if (tg) { tg.setHeaderColor(x.vars.bg); tg.setBackgroundColor(x.vars.bg); } } catch (e) { /* старые версии Telegram */ }
  }
  // вызывается из app.js после смены светлой/тёмной темы
  function reapply() { if (TH.eq) { const id = TH.eq; TH.userScheme = null; apply(id); } }

  async function load() {
    const r = await Y().api("/api/themes");
    TH.data = r;
    TH.cat = Object.fromEntries(r.catalog.map((x) => [x.id, x]));
    apply(r.equipped);
    return r;
  }

  // ── строки в рейтинге ──
  function rowProps(r, kind) {
    const o = { cls: " tap" };
    const x = r.theme && TH.cat[r.theme];
    if (x) { o.cls += " throw"; o.style = `--rj:${x.vars.jade};--rg:${x.vars.gold}`; }
    if (r.ref) o.onclick = () => openProfile(r.ref, kind);
    return o;
  }
  function mark(r) {
    const x = r.theme && TH.cat[r.theme];
    return x ? h("span", { class: "thmark", title: x.name }, x.emoji) : null;
  }

  // ── карточка игрока ──
  async function openProfile(ref, kind) {
    await Y().safe(async () => {
      const p = await Y().api("/api/profile/public", { ref, kind });
      if (!p.ok) return Y().toast(tt("closed"));
      const x = p.theme && TH.cat[p.theme];
      const crown = p.wins && p.wins.total > 0;
      const av = p.kind === "quest" && window.QART
        ? h("div", { class: "pav", html: window.QART.avatar(p.hero) })
        : h("div", { class: "pav em" }, p.emoji || "茶");
      const stat = (v, k) => h("div", {}, h("b", {}, v), h("span", {}, tt(k)));
      const stats = p.kind === "quest"
        ? [stat(p.week, "week"), stat(p.total, "total"), stat(`${p.scenes}/${p.scenes_total}`, "scenes")]
        : [stat(p.week, "week"), stat(p.season, "season"), stat(p.streak, "streak")];
      const card = h("div", { class: "pcard" + (x ? " themed" : ""), style: x ? scope(x) : null },
        h("div", { class: "phead" }, av,
          h("div", { class: "pinfo" }, h("h2", {}, p.name),
            p.kind === "word" ? h("div", { class: "psub" }, (p.emoji || "") + " " + (p.title || "")) : null,
            x ? h("div", { class: "pchip" }, x.emoji + " " + x.name) : h("div", { class: "pchip dim" }, tt("none")))),
        crown ? h("div", { class: "pwins" }, h("span", { class: "k" }, "👑"), h("div", {}, h("b", {}, tt("wins") + ": " + p.wins.total), h("small", {}, tt("wins_sub", { a: p.wins.word, b: p.wins.quest })))) : null,
        h("div", { class: "pgrid" }, stats),
        h("div", { class: "pnote" }, tt("coin_hidden")));
      Y().sheet([card, h("button", { class: "btn line", style: "margin-top:12px", onclick: (e) => e.target.closest(".sheetbg").remove() }, tt("close"))]);
    });
  }

  // ── окно «Оформления» ──
  const tierName = (x) => (x.tier ? tt(x.tier) : tt("weekly"));
  function swatch(x) {
    return h("div", { class: "thprev" }, h("i", { class: "c1" }), h("i", { class: "c2" }), h("i", { class: "c3" }));
  }
  async function equip(id, silent) {
    await Y().safe(async () => {
      const r = await Y().api("/api/themes/equip", { id });
      if (!r.ok) return;
      TH.data.equipped = r.equipped; apply(r.equipped);
      if (!silent) Y().toast(id ? tt("worn_ok") : tt("off_ok"));
      Y().haptic("ok"); Y().render();
    });
  }
  async function afterBuy(id) {
    await load();
    if (TH.data.owned[id]) { await equip(id, true); Y().toast(tt("bought")); }
    draw();
  }
  let wrapEl = null;
  function priceButtons(item, x, afterId) {
    const Q = window.QUEST;
    const row = h("div", { class: "prow" });
    const coinsOk = TH.data.has_hero;
    row.append(h("button", { class: "btn jade sm", disabled: !coinsOk, onclick: () => Q.buyCoins(item, () => afterBuy(afterId)) }, `🪙 ${x.coins}`));
    if (TH.data.stars_on) row.append(h("button", { class: "btn star sm", disabled: !coinsOk, onclick: () => Q.buyStars(item, () => afterBuy(afterId)) }, `⭐ ${x.stars}`));
    return row;
  }
  function itemCard(x, mode) {
    const d = TH.data, own = d.owned[x.id];
    const sub = own ? (own.expires ? tt("until", { d: own.expires.slice(8, 10) + "." + own.expires.slice(5, 7) }) : tt("forever")) : tierName(x);
    const card = h("div", { class: "thc" + (TH.eq === x.id ? " on" : ""), style: scope(x) }, swatch(x),
      h("div", { class: "tx" }, h("b", {}, x.emoji + " " + x.name), h("small", {}, (own ? tierName(x) + " · " : "") + sub)));
    if (mode === "mine") {
      card.append(TH.eq === x.id
        ? h("span", { class: "thon" }, "✓ " + tt("worn"))
        : h("button", { class: "btn jade sm", onclick: () => equip(x.id).then(draw) }, tt("wear")));
    } else if (own) {
      card.append(TH.eq === x.id ? h("span", { class: "thon" }, "✓ " + tt("worn")) : h("button", { class: "btn jade sm", onclick: () => equip(x.id).then(draw) }, tt("wear")));
    } else {
      card.append(priceButtons("theme_" + x.id, x, x.id));
    }
    return card;
  }
  function draw() {
    if (!wrapEl || !document.body.contains(wrapEl)) return;
    const d = TH.data, cat = d.catalog;
    const mine = cat.filter((x) => d.owned[x.id]);
    const shop = cat.filter((x) => x.kind === "shop");
    const out = [h("h3", {}, "🎨 " + tt("title"))];
    if (d.coins != null) out.push(h("div", { class: "muted", style: "margin-top:4px" }, tt("coins", { n: d.coins })));
    if (!d.has_hero) out.push(h("div", { class: "muted", style: "margin-top:6px" }, tt("need_hero")));
    out.push(h("h4", { class: "thh" }, tt("mine")));
    out.push(mine.length ? h("div", { class: "thlist" }, mine.map((x) => itemCard(x, "mine"))) : h("div", { class: "muted" }, tt("empty")));
    if (TH.eq) out.push(h("button", { class: "btn line sm", style: "margin-top:10px", onclick: () => equip(null).then(draw) }, tt("off")));
    out.push(h("div", { class: "muted", style: "font-size:12.5px;margin-top:10px" }, tt("weekly_note")));
    out.push(h("h4", { class: "thh" }, tt("shop")));
    out.push(h("div", { class: "thlist" }, shop.map((x) => itemCard(x, "shop"))));
    if (d.packs && d.packs.length && d.stars_on) {
      out.push(h("h4", { class: "thh" }, tt("packs")));
      out.push(h("div", { class: "thpacks" }, d.packs.map((pk) => h("button", { class: "btn star sm", disabled: !d.has_hero, onclick: () => window.QUEST.buyStars(pk.id, () => afterBuy(null)) }, `🪙 ${pk.coins} · ⭐ ${pk.stars}`))));
      out.push(h("div", { class: "muted", style: "font-size:12.5px;margin-top:8px" }, tt("pack_note")));
    }
    wrapEl.replaceChildren(...out);
  }
  async function open() {
    await Y().safe(async () => {
      await load();
      wrapEl = h("div", { class: "thwrap" });
      Y().sheet(wrapEl);
      draw();
    });
  }

  // карточка-вход на вкладках «Профиль» и в магазине
  function card() {
    const x = TH.eq && TH.cat[TH.eq];
    return h("div", { class: "card thentry", onclick: open, style: x ? scope(x) : null },
      h("div", { class: "row" }, h("span", { class: "em" }, x ? x.emoji : "🎨"),
        h("div", { style: "flex:1;min-width:0" }, h("b", {}, tt("title")), h("div", { class: "muted" }, x ? x.name : tt("card_sub"))),
        h("span", { class: "btn jade sm", style: "width:auto" }, tt("open"))));
  }
  const active = () => !!TH.eq;

  window.TH = { title: () => tt("title"), load, apply, reapply, rowProps, mark, openProfile, open, card, active, cat: () => TH.cat };
})();
