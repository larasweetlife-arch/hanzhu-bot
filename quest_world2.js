/* 清越 · «Путешествие по Китаю с 茶茶»: фоны глав 2 (Сиань) и 3 (Чэнду).
   Подключается после quest_world.js и регистрирует темы и ориентиры для сцен s9–s24 через QWORLD.EXT.
   Всё векторное и собирается кодом, картинок нет. */
(() => {
  "use strict";
  const Q = window.QWORLD;
  if (!Q || !Q.EXT) return;
  const { EXT, KINDS, PAL: P } = Q, K = Q.h, W = Q.W, H = Q.H, GY = Q.GY;
  const { plaque, bluesign, roof, ginkgo, pine, lampPost, bike, xcloud, ridge, farMountains, wallOnRidge, skyline, rng, f1, SERIF, RED, RED2, GOLD, GOLD2, YEL, YEL2, A, wallRed, hutongRow } = K;
  const lant = (x, y, s) => A().lantern(f1(x), f1(y), s);
  const steam = (x, y, s) => `<path class="qsteam" d="M${x - 14 * s} ${y} C${x - 26 * s} ${y - 20 * s} ${x - 2 * s} ${y - 28 * s} ${x - 12 * s} ${y - 52 * s} M${x + 12 * s} ${y} C${x} ${y - 20 * s} ${x + 24 * s} ${y - 28 * s} ${x + 14 * s} ${y - 52 * s}" stroke="#fff" stroke-width="${f1(7 * s)}" fill="none" stroke-linecap="round" opacity=".8"/>`;

  // ── палитры ──
  Object.assign(P, {
    s9: { theme: "rail", sky: ["#8fcdea", "#cfe9f3", "#f7f1de"], sun: ["#fffbe0", 1250, 230, 60], far: "#b9cbd6", far2: "#9fb6c4", far3: "#87a2b3", ground: "#d4d6d6", ground2: "#a3a8ab", road: "#5a5f66", ob: ["几号车", "jǐ hào chē"] },
    s10: { theme: "xwall", sky: ["#7fb8e8", "#bfe0ee", "#fbeccb"], sun: ["#fffbe0", 320, 230, 60], far: "#aec7bd", far2: "#93b3a8", far3: "#7a9f94", ob: ["多少钱", "duōshao qián"] },
    s11: { theme: "xsq", sky: ["#6f8fc9", "#f2a885", "#fde0b0"], sun: ["#fff0b8", 1180, 500, 84, true], far: "#c4a0a4", far2: "#aa8590", far3: "#8f6f80", ob: ["几点", "jǐ diǎn"] },
    s12: { theme: "xstreet", sky: ["#ffb98a", "#ffd9a8", "#fff0cf"], sun: ["#fff3c0", 280, 320, 66, true], far: "#d3b79d", far2: "#bd9f86", far3: "#a58a74", ob: ["不要辣", "bú yào là"] },
    s13: { theme: "xroad", sky: ["#8fcdea", "#d3ecee", "#f6efd8"], sun: ["#fffbe0", 1300, 220, 58], far: "#b3c7d2", far2: "#97b0bf", far3: "#7f9aab", ob: ["车站", "chēzhàn"] },
    s14: { theme: "pit", indoor: true, sky: ["#2b2420", "#3b3029", "#52443a"], sun: ["#fff", 0, 0, 0], far: "#6a5646", far2: "#584638", far3: "#483a2e", floor: "#8b765f", ob: ["安静", "ānjìng"] },
    s15: { theme: "night", sky: ["#141a3f", "#2b2a63", "#5a3b6e"], sun: ["#fff7d6", 300, 200, 50], far: "#3b3a6e", far2: "#2d2c5a", far3: "#232249", ground: "#7a7387", ground2: "#4a4558", road: "#33303f", cloud: "#5b5896", nobirds: true, ob: ["便宜点", "piányi diǎn"] },
    s16: { theme: "gate", sky: ["#4d5f9e", "#e99a8f", "#ffd9a2"], sun: ["#fff0b0", 400, 540, 90, true], far: "#a893bd", far2: "#8873a8", far3: "#6f5e94", ob: ["关卡", "guānkǎ"] },
    s17: { theme: "rain", sky: ["#7f8e9b", "#a9b6c0", "#cfd8dc"], sun: ["#fff", 0, 0, 0], far: "#93a7a2", far2: "#7f958f", far3: "#6b827c", ground: "#9aa3a8", ground2: "#6e777c", road: "#454c52", cloud: "#8d9aa4", nobirds: true, pine: "#3c6e55", pine2: "#4d8467", ob: ["出口", "chūkǒu"] },
    s18: { theme: "teahouse", sky: ["#9fd3c4", "#d4ecd8", "#f6efd4"], sun: ["#fffbe0", 1280, 230, 56], far: "#9cc4ae", far2: "#82b098", far3: "#699c84", ob: ["盖碗", "gàiwǎn"] },
    s19: { theme: "hotpot", sky: ["#2a1f4a", "#7a2f55", "#e5775a"], sun: ["#ffd9a0", 300, 520, 70, true], far: "#5a3a62", far2: "#472f55", far3: "#372548", ground: "#8a7368", ground2: "#5e4a44", road: "#3a2f34", cloud: "#8a4a6a", nobirds: true, ob: ["微辣", "wēilà"] },
    s20: { theme: "alley", sky: ["#8fcdea", "#d8eef0", "#f8efd8"], sun: ["#fffbe0", 260, 240, 58], far: "#b3c7c4", far2: "#9bb3b1", far3: "#849f9f", ob: ["转盘", "zhuànpán"] },
    s21: { theme: "stage", indoor: true, sky: ["#4a1210", "#7a1812", "#a3281f"], sun: ["#fff", 0, 0, 0], far: "#6b1a14", far2: "#5a1510", far3: "#4a110d", floor: "#a07044", ob: ["变脸", "biànliǎn"] },
    s22: { theme: "dawn", sky: ["#1b2650", "#7a5a9a", "#f6b9a0"], sun: ["#ffe9b8", 1180, 600, 66, true], far: "#4a4a7a", far2: "#3d3d6a", far3: "#313159", ground: "#8a8a98", ground2: "#5c5c6c", road: "#3a3b48", cloud: "#8a74ad", nobirds: true, ob: ["早班车", "zǎobānchē"] },
    s23: { theme: "bamboo", sky: ["#bfe3cf", "#dff0dc", "#f4f1d8"], sun: ["#fffbe0", 1240, 210, 56], far: "#9cc9ae", far2: "#80b597", far3: "#659f81", ground: "#9a8a68", ground2: "#6e5f44", ob: ["别吵", "bié chǎo"] },
    s24: { theme: "bamboo", sky: ["#bfe3cf", "#e7f2d6", "#fbf0cf"], sun: ["#fff3c0", 1240, 210, 62], far: "#9cc9ae", far2: "#80b597", far3: "#659f81", ground: "#9a8a68", ground2: "#6e5f44", ob: ["喂熊猫", "wèi xióngmāo"] },
  });
  Object.assign(KINDS, {
    s9: ["door", "gate", "crates", "barrier", "door"], s10: ["crates", "barrier", "gate", "door", "crates"], s11: ["gate", "barrier", "door", "crates", "gate"],
    s12: ["crates", "door", "barrier", "gate", "crates"], s13: ["barrier", "gate", "crates", "door", "barrier"], s14: ["gate", "door", "barrier", "crates", "gate"],
    s15: ["crates", "gate", "door", "barrier", "crates"], s16: ["gate", "barrier", "door", "crates", "gate"], s17: ["door", "barrier", "crates", "gate", "door"],
    s18: ["crates", "gate", "barrier", "door", "crates"], s19: ["door", "crates", "gate", "barrier", "door"], s20: ["gate", "crates", "door", "barrier", "gate"],
    s21: ["barrier", "gate", "crates", "door", "barrier"], s22: ["gate", "barrier", "door", "crates", "gate"], s23: ["barrier", "door", "gate", "crates", "barrier"], s24: ["gate", "crates", "door", "barrier", "gate"],
  });

  // ── детали ──
  const stars = (id, n, ymax) => { const R = rng("st" + id); let s = ""; for (let i = 0; i < n; i++) s += `<circle class="qtw" style="animation-delay:-${(R() * 3).toFixed(1)}s" cx="${f1(R() * W)}" cy="${f1(R() * ymax)}" r="${f1(1.2 + R() * 2.2)}" fill="#fff8e0"/>`; return s; };
  const tree = (x, base, s, c1, c2) => `<g transform="translate(${x} ${base}) scale(${s})"><path d="M-8 0 Q-4 -80 -10 -130" stroke="#6b4a2a" stroke-width="16" fill="none" stroke-linecap="round"/><g fill="${c2}"><circle cx="-50" cy="-150" r="52"/><circle cx="52" cy="-154" r="54"/><circle cx="0" cy="-196" r="62"/></g><g fill="${c1}"><circle cx="-30" cy="-168" r="40"/><circle cx="34" cy="-176" r="42"/><circle cx="2" cy="-210" r="46"/></g></g>`;
  const bambooStand = (x, base, s, c1, c2) => {
    let o = `<g transform="translate(${x} ${base}) scale(${s})">`;
    [[-34, 430, 17], [0, 520, 20], [36, 380, 16]].forEach(([dx, hh, w], k) => {
      o += `<rect x="${dx - w / 2}" y="${-hh}" width="${w}" height="${hh}" rx="${w / 2}" fill="${c1}"/>`;
      for (let y = 70 + k * 12; y < hh; y += 92) o += `<rect x="${dx - w / 2 - 2}" y="${-y}" width="${w + 4}" height="7" rx="3" fill="${c2}"/>`;
      for (let j = 0; j < 4; j++) { const ly = -hh + 26 + j * 46, d = j % 2 ? 1 : -1; o += `<path d="M${dx} ${ly} q${d * 44} -16 ${d * 86} 8 q${d * -42} 8 ${d * -86} -8Z" fill="${c1}"/><path d="M${dx} ${ly + 8} q${d * 36} 6 ${d * 70} 30 q${d * -38} -6 ${d * -70} -30Z" fill="${c2}" opacity=".85"/>`; }
    });
    return o + "</g>";
  };
  const warrior = (x, base, s, c) => `<g transform="translate(${x} ${base}) scale(${s})"><rect x="-38" y="-8" width="76" height="12" rx="3" fill="#6d5642"/><rect x="-24" y="-86" width="48" height="80" fill="${c}"/><path d="M-36 -172 H36 L30 -86 H-30Z" fill="${c}"/><path d="M-36 -172 H36 L34 -150 H-34Z" fill="rgba(0,0,0,.14)"/><g stroke="rgba(0,0,0,.2)" stroke-width="3"><path d="M-22 -140 H22 M-24 -122 H24 M-26 -104 H26"/></g><rect x="-48" y="-166" width="14" height="72" rx="7" fill="${c}"/><rect x="34" y="-166" width="14" height="72" rx="7" fill="${c}"/><circle cx="0" cy="-196" r="22" fill="${c}"/><circle cx="0" cy="-226" r="9" fill="${c}"/><path d="M-12 -198 H12" stroke="rgba(0,0,0,.35)" stroke-width="3"/></g>`;
  const panda = (x, base, s, bam) => `<g transform="translate(${x} ${base}) scale(${s})"><ellipse cx="0" cy="-80" rx="84" ry="76" fill="#fff"/><ellipse cx="-56" cy="-18" rx="30" ry="24" fill="#2a2a2e"/><ellipse cx="56" cy="-18" rx="30" ry="24" fill="#2a2a2e"/><ellipse cx="-74" cy="-92" rx="22" ry="46" fill="#2a2a2e" transform="rotate(14 -74 -92)"/><ellipse cx="74" cy="-92" rx="22" ry="46" fill="#2a2a2e" transform="rotate(-14 74 -92)"/><ellipse cx="0" cy="-100" rx="74" ry="14" fill="#2a2a2e" opacity=".9"/><circle cx="0" cy="-170" r="62" fill="#fff"/><circle cx="-50" cy="-218" r="22" fill="#2a2a2e"/><circle cx="50" cy="-218" r="22" fill="#2a2a2e"/><ellipse cx="-26" cy="-172" rx="15" ry="20" fill="#2a2a2e" transform="rotate(20 -26 -172)"/><ellipse cx="26" cy="-172" rx="15" ry="20" fill="#2a2a2e" transform="rotate(-20 26 -172)"/><circle cx="-26" cy="-174" r="6" fill="#fff"/><circle cx="26" cy="-174" r="6" fill="#fff"/><circle cx="-25" cy="-173" r="3" fill="#222"/><circle cx="27" cy="-173" r="3" fill="#222"/><ellipse cx="0" cy="-152" rx="11" ry="8" fill="#2a2a2e"/><path d="M-12 -138 Q0 -128 12 -138" fill="none" stroke="#2a2a2e" stroke-width="3" stroke-linecap="round"/>${bam ? `<rect x="-90" y="-132" width="14" height="110" rx="7" fill="#7fbf6a" transform="rotate(18 -90 -132)"/><path d="M-96 -136 q-50 -20 -72 10 q40 10 72 -10Z" fill="#5ea053"/>` : ""}</g>`;
  const bus = (x, base, s, c, num) => `<g transform="translate(${x} ${base}) scale(${s})"><rect x="0" y="-215" width="430" height="190" rx="24" fill="${c}"/><rect x="0" y="-90" width="430" height="24" fill="rgba(0,0,0,.14)"/>${[0, 1, 2, 3].map((k) => `<rect x="${20 + k * 92}" y="-192" width="80" height="82" rx="8" fill="#cfe9f5"/>`).join("")}<rect x="372" y="-192" width="46" height="150" rx="8" fill="#cfe9f5" stroke="${c}" stroke-width="4"/><path d="M395 -192 V-42" stroke="${c}" stroke-width="4"/><rect x="150" y="-240" width="130" height="34" rx="8" fill="#1d2329"/><text x="215" y="-214" text-anchor="middle" font-size="26" font-weight="800" fill="#ffc86a" font-family="${SERIF}">${num}</text><circle cx="90" cy="-22" r="30" fill="#25282c"/><circle cx="90" cy="-22" r="12" fill="#bbb"/><circle cx="330" cy="-22" r="30" fill="#25282c"/><circle cx="330" cy="-22" r="12" fill="#bbb"/><rect x="2" y="-70" width="16" height="12" rx="4" fill="#fff6c9"/></g>`;
  const umbrella = (x, y, s, c) => `<g transform="translate(${x} ${y}) scale(${s})"><path d="M0 -4 V-70" stroke="#4a3b35" stroke-width="5"/><path d="M-60 -70 Q0 -130 60 -70 Q40 -80 30 -70 Q15 -82 0 -70 Q-15 -82 -30 -70 Q-40 -80 -60 -70Z" fill="${c}"/></g>`;
  const stall = (x, base, w, c1, c2, tall) => `<g><rect x="${x}" y="${base - (tall || 190)}" width="${w}" height="${tall || 190}" fill="#6b4a3a"/>${Array.from({ length: Math.round(w / 40) }, (_, i) => `<path d="M${x + i * 40} ${base - (tall || 190) - 20} h40 v34 q-20 18 -40 0Z" fill="${i % 2 ? c1 : c2}"/>`).join("")}</g>`;
  const crossCam = (x, y, s) => `<g transform="translate(${x} ${y}) scale(${s})"><circle r="46" fill="#fff" stroke="#d93a30" stroke-width="9"/><rect x="-26" y="-14" width="52" height="34" rx="6" fill="#33383d"/><circle cy="3" r="10" fill="#fff"/><rect x="-10" y="-22" width="20" height="9" fill="#33383d"/><path d="M-32 32 L32 -32" stroke="#d93a30" stroke-width="9"/></g>`;
  const mask = (x, y, s, c, kind) => `<g transform="translate(${x} ${y}) scale(${s})"><path d="M0 -60 Q50 -60 50 0 Q50 56 0 70 Q-50 56 -50 0 Q-50 -60 0 -60Z" fill="${c}" stroke="#2a1a14" stroke-width="5"/><path d="M-34 -14 Q-20 -30 -6 -12 M34 -14 Q20 -30 6 -12" fill="none" stroke="#1a1210" stroke-width="7" stroke-linecap="round"/><circle cx="-20" cy="-2" r="6" fill="#fff"/><circle cx="20" cy="-2" r="6" fill="#fff"/><path d="M-20 38 Q0 52 20 38" fill="none" stroke="#1a1210" stroke-width="6" stroke-linecap="round"/>${kind ? `<path d="M0 -58 V-20" stroke="#f4d675" stroke-width="7"/>` : `<path d="M-30 -40 Q0 -54 30 -40" fill="none" stroke="#f4d675" stroke-width="6"/>`}</g>`;
  const teacup = (x, y, s) => `<g transform="translate(${x} ${y}) scale(${s})"><ellipse cx="0" cy="0" rx="46" ry="9" fill="#e9eef0" stroke="#aeb9be" stroke-width="2"/><path d="M-30 -4 Q-32 -34 0 -36 Q32 -34 30 -4 Q0 8 -30 -4Z" fill="#fff" stroke="#aeb9be" stroke-width="2"/><path d="M-36 -46 Q0 -64 36 -46 Q30 -36 0 -38 Q-30 -36 -36 -46Z" fill="#fff" stroke="#aeb9be" stroke-width="2"/><circle cx="0" cy="-57" r="5" fill="#cfd6d8"/><path d="M-20 -12 Q-14 -16 0 -16" stroke="#3e8f6a" stroke-width="5" fill="none" opacity=".7"/></g>`;
  const flagstone = (p, w, y0, hgt) => { let s = `<rect x="0" y="${y0}" width="${w}" height="${hgt}" fill="${p.ground || "#a39a8c"}"/>`; for (let r = 0; r < Math.ceil(hgt / 34); r++) for (let x = (r % 2) * 70; x < w; x += 140) s += `<rect x="${x}" y="${y0 + r * 34 + 2}" width="136" height="30" rx="3" fill="${r % 2 ? "rgba(0,0,0,.05)" : "rgba(255,255,255,.07)"}" stroke="rgba(0,0,0,.2)" stroke-width="2"/>`; return s; };

  // ── небо ──
  EXT.skyx.night = (id) => stars(id, 70, 400);
  EXT.skyx.dawn = (id) => stars(id, 40, 300);
  EXT.skyx.hotpot = (id) => stars(id, 36, 280);
  EXT.skyx.rain = (id) => {
    const R = rng("rn" + id); let s = "";
    for (let ix = 0; ix < 14; ix++) { const jx = R() * 90, jy = R() * 120; for (let iy = -2; iy < 9; iy++) s += `<path d="M${f1(ix * 120 + jx)} ${f1(iy * 120 + jy)} l-9 38" />`; }
    return `<g class="qrain" stroke="rgba(230,240,250,.7)" stroke-width="3" stroke-linecap="round">${s}</g>`;
  };
  const indoorSky = (id, p, deco) => `<defs><linearGradient id="sk${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${p.sky[0]}"/><stop offset="1" stop-color="${p.sky[2]}"/></linearGradient></defs><rect width="${W}" height="${H}" fill="url(#sk${id})"/>${deco}`;
  EXT.sky.pit = (id, p) => indoorSky(id, p, `<g stroke="#1a1512" stroke-width="14" fill="none"><path d="M0 40 L800 160 L1600 40"/><path d="M0 130 L800 190 L1600 130"/><path d="M200 70 V150 M520 120 V176 M1080 120 V176 M1400 70 V150"/></g><rect width="${W}" height="34" fill="#171210"/>` + [260, 620, 980, 1340].map((x) => `<path d="M${x - 26} 34 L${x - 120} 560 H${x + 120} L${x + 26} 34Z" fill="#ffe9b0" opacity=".08"/><rect x="${x - 40}" y="30" width="80" height="14" rx="6" fill="#fff4cc"/>`).join(""));
  EXT.sky.stage = (id, p) => indoorSky(id, p, `<rect y="0" width="${W}" height="${GY}" fill="#5a1510"/>${Array.from({ length: 16 }, (_, i) => `<path d="M${i * 100 + 50} 0 V${GY}" stroke="rgba(0,0,0,.18)" stroke-width="12"/>`).join("")}<rect y="0" width="${W}" height="70" fill="#3d0f0b"/><rect y="64" width="${W}" height="12" fill="${GOLD}"/>` + Array.from({ length: 20 }, (_, i) => `<path d="M${i * 82} 76 q41 44 82 0" fill="#7a1812" stroke="${GOLD2}" stroke-width="3"/>`).join("") + [300, 800, 1300].map((x) => `<path d="M${x - 20} 76 L${x - 150} ${GY} H${x + 150} L${x + 20} 76Z" fill="#ffe9b0" opacity=".07"/>`).join("") + lant(150, 200, 2.4) + lant(1450, 200, 2.4));

  // ── даль ──
  const withMtn = (extra) => (id, p, screens, R, w) => farMountains(id, p, R, w) + extra(id, p, screens, R, w);
  const sk = (op, col) => (id, p, s, R, w) => `<g opacity="${op}">${skyline(R, 0, w, 760, col || p.far2, "rgba(255,255,255,.45)")}</g>`;
  EXT.far.rail = withMtn(sk(0.55));
  EXT.far.xroad = withMtn(sk(0.6));
  EXT.far.dawn = withMtn((id, p, s, R, w) => `<g opacity=".8">${skyline(R, 0, w, 760, p.far3, "rgba(255,214,120,.8)")}</g>`);
  EXT.far.night = withMtn((id, p, s, R, w) => `<g opacity=".9">${skyline(R, 0, w, 760, p.far3, "rgba(255,214,120,.85)")}</g>`);
  EXT.far.rain = withMtn(sk(0.7, "#8a9ca0"));
  EXT.far.hotpot = withMtn((id, p, s, R, w) => `<g opacity=".9">${skyline(R, 0, w, 760, p.far3, "rgba(255,190,110,.8)")}</g>`);
  EXT.far.xwall = withMtn((id, p, s, R, w) => `<g opacity=".85">${wallOnRidge(R, 0, w, 640, 90, 0.55, 3)}</g>`);
  EXT.far.gate = withMtn((id, p, s, R, w) => `<g opacity=".9">${wallOnRidge(R, 0, w, 600, 120, 0.7, 3)}</g>`);
  EXT.far.xsq = withMtn((id, p, s, R, w) => [0, 1].map((i) => `<g opacity=".85">${K.pagoda(f1(500 + i * 1900 + R() * 300), 770, 0.9, "#8a6a64", p.far2, 5)}</g>`).join(""));
  EXT.far.xstreet = EXT.far.xsq;
  EXT.far.alley = withMtn((id, p, s, R, w) => [0, 1].map((i) => `<g opacity=".8">${K.pagoda(f1(700 + i * 1800 + R() * 200), 770, 0.8, "#7c8f8c", p.far2, 4)}</g>`).join(""));
  EXT.far.teahouse = (id, p, screens, R, w) => { let s = farMountains(id, p, R, w); for (let x = 60; x < w; x += 130 + R() * 90) s += bambooStand(f1(x), 780, 0.55 + R() * 0.3, "#7fb08a", "#5f9470"); return s; };
  EXT.far.bamboo = (id, p, screens, R, w) => { let s = farMountains(id, p, R, w); for (let x = 40; x < w; x += 110 + R() * 80) s += bambooStand(f1(x), 780, 0.6 + R() * 0.4, "#86bd8f", "#62a174"); return s; };
  EXT.far.pit = (id, p, screens, R, w) => {
    let s = `<rect y="260" width="${w}" height="${GY - 260}" fill="${p.far2}"/>`;
    for (let x = 0; x < w; x += 70) s += `<path d="M${x} 260 V${GY}" stroke="rgba(0,0,0,.18)" stroke-width="4"/>`;
    for (let r = 0; r < 3; r++) for (let x = 40 + r * 22; x < w; x += 84) s += warrior(f1(x), 470 + r * 90, 0.42 + r * 0.06, ["#9a7752", "#a8845c", "#b69067"][r]);
    return s;
  };
  EXT.far.stage = (id, p, screens, R, w) => `<rect x="0" y="120" width="${w}" height="${GY - 120}" fill="${p.far2}"/>` + Array.from({ length: Math.ceil(w / 340) }, (_, i) => `<g opacity=".55"><path d="M${i * 340 + 40} ${GY} V330 Q${i * 340 + 170} 190 ${i * 340 + 300} 330 V${GY}Z" fill="#3a0f0b" stroke="${GOLD2}" stroke-width="6"/></g>`).join("");

  // ── средний план ──
  const shopRow = (R, x0, x1, base, cols, signs) => {
    let s = "", x = x0, k = 0;
    while (x < x1) {
      const w = 220 + R() * 120, h = 190 + R() * 90;
      s += `<g><rect x="${f1(x)}" y="${f1(base - h)}" width="${f1(w)}" height="${f1(h)}" fill="${["#d9c9a9", "#cfb894", "#e0d2b4"][k % 3]}"/>` +
        `<path d="M${f1(x - 16)} ${f1(base - h)} Q${f1(x + w / 2)} ${f1(base - h - 70)} ${f1(x + w + 16)} ${f1(base - h)} Z" fill="#5d6571"/>` +
        stall(f1(x + 14), base, f1(w - 28), cols[k % cols.length], "#fff", 120) +
        `<rect x="${f1(x + w / 2 - 50)}" y="${f1(base - h + 30)}" width="100" height="44" rx="6" fill="#7a1812" stroke="${GOLD}" stroke-width="3"/><text x="${f1(x + w / 2)}" y="${f1(base - h + 62)}" text-anchor="middle" font-size="30" font-weight="800" fill="#f4d675" font-family="${SERIF}">${signs[k % signs.length]}</text>` +
        lant(f1(x + 20), base - h + 40, 1.2) + `</g>`;
      x += w + 14; k++;
    }
    return s;
  };
  EXT.mid.rail = (id, p, s, R, w) => { let o = ""; for (let x = 200; x < w; x += 520) o += `<g><rect x="${x}" y="150" width="14" height="${GY - 150}" fill="#6a737a"/><rect x="${x - 60}" y="170" width="134" height="10" fill="#6a737a"/><path d="M${x - 480} 190 Q${x - 240} 214 ${x} 190 M${x - 480} 232 Q${x - 240} 252 ${x} 232" stroke="#4a5258" stroke-width="3" fill="none"/></g>`; return o; };
  EXT.mid.xwall = (id, p, s, R, w) => {
    let o = `<rect y="${GY - 330}" width="${w}" height="330" fill="#a79f90"/><rect y="${GY - 350}" width="${w}" height="26" fill="#bdb4a2"/>`;
    for (let x = 0; x < w; x += 84) o += `<rect x="${x + 8}" y="${GY - 392}" width="52" height="46" fill="#a79f90" stroke="#8f8676" stroke-width="3"/>`;
    for (let y = GY - 300; y < GY; y += 36) o += `<path d="M0 ${y} H${w}" stroke="rgba(0,0,0,.14)" stroke-width="3"/>`;
    for (let x = 300; x < w; x += 1100) o += `<g><rect x="${x - 120}" y="${GY - 520}" width="240" height="190" fill="#a79f90"/>${roof(x, GY - 650, 300, 100, "#5d6571", "#46505c")}<rect x="${x - 50}" y="${GY - 480}" width="100" height="110" fill="#7a1812"/></g>`;
    for (let x = 100; x < w; x += 260 + R() * 160) o += tree(f1(x), GY - 8, 0.7 + R() * 0.3, "#5a9a58", "#3e7f48");
    return o;
  };
  EXT.mid.xsq = (id, p, s, R, w) => hutongRow(R, 0, w, GY - 10);
  EXT.mid.xstreet = (id, p, s, R, w) => shopRow(R, 0, w, GY - 10, ["#d9473f", "#2f8f83", "#e8a23a", "#4f86c6"], ["凉皮", "烤肉", "泡馍", "糕点", "饮料"]);
  EXT.mid.hotpot = (id, p, s, R, w) => shopRow(R, 0, w, GY - 10, ["#c5231e", "#e8793a", "#a3281f"], ["火锅", "串串", "川菜", "小面", "茶"]);
  EXT.mid.xroad = (id, p, s, R, w) => { let o = ""; for (let x = 120; x < w; x += 300 + R() * 160) o += tree(f1(x), GY - 12, 1 + R() * 0.3, "#6aa860", "#4a8a48") + lampPost(f1(x + 150), GY - 4); return o; };
  EXT.mid.dawn = (id, p, s, R, w) => { let o = ""; for (let x = 100; x < w; x += 360 + R() * 160) o += tree(f1(x), GY - 12, 1.1, "#3f5f58", "#2e4a48") + `<g>${lampPost(f1(x + 180), GY - 4)}<circle cx="${f1(x + 180)}" cy="${GY - 240}" r="70" fill="#ffd27a" opacity=".22"/></g>`; return o; };
  EXT.mid.night = (id, p, s, R, w) => { let o = ""; for (let x = 0; x < w; x += 430) o += `<g><rect x="${x + 30}" y="${GY - 250}" width="330" height="240" fill="#3c3560"/><path d="M${x + 14} ${GY - 250} H${x + 376} L${x + 350} ${GY - 300} H${x + 40}Z" fill="#7a1812"/>${Array.from({ length: 5 }, (_, i) => `<circle cx="${x + 60 + i * 66}" cy="${GY - 232}" r="9" fill="#ffd36b"/>`).join("")}${lant(x + 80, GY - 190, 1.2)}${lant(x + 310, GY - 190, 1.2)}<rect x="${x + 70}" y="${GY - 150}" width="250" height="140" fill="#ffd89a" opacity=".5"/></g>`; return o; };
  EXT.mid.gate = (id, p, s, R, w) => { let o = `<rect y="${GY - 300}" width="${w}" height="300" fill="#9a9388"/><rect y="${GY - 322}" width="${w}" height="28" fill="#b3ab9b"/>`; for (let x = 0; x < w; x += 80) o += `<rect x="${x + 8}" y="${GY - 362}" width="50" height="44" fill="#9a9388" stroke="#7d766a" stroke-width="3"/>`; for (let y = GY - 270; y < GY; y += 36) o += `<path d="M0 ${y} H${w}" stroke="rgba(0,0,0,.14)" stroke-width="3"/>`; return o; };
  EXT.mid.rain = (id, p, s, R, w) => { let o = ""; for (let x = 0; x < w; x += 360) o += `<rect x="${x + 20}" y="${GY - 300 - (x % 3) * 40}" width="300" height="${300 + (x % 3) * 40}" fill="#8e9ea4"/><g fill="rgba(255,255,255,.35)">${Array.from({ length: 6 }, (_, i) => `<rect x="${x + 40 + (i % 3) * 90}" y="${GY - 270 - (x % 3) * 40 + Math.floor(i / 3) * 70}" width="50" height="40"/>`).join("")}</g>`; for (let x = 150; x < w; x += 380 + R() * 140) o += tree(f1(x), GY - 12, 1.1, "#4f8a64", "#3c6e55"); return o; };
  EXT.mid.teahouse = (id, p, s, R, w) => { let o = ""; for (let x = 100; x < w; x += 640) o += `<g><rect x="${x}" y="${GY - 250}" width="420" height="240" fill="#7a5a44"/>${roof(x + 210, GY - 380, 520, 130, "#59626a", "#434b52")}<g stroke="#4a3426" stroke-width="8"><path d="M${x + 30} ${GY - 250} V${GY - 10} M${x + 210} ${GY - 250} V${GY - 10} M${x + 390} ${GY - 250} V${GY - 10}"/></g>${lant(x + 120, GY - 215, 1.4)}${lant(x + 300, GY - 215, 1.4)}</g>` + bambooStand(f1(x + 520), GY - 8, 0.9, "#6aa878", "#4f8c5f"); return o; };
  EXT.mid.alley = (id, p, s, R, w) => { let o = `<rect y="${GY - 340}" width="${w}" height="340" fill="#8e8a82"/>`; for (let y = GY - 320; y < GY; y += 34) o += `<path d="M0 ${y} H${w}" stroke="rgba(0,0,0,.16)" stroke-width="3"/>`; for (let x = 0; x < w; x += 420) o += `<g><path d="M${x - 20} ${GY - 340} Q${x + 190} ${GY - 450} ${x + 400} ${GY - 340} L${x + 380} ${GY - 300} H${x} Z" fill="#59626a"/><rect x="${x + 150}" y="${GY - 290}" width="80" height="200" rx="40" fill="#4a3b35"/>${lant(x + 80, GY - 260, 1.6)}${lant(x + 320, GY - 260, 1.6)}</g>`; return o; };
  EXT.mid.bamboo = (id, p, s, R, w) => { let o = ""; for (let x = 40; x < w; x += 150 + R() * 100) o += bambooStand(f1(x), GY - 8, 0.9 + R() * 0.5, "#6fae78", "#4c8c5c"); return o; };
  EXT.mid.pit = (id, p, s, R, w) => { let o = `<rect y="${GY - 90}" width="${w}" height="90" fill="#7a6650"/>`; for (let x = 0; x < w; x += 180) o += `<rect x="${x}" y="${GY - 90}" width="14" height="90" fill="#5e4c3a"/>`; for (let r = 0; r < 2; r++) for (let x = 60 + r * 40; x < w; x += 130) o += warrior(x, GY - 90 + r * 20, 0.55 + r * 0.1, r ? "#b0895f" : "#a07c56"); return o; };
  EXT.mid.stage = (id, p, s, R, w) => { let o = ""; for (let x = 120; x < w; x += 520) o += `<g><rect x="${x}" y="150" width="46" height="${GY - 150}" fill="#8a1a14"/><rect x="${x - 10}" y="150" width="66" height="22" fill="${GOLD2}"/>${lant(x + 120, 330, 2.2)}</g>`; return o; };

  // ── земля ──
  const plain = (p, w, hgt) => `<rect x="0" y="${GY}" width="${w}" height="${hgt}" fill="${p.ground}"/>`;
  EXT.ground.rail = (id, p, s, R, w) => `<rect x="0" y="${GY}" width="${w}" height="${H - GY}" fill="${p.ground}"/><rect x="0" y="${GY}" width="${w}" height="10" fill="#e8c93a"/><rect x="0" y="${GY + 10}" width="${w}" height="14" fill="#cfd1d1"/>` + Array.from({ length: Math.ceil(w / 150) }, (_, i) => `<path d="M${i * 150} ${GY + 24} V${H}" stroke="rgba(0,0,0,.1)" stroke-width="3"/>`).join("") + `<rect x="0" y="${GY + 78}" width="${w}" height="${H - GY - 78}" fill="#4d5258"/><path d="M0 ${GY + 98} H${w} M0 ${GY + 126} H${w}" stroke="#8d949a" stroke-width="5"/>`;
  const stoneGround = (id, p, s, R, w) => flagstone(p, w, GY, H - GY) + `<rect x="0" y="${GY}" width="${w}" height="8" fill="rgba(255,255,255,.35)"/>`;
  EXT.ground.xsq = stoneGround; EXT.ground.xstreet = stoneGround; EXT.ground.alley = stoneGround; EXT.ground.teahouse = stoneGround; EXT.ground.night = stoneGround; EXT.ground.hotpot = stoneGround;
  EXT.ground.rain = (id, p, s, R, w) => { let o = flagstone(p, w, GY, H - GY); for (let x = 120; x < w; x += 240 + R() * 200) o += `<ellipse cx="${f1(x)}" cy="${GY + 40 + R() * 60}" rx="${f1(50 + R() * 40)}" ry="9" fill="#cfe0ea" opacity=".6"/>`; return o; };
  EXT.ground.bamboo = (id, p, s, R, w) => `<rect x="0" y="${GY}" width="${w}" height="${H - GY}" fill="${p.ground2}"/><rect x="0" y="${GY}" width="${w}" height="52" fill="${p.ground}"/>` + Array.from({ length: Math.ceil(w / 70) }, (_, i) => `<path d="M${i * 70 + 10} ${GY + 52} q8 -26 14 0 q8 -20 14 0" fill="#6aa860"/>`).join("") + `<rect x="0" y="${GY - 6}" width="${w}" height="14" fill="#7cb86a"/>`;
  EXT.ground.pit = (id, p, s, R, w) => `<rect x="0" y="${GY}" width="${w}" height="${H - GY}" fill="${p.floor}"/><rect x="0" y="${GY}" width="${w}" height="10" fill="#c9b79c"/>` + Array.from({ length: Math.ceil(w / 120) }, (_, i) => `<path d="M${i * 120} ${GY + 10} V${H}" stroke="rgba(0,0,0,.12)" stroke-width="3"/>`).join("") + Array.from({ length: Math.ceil(w / 600) }, (_, i) => `<g><rect x="${i * 600 + 100}" y="${GY - 66}" width="380" height="10" rx="4" fill="#cfe9f5" opacity=".7"/><rect x="${i * 600 + 100}" y="${GY - 56}" width="10" height="56" fill="#555"/><rect x="${i * 600 + 470}" y="${GY - 56}" width="10" height="56" fill="#555"/></g>`).join("");
  EXT.ground.stage = (id, p, s, R, w) => `<rect x="0" y="${GY}" width="${w}" height="${H - GY}" fill="${p.floor}"/><rect x="0" y="${GY}" width="${w}" height="14" fill="#c99a5a"/>` + Array.from({ length: 5 }, (_, i) => `<path d="M0 ${GY + 28 + i * 24} H${w}" stroke="rgba(0,0,0,.14)" stroke-width="3"/>`).join("") + Array.from({ length: Math.ceil(w / 240) }, (_, i) => `<path d="M${i * 240} ${GY + 14} V${H}" stroke="rgba(0,0,0,.1)" stroke-width="3"/>`).join("");

  // ── детали на переднем и заднем плане ──
  const treeDec = (c1, c2, front) => (id, p, screens, R, w, free) => {
    let back = "", fr = "";
    for (let x = 200; x < w - 100; x += 320 + R() * 420) { if (!free(x, 260)) continue; back += R() > 0.5 ? lampPost(f1(x), GY - 2) : tree(f1(x), GY - 4, 0.9 + R() * 0.4, c1, c2); }
    for (let x = 80; x < w; x += 140 + R() * 160) { if (!free(x, 70)) continue; fr += front ? front(x, R) : ""; }
    return { back, front: fr };
  };
  EXT.decor.rail = (id, p, s, R, w, free) => ({ back: "", front: Array.from({ length: Math.floor(w / 700) }, (_, i) => (free(300 + i * 700, 120) ? `<g transform="translate(${300 + i * 700} ${GY})"><rect x="-30" y="-92" width="60" height="92" rx="8" fill="${["#4f86c6", "#c5413a", "#2f8f83"][i % 3]}"/><rect x="-6" y="-120" width="12" height="30" fill="#555"/></g>` : "")).join("") });
  EXT.decor.xwall = treeDec("#5a9a58", "#3e7f48", (x, R) => (R() > 0.55 ? bike(f1(x), GY + 2, ["#2f6db0", "#c5413a", "#e8a23a"][Math.floor(R() * 3)]) : ""));
  EXT.decor.xroad = treeDec("#6aa860", "#4a8a48", null);
  EXT.decor.xsq = treeDec("#e8b630", "#c99a2e", null);
  EXT.decor.xstreet = treeDec("#e8b630", "#c99a2e", (x, R) => (R() > 0.7 ? K.pot(f1(x), GY + 2, ["#d9473f", "#f2a6bd", "#f2c230"][Math.floor(R() * 3)]) : ""));
  EXT.decor.night = treeDec("#4a4a7a", "#34345c", null);
  EXT.decor.gate = (id, p, s, R, w, free) => { let back = ""; for (let x = 220; x < w - 100; x += 520 + R() * 300) if (free(x, 260)) back += pine(f1(x), GY - 4, 1 + R() * 0.4, "#4c8a68", "#366c52"); return { back, front: "" }; };
  EXT.decor.rain = treeDec("#4f8a64", "#3c6e55", (x, R) => (R() > 0.45 ? umbrella(f1(x), GY + 70, 0.9 + R() * 0.4, ["#d9473f", "#2f6db0", "#f2a6bd", "#e8b630"][Math.floor(R() * 4)]) : ""));
  EXT.decor.teahouse = treeDec("#6aa878", "#4f8c5f", null);
  EXT.decor.hotpot = treeDec("#6a4a6a", "#4a3050", (x, R) => (R() > 0.7 ? lant(f1(x), GY - 90, 1.2) : ""));
  EXT.decor.alley = treeDec("#6aa860", "#4a8a48", (x, R) => (R() > 0.6 ? K.pot(f1(x), GY + 2, ["#d9473f", "#f2a6bd", "#f2c230"][Math.floor(R() * 3)]) : ""));
  EXT.decor.dawn = (id, p, s, R, w, free) => ({ back: "", front: Array.from({ length: Math.floor(w / 500) }, (_, i) => (free(260 + i * 500, 100) ? `<rect x="${260 + i * 500}" y="${GY - 8}" width="60" height="14" rx="6" fill="#4a4a60"/>` : "")).join("") });
  EXT.decor.bamboo = (id, p, s, R, w, free) => {
    let back = "", fr = "";
    for (let x = 160; x < w - 100; x += 300 + R() * 360) if (free(x, 240)) back += bambooStand(f1(x), GY - 4, 0.85 + R() * 0.3, "#6fae78", "#4c8c5c");
    for (let x = 80; x < w; x += 110 + R() * 150) if (free(x, 70)) fr += `<path d="M${f1(x - 18)} ${GY + 2} q4 -34 12 -6 q4 -38 12 0 q8 -30 12 6Z" fill="#4f9a48"/>`;
    return { back, front: fr };
  };
  EXT.decor.pit = () => ({ back: "", front: "" });
  EXT.decor.stage = () => ({ back: "", front: "" });

  // экспорт нужного для landmarks (файл quest_world3.js)
  Q.h2 = { lant, steam, stars, tree, bambooStand, warrior, panda, bus, umbrella, stall, crossCam, mask, teacup, flagstone };
})();
