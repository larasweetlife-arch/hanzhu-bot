/* 清越 · «Путешествие по Китаю с 茶茶»: ориентиры сцен 9–24 и карты глав 2–3 (подключается после quest_world2.js). */
(() => {
  "use strict";
  const Q = window.QWORLD;
  if (!Q || !Q.h2) return;
  const { EXT } = Q, K = Q.h, X = Q.h2, W = Q.W, GY = Q.GY;
  const { plaque, bluesign, roof, bike, xcloud, ridge, wallOnRidge, rng, f1, SERIF, RED, RED2, GOLD, GOLD2, A, pagoda } = K;
  const { lant, steam, tree, bambooStand, warrior, panda, bus, umbrella, crossCam, mask, teacup } = X;
  const L = EXT.landmark;

  // ── глава 2 · Сиань ──
  // s9: перрон скоростного поезда
  L.s9 = () => {
    const train = `<g transform="translate(560 ${GY - 28})"><path d="M0 -190 H760 Q860 -190 900 -120 L930 -30 H0Z" fill="#f4f7f8"/><path d="M0 -92 H910 L930 -62 H0Z" fill="#2f6db0"/><path d="M0 -62 H930 V-46 H0Z" fill="#c5413a"/>
      ${[0, 1, 2, 3, 4, 5].map((k) => `<rect x="${28 + k * 120}" y="-160" width="86" height="54" rx="12" fill="#2b3a4a"/>`).join("")}
      <path d="M760 -176 Q840 -176 872 -122 H760Z" fill="#2b3a4a"/>
      <rect x="760" y="-176" width="8" height="150" fill="#2f6db0" opacity=".0"/>
      <g><rect x="600" y="-170" width="86" height="140" rx="10" fill="#d7dee2" stroke="#9aa5ab" stroke-width="5"/><path d="M643 -170 V-30" stroke="#9aa5ab" stroke-width="4"/></g>
      <rect x="0" y="-30" width="930" height="20" fill="#3b4048"/>${[110, 330, 560, 780].map((x) => `<circle cx="${x}" cy="-8" r="22" fill="#2a2d33"/>`).join("")}</g>`;
    return `<g><rect x="500" y="${GY - 520}" width="1040" height="26" fill="#e8ecee"/><rect x="500" y="${GY - 494}" width="1040" height="12" fill="#2f6db0"/>${[520, 1010, 1500].map((x) => `<rect x="${x - 10}" y="${GY - 494}" width="20" height="470" fill="#8b949a"/>`).join("")}
      ${train}${bluesign(1000, GY - 360, 190, "05", "chēxiāng", "#1f4f8a", 60)}
      <g><rect x="700" y="${GY - 450}" width="440" height="84" rx="10" fill="#1d2329"/><text x="920" y="${GY - 402}" text-anchor="middle" font-size="42" font-weight="800" fill="#ffc86a" font-family="${SERIF}">G87 → 西安</text><text x="920" y="${GY - 376}" text-anchor="middle" font-size="22" fill="#9fb2bd" font-family="sans-serif">Xī'ān</text></g>
      <g transform="translate(1320 ${GY})"><rect x="-34" y="-96" width="68" height="96" rx="10" fill="#d9473f"/><rect x="-10" y="-130" width="20" height="38" rx="8" fill="none" stroke="#7a2a26" stroke-width="8"/><circle cx="-18" cy="-8" r="8" fill="#222"/><circle cx="18" cy="-8" r="8" fill="#222"/></g></g>`;
  };

  // s10: городская стена и прокат велосипедов
  L.s10 = () => `<g>
    <rect x="520" y="${GY - 330}" width="980" height="330" fill="#a79f90"/>${Array.from({ length: 9 }, (_, i) => `<path d="M520 ${GY - 300 + i * 36} H1500" stroke="rgba(0,0,0,.14)" stroke-width="3"/>`).join("")}
    ${Array.from({ length: 12 }, (_, i) => `<rect x="${520 + i * 84}" y="${GY - 376}" width="52" height="46" fill="#a79f90" stroke="#8f8676" stroke-width="3"/>`).join("")}
    <path d="M610 ${GY} V${GY - 200} Q710 ${GY - 330} 810 ${GY - 200} V${GY}Z" fill="#2c1a14"/>
    <rect x="590" y="${GY - 560}" width="240" height="190" fill="#a79f90"/>${roof(710, GY - 680, 330, 110, "#5d6571", "#46505c")}${plaque(610, GY - 540, 200, "城墙", "chéngqiáng", 46)}
    <g><rect x="900" y="${GY - 240}" width="560" height="26" rx="6" fill="#c5413a"/>${Array.from({ length: 14 }, (_, i) => `<path d="M${900 + i * 40} ${GY - 214} h40 v28 q-20 18 -40 0Z" fill="${i % 2 ? "#fff" : "#c5413a"}"/>`).join("")}
      <rect x="1060" y="${GY - 170}" width="240" height="170" rx="8" fill="#b9814a"/><rect x="1080" y="${GY - 150}" width="200" height="86" fill="#243b2f"/><text x="1180" y="${GY - 112}" text-anchor="middle" font-size="40" font-weight="800" fill="#f4f2ec" font-family="${SERIF}">20元/小时</text><text x="1180" y="${GY - 80}" text-anchor="middle" font-size="22" fill="#cfe0d0" font-family="sans-serif">20 yuán / xiǎoshí</text>
      ${bike(940, GY, "#e8b630")}${bike(1360, GY, "#2f6db0")}${bike(1440, GY, "#2f8f83")}${plaque(1040, GY - 330, 280, "租车", "zūchē", 52)}</g></g>`;

  // s11: Колокольная башня
  L.s11 = () => `<g>
    <rect x="560" y="${GY - 200}" width="640" height="200" fill="#9a9488" stroke="#7a7466" stroke-width="5"/>${Array.from({ length: 5 }, (_, i) => `<path d="M560 ${GY - 160 + i * 36} H1200" stroke="rgba(0,0,0,.14)" stroke-width="3"/>`).join("")}
    <path d="M800 ${GY} V${GY - 120} Q880 ${GY - 190} 960 ${GY - 120} V${GY}Z" fill="#2c1a14"/>
    <rect x="610" y="${GY - 340}" width="540" height="140" fill="#a3281f"/>${Array.from({ length: 6 }, (_, i) => `<rect x="${640 + i * 86}" y="${GY - 318}" width="56" height="96" fill="#4a1d14"/>`).join("")}
    ${roof(880, GY - 430, 640, 120, "#2f8f7a", "#1f6a5a")}
    <rect x="720" y="${GY - 560}" width="320" height="130" fill="#a3281f"/>${Array.from({ length: 4 }, (_, i) => `<rect x="${742 + i * 74}" y="${GY - 540}" width="48" height="84" fill="#4a1d14"/>`).join("")}
    ${roof(880, GY - 640, 460, 110, "#2f8f7a", "#1f6a5a")}<path d="M880 ${GY - 650} V${GY - 730}" stroke="${GOLD}" stroke-width="8"/><circle cx="880" cy="${GY - 742}" r="16" fill="${GOLD}"/>
    ${plaque(790, GY - 410, 180, "钟楼", "Zhōnglóu", 52)}
    <g transform="translate(1290 ${GY})"><rect x="-70" y="-190" width="140" height="130" rx="30" fill="#b3261e" stroke="${GOLD}" stroke-width="8"/><ellipse cx="0" cy="-190" rx="70" ry="16" fill="#e9c96d"/><path d="M-60 -60 L-90 0 M60 -60 L90 0" stroke="#4a3b35" stroke-width="10" stroke-linecap="round"/><path d="M-50 -250 L-10 -200 M50 -250 L10 -200" stroke="#8a5a2f" stroke-width="9" stroke-linecap="round"/></g>
    <g><rect x="1090" y="${GY - 340}" width="270" height="110" rx="10" fill="#1d2329"/><text x="1225" y="${GY - 280}" text-anchor="middle" font-size="46" font-weight="800" fill="#ffc86a" font-family="${SERIF}">19:30 表演</text><text x="1225" y="${GY - 250}" text-anchor="middle" font-size="22" fill="#9fb2bd" font-family="sans-serif">biǎoyǎn</text></g>
    ${[560, 700, 1060, 1200].map((x) => `<g><rect x="${x - 5}" y="${GY - 70}" width="10" height="70" fill="#8a949a"/><circle cx="${x}" cy="${GY - 74}" r="9" fill="${GOLD}"/></g>`).join("")}<path d="M560 ${GY - 52} Q630 ${GY - 30} 700 ${GY - 52} M1060 ${GY - 52} Q1130 ${GY - 30} 1200 ${GY - 52}" fill="none" stroke="#c5413a" stroke-width="8"/></g>`;

  // s12: Мусульманский квартал
  L.s12 = () => `<g>${K.pailou(760, GY - 6, 1.05, { text: "回民街" })}
    <path d="M520 ${GY - 480} Q900 ${GY - 400} 1500 ${GY - 480}" fill="none" stroke="#7a5a2f" stroke-width="5"/>${[600, 760, 920, 1080, 1240, 1400].map((x) => lant(x, GY - 400 + Math.abs(x - 960) * 0.12, 1.3)).join("")}
    <g><rect x="1060" y="${GY - 140}" width="420" height="30" rx="8" fill="#d2a066"/><rect x="1076" y="${GY - 110}" width="388" height="110" fill="#b9814a"/><rect x="1100" y="${GY - 250}" width="150" height="110" rx="10" fill="#2a2a2e"/><rect x="1110" y="${GY - 222}" width="130" height="18" fill="#e8793a" class="qglow"/>
      ${Array.from({ length: 6 }, (_, i) => `<path d="M${1118 + i * 20} ${GY - 270} v34" stroke="#c5842f" stroke-width="6"/>`).join("")}${steam(1175, GY - 270, 1)}${steam(1320, GY - 150, 0.9)}
      <ellipse cx="1350" cy="${GY - 150}" rx="60" ry="14" fill="#e9eef0"/><path d="M1290 ${GY - 150} Q1350 ${GY - 70} 1410 ${GY - 150}Z" fill="#fff" stroke="#aeb9be" stroke-width="3"/>
      ${plaque(1100, GY - 400, 330, "羊肉串", "yángròuchuàn", 52)}</g>
    <g transform="translate(580 ${GY})"><rect x="-60" y="-110" width="120" height="110" fill="#d9c9a9"/><path d="M-76 -110 H76 L56 -150 H-56Z" fill="#c5413a"/><text x="0" y="-62" text-anchor="middle" font-size="34" font-weight="800" fill="#7a1812" font-family="${SERIF}">凉皮</text></g></g>`;

  // s13: автобусная остановка в Сиане
  L.s13 = () => `<g>${bus(520, GY - 8, 1.7, "#2f8f83", "5路")}
    <g transform="translate(1250 ${GY})"><rect x="-8" y="-420" width="16" height="420" fill="#8b949a"/>${bluesign(-130, -520, 260, "钟楼站", "Zhōnglóu zhàn", "#1f4f8a", 50)}<rect x="-130" y="-452" width="260" height="120" rx="8" fill="#fff" stroke="#8b949a" stroke-width="5"/>
      <text x="0" y="-395" text-anchor="middle" font-size="40" font-weight="800" fill="#22302b" font-family="${SERIF}">5路 · 6路</text><text x="0" y="-360" text-anchor="middle" font-size="22" fill="#67756f" font-family="sans-serif">wǔ lù · liù lù</text></g>
    <g><rect x="1120" y="${GY - 250}" width="120" height="160" rx="10" fill="#33383d"/><rect x="1136" y="${GY - 236}" width="88" height="88" fill="#fff"/><g fill="#22302b">${[0, 1, 2, 3, 4].flatMap((r) => [0, 1, 2, 3, 4].map((c) => ((r * 3 + c * 5) % 4 < 2 ? `<rect x="${1142 + c * 16}" y="${-230 + GY + r * 16}" width="12" height="12"/>` : ""))).join("")}</g><text x="1180" y="${GY - 120}" text-anchor="middle" font-size="26" font-weight="800" fill="#fff" font-family="${SERIF}">扫码</text></g></g>`;

  // s14: музей терракотовой армии
  L.s14 = () => `<g>${plaque(780, GY - 600, 480, "兵马俑", "Bīngmǎyǒng", 70)}
    <g>${[0, 1, 2, 3, 4].map((i) => warrior(f1(640 + i * 190), GY - 6, 1.55, "#a8845c")).join("")}</g>
    <g>${[0, 1, 2].map((i) => warrior(f1(740 + i * 290), GY + 30, 1.1, "#b69067")).join("")}</g>
    <rect x="500" y="${GY - 110}" width="1000" height="12" rx="5" fill="#cfe9f5" opacity=".75"/><g fill="#555">${[500, 760, 1020, 1280, 1490].map((x) => `<rect x="${x - 5}" y="${GY - 100}" width="10" height="100"/>`).join("")}</g>
    <g>${crossCam(1380, GY - 300, 1.5)}${plaque(1250, GY - 220, 260, "禁止闪光", "jìnzhǐ shǎnguāng", 40)}</g></g>`;

  // s15: ночной рынок
  L.s15 = () => `<g>
    <path d="M500 ${GY - 520} Q1000 ${GY - 430} 1520 ${GY - 520}" fill="none" stroke="#7a5a2f" stroke-width="5"/>${Array.from({ length: 16 }, (_, i) => `<circle cx="${520 + i * 66}" cy="${GY - 515 + Math.sin((i / 15) * Math.PI) * 74}" r="11" fill="#ffd36b" class="qglow"/>`).join("")}
    <rect x="600" y="${GY - 360}" width="820" height="360" fill="#3c3560"/><path d="M570 ${GY - 360} H1450 L1410 ${GY - 430} H610Z" fill="#c5231e"/>${Array.from({ length: 16 }, (_, i) => `<path d="M${590 + i * 54} ${GY - 360} h54 v32 q-27 20 -54 0Z" fill="${i % 2 ? "#fff" : "#e8793a"}"/>`).join("")}
    <rect x="640" y="${GY - 200}" width="740" height="40" rx="8" fill="#b9814a"/><rect x="660" y="${GY - 160}" width="700" height="160" fill="#8b5a33"/>
    ${[0, 1, 2, 3].map((i) => `<g transform="translate(${720 + i * 160} ${GY - 340})"><line x1="0" y1="0" x2="0" y2="40" stroke="#7a5a2f" stroke-width="4"/><path d="M0 40 q-26 6 -26 34 q10 10 -4 40 q30 16 30 -4 q30 22 40 -12 q-8 -30 6 -44 q-14 -22 -46 -14Z" fill="${["#d9473f", "#2f8f83", "#e8a23a", "#7a4aa8"][i]}" opacity=".92"/></g>`).join("")}
    ${[0, 1, 2].map((i) => `<g transform="translate(${760 + i * 230} ${GY - 270})"><rect width="120" height="70" rx="6" fill="#d9473f"/><text x="60" y="52" text-anchor="middle" font-size="50" font-weight="900" fill="#f4d675" font-family="${SERIF}">福</text></g>`).join("")}
    ${plaque(930, GY - 520, 280, "夜市", "yèshì", 56)}
    <g transform="translate(1200 ${GY - 200})"><rect x="0" y="-70" width="150" height="62" fill="#fff"/><text x="75" y="-24" text-anchor="middle" font-size="38" font-weight="800" fill="#c5231e" font-family="${SERIF}">¥50</text><path d="M20 -30 L130 -52" stroke="#c5231e" stroke-width="4" opacity="0"/></g>
    ${lant(560, GY - 320, 1.8)}${lant(1460, GY - 320, 1.8)}</g>`;

  // s16: ворота Юннинмэнь
  L.s16 = () => `<g>
    <rect x="520" y="${GY - 300}" width="1000" height="300" fill="#9a9388"/>${Array.from({ length: 12 }, (_, i) => `<rect x="${520 + i * 84}" y="${GY - 344}" width="52" height="44" fill="#9a9388" stroke="#7d766a" stroke-width="3"/>`).join("")}
    <path d="M770 ${GY} V${GY - 190} Q890 ${GY - 330} 1010 ${GY - 190} V${GY}Z" fill="#2c1a14"/>
    <rect x="640" y="${GY - 560}" width="500" height="230" fill="#a3281f"/>${Array.from({ length: 5 }, (_, i) => `<rect x="${672 + i * 92}" y="${GY - 520}" width="56" height="86" fill="#4a1d14"/>`).join("")}
    ${roof(890, GY - 650, 640, 120, "#59626a", "#434b52")}<rect x="780" y="${GY - 720}" width="220" height="80" fill="#a3281f"/>${roof(890, GY - 780, 360, 90, "#59626a", "#434b52")}
    ${plaque(780, GY - 480, 220, "永宁门", "Yǒngníngmén", 50)}
    ${[600, 1180].map((x, i) => `<g transform="translate(${x} ${GY})"><rect x="-6" y="-300" width="12" height="300" fill="#7a5a2f"/><g class="qflag" style="transform-origin:${x}px ${GY - 280}px"><path d="M6 -296 H130 V-210 H6Z" fill="${i ? "#2f6db0" : "#c8302a"}"/><text x="68" y="-238" text-anchor="middle" font-size="46" font-weight="900" fill="#f4d675" font-family="${SERIF}">唐</text></g></g>`).join("")}
    <g transform="translate(1330 ${GY})"><rect x="-70" y="-150" width="140" height="110" rx="26" fill="#b3261e" stroke="${GOLD}" stroke-width="8"/><ellipse cx="0" cy="-150" rx="70" ry="14" fill="#e9c96d"/><path d="M-56 -40 L-84 0 M56 -40 L84 0" stroke="#4a3b35" stroke-width="10" stroke-linecap="round"/></g></g>`;

  // ── глава 3 · Чэнду ──
  // s17: выход из метро под дождём
  L.s17 = () => `<g>
    <path d="M560 ${GY} V${GY - 380} H1150 V${GY}Z" fill="#7f8d95" opacity=".0"/>
    <path d="M540 ${GY - 330} Q860 ${GY - 480} 1180 ${GY - 330} L1150 ${GY - 290} Q860 ${GY - 420} 570 ${GY - 290}Z" fill="#bfe0f1" stroke="#6f7d85" stroke-width="8"/>
    ${[580, 860, 1140].map((x) => `<rect x="${x - 10}" y="${GY - 330}" width="20" height="330" fill="#6f7d85"/>`).join("")}
    <path d="M600 ${GY} H1120 L1060 ${GY + 70} H660Z" fill="#454c52"/>${Array.from({ length: 5 }, (_, i) => `<path d="M${640 + i * 12} ${GY + i * 14} H${1080 - i * 12}" stroke="#7f8d95" stroke-width="6"/>`).join("")}
    ${bluesign(720, GY - 560, 300, "出口 B", "chūkǒu B", "#1f4f8a", 62)}
    <g transform="translate(1290 ${GY - 330})"><circle r="70" fill="#fff" stroke="#c5231e" stroke-width="12"/><text y="14" text-anchor="middle" font-size="44" font-weight="900" fill="#c5231e" font-family="${SERIF}">地铁</text></g>
    ${umbrella(1180, GY, 1.6, "#d9473f")}${umbrella(1290, GY, 1.4, "#e8b630")}${umbrella(1400, GY, 1.5, "#2f6db0")}</g>`;

  // s18: чайный дом
  L.s18 = () => `<g>
    <rect x="560" y="${GY - 320}" width="900" height="320" fill="#7a5a44"/>${roof(1010, GY - 460, 1040, 150, "#59626a", "#434b52")}
    <g stroke="#4a3426" stroke-width="12">${[600, 840, 1080, 1320, 1440].map((x) => `<path d="M${x} ${GY - 320} V${GY}"/>`).join("")}</g>
    <rect x="620" y="${GY - 300}" width="1000" height="0" fill="none"/>
    ${plaque(880, GY - 300, 260, "茶馆", "cháguǎn", 60)}${lant(640, GY - 230, 1.8)}${lant(1380, GY - 230, 1.8)}
    ${[0, 1].map((i) => `<g transform="translate(${700 + i * 520} ${GY})"><rect x="-80" y="-120" width="160" height="14" rx="6" fill="#b9814a"/><rect x="-70" y="-106" width="12" height="106" fill="#8b5a33"/><rect x="58" y="-106" width="12" height="106" fill="#8b5a33"/>${teacup(0, -122, 1.2)}</g>`).join("")}
    <g transform="translate(1040 ${GY})"><path d="M-70 -30 Q-70 -110 0 -110 Q70 -110 70 -30Z" fill="#8a5a3a"/><path d="M60 -80 Q150 -120 180 -170" stroke="#8a5a3a" stroke-width="16" fill="none" stroke-linecap="round"/><rect x="-60" y="-34" width="120" height="14" rx="6" fill="#6b4a2a"/>${steam(180, -176, 0.8)}</g>
    ${bambooStand(1490, GY - 8, 0.9, "#6aa878", "#4f8c5f")}</g>`;

  // s19: хот-пот
  L.s19 = () => `<g>
    <rect x="540" y="${GY - 400}" width="960" height="400" fill="#7a1812"/><rect x="540" y="${GY - 420}" width="960" height="30" fill="${GOLD}"/>
    <rect x="600" y="${GY - 260}" width="840" height="200" fill="#ffd89a" opacity=".55"/>${[0, 1, 2].map((i) => `<path d="M${860 + i * 0} ${GY - 260}"/>`).join("")}<path d="M1020 ${GY - 260} V${GY - 60}" stroke="${GOLD2}" stroke-width="6"/>
    ${plaque(830, GY - 590, 380, "火锅", "huǒguō", 72)}${lant(580, GY - 330, 2.2)}${lant(1460, GY - 330, 2.2)}
    <g transform="translate(1020 ${GY - 40})"><ellipse cx="0" cy="0" rx="200" ry="40" fill="#5a3a2a"/><ellipse cx="0" cy="-30" rx="170" ry="38" fill="#2a2024"/><path d="M0 -68 A85 38 0 0 0 0 8 A85 38 0 0 1 0 -68Z" fill="#d9231a"/><path d="M0 -68 A85 38 0 0 1 0 8 A85 38 0 0 0 0 -68Z" fill="#f6e9c4" opacity="0"/><path d="M0 -68 Q-60 -30 0 8 Q60 -30 0 -68" fill="none" stroke="#f1d27a" stroke-width="0"/>
      <ellipse cx="85" cy="-30" rx="85" ry="38" fill="#f0e7c8" opacity=".9"/><ellipse cx="-85" cy="-30" rx="85" ry="38" fill="#c5231e"/>${[[-120, -34], [-80, -22], [-60, -42], [-100, -48]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="7" fill="#7a0f0a"/>`).join("")}
      ${steam(-80, -60, 1.2)}${steam(90, -60, 1.1)}</g>
    ${[0, 1].map((i) => `<g transform="translate(${660 + i * 640} ${GY})"><ellipse cx="0" cy="-30" rx="60" ry="14" fill="#e9eef0"/><path d="M-50 -34 q50 -40 100 0Z" fill="#c5413a"/><circle cx="-20" cy="-52" r="10" fill="#e8793a"/><circle cx="14" cy="-56" r="10" fill="#d9231a"/></g>`).join("")}</g>`;

  // s20: переулок Куанчжай, сахарные картинки
  L.s20 = () => `<g>
    <rect x="520" y="${GY - 330}" width="1000" height="330" fill="#8e8a82"/>${Array.from({ length: 9 }, (_, i) => `<path d="M520 ${GY - 300 + i * 36} H1520" stroke="rgba(0,0,0,.16)" stroke-width="3"/>`).join("")}
    <path d="M500 ${GY - 330} Q1010 ${GY - 480} 1540 ${GY - 330} L1510 ${GY - 290} H530Z" fill="#59626a"/>${plaque(780, GY - 560, 460, "宽窄巷子", "Kuānzhǎi xiàngzi", 56)}${lant(580, GY - 270, 2)}${lant(1450, GY - 270, 2)}
    <g transform="translate(900 ${GY - 220})"><g class="qspin" style="transform-origin:0px 0px"><circle r="150" fill="#fff6dc" stroke="#7a4a24" stroke-width="12"/>${Array.from({ length: 8 }, (_, i) => `<path d="M0 0 L${f1(Math.cos((i / 8) * 6.2832) * 140)} ${f1(Math.sin((i / 8) * 6.2832) * 140)}" stroke="#7a4a24" stroke-width="5"/>`).join("")}${["龙", "凤", "兔", "猴", "鱼", "猪", "鸡", "鼠"].map((c, i) => `<text x="${f1(Math.cos(((i + 0.5) / 8) * 6.2832) * 98)}" y="${f1(Math.sin(((i + 0.5) / 8) * 6.2832) * 98 + 14)}" text-anchor="middle" font-size="40" font-weight="800" fill="${i % 2 ? "#c5231e" : "#2f6db0"}" font-family="${SERIF}">${c}</text>`).join("")}</g>
      <circle r="18" fill="#7a4a24"/><path d="M0 -158 L-18 -196 H18Z" fill="#c5231e"/></g>
    <g><rect x="700" y="${GY - 80}" width="400" height="26" rx="8" fill="#b9814a"/><rect x="720" y="${GY - 56}" width="360" height="56" fill="#8b5a33"/></g>
    <g transform="translate(1250 ${GY})">${[0, 1, 2].map((i) => `<g transform="translate(${i * 70} 0)"><path d="M0 0 V-200" stroke="#7a5a2f" stroke-width="7"/><path d="M0 -200 q-34 -20 -24 -58 q22 -10 24 20 q4 -34 28 -36 q10 30 -4 56 q-12 26 -24 18Z" fill="#e8a23a" opacity=".92"/></g>`).join("")}</g>
    ${plaque(1170, GY - 420, 240, "糖画", "tánghuà", 56)}</g>`;

  // s21: сцена сычуаньской оперы
  L.s21 = () => `<g>
    <rect x="520" y="${GY - 20}" width="1000" height="20" fill="#c99a5a"/>
    <path d="M520 ${GY - 20} V${GY - 600} Q700 ${GY - 560} 760 ${GY - 330} Q720 ${GY - 150} 640 ${GY - 20}Z" fill="#8a1210" stroke="${GOLD}" stroke-width="6"/>
    <path d="M1520 ${GY - 20} V${GY - 600} Q1340 ${GY - 560} 1280 ${GY - 330} Q1320 ${GY - 150} 1400 ${GY - 20}Z" fill="#8a1210" stroke="${GOLD}" stroke-width="6"/>
    <rect x="520" y="${GY - 640}" width="1000" height="60" fill="#5a1510" stroke="${GOLD}" stroke-width="6"/>${plaque(850, GY - 636, 340, "川剧", "chuānjù", 50)}
    <rect x="780" y="${GY - 560}" width="480" height="420" fill="#c33a30" opacity=".35"/>
    ${mask(850, GY - 380, 1.3, "#d9231a", 0)}${mask(1010, GY - 380, 1.3, "#2f6db0", 1)}${mask(1170, GY - 380, 1.3, "#f0c53a", 0)}${mask(1330, GY - 330, 1.0, "#2a2a2e", 1)}
    <path d="M640 ${GY - 20} L760 ${GY - 600} H1280 L1400 ${GY - 20}Z" fill="#ffe9b0" opacity=".1"/></g>`;

  // s22: ранний автобус на рассвете
  L.s22 = () => `<g>${bus(520, GY - 8, 1.7, "#c5413a", "9路")}
    <g transform="translate(1270 ${GY})"><rect x="-8" y="-420" width="16" height="420" fill="#8b949a"/>${bluesign(-140, -520, 280, "早班车", "zǎobānchē", "#1f4f8a", 54)}<rect x="-140" y="-452" width="280" height="130" rx="8" fill="#1d2329"/><text x="0" y="-384" text-anchor="middle" font-size="62" font-weight="800" fill="#ffc86a" font-family="sans-serif">5:30</text><text x="0" y="-346" text-anchor="middle" font-size="26" fill="#9fb2bd" font-family="${SERIF}">首班车</text></g>
</g>`;

  // s23: вход на базу панд
  L.s23 = () => `<g>
    <rect x="590" y="${GY - 360}" width="40" height="360" fill="#8a5a2f"/><rect x="1130" y="${GY - 360}" width="40" height="360" fill="#8a5a2f"/>
    <rect x="570" y="${GY - 400}" width="620" height="50" rx="10" fill="#6b4a2a"/>${roof(880, GY - 500, 720, 120, "#2f7a6a", "#1f5f56")}
    ${plaque(700, GY - 340, 360, "熊猫基地", "xióngmāo jīdì", 60)}
    <g transform="translate(1290 ${GY})"><rect x="-8" y="-320" width="16" height="320" fill="#8b949a"/><rect x="-130" y="-420" width="260" height="130" rx="12" fill="#2f8f83" stroke="#fff" stroke-width="6"/><text x="0" y="-348" text-anchor="middle" font-size="54" font-weight="800" fill="#fff" font-family="${SERIF}">请安静</text><text x="0" y="-312" text-anchor="middle" font-size="26" fill="#e6f5ef" font-family="sans-serif">qǐng ānjìng</text></g>
    ${panda(1480, GY - 6, 0.7, true)}${bambooStand(540, GY - 6, 1.1, "#6fae78", "#4c8c5c")}
    <g transform="translate(940 ${GY})">${Array.from({ length: 4 }, (_, i) => `<rect x="${-120 + i * 80}" y="-40" width="60" height="40" rx="6" fill="#cfc8b8"/>`).join("")}</g></g>`;

  // s24: кормление панды (финал)
  L.s24 = () => `<g>
    <rect x="520" y="${GY - 36}" width="1000" height="36" fill="#a07044"/>${Array.from({ length: 10 }, (_, i) => `<path d="M${520 + i * 100} ${GY - 36} V${GY}" stroke="rgba(0,0,0,.18)" stroke-width="3"/>`).join("")}
    ${panda(960, GY - 30, 1.7, true)}
    <g transform="translate(640 ${GY - 30})"><path d="M-50 0 L-40 -80 H40 L50 0Z" fill="#c5a45a"/><path d="M-44 -80 H44" stroke="#8a6a2a" stroke-width="6"/>${Array.from({ length: 3 }, (_, i) => `<path d="M${-24 + i * 24} -80 L${-18 + i * 24} -150" stroke="#7fbf6a" stroke-width="12" stroke-linecap="round"/>`).join("")}</g>
    <g transform="translate(1340 ${GY - 30})">${Array.from({ length: 3 }, (_, i) => `<path d="M${-50 + i * 34} 0 q10 -50 24 0Z" fill="#e8b630" stroke="#c99a2e" stroke-width="3"/>`).join("")}<ellipse cx="-4" cy="2" rx="70" ry="10" fill="#8a6a3a"/></g>
    ${plaque(1130, GY - 560, 380, "喂熊猫", "wèi xióngmāo", 62)}${bambooStand(540, GY - 6, 1.0, "#6fae78", "#4c8c5c")}${bambooStand(1500, GY - 6, 1.0, "#6fae78", "#4c8c5c")}</g>`;

  // ── карты глав ──
  const mapShell = (w, h, c1, c2, c3, inner) => `<svg class="qmapbg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" aria-hidden="true"><defs><linearGradient id="mpsk${c1.slice(1)}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${c1}"/><stop offset=".6" stop-color="${c2}"/><stop offset="1" stop-color="${c3}"/></linearGradient></defs><rect width="${w}" height="${h}" fill="url(#mpsk${c1.slice(1)})"/>${inner}</svg>`;
  EXT.map[1] = (w, h) => {
    const R = rng("map1" + w), sc = h / 900;
    return mapShell(w, h, "#f2a885", "#fbd7a6", "#efe3c6", `<circle cx="${f1(w * 0.12)}" cy="${f1(h * 0.28)}" r="${f1(h * 0.1)}" fill="#f6c46a" opacity=".9"/>
      <g transform="scale(${f1(sc)} ${f1(sc)})">${ridge(R, 0, w / sc, 720, 280, 170, "#cdaaa8").d}${ridge(R, 0, w / sc, 790, 190, 150, "#b08d94").d}<g opacity=".9">${wallOnRidge(R, 0, w / sc, 700, 40, 0.6, 3)}</g></g>
      <g transform="translate(${f1(w * 0.7)} ${f1(h * 0.88)}) scale(${f1(sc * 0.55)})">${pagoda(0, 0, 1, "#7a6a60", "#a88a7a", 5)}</g>
      <g transform="translate(${f1(w * 0.3)} ${f1(h * 0.9)}) scale(${f1(sc * 0.5)})">${warrior(0, 0, 0.9, "#b0895f")}${warrior(70, 0, 0.9, "#a07c56")}${warrior(140, 0, 0.9, "#b0895f")}</g>
      <g opacity=".8">${xcloud(w * 0.5, h * 0.12, sc * 0.5, 0.85)}${xcloud(w * 0.85, h * 0.22, sc * 0.4, 0.8)}</g>`);
  };
  EXT.map[2] = (w, h) => {
    const R = rng("map2" + w), sc = h / 900;
    let bam = ""; for (let x = 20; x < w; x += 70 + R() * 50) bam += bambooStand(f1(x), h, f1(sc * (0.5 + R() * 0.3)), "#86bd8f", "#62a174");
    return mapShell(w, h, "#bfe3cf", "#e1f1d9", "#f0efce", `<g transform="scale(${f1(sc)} ${f1(sc)})">${ridge(R, 0, w / sc, 720, 300, 170, "#a9d0b6").d}${ridge(R, 0, w / sc, 790, 200, 150, "#8dbb9d").d}</g>${bam}
      <g transform="translate(${f1(w * 0.82)} ${f1(h * 0.97)}) scale(${f1(sc * 0.3)})">${panda(0, 0, 1, true)}</g>
      <g opacity=".85">${xcloud(w * 0.3, h * 0.14, sc * 0.5, 0.9)}${xcloud(w * 0.7, h * 0.2, sc * 0.4, 0.8)}</g>`);
  };
})();
