/* 清越 · «Путешествие с Чачей»: рисованная графика (SVG, без картинок и внешних файлов).
   Герои собираются из частей: кожа, волосы, наряд, аксессуары. Фоны сцен рисуются по одному на сцену. */
(() => {
  "use strict";

  // ── палитра ──
  const INK = "#2a2220", SKIN = "#f6d3b3", SKIN2 = "#f0c4a0", BLUSH = "#f2958c";

  // 6 нарядов героя: [основной цвет, второй цвет, узор]
  const SKINS = [
    { top: "#3f8f77", top2: "#f4ecd6", motif: "leaf", names: { ru: "Чайный", uz: "Choy", en: "Tea green", zh: "茶绿" } },
    { top: "#d9473f", top2: "#e9c96d", motif: "frog", names: { ru: "Красный фонарик", uz: "Qizil fonus", en: "Red lantern", zh: "红灯笼" } },
    { top: "#5aa7d8", top2: "#ffffff", motif: "cloud", names: { ru: "Небесный", uz: "Osmon", en: "Sky blue", zh: "天蓝" } },
    { top: "#e2b13c", top2: "#c5413a", motif: "dragon", names: { ru: "Золотой дракон", uz: "Oltin ajdar", en: "Golden dragon", zh: "金龙" } },
    { top: "#f2a6bd", top2: "#ffffff", motif: "petal", names: { ru: "Сакура", uz: "Sakura", en: "Sakura", zh: "樱花" } },
    { top: "#2f3438", top2: "#ffffff", motif: "ink", names: { ru: "Тушь", uz: "Siyoh", en: "Ink", zh: "水墨" } },
  ];

  function motif(kind, c) {
    switch (kind) {
      case "leaf": return `<path d="M60 112 C52 118 52 128 60 134 C68 128 68 118 60 112Z" fill="${c}" opacity=".9"/>`;
      case "frog": return `<g stroke="${c}" stroke-width="2.4" fill="none" stroke-linecap="round"><path d="M60 100 V150"/><path d="M52 112 Q60 106 68 112M52 126 Q60 120 68 126M52 140 Q60 134 68 140"/></g>`;
      case "cloud": return `<g fill="${c}" opacity=".9"><circle cx="46" cy="124" r="5"/><circle cx="54" cy="121" r="6"/><circle cx="63" cy="124" r="5"/><circle cx="76" cy="136" r="4"/><circle cx="82" cy="133" r="4.5"/></g>`;
      case "dragon": return `<path d="M44 140 C44 120 62 132 62 116 C62 106 78 108 76 120" fill="none" stroke="${c}" stroke-width="3.4" stroke-linecap="round"/><circle cx="76" cy="119" r="2.6" fill="${c}"/>`;
      case "petal": return `<g fill="${c}" opacity=".95"><circle cx="46" cy="118" r="3.4"/><circle cx="72" cy="126" r="3.4"/><circle cx="54" cy="140" r="3.4"/><circle cx="80" cy="144" r="3"/></g>`;
      case "ink": return `<path d="M42 142 C56 120 70 140 82 112" fill="none" stroke="${c}" stroke-width="3.2" stroke-linecap="round" opacity=".9"/>`;
    }
    return "";
  }

  // ── части героя ──
  function hairBack(style, c) {
    if (style === "long") return `<path d="M22 60 C16 24 104 24 98 60 L100 122 Q60 136 20 122 Z" fill="${c}"/>`;
    if (style === "bun") return `<circle cx="60" cy="15" r="13" fill="${c}"/><circle cx="60" cy="15" r="5" fill="rgba(255,255,255,.2)"/>`;
    if (style === "buns2") return `<circle cx="26" cy="34" r="12" fill="${c}"/><circle cx="94" cy="34" r="12" fill="${c}"/>`;
    return "";
  }
  function hairFront(style, c) {
    switch (style) {
      case "short": return `<path d="M25 64 C19 26 44 20 60 20 C78 20 101 27 95 64 C92 50 84 42 72 40 C64 47 44 47 36 41 C30 46 26 54 25 64Z" fill="${c}"/>`;
      case "bob": return `<path d="M23 62 C17 24 44 19 60 19 C78 19 103 26 97 62 L99 90 Q90 94 84 86 L84 58 C76 50 66 45 60 40 C54 47 44 52 36 58 L36 86 Q30 94 21 90 Z" fill="${c}"/>`;
      case "long": return `<path d="M24 66 C18 26 44 20 60 20 C78 20 102 27 96 66 C92 48 80 40 66 38 C62 46 40 50 30 56 C27 58 25 62 24 66Z" fill="${c}"/>`;
      case "bun": case "buns2": return `<path d="M25 64 C21 28 44 22 60 22 C78 22 99 29 95 64 C90 50 80 44 70 41 C62 47 44 47 36 41 C30 46 26 54 25 64Z" fill="${c}"/>`;
      case "white": return `<path d="M25 62 C21 28 44 22 60 22 C78 22 99 29 95 62 C92 50 84 44 72 42 C64 47 44 47 36 42 C30 46 26 54 25 62Z" fill="#f1efe8" stroke="#d9d5c8" stroke-width="1.2"/>`;
    }
    return "";
  }

  function face(mood, glasses, nobrows) {
    const eyes = mood === "happy"
      ? `<path d="M41 67 Q47 59 53 67" fill="none" stroke="${INK}" stroke-width="3.4" stroke-linecap="round"/><path d="M67 67 Q73 59 79 67" fill="none" stroke="${INK}" stroke-width="3.4" stroke-linecap="round"/>`
      : `<g class="qblink"><ellipse cx="47" cy="66" rx="4.6" ry="5.8" fill="${INK}"/><ellipse cx="73" cy="66" rx="4.6" ry="5.8" fill="${INK}"/><circle cx="48.8" cy="63.6" r="1.9" fill="#fff"/><circle cx="74.8" cy="63.6" r="1.9" fill="#fff"/><circle cx="45.6" cy="68.4" r=".9" fill="#fff" opacity=".8"/><circle cx="71.6" cy="68.4" r=".9" fill="#fff" opacity=".8"/></g>`;
    const mouth = mood === "open"
      ? `<g class="qmouth"><path d="M52 77 Q60 90 68 77 Z" fill="#8a2f2f"/><path d="M55 83 Q60 87 65 83 Q60 80 55 83Z" fill="#f08a84"/></g>`
      : mood === "sad"
        ? `<path d="M53 83 Q60 76 67 83" fill="none" stroke="${INK}" stroke-width="2.8" stroke-linecap="round"/>`
        : `<path d="M52 78 Q60 85 68 78" fill="none" stroke="${INK}" stroke-width="2.8" stroke-linecap="round"/>`;
    const bw = mood === "sad" ? "M39 54 Q45 55 53 58 M81 54 Q75 55 67 58" : mood === "happy" || mood === "open" ? "M39 54 Q46 47 53 52 M81 54 Q74 47 67 52" : "M39 55 Q46 50 53 54 M81 55 Q74 50 67 54";
    const brows = nobrows ? "" : `<path d="${bw}" fill="none" stroke="${INK}" stroke-opacity=".55" stroke-width="2.4" stroke-linecap="round"/>`;
    const gl = glasses ? `<g fill="rgba(255,255,255,.25)" stroke="#4a3b35" stroke-width="2"><circle cx="47" cy="66" r="9"/><circle cx="73" cy="66" r="9"/><path d="M56 66 H64" fill="none"/></g>` : "";
    return `${brows}${eyes}${mouth}${gl}`;
  }

  function acc(list, o) {
    let before = "", after = "", behind = "";
    for (const a of list || []) {
      switch (a) {
        case "cap": after += `<path d="M27 52 C27 20 93 20 93 52 Z" fill="${o.cap || "#27425f"}"/><path d="M22 52 H98 Q98 60 60 60 Q22 60 22 52Z" fill="${o.cap || "#27425f"}"/><circle cx="60" cy="38" r="5" fill="#e9c96d"/>`; break;
        case "driver": after += `<path d="M27 52 C27 22 93 22 93 52 Z" fill="#3a3f45"/><path d="M24 52 H96 Q96 58 60 58 Q24 58 24 52Z" fill="#2c3035"/><rect x="40" y="43" width="40" height="4" fill="#e9c96d"/>`; break;
        case "straw": after += `<ellipse cx="60" cy="42" rx="54" ry="11" fill="#e6c377"/><path d="M30 42 C30 12 90 12 90 42 Z" fill="#efd28c"/><path d="M30 40 H90" stroke="#c5413a" stroke-width="5"/><path d="M12 42 Q60 52 108 42" fill="none" stroke="#c9a257" stroke-width="2"/>`; break;
        case "chef": after += `<path d="M30 44 C14 40 20 14 40 20 C44 4 76 4 80 20 C100 14 106 40 90 44 Z" fill="#fff" stroke="#e4e0d4" stroke-width="1.4"/><rect x="32" y="42" width="56" height="8" rx="3" fill="#fff" stroke="#e4e0d4" stroke-width="1.4"/>`; break;
        case "beard": after += `<path d="M34 76 Q38 112 60 114 Q82 112 86 76 Q74 92 60 92 Q46 92 34 76Z" fill="#f4f2ec" stroke="#d9d5c8" stroke-width="1.2"/><path d="M48 80 Q60 76 72 80 Q60 86 48 80Z" fill="#f4f2ec" stroke="#d9d5c8" stroke-width="1"/>`; break;
        case "brows": after += `<path d="M38 53 Q47 47 54 53M66 53 Q73 47 82 53" fill="none" stroke="#d9d5c8" stroke-width="3.4" stroke-linecap="round"/>`; break;
        case "headset": after += `<path d="M28 62 C28 26 92 26 92 62" fill="none" stroke="#2f3438" stroke-width="5"/><rect x="21" y="58" width="11" height="18" rx="5" fill="#2f3438"/><rect x="88" y="58" width="11" height="18" rx="5" fill="#2f3438"/>`; break;
        case "backpack": behind += `<rect x="76" y="98" width="30" height="46" rx="12" fill="#e08a3c"/><rect x="82" y="108" width="18" height="12" rx="5" fill="#c46f2a"/>`; before += `<path d="M44 98 L40 144 M76 98 L80 144" stroke="#c46f2a" stroke-width="5" stroke-linecap="round"/>`; break;
        case "scarf": before += `<path d="M38 96 Q60 108 82 96 L82 108 Q60 120 38 108 Z" fill="${o.scarf || "#e9c96d"}"/><path d="M74 106 L80 134 L70 130 L68 110Z" fill="${o.scarf || "#e9c96d"}"/>`; break;
        case "apron": before += `<path d="M42 112 H78 L82 152 Q60 158 38 152 Z" fill="#fffdf6" stroke="#e4e0d4" stroke-width="1.4"/><path d="M42 112 L46 98 M78 112 L74 98" stroke="#e4e0d4" stroke-width="3"/>`; break;
        case "vest": before += `<path d="M38 100 L52 104 L52 150 L32 148 Z M82 100 L68 104 L68 150 L88 148 Z" fill="${o.vest || "#f0a73a"}"/><path d="M40 118 H50 M70 118 H80" stroke="#fffbe8" stroke-width="3"/>`; break;
        case "badge": before += `<rect x="68" y="108" width="12" height="9" rx="2" fill="#fff" stroke="#9ab" stroke-width="1"/>`; break;
        case "tie": before += `<path d="M56 98 L64 98 L66 106 L60 128 L54 106Z" fill="#c5413a"/>`; break;
        case "towel": before += `<path d="M36 96 Q60 112 84 96 L86 106 Q60 122 34 106Z" fill="#fff" stroke="#d9d5c8" stroke-width="1.2"/><path d="M42 102 L44 116 M78 102 L76 116" stroke="#3a8fb7" stroke-width="2"/>`; break;
        case "cane": behind += `<path d="M96 120 L102 182" stroke="#8a5a2f" stroke-width="5" stroke-linecap="round"/><path d="M92 122 Q96 114 102 120" fill="none" stroke="#8a5a2f" stroke-width="5" stroke-linecap="round"/>`; break;
        case "flower": after += `<g><circle cx="86" cy="36" r="5" fill="#f2a6bd"/><circle cx="92" cy="40" r="5" fill="#f2a6bd"/><circle cx="90" cy="46" r="5" fill="#f2a6bd"/><circle cx="83" cy="44" r="5" fill="#f2a6bd"/><circle cx="87" cy="41" r="3.6" fill="#f6d36b"/></g>`; break;
        case "bow": after += `<path d="M84 34 L98 28 L98 46Z M84 34 L70 28 L70 46Z" fill="${o.bow || "#d9473f"}" transform="translate(0 -2)"/><circle cx="84" cy="34" r="4" fill="${o.bow || "#d9473f"}"/>`; break;
      }
    }
    return { before, after, behind };
  }

  // ── цвет: осветлить и затемнить (для объёма) ──
  const hx = (c) => { c = String(c || "").trim(); if (/^#[0-9a-f]{3}$/i.test(c)) c = "#" + c[1] + c[1] + c[2] + c[2] + c[3] + c[3]; return /^#[0-9a-f]{6}$/i.test(c) ? [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16)) : null; };
  const mixc = (c, t, a) => { const r = hx(c), q = hx(t); return r && q ? "#" + r.map((v, i) => Math.round(v + (q[i] - v) * a).toString(16).padStart(2, "0")).join("") : c; };
  const lit = (c, a) => mixc(c, "#ffffff", a), drk = (c, a) => mixc(c, "#1a0d08", a);
  const OL = "#4a2c20";             // мягкий тёплый контур
  let GID = 0;

  /* person: o = { hair, style, top, top2, motif, skirt, acc[], wide, mood, bottom, skin, shoes, flip } */
  function person(o) {
    o = Object.assign({ hair: INK, style: "short", top: "#3f8f77", top2: "#f4ecd6", bottom: "#3b4a63", shoes: "#2a2220", skin: SKIN, mood: "smile", acc: [], motif: "", skirt: false, wide: false }, o || {});
    const g = "p" + (++GID), a = acc(o.acc, o), w = o.wide ? 1.16 : 1;
    const stk = `stroke="${OL}" stroke-opacity=".5" stroke-width="1.5" stroke-linejoin="round"`;
    const defs = `<defs>
      <radialGradient id="${g}k" cx=".36" cy=".3" r=".85"><stop offset="0" stop-color="${lit(o.skin, 0.4)}"/><stop offset=".55" stop-color="${o.skin}"/><stop offset="1" stop-color="${drk(o.skin, 0.1)}"/></radialGradient>
      <linearGradient id="${g}t" x1="0" y1="0" x2=".8" y2="1"><stop offset="0" stop-color="${lit(o.top, 0.28)}"/><stop offset=".5" stop-color="${o.top}"/><stop offset="1" stop-color="${drk(o.top, 0.22)}"/></linearGradient>
      <linearGradient id="${g}b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${lit(o.bottom, 0.15)}"/><stop offset="1" stop-color="${drk(o.bottom, 0.2)}"/></linearGradient>
      <linearGradient id="${g}h" x1="0" y1="0" x2=".7" y2="1"><stop offset="0" stop-color="${lit(o.hair, 0.3)}"/><stop offset=".5" stop-color="${o.hair}"/><stop offset="1" stop-color="${drk(o.hair, 0.25)}"/></linearGradient>
      <radialGradient id="${g}c"><stop offset="0" stop-color="${BLUSH}" stop-opacity=".75"/><stop offset="1" stop-color="${BLUSH}" stop-opacity="0"/></radialGradient>
    </defs>`;
    const HAIR = o.style === "white" ? o.hair : `url(#${g}h)`;
    const TOP = `url(#${g}t)`, SK = `url(#${g}k)`;
    const torso = o.skirt
      ? `<path d="M40 98 Q60 90 80 98 L98 154 Q60 164 22 154 Z" fill="${TOP}" ${stk}/><path d="M26 140 Q60 150 94 140" fill="none" stroke="${o.top2}" stroke-width="3" opacity=".8"/><path d="M40 100 Q36 130 28 150" fill="none" stroke="#fff" stroke-opacity=".18" stroke-width="5" stroke-linecap="round"/>`
      : `<path d="M38 98 Q60 90 82 98 L89 150 Q60 158 31 150 Z" fill="${TOP}" ${stk}/><path d="M41 102 Q38 128 35 146" fill="none" stroke="#fff" stroke-opacity=".18" stroke-width="5" stroke-linecap="round"/>`;
    const leg = (x, side) => (o.skirt
      ? `<g class="qleg ${side}" style="transform-origin:${x + 5}px 152px"><rect x="${x}" y="150" width="10" height="28" rx="5" fill="${SK}" ${stk}/><ellipse cx="${x + 5 + (side === "l" ? -1 : 1)}" cy="180" rx="9" ry="5" fill="${o.shoes}"/><ellipse cx="${x + 3 + (side === "l" ? -1 : 1)}" cy="178" rx="4" ry="1.8" fill="#fff" opacity=".18"/></g>`
      : `<g class="qleg ${side}" style="transform-origin:${x + 7}px 148px"><rect x="${x}" y="144" width="14" height="36" rx="6" fill="url(#${g}b)" ${stk}/><ellipse cx="${x + 7 + (side === "l" ? -1 : 1)}" cy="180" rx="9" ry="5" fill="${o.shoes}"/><ellipse cx="${x + 5 + (side === "l" ? -1 : 1)}" cy="178" rx="4" ry="1.8" fill="#fff" opacity=".18"/></g>`);
    const sleeve = o.sleeve || o.top;
    const arm = (side) => {
      const l = side === "l";
      const d = l ? "M38 102 Q26 120 28 138" : "M82 102 Q94 120 92 138";
      const hx_ = l ? 28 : 92;
      return `<g class="qarm ${side}" style="transform-origin:${l ? 38 : 82}px 103px"><path d="${d}" fill="none" stroke="${drk(sleeve, 0.4)}" stroke-width="14" stroke-linecap="round" opacity=".55"/><path d="${d}" fill="none" stroke="${sleeve}" stroke-width="12" stroke-linecap="round"/><circle cx="${hx_}" cy="141" r="6.4" fill="${SK}" ${stk}/></g>`;
    };
    return `<svg class="qperson" viewBox="0 0 120 190" aria-hidden="true">${defs}
      <ellipse cx="60" cy="184" rx="32" ry="5" fill="rgba(34,48,43,.25)"/>
      ${a.behind}
      <g class="qbody">
      <g ${stk}>${hairBack(o.style, HAIR)}</g>
      <g transform="translate(60 0) scale(${w} 1) translate(-60 0)">
        ${leg(43, "l").replace("{x}", "")}${leg(o.skirt ? 64 : 63, "r")}
        ${arm("l")}${arm("r")}
        ${torso}
        <path d="M50 96 Q60 106 70 96 L66 92 Q60 98 54 92Z" fill="${o.top2}"/>
        ${motif(o.motif, o.top2)}
        ${a.before}
      </g>
      <ellipse cx="60" cy="97" rx="14" ry="5" fill="rgba(60,30,20,.16)"/>
      <circle cx="25" cy="66" r="6.5" fill="${SK}" ${stk}/><circle cx="95" cy="66" r="6.5" fill="${SK}" ${stk}/>
      <g class="qhead">
      <circle cx="60" cy="62" r="35" fill="${SK}" ${stk}/>
      <ellipse cx="46" cy="40" rx="11" ry="5.5" fill="#fff" opacity=".2" transform="rotate(-24 46 40)"/>
      <ellipse cx="37" cy="76" rx="9" ry="6" fill="url(#${g}c)"/><ellipse cx="83" cy="76" rx="9" ry="6" fill="url(#${g}c)"/>
      ${face(o.mood, (o.acc || []).includes("glasses"), (o.acc || []).includes("brows"))}
      <g ${stk}>${hairFront(o.style, HAIR)}</g>
      <path d="M40 30 Q52 24 66 27" fill="none" stroke="#fff" stroke-opacity=".25" stroke-width="3.2" stroke-linecap="round"/>
      ${a.after}
      </g>
      </g>
    </svg>`;
  }

  // ── 茶茶: маленький чайный дух-мальчуган в гайвани, с красным шарфиком и чубчиком-листочком ──
  function chacha(mood) {
    const g = "c" + (++GID), D = "#22302b";
    const eyes = mood === "happy"
      ? `<path d="M39 82 Q46 73 53 82" fill="none" stroke="${D}" stroke-width="3.6" stroke-linecap="round"/><path d="M67 82 Q74 73 81 82" fill="none" stroke="${D}" stroke-width="3.6" stroke-linecap="round"/>`
      : `<g class="qblink"><ellipse cx="46" cy="81" rx="5" ry="5.6" fill="${D}"/><ellipse cx="74" cy="81" rx="5" ry="5.6" fill="${D}"/><circle cx="47.6" cy="78.8" r="1.9" fill="#fff"/><circle cx="75.6" cy="78.8" r="1.9" fill="#fff"/><circle cx="44.8" cy="83.4" r=".9" fill="#fff" opacity=".8"/><circle cx="72.8" cy="83.4" r=".9" fill="#fff" opacity=".8"/></g>`;
    const brows = mood === "sad"
      ? `<path d="M38 71 Q45 71 53 75 M82 71 Q75 71 67 75" fill="none" stroke="#3a5a4c" stroke-width="3.4" stroke-linecap="round"/>`
      : `<path d="M38 72 Q46 66 54 70 M82 72 Q74 66 66 70" fill="none" stroke="#3a5a4c" stroke-width="3.6" stroke-linecap="round"/>`;
    const mouth = mood === "sad" ? `<path d="M53 94 Q60 87 67 94" fill="none" stroke="${D}" stroke-width="3" stroke-linecap="round"/>`
      : mood === "open" ? `<g class="qmouth"><path d="M51 88 Q60 103 69 88 Z" fill="#7a2a2a"/><path d="M54 95 Q60 99 66 95 Q60 92 54 95Z" fill="#f08a84"/></g>`
        : `<path d="M52 88 Q60 96 68 88" fill="none" stroke="${D}" stroke-width="3" stroke-linecap="round"/><path d="M57 91.4 l2.6 4 l2.6 -4" fill="#fff" stroke="none" opacity=".95"/>`;
    return `<svg class="qperson qcha" viewBox="0 0 120 130" aria-hidden="true"><defs>
        <radialGradient id="${g}u" cx=".34" cy=".3" r=".9"><stop offset="0" stop-color="#ffffff"/><stop offset=".6" stop-color="#fbf6e6"/><stop offset="1" stop-color="#e3d9bd"/></radialGradient>
        <radialGradient id="${g}t" cx=".5" cy=".4" r=".7"><stop offset="0" stop-color="#b9dcae"/><stop offset="1" stop-color="#7fb08e"/></radialGradient>
        <linearGradient id="${g}s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e5483f"/><stop offset="1" stop-color="#a8231c"/></linearGradient>
        <radialGradient id="${g}c"><stop offset="0" stop-color="#f2958c" stop-opacity=".7"/><stop offset="1" stop-color="#f2958c" stop-opacity="0"/></radialGradient>
      </defs>
      <g class="qsteam" fill="none" stroke="#fffcf4" stroke-width="3" stroke-linecap="round" opacity=".85"><path d="M30 34 C24 24 36 20 30 8"/><path d="M90 34 C84 24 96 20 90 8"/></g>
      <ellipse cx="60" cy="122" rx="38" ry="5.5" fill="rgba(34,48,43,.25)"/>
      <g class="qleg l" style="transform-origin:46px 108px"><rect x="40" y="106" width="13" height="13" rx="6" fill="#7fb08e" stroke="${OL}" stroke-opacity=".45" stroke-width="1.4"/></g>
      <g class="qleg r" style="transform-origin:74px 108px"><rect x="67" y="106" width="13" height="13" rx="6" fill="#7fb08e" stroke="${OL}" stroke-opacity=".45" stroke-width="1.4"/></g>
      <path d="M98 64 C118 62 118 90 94 92" fill="none" stroke="${OL}" stroke-opacity=".4" stroke-width="9" stroke-linecap="round"/>
      <path d="M98 64 C116 62 116 88 94 90" fill="none" stroke="#fbf6e6" stroke-width="6" stroke-linecap="round"/>
      <g class="qarm l" style="transform-origin:22px 84px"><path d="M23 82 Q10 86 8 98" fill="none" stroke="#7fb08e" stroke-width="9" stroke-linecap="round"/><circle cx="8" cy="100" r="6" fill="#fbf6e6" stroke="${OL}" stroke-opacity=".45" stroke-width="1.4"/></g>
      <path d="M20 58 H100 C100 92 84 110 60 110 C36 110 20 92 20 58 Z" fill="url(#${g}u)" stroke="${OL}" stroke-opacity=".45" stroke-width="1.6" stroke-linejoin="round"/>
      <path d="M26 66 C24 82 28 94 38 102" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".55"/>
      <path d="M20 58 H100 C100 64 99 70 97 75 C80 70 40 70 23 75 C21 70 20 64 20 58 Z" fill="#e9e2cf" opacity=".7"/>
      <ellipse cx="60" cy="58" rx="40" ry="9" fill="#8db39a" stroke="${OL}" stroke-opacity=".4" stroke-width="1.4"/><ellipse cx="60" cy="57" rx="34" ry="6" fill="url(#${g}t)"/>
      <g class="qtuft" style="transform-origin:60px 56px"><path d="M60 56 C59 46 61 38 58 30" fill="none" stroke="#2c6c5b" stroke-width="3.2" stroke-linecap="round"/><path d="M58 33 C46 34 40 24 42 17 C52 17 58 24 58 33Z" fill="#3f9a78" stroke="#245a4b" stroke-width="1.2"/><path d="M59 38 C70 38 78 30 76 22 C66 22 60 30 59 38Z" fill="#56b58d" stroke="#245a4b" stroke-width="1.2"/></g>
      <ellipse cx="38" cy="90" rx="9" ry="6" fill="url(#${g}c)"/><ellipse cx="82" cy="90" rx="9" ry="6" fill="url(#${g}c)"/>
      ${brows}${eyes}${mouth}
      <path d="M26 99 Q60 114 94 99 L91 108 Q60 121 29 108 Z" fill="url(#${g}s)" stroke="#6d1410" stroke-opacity=".5" stroke-width="1.2"/>
      <g class="qscarf" style="transform-origin:86px 106px"><path d="M84 106 L100 112 L96 120 L82 112Z" fill="#c9302a" stroke="#6d1410" stroke-opacity=".5" stroke-width="1.2"/><circle cx="85" cy="106" r="4.4" fill="#e5483f" stroke="#6d1410" stroke-opacity=".5" stroke-width="1.2"/></g>
      <g class="qarm r ${mood === "happy" ? "wave" : ""}" style="transform-origin:98px 84px"><path d="M97 82 Q110 84 112 98" fill="none" stroke="#7fb08e" stroke-width="9" stroke-linecap="round"/><circle cx="112" cy="100" r="6" fill="#fbf6e6" stroke="${OL}" stroke-opacity=".45" stroke-width="1.4"/></g>
    </svg>`;
  }

  // ── кто есть кто ──
  const NPC = {
    li:     { hair: INK, style: "bob", top: "#27425f", top2: "#e9c96d", skirt: true, acc: ["cap", "scarf", "badge"], scarf: "#c5413a" },
    wang:   { hair: INK, style: "short", top: "#7b8a96", top2: "#fff", wide: true, acc: ["driver", "vest"], vest: "#f0a73a", bottom: "#33383d" },
    lin:    { hair: "#4a3b35", style: "bun", top: "#c5413a", top2: "#e9c96d", skirt: true, motif: "frog", acc: ["glasses"] },
    zhang:  { hair: INK, style: "short", top: "#e8e2d2", top2: "#fff", wide: true, acc: ["chef", "apron"], bottom: "#5b6b73" },
    dm:     { hair: INK, style: "short", top: "#4f86c6", top2: "#f4ecd6", acc: ["backpack", "headset"], bottom: "#3b4a63" },
    staff:  { hair: INK, style: "bob", top: "#e8793a", top2: "#fff", skirt: false, acc: ["cap", "vest", "badge"], cap: "#e8793a", vest: "#f0c53a", bottom: "#33383d" },
    ticket: { hair: INK, style: "bun", top: "#27425f", top2: "#fff", acc: ["cap", "glasses", "tie", "badge"], cap: "#27425f", bottom: "#27425f" },
    vend:   { hair: "#3a3128", style: "short", top: "#7fa66f", top2: "#fff", wide: true, acc: ["straw", "towel"], bottom: "#6c5a46" },
    old:    { hair: "#f1efe8", style: "white", skin: SKIN2, top: "#8d7f74", top2: "#e9c96d", motif: "frog", acc: ["beard", "brows", "cane"], bottom: "#4a3f38" },
  };

  function heroOpts(ch, mood) {
    const sk = SKINS[(ch && ch.skin) || 0] || SKINS[0];
    const girl = ch && ch.gender === "f";
    return girl
      ? { hair: "#2f241f", style: "long", top: sk.top, top2: sk.top2, motif: sk.motif, skirt: true, acc: ["bow"], bow: sk.top2 === "#ffffff" ? sk.top : sk.top2, mood }
      : { hair: "#2f241f", style: "short", top: sk.top, top2: sk.top2, motif: sk.motif, bottom: "#3b4a63", mood };
  }

  function figure(id, ch, mood) {
    if (id === "cc") return chacha(mood);
    if (id === "me") return person(heroOpts(ch, mood));
    return person(Object.assign({ mood }, NPC[id] || {}));
  }
  function avatarOf(id, ch) {   // голова и плечи любого персонажа
    if (id === "cc") return chacha("smile").replace('class="qperson qcha"', 'class="qperson qcha qavatar"');
    return figure(id, ch, "smile").replace('class="qperson" viewBox="0 0 120 190"', 'class="qperson qavatar" viewBox="14 12 92 104"');
  }
  const avatar = (ch) => avatarOf("me", ch);

  // ── вывески внутри фонов (иероглифы + пиньинь) ──
  const sign = (x, y, w, zh, py, bg = "#27425f", fg = "#fff", zs = 15) =>
    `<g><rect x="${x}" y="${y}" width="${w}" height="${zs + 13}" rx="4" fill="${bg}" stroke="rgba(0,0,0,.18)"/><text x="${x + w / 2}" y="${y + zs}" text-anchor="middle" font-size="${zs}" font-weight="700" fill="${fg}" font-family="'Noto Serif SC','Songti SC',serif">${zh}</text><text x="${x + w / 2}" y="${y + zs + 9}" text-anchor="middle" font-size="7" fill="${fg}" opacity=".85" font-family="sans-serif">${py}</text></g>`;
  const cloud = (x, y, s = 1, o = 0.9) => `<g transform="translate(${x} ${y}) scale(${s})" fill="#fff" opacity="${o}"><ellipse cx="0" cy="0" rx="20" ry="8"/><ellipse cx="-12" cy="3" rx="13" ry="7"/><ellipse cx="14" cy="3" rx="14" ry="7"/><ellipse cx="2" cy="-6" rx="11" ry="8"/></g>`;
  const lantern = (x, y, s = 1) => `<g class="qsway" style="transform-origin:${x}px ${y - 30 * s}px"><g transform="translate(${x} ${y}) scale(${s})"><path d="M0 -30 V-14" stroke="#7a5a2f" stroke-width="1.6"/><rect x="-6" y="-15" width="12" height="4" rx="1.5" fill="#e9c96d"/><ellipse cx="0" cy="0" rx="13" ry="14" fill="#d9473f"/><path d="M-6 -12 Q-10 0 -6 12 M6 -12 Q10 0 6 12 M0 -14 V14" stroke="#b5352f" stroke-width="1.2" fill="none"/><rect x="-6" y="12" width="12" height="4" rx="1.5" fill="#e9c96d"/><path d="M0 16 V26 M-3 26 H3" stroke="#e9c96d" stroke-width="1.6"/></g></g>`;
  const window_ = (x, y, w, h, inner) => `<g><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#bfe0f1"/>${inner || ""}<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="none" stroke="#7f8d95" stroke-width="3"/></g>`;
  const plane = (x, y, s = 1, tail = "#c5413a") => `<g transform="translate(${x} ${y}) scale(${s})"><path d="M-30 0 Q-30 -8 -18 -8 H24 Q36 -6 38 0 Q36 6 24 6 H-18 Q-30 6 -30 0Z" fill="#fbfbf7"/><path d="M-26 -6 L-34 -22 L-24 -22 L-14 -7Z" fill="${tail}"/><path d="M-4 4 L8 20 L16 20 L12 4Z" fill="#dfe3e0"/><path d="M-4 -6 L8 -20 L14 -20 L12 -6Z" fill="#e9ecea"/><g fill="#8fb9d6"><rect x="14" y="-5" width="4" height="4" rx="1"/><rect x="21" y="-5" width="4" height="4" rx="1"/><rect x="28" y="-4" width="4" height="3" rx="1"/></g></g>`;

  // ── фоны сцен (360×220) ──
  const BG = {};

  BG.s1 = () => `
    <defs><linearGradient id="g1w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cfe6f3"/><stop offset="1" stop-color="#f4efe2"/></linearGradient>
    <linearGradient id="g1s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fcdf0"/><stop offset="1" stop-color="#e8f5fb"/></linearGradient>
    <linearGradient id="g1f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9e2d0"/><stop offset="1" stop-color="#cdc3aa"/></linearGradient></defs>
    <rect width="360" height="220" fill="url(#g1w)"/>
    <rect width="360" height="14" fill="#9fb0bd"/><g fill="#fff" opacity=".9"><rect x="30" y="4" width="34" height="5" rx="2"/><rect x="110" y="4" width="34" height="5" rx="2"/><rect x="190" y="4" width="34" height="5" rx="2"/><rect x="270" y="4" width="34" height="5" rx="2"/></g>
    ${window_(36, 28, 288, 96, `<rect x="36" y="28" width="288" height="96" fill="url(#g1s)"/>${cloud(90, 56, 1)}${cloud(250, 48, .8)}${plane(250, 78, .55)}<rect x="36" y="100" width="288" height="24" fill="#9aa5ab"/><path d="M36 112 H324" stroke="#fff" stroke-width="2" stroke-dasharray="14 10"/>${plane(120, 98, 1)}<path d="M180 28 V124 M108 28 V124 M252 28 V124" stroke="#7f8d95" stroke-width="3"/>`)}
    ${sign(120, 17, 120, "到达", "dàodá", "#1f4f8a", "#fff", 13).replace('y="17"', 'y="1"')}
    <rect y="150" width="360" height="70" fill="url(#g1f)"/><g stroke="rgba(0,0,0,.07)" stroke-width="1.5"><path d="M0 170 H360 M0 192 H360"/><path d="M60 150 L20 220 M150 150 L130 220 M240 150 L250 220 M330 150 L370 220"/></g>
    <g><rect x="272" y="104" width="78" height="46" rx="4" fill="#fff" opacity=".35" stroke="#7f8d95"/><rect x="262" y="140" width="98" height="14" rx="3" fill="#8b6a4a"/><rect x="262" y="140" width="98" height="4" fill="#a98458"/></g>
    ${sign(278, 82, 66, "边检", "biānjiǎn", "#c5413a", "#fff", 14)}
    <g><rect x="12" y="130" width="34" height="26" rx="6" fill="#d9473f"/><rect x="22" y="123" width="14" height="8" rx="3" fill="none" stroke="#7a2a26" stroke-width="2.5"/><rect x="50" y="138" width="28" height="20" rx="5" fill="#2f8f83"/><rect x="58" y="132" width="12" height="7" rx="3" fill="none" stroke="#1d5f58" stroke-width="2.5"/></g>`;

  BG.s2 = () => `
    <defs><linearGradient id="g2s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9ed3f1"/><stop offset="1" stop-color="#f6efe0"/></linearGradient></defs>
    <rect width="360" height="220" fill="url(#g2s)"/>${cloud(70, 34, 1)}${cloud(260, 22, 1.2)}${cloud(330, 60, .7)}
    <g fill="#b8c4cc"><rect x="20" y="70" width="30" height="80"/><rect x="54" y="52" width="26" height="98"/><rect x="84" y="82" width="34" height="68"/><rect x="250" y="60" width="28" height="90"/><rect x="282" y="78" width="36" height="72"/><rect x="322" y="56" width="30" height="94"/></g>
    <g fill="#e8eef2" opacity=".9"><rect x="26" y="78" width="6" height="6"/><rect x="38" y="78" width="6" height="6"/><rect x="26" y="94" width="6" height="6"/><rect x="38" y="94" width="6" height="6"/><rect x="60" y="62" width="6" height="6"/><rect x="70" y="62" width="6" height="6"/><rect x="60" y="78" width="6" height="6"/><rect x="256" y="70" width="6" height="6"/><rect x="266" y="70" width="6" height="6"/><rect x="330" y="68" width="6" height="6"/></g>
    <g transform="translate(140 40)"><path d="M0 40 H80 V30 H72 V22 H8 V30 H0Z" fill="#b5352f"/><path d="M-6 22 Q40 4 86 22 Q40 14 -6 22Z" fill="#7a2a26"/><path d="M6 12 Q40 -10 74 12 Q40 4 6 12Z" fill="#9c3a32"/><rect x="12" y="30" width="56" height="10" fill="#d9c9a4"/><rect x="34" y="32" width="12" height="8" fill="#6b3a2a"/></g>
    <rect y="150" width="360" height="70" fill="#59626a"/><rect y="150" width="360" height="5" fill="#8a949c"/><path d="M0 188 H360" stroke="#f4efe2" stroke-width="3" stroke-dasharray="26 16"/>
    <g fill="#5f9a54"><circle cx="16" cy="140" r="16"/><circle cx="344" cy="138" r="18"/></g><rect x="13" y="148" width="6" height="10" fill="#6b4a2a"/><rect x="341" y="148" width="6" height="10" fill="#6b4a2a"/>
    <g opacity=".85"><g transform="translate(236 168)"><rect width="46" height="18" rx="6" fill="#4f86c6"/><rect x="10" y="-8" width="24" height="12" rx="5" fill="#4f86c6"/><circle cx="10" cy="19" r="6" fill="#222"/><circle cx="36" cy="19" r="6" fill="#222"/></g>
    <g transform="translate(290 166)"><rect width="46" height="18" rx="6" fill="#c5413a"/><rect x="10" y="-8" width="24" height="12" rx="5" fill="#c5413a"/><circle cx="10" cy="19" r="6" fill="#222"/><circle cx="36" cy="19" r="6" fill="#222"/></g></g>
    <g transform="translate(70 150)"><path d="M0 40 Q0 24 14 22 L30 4 H70 L88 22 Q104 24 104 40 V50 H0Z" fill="#f2c230"/><path d="M34 8 H66 L80 22 H24Z" fill="#cfe9f5"/><path d="M52 8 V22" stroke="#f2c230" stroke-width="3"/><rect x="38" y="-6" width="28" height="10" rx="3" fill="#fff" stroke="#999"/><text x="52" y="2" text-anchor="middle" font-size="7.5" font-weight="700" fill="#222" font-family="'Noto Serif SC',serif">出租车</text><rect x="0" y="34" width="104" height="5" fill="#d29f14"/><circle cx="24" cy="52" r="10" fill="#26292c"/><circle cx="24" cy="52" r="4" fill="#bbb"/><circle cx="82" cy="52" r="10" fill="#26292c"/><circle cx="82" cy="52" r="4" fill="#bbb"/><rect x="96" y="30" width="8" height="5" rx="2" fill="#fff6c9"/></g>
    ${sign(300, 100, 54, "出租车", "chūzūchē", "#1f4f8a", "#fff", 11)}<rect x="324" y="124" width="5" height="30" fill="#7f8d95"/>`;

  BG.s3 = () => `
    <defs><linearGradient id="g3w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6e7c5"/><stop offset="1" stop-color="#ecd4a0"/></linearGradient></defs>
    <rect width="360" height="220" fill="url(#g3w)"/>
    <g fill="#e2c585" opacity=".55"><circle cx="40" cy="60" r="18"/><circle cx="120" cy="40" r="14"/><circle cx="300" cy="64" r="20"/><circle cx="222" cy="30" r="12"/></g>
    <rect y="112" width="360" height="108" fill="#7b2d26"/><rect y="112" width="360" height="6" fill="#c79a3b"/>
    <g stroke="#69241f" stroke-width="2"><path d="M60 118 V176 M120 118 V176 M180 118 V176 M240 118 V176 M300 118 V176"/></g>
    ${lantern(34, 40, 1.1)}${lantern(110, 28, .9)}${lantern(250, 28, .9)}${lantern(326, 40, 1.1)}
    <rect y="176" width="360" height="44" fill="#4e1d19"/><rect x="40" y="176" width="280" height="44" fill="#a63a31"/><path d="M40 176 H320" stroke="#e9c96d" stroke-width="3"/>
    <g><rect x="110" y="104" width="140" height="52" rx="4" fill="#8b5a33"/><rect x="104" y="98" width="152" height="10" rx="3" fill="#b9814a"/><rect x="110" y="104" width="140" height="4" fill="#d2a066"/><path d="M130 112 V152 M180 112 V152 M230 112 V152" stroke="#6f4525" stroke-width="2"/>
    <circle cx="150" cy="94" r="6" fill="#e9c96d"/><rect x="146" y="98" width="8" height="2" fill="#a07e2a"/></g>
    ${sign(120, 52, 120, "清茶酒店", "Qīngchá jiǔdiàn", "#2a1c18", "#f1d27a", 20)}
    <g><rect x="276" y="80" width="62" height="86" rx="3" fill="#c7ced2" stroke="#7f8d95" stroke-width="3"/><path d="M307 80 V166" stroke="#7f8d95" stroke-width="2"/><circle cx="296" cy="72" r="4" fill="#e9c96d"/></g>
    ${sign(279, 50, 56, "电梯", "diàntī", "#27425f", "#fff", 13)}
    <g><rect x="18" y="148" width="30" height="26" rx="5" fill="#b9814a"/><path d="M33 148 C20 124 24 108 20 98 M33 148 C34 120 36 104 42 92 M33 148 C46 128 52 118 60 112" stroke="#4f9a5c" stroke-width="4" fill="none" stroke-linecap="round"/><g fill="#6fb577"><ellipse cx="20" cy="96" rx="4" ry="8"/><ellipse cx="42" cy="90" rx="4" ry="8"/><ellipse cx="60" cy="110" rx="4" ry="8"/></g></g>`;

  BG.s4 = () => `
    <defs><linearGradient id="g4s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe3b0"/><stop offset="1" stop-color="#fbf1dc"/></linearGradient></defs>
    <rect width="360" height="220" fill="url(#g4s)"/>
    <rect y="40" width="360" height="110" fill="#9c8f82"/><g stroke="rgba(0,0,0,.12)" stroke-width="1.4"><path d="M0 60 H360 M0 80 H360 M0 100 H360 M0 120 H360 M0 140 H360"/><path d="M30 40 V60 M90 60 V80 M150 40 V60 M210 60 V80 M270 40 V60 M330 60 V80 M60 80 V100 M120 100 V120 M180 80 V100 M240 100 V120 M300 80 V100"/></g>
    <path d="M0 24 H360 V54 H0Z" fill="#fff"/><g fill="#d9473f"><path d="M0 24 H30 V54 H0Z M60 24 H90 V54 H60Z M120 24 H150 V54 H120Z M180 24 H210 V54 H180Z M240 24 H270 V54 H240Z M300 24 H330 V54 H300Z"/></g>
    <path d="M0 54 Q15 66 30 54 Q45 66 60 54 Q75 66 90 54 Q105 66 120 54 Q135 66 150 54 Q165 66 180 54 Q195 66 210 54 Q225 66 240 54 Q255 66 270 54 Q285 66 300 54 Q315 66 330 54 Q345 66 360 54" fill="#fff" stroke="#e0d6c0"/>
    ${lantern(26, 96, .8)}${lantern(334, 96, .8)}
    ${sign(130, 70, 100, "包子铺", "bāozi pù", "#2a1c18", "#f1d27a", 20)}
    <g><rect x="12" y="116" width="336" height="40" fill="#b9814a"/><rect x="8" y="110" width="344" height="9" rx="3" fill="#d2a066"/></g>
    <g><g transform="translate(36 70)"><rect width="46" height="38" rx="4" fill="#7a4a24"/><rect x="4" y="4" width="38" height="30" fill="#f6efd8"/><text x="23" y="17" text-anchor="middle" font-size="9" font-weight="700" fill="#27302b" font-family="'Noto Serif SC',serif">饺子 面条</text><text x="23" y="27" text-anchor="middle" font-size="6" fill="#67756f">jiǎozi miàntiáo</text></g></g>
    <g transform="translate(240 70)"><rect width="84" height="38" rx="4" fill="#7a4a24"/><rect x="4" y="4" width="76" height="30" fill="#f6efd8"/><text x="42" y="17" text-anchor="middle" font-size="9" font-weight="700" fill="#27302b" font-family="'Noto Serif SC',serif">豆浆 茶 包子</text><text x="42" y="27" text-anchor="middle" font-size="6" fill="#67756f">dòujiāng chá bāozi</text></g>
    <g><g transform="translate(88 78)"><ellipse cx="22" cy="40" rx="25" ry="6" fill="#d8b878"/><rect x="0" y="22" width="44" height="18" rx="3" fill="#e6c98a"/><ellipse cx="22" cy="22" rx="22" ry="6" fill="#efd8a0"/><rect x="2" y="6" width="40" height="16" rx="3" fill="#e6c98a"/><ellipse cx="22" cy="6" rx="20" ry="5.5" fill="#efd8a0"/><path d="M12 -2 C6 -12 18 -16 12 -28 M24 -2 C18 -12 30 -16 24 -28 M36 -2 C30 -12 42 -16 36 -28" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" opacity=".85" class="qsteam"/></g>
    <g transform="translate(178 86)"><ellipse cx="22" cy="32" rx="25" ry="6" fill="#d8b878"/><rect x="0" y="14" width="44" height="18" rx="3" fill="#e6c98a"/><ellipse cx="22" cy="14" rx="22" ry="6" fill="#efd8a0"/><path d="M12 6 C6 -4 18 -8 12 -20 M30 6 C24 -4 36 -8 30 -20" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" opacity=".85" class="qsteam"/></g></g>
    <rect y="156" width="360" height="64" fill="#cfc2a6"/><g stroke="rgba(0,0,0,.08)" stroke-width="1.4"><path d="M0 178 H360 M0 200 H360 M40 156 V220 M140 156 V220 M240 156 V220 M340 156 V220"/></g>
    <g><rect x="296" y="174" width="26" height="9" rx="3" fill="#8b5a33"/><rect x="300" y="183" width="4" height="16" fill="#8b5a33"/><rect x="314" y="183" width="4" height="16" fill="#8b5a33"/></g>`;

  BG.s5 = () => `
    <defs><linearGradient id="g5c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3c4650"/><stop offset="1" stop-color="#6b7882"/></linearGradient></defs>
    <rect width="360" height="220" fill="url(#g5c)"/>
    <rect width="360" height="16" fill="#2b333b"/><g fill="#fffbe0"><rect x="20" y="5" width="50" height="6" rx="3"/><rect x="110" y="5" width="50" height="6" rx="3"/><rect x="200" y="5" width="50" height="6" rx="3"/><rect x="290" y="5" width="50" height="6" rx="3"/></g>
    <g><rect x="196" y="82" width="164" height="76" fill="#cfd6dc"/><rect x="196" y="82" width="164" height="12" fill="#2f6db0"/><rect x="196" y="140" width="164" height="6" fill="#2f6db0"/>
    <rect x="210" y="98" width="42" height="42" rx="3" fill="#2b333b"/><rect x="214" y="102" width="34" height="38" fill="#f4e7b8"/><path d="M231 102 V140" stroke="#999" stroke-width="1.5"/>
    <rect x="270" y="98" width="42" height="42" rx="3" fill="#2b333b"/><rect x="274" y="102" width="34" height="38" fill="#f4e7b8"/><path d="M291 102 V140" stroke="#999" stroke-width="1.5"/>
    <rect x="326" y="98" width="30" height="42" rx="3" fill="#2b333b"/><rect x="330" y="102" width="22" height="38" fill="#f4e7b8"/></g>
    <g fill="#8e9aa4"><rect x="70" y="16" width="16" height="136"/><rect x="170" y="16" width="14" height="136"/></g>
    <rect x="12" y="26" width="88" height="40" rx="3" fill="#fff" opacity=".95"/><rect x="12" y="26" width="88" height="40" rx="3" fill="none" stroke="#9aa5ab" stroke-width="2"/>
    <circle cx="30" cy="46" r="11" fill="#c5413a"/><text x="30" y="51" text-anchor="middle" font-size="12" font-weight="800" fill="#fff" font-family="sans-serif">2</text>
    <text x="62" y="43" text-anchor="middle" font-size="14" font-weight="700" fill="#22302b" font-family="'Noto Serif SC',serif">西直门</text><text x="62" y="56" text-anchor="middle" font-size="7.5" fill="#67756f" font-family="sans-serif">Xīzhímén · 2号线</text>
    ${sign(110, 30, 74, "请排队", "qǐng páiduì", "#2f6db0", "#fff", 13)}
    <rect y="152" width="360" height="68" fill="#d8d2c2"/><rect y="152" width="360" height="5" fill="#b5ad98"/><rect y="164" width="360" height="6" fill="#f0c53a"/><g stroke="rgba(0,0,0,.07)" stroke-width="1.5"><path d="M0 188 H360 M0 206 H360 M60 170 V220 M180 170 V220 M300 170 V220"/></g>
    <g><rect x="14" y="132" width="52" height="8" rx="3" fill="#6b7882"/><rect x="18" y="140" width="4" height="14" fill="#555"/><rect x="58" y="140" width="4" height="14" fill="#555"/></g>`;

  BG.s6 = () => `
    <defs><linearGradient id="g6w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9edf0"/><stop offset="1" stop-color="#d7dde1"/></linearGradient></defs>
    <rect width="360" height="220" fill="url(#g6w)"/>
    <g fill="#a9c9dd"><path d="M20 120 V60 Q20 30 50 30 Q80 30 80 60 V120Z"/><path d="M110 120 V60 Q110 30 140 30 Q170 30 170 60 V120Z" opacity="0"/></g>
    <g fill="#bfdcee" stroke="#8a97a0" stroke-width="3"><path d="M18 122 V62 Q18 34 46 34 Q74 34 74 62 V122Z"/><path d="M286 122 V62 Q286 34 314 34 Q342 34 342 62 V122Z"/></g>
    <rect x="88" y="14" width="184" height="86" rx="5" fill="#1d2329" stroke="#6b7882" stroke-width="3"/>
    <text x="180" y="29" text-anchor="middle" font-size="10" font-weight="700" fill="#f0a73a" font-family="'Noto Serif SC',serif">车次 · 时间 · 目的地</text>
    <g font-family="'Noto Serif SC',serif" font-size="9.5" fill="#ffc86a" font-weight="700"><text x="98" y="46">S2</text><text x="124" y="46">08:00</text><text x="166" y="46">八达岭长城</text><text x="244" y="46" fill="#ff6b5e">票完</text>
    <text x="98" y="62">S2</text><text x="124" y="62">09:00</text><text x="166" y="62">八达岭长城</text><text x="244" y="62" fill="#7de08b">有票</text>
    <text x="98" y="78">S2</text><text x="124" y="78">10:00</text><text x="166" y="78">八达岭长城</text><text x="244" y="78" fill="#7de08b">有票</text></g>
    <text x="180" y="94" text-anchor="middle" font-size="6.5" fill="#9fb2bd" font-family="sans-serif">Bādálǐng Chángchéng · piào wán / yǒu piào</text>
    <g><rect x="238" y="112" width="116" height="46" rx="4" fill="#fff" opacity=".4" stroke="#7f8d95"/><rect x="230" y="146" width="130" height="14" rx="3" fill="#6b4a2a"/><rect x="230" y="146" width="130" height="4" fill="#8f673a"/></g>
    ${sign(262, 90, 70, "售票处", "shòupiàochù", "#2f6db0", "#fff", 14)}
    <rect y="156" width="360" height="64" fill="#cbc3ad"/><g stroke="rgba(0,0,0,.07)" stroke-width="1.5"><path d="M0 176 H360 M0 198 H360 M50 156 V220 M150 156 V220 M250 156 V220 M350 156 V220"/></g>
    <g transform="translate(20 134)"><rect width="30" height="22" rx="5" fill="#2f8f83"/><rect x="8" y="-6" width="14" height="7" rx="3" fill="none" stroke="#1d5f58" stroke-width="2.5"/></g>`;

  BG.s7 = () => `
    <defs><linearGradient id="g7s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fd0f2"/><stop offset="1" stop-color="#e5f4ef"/></linearGradient></defs>
    <rect width="360" height="220" fill="url(#g7s)"/>${cloud(80, 30, 1)}${cloud(280, 44, .9)}
    <path d="M0 120 Q60 60 130 100 Q180 50 250 96 Q310 56 360 90 V220 H0Z" fill="#8fb89a"/>
    <path d="M0 140 Q80 90 160 126 Q240 80 360 128 V220 H0Z" fill="#6ea383"/>
    <g stroke="#b9a98a" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M70 120 Q100 112 130 108 Q160 100 190 96 Q220 90 250 94" stroke="#c9b794"/></g>
    <g fill="#c9b794" stroke="#a5946f" stroke-width="1.2"><rect x="124" y="98" width="14" height="16"/><rect x="190" y="86" width="14" height="16"/><rect x="244" y="86" width="14" height="16"/></g>
    <g fill="#a5946f"><rect x="122" y="96" width="4" height="4"/><rect x="128" y="96" width="4" height="4"/><rect x="134" y="96" width="4" height="4"/><rect x="188" y="84" width="4" height="4"/><rect x="194" y="84" width="4" height="4"/><rect x="200" y="84" width="4" height="4"/></g>
    <path d="M250 220 L216 196 L270 180 L206 164 L262 150 L210 138" fill="none" stroke="#d8cdb4" stroke-width="22" stroke-linejoin="round"/>
    <g stroke="rgba(0,0,0,.10)" stroke-width="2"><path d="M224 196 L260 186 M214 168 L254 158 M214 142 L250 146"/></g>
    <g fill="#4f8a5c"><circle cx="30" cy="150" r="20"/><circle cx="56" cy="160" r="16"/><circle cx="330" cy="150" r="22"/><circle cx="306" cy="166" r="16"/></g><g fill="#6b4a2a"><rect x="28" y="162" width="5" height="12"/><rect x="328" y="162" width="5" height="12"/></g>
    <rect y="176" width="360" height="44" fill="#a99a7c"/><g stroke="rgba(0,0,0,.09)" stroke-width="1.5"><path d="M0 196 H360 M0 212 H360"/></g>
    <g transform="translate(14 112)"><path d="M0 8 Q36 -18 72 8Z" fill="#d9473f"/><path d="M36 -4 V50" stroke="#7a5a2f" stroke-width="3"/><rect x="2" y="30" width="68" height="8" rx="2" fill="#b9814a"/>
    <g fill="#6fb8e8"><rect x="8" y="14" width="8" height="16" rx="3"/><rect x="20" y="14" width="8" height="16" rx="3"/><rect x="44" y="14" width="8" height="16" rx="3"/><rect x="56" y="14" width="8" height="16" rx="3"/></g><g fill="#fff"><rect x="9" y="12" width="6" height="3"/><rect x="21" y="12" width="6" height="3"/><rect x="45" y="12" width="6" height="3"/><rect x="57" y="12" width="6" height="3"/></g></g>
    ${sign(20, 78, 60, "水", "shuǐ", "#2f6db0", "#fff", 18)}`;

  BG.s8 = () => `
    <defs><linearGradient id="g8s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5b7fc2"/><stop offset=".45" stop-color="#f2a6a0"/><stop offset=".8" stop-color="#ffd9a0"/><stop offset="1" stop-color="#fff0c8"/></linearGradient>
    <radialGradient id="g8sun"><stop offset="0" stop-color="#fff6c8"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient></defs>
    <rect width="360" height="220" fill="url(#g8s)"/><circle cx="250" cy="120" r="70" fill="url(#g8sun)"/><circle cx="250" cy="122" r="22" fill="#fff3b8"/>
    ${cloud(60, 40, 1, .7)}${cloud(300, 28, .8, .6)}
    <g fill="#18222f" opacity=".7"><path d="M60 60 q4 -5 8 0 q4 -5 8 0 q-8 2 -8 6 q0 -4 -8 -6Z" transform="translate(0 0)"/><path d="M96 48 q3 -4 6 0 q3 -4 6 0 q-6 2 -6 5 q0 -3 -6 -5Z"/></g>
    <path d="M0 130 Q50 96 100 118 Q150 80 210 116 Q270 86 330 112 Q350 104 360 108 V220 H0Z" fill="#9c88b8"/>
    <path d="M0 150 Q70 112 140 140 Q210 100 280 138 Q330 118 360 130 V220 H0Z" fill="#6f6a9c"/>
    <path d="M0 170 Q60 136 130 160 Q200 128 270 158 Q320 140 360 150 V220 H0Z" fill="#4a557f"/>
    <path d="M10 164 Q60 138 130 156 Q200 126 270 152 Q320 138 352 146" fill="none" stroke="#d7c7a6" stroke-width="9" stroke-linecap="round"/>
    <path d="M10 160 Q60 134 130 152 Q200 122 270 148 Q320 134 352 142" fill="none" stroke="#efe1c0" stroke-width="3" stroke-dasharray="6 4" stroke-linecap="round"/>
    <g fill="#d7c7a6" stroke="#a5946f" stroke-width="1.2"><rect x="118" y="122" width="20" height="34"/><rect x="206" y="108" width="22" height="38"/><rect x="290" y="116" width="20" height="34"/></g>
    <g fill="#a5946f"><rect x="116" y="119" width="6" height="5"/><rect x="125" y="119" width="6" height="5"/><rect x="134" y="119" width="6" height="5"/><rect x="204" y="105" width="6" height="5"/><rect x="213" y="105" width="6" height="5"/><rect x="222" y="105" width="6" height="5"/><rect x="288" y="113" width="6" height="5"/><rect x="297" y="113" width="6" height="5"/><rect x="306" y="113" width="6" height="5"/></g>
    <g fill="#4a3b35"><rect x="124" y="132" width="8" height="10" rx="4"/><rect x="212" y="120" width="8" height="10" rx="4"/><rect x="296" y="128" width="8" height="10" rx="4"/></g>
    <g><path d="M214 108 V92" stroke="#7a5a2f" stroke-width="2"/><path d="M214 92 L232 97 L214 102Z" fill="#c5413a"/></g>
    <rect y="186" width="360" height="34" fill="#8b8576"/><g stroke="rgba(0,0,0,.18)" stroke-width="1.6"><path d="M0 200 H360 M0 214 H360"/><path d="M30 186 V200 M90 200 V214 M150 186 V200 M210 200 V214 M270 186 V200 M330 200 V214"/></g>
    <g fill="#7a7466"><rect x="0" y="178" width="22" height="10"/><rect x="34" y="178" width="22" height="10"/><rect x="68" y="178" width="22" height="10"/><rect x="102" y="178" width="22" height="10"/><rect x="136" y="178" width="22" height="10"/><rect x="170" y="178" width="22" height="10"/><rect x="204" y="178" width="22" height="10"/><rect x="238" y="178" width="22" height="10"/><rect x="272" y="178" width="22" height="10"/><rect x="306" y="178" width="22" height="10"/><rect x="340" y="178" width="22" height="10"/></g>`;

  function bg(id) {
    const f = BG[id] || BG.s1;
    return `<svg class="qbg" viewBox="0 0 360 220" preserveAspectRatio="xMidYMid slice" aria-hidden="true">${f()}</svg>`;
  }

  // ── карта пути: пейзаж за узлами ──
  function mapBackdrop(w, h) {
    return `<svg class="qmapbg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" aria-hidden="true">
      <defs><linearGradient id="mpg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eaf3ea"/><stop offset=".6" stop-color="#f3eee1"/><stop offset="1" stop-color="#f0dfc0"/></linearGradient></defs>
      <rect width="${w}" height="${h}" rx="22" fill="url(#mpg)"/>
      <g fill="#d6e6d9" opacity=".9"><path d="M0 ${h * 0.82} Q${w * 0.2} ${h * 0.7} ${w * 0.4} ${h * 0.8} T${w * 0.8} ${h * 0.78} T${w} ${h * 0.8} V${h} H0Z"/></g>
      <g fill="#bcd6c4" opacity=".9"><path d="M0 ${h * 0.9} Q${w * 0.25} ${h * 0.8} ${w * 0.5} ${h * 0.9} T${w} ${h * 0.88} V${h} H0Z"/></g>
      <g fill="#fff" opacity=".8"><ellipse cx="${w * 0.2}" cy="${h * 0.1}" rx="26" ry="9"/><ellipse cx="${w * 0.8}" cy="${h * 0.3}" rx="30" ry="10"/><ellipse cx="${w * 0.15}" cy="${h * 0.55}" rx="22" ry="8"/></g>
    </svg>`;
  }

  window.QART = { person, chacha, figure, avatar, avatarOf, bg, mapBackdrop, SKINS, NPC, sign, cloud, lantern };
})();
