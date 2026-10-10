/* 清越 · «Путешествие с Чачей»: горизонтальный мир сцен (формат 16:9, вид сбоку), оформленный по-китайски.
   Пекин: красные дворцовые стены и жёлтая черепица, ворота-пайлоу, хутуны с фонариками, золотые гинкго, метро и вокзал.
   В горах вдали видна Великая стена, а в финале сцена идёт прямо по ней.
   Один экран = 1600 × 900 условных единиц. Слои двигаются с разной скоростью (параллакс): небо, дальние горы, средний план, земля с препятствиями.
   Всё векторное и собирается кодом, картинок нет. */
(() => {
  "use strict";
  const W = 1600, H = 900, GY = 770;
  const A = () => window.QART;

  function rng(seed) {
    let h = 1779033703 ^ seed.length;
    for (let i = 0; i < seed.length; i++) { h = Math.imul(h ^ seed.charCodeAt(i), 3432918353); h = (h << 13) | (h >>> 19); }
    let a = h >>> 0;
    return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }
  const f1 = (n) => Math.round(n * 10) / 10;
  const SERIF = "'Noto Serif SC','Songti SC','STSong',serif";

  // ── палитры сцен ──
  const RED = "#b3261e", RED2 = "#8c1b14", GOLD = "#e0b24a", GOLD2 = "#c99a2e", YEL = "#e6b93f", YEL2 = "#c99a2a";
  const BASE = { ground: "#cfc6b4", ground2: "#8f877a", road: "#585c63", tree: "#5a9a58", tree2: "#3e7f48", gink: "#e8b630", gink2: "#f2cc54", pine: "#2f6d4b", pine2: "#3f8660" };
  const P = {
    s1: { theme: "airport", sky: ["#f9c99b", "#fde4c3", "#e8efe6"], sun: ["#fff0b8", 1220, 330, 74, true], far: "#c3cfc8", far2: "#a7b9b0", far3: "#8fa69d", ob: ["边检", "biānjiǎn"] },
    s2: { theme: "road", sky: ["#8fcdea", "#c7e6ee", "#f4efd8"], sun: ["#fffbe0", 300, 250, 62], far: "#b3c7d2", far2: "#97b0bf", far3: "#7f9aab", ob: ["堵车", "dǔchē"] },
    s3: { theme: "hotel", sky: ["#ef9a82", "#f6bf92", "#ffe2b4"], sun: ["#ffd9a0", 1180, 450, 84, true], far: "#c59a98", far2: "#ad8185", far3: "#966c74", ob: ["电梯", "diàntī"] },
    s4: { theme: "food", sky: ["#ffd392", "#ffe8b8", "#fff4d8"], sun: ["#fff3c0", 260, 300, 66, true], far: "#d3bf9d", far2: "#bfa882", far3: "#a89270", ob: ["辣", "là"] },
    s5: { theme: "subway", indoor: true, sky: ["#2e4a58", "#456572", "#6a8994"], sun: ["#fff", 0, 0, 0], far: "#566f7b", far2: "#455e6b", far3: "#3a525e", floor: "#cfd3cf", ob: ["请排队", "qǐng páiduì"] },
    s6: { theme: "station", indoor: true, sky: ["#e7dcc0", "#f1e9d3", "#f7f1e1"], sun: ["#fff", 0, 0, 0], far: "#d4c7a6", far2: "#c3b48d", far3: "#b0a07a", floor: "#d6cfbb", ob: ["票完", "piào wán"] },
    s7: { theme: "mountain", sky: ["#86c8ee", "#c6e8ee", "#eaf4ea"], sun: ["#fffbe0", 1260, 210, 58], far: "#a8c5b8", far2: "#8bb0a2", far3: "#729a8c", ob: ["台阶", "táijiē"] },
    s8: { theme: "wall", sky: ["#5d7fc4", "#eea49f", "#ffd9a2"], sun: ["#fff0b0", 1160, 540, 92, true], far: "#a893bd", far2: "#8873a8", far3: "#6f5e94", ob: ["烽火台", "fēnghuǒtái"] },
  };
  const pal = (id) => Object.assign({}, BASE, P[id] || P.s1);

  // ── строительные детали ──
  const plaque = (x, y, w, zh, py, zs) => `<g><rect x="${x}" y="${y}" width="${w}" height="${zs + 36}" rx="6" fill="#7a1812" stroke="${GOLD}" stroke-width="4"/><rect x="${x + 7}" y="${y + 7}" width="${w - 14}" height="${zs + 22}" rx="3" fill="none" stroke="${GOLD}" stroke-width="1.6" opacity=".7"/><text x="${x + w / 2}" y="${y + zs + 4}" text-anchor="middle" font-size="${zs}" font-weight="900" fill="#f4d675" font-family="${SERIF}">${zh}</text><text x="${x + w / 2}" y="${y + zs + 26}" text-anchor="middle" font-size="${Math.max(16, zs * 0.38)}" fill="#f4d675" opacity=".92" font-family="sans-serif">${py}</text></g>`;
  const bluesign = (x, y, w, zh, py, bg, zs) => A().sign(x, y, w, zh, py, bg, "#fff", zs);
  // черепичная крыша с загнутыми углами: центр cx, гребень y
  function roof(cx, y, w, h, c, c2) {
    const x0 = cx - w / 2, x1 = cx + w / 2;
    let t = ""; for (let i = 1; i < 9; i++) t += `<path d="M${f1(x0 + (w * i) / 9)} ${f1(y + h * 0.1)} L${f1(x0 + (w * i) / 9 + (i - 4.5) * 3)} ${f1(y + h * 0.95)}" stroke="${c2}" stroke-width="3" opacity=".55"/>`;
    return `<g><path d="M${f1(x0)} ${f1(y + h * 0.48)} Q${f1(x0 + w * 0.05)} ${f1(y + h * 0.96)} ${f1(x0 + w * 0.2)} ${f1(y + h)} L${f1(x1 - w * 0.2)} ${f1(y + h)} Q${f1(x1 - w * 0.05)} ${f1(y + h * 0.96)} ${f1(x1)} ${f1(y + h * 0.48)} L${f1(x1 - w * 0.1)} ${f1(y + h * 0.42)} L${f1(x1 - w * 0.2)} ${f1(y)} H${f1(x0 + w * 0.2)} L${f1(x0 + w * 0.1)} ${f1(y + h * 0.42)}Z" fill="${c}"/>${t}<rect x="${f1(x0 + w * 0.2)}" y="${f1(y - 8)}" width="${f1(w * 0.6)}" height="12" rx="5" fill="${c2}"/><circle cx="${f1(x0 + w * 0.2)}" cy="${f1(y - 6)}" r="9" fill="${c2}"/><circle cx="${f1(x1 - w * 0.2)}" cy="${f1(y - 6)}" r="9" fill="${c2}"/></g>`;
  }
  // ворота-башня как в императорском Пекине: красная стена, три арки, двойная жёлтая крыша
  function tower(cx, base, s) {
    const w = 560 * s, h = 150 * s, b = base - 70 * s;
    return `<g>
      <rect x="${f1(cx - w / 2 - 20 * s)}" y="${f1(b)}" width="${f1(w + 40 * s)}" height="${f1(70 * s)}" fill="#cfc8b8"/>
      <rect x="${f1(cx - w / 2)}" y="${f1(b - h)}" width="${f1(w)}" height="${f1(h)}" fill="#a3281f"/>
      ${[-1, 0, 1].map((k) => `<path d="M${f1(cx + k * 150 * s - 44 * s)} ${f1(b)} V${f1(b - 70 * s)} Q${f1(cx + k * 150 * s)} ${f1(b - 120 * s)} ${f1(cx + k * 150 * s + 44 * s)} ${f1(b - 70 * s)} V${f1(b)}Z" fill="#2c1a14"/>`).join("")}
      <rect x="${f1(cx - w / 2 + 40 * s)}" y="${f1(b - h - 120 * s)}" width="${f1(w - 80 * s)}" height="${f1(120 * s)}" fill="#a3281f"/>
      ${[-2, -1, 0, 1, 2].map((k) => `<rect x="${f1(cx + k * 90 * s - 18 * s)}" y="${f1(b - h - 96 * s)}" width="${f1(36 * s)}" height="${f1(52 * s)}" fill="#4a1d14"/>`).join("")}
      ${roof(cx, b - h - 120 * s - 90 * s, w - 20 * s, 96 * s, YEL, YEL2)}
      ${roof(cx, b - h - 120 * s - 230 * s, w * 0.74, 100 * s, YEL, YEL2)}
      <rect x="${f1(cx - w * 0.3)}" y="${f1(b - h - 120 * s - 135 * s)}" width="${f1(w * 0.6)}" height="${f1(46 * s)}" fill="#a3281f"/></g>`;
  }
  function pagoda(cx, base, s, c, c2, tiers) {
    let out = "", y = base, w = 170 * s;
    for (let i = 0; i < tiers; i++) {
      const bh = 52 * s, rh = 44 * s;
      out += `<rect x="${f1(cx - w * 0.36)}" y="${f1(y - bh)}" width="${f1(w * 0.72)}" height="${f1(bh)}" fill="${c2}"/>` + roof(cx, y - bh - rh + 6 * s, w, rh, c, c2);
      y -= bh + rh - 12 * s; w *= 0.84;
    }
    return out + `<path d="M${cx} ${f1(y - 6)} V${f1(y - 70 * s)}" stroke="${c2}" stroke-width="${f1(7 * s)}"/><circle cx="${cx}" cy="${f1(y - 76 * s)}" r="${f1(9 * s)}" fill="${c2}"/>`;
  }
  // пайлоу: ворота-арка
  function pailou(cx, base, s, o) {
    o = o || {}; const w = 460 * s, h = 300 * s;
    const col = (x) => `<rect x="${f1(x - 15 * s)}" y="${f1(base - h)}" width="${f1(30 * s)}" height="${f1(h)}" fill="#a3281f"/><rect x="${f1(x - 24 * s)}" y="${f1(base - 26 * s)}" width="${f1(48 * s)}" height="${f1(26 * s)}" fill="#cfc8b8"/>`;
    return `<g>${[-1, 0, 1].map((k) => col(cx + k * (w / 2))).join("")}
      <rect x="${f1(cx - w / 2 - 30 * s)}" y="${f1(base - h + 20 * s)}" width="${f1(w + 60 * s)}" height="${f1(34 * s)}" fill="#1f5f56"/><rect x="${f1(cx - w / 2 - 30 * s)}" y="${f1(base - h + 54 * s)}" width="${f1(w + 60 * s)}" height="${f1(10 * s)}" fill="${GOLD}"/>
      <rect x="${f1(cx - 80 * s)}" y="${f1(base - h - 66 * s)}" width="${f1(160 * s)}" height="${f1(66 * s)}" fill="#7a1812" stroke="${GOLD}" stroke-width="${f1(4 * s)}"/>
      ${o.text ? `<text x="${cx}" y="${f1(base - h - 20 * s)}" text-anchor="middle" font-size="${f1(46 * s)}" font-weight="900" fill="#f4d675" font-family="${SERIF}">${o.text}</text>` : ""}
      ${roof(cx, base - h - 138 * s, 200 * s, 70 * s, "#2f7a6a", "#1f5f56")}${[-1, 1].map((k) => roof(cx + k * (w / 2), base - h - 40 * s, 170 * s, 62 * s, "#2f7a6a", "#1f5f56")).join("")}</g>`;
  }
  function ginkgo(x, base, s) {
    return `<g transform="translate(${x} ${base}) scale(${s})"><path d="M-9 0 Q-6 -70 -12 -120 M9 0 Q6 -70 14 -118 M0 -60 Q-30 -100 -52 -128 M0 -70 Q34 -104 58 -130" stroke="#6b4a2a" stroke-width="14" fill="none" stroke-linecap="round"/>
      <g fill="${BASE.gink}"><circle cx="-56" cy="-150" r="44"/><circle cx="58" cy="-152" r="46"/><circle cx="0" cy="-176" r="52"/><circle cx="-24" cy="-132" r="38"/><circle cx="30" cy="-130" r="38"/></g>
      <g fill="${BASE.gink2}"><circle cx="-62" cy="-166" r="26"/><circle cx="10" cy="-196" r="30"/><circle cx="64" cy="-168" r="24"/></g>
      <g fill="#f7dc7a" opacity=".9"><circle cx="-20" cy="-150" r="5"/><circle cx="40" cy="-140" r="5"/><circle cx="-70" cy="-120" r="5"/><circle cx="70" cy="-110" r="5"/><circle cx="6" cy="-100" r="5"/></g></g>`;
  }
  function pine(x, base, s, c1, c2) {
    return `<g transform="translate(${x} ${base}) scale(${s})"><path d="M0 0 Q-14 -60 6 -120 Q18 -170 -4 -230" stroke="#5b3b24" stroke-width="16" fill="none" stroke-linecap="round"/>
      ${[[-70, -110, 76], [64, -150, 70], [-56, -190, 62], [50, -226, 56], [0, -258, 48]].map(([dx, dy, rw]) => `<g><ellipse cx="${dx}" cy="${dy}" rx="${rw}" ry="${rw * 0.3}" fill="${c2}"/><ellipse cx="${dx}" cy="${dy - 12}" rx="${rw * 0.88}" ry="${rw * 0.26}" fill="${c1}"/></g>`).join("")}</g>`;
  }
  const lampPost = (x, y) => `<g><rect x="${x - 5}" y="${y - 230}" width="10" height="230" fill="#4a3b35"/><path d="M${x - 40} ${y - 236} Q${x} ${y - 270} ${x + 40} ${y - 236} Z" fill="#7a1812"/>${A().lantern(f1(x), y - 188, 1.1)}</g>`;
  const bike = (x, y, c) => `<g transform="translate(${x} ${y})"><circle cx="-42" cy="-30" r="30" fill="none" stroke="#2a2a2e" stroke-width="6"/><circle cx="42" cy="-30" r="30" fill="none" stroke="#2a2a2e" stroke-width="6"/><path d="M-42 -30 L-8 -78 H30 L42 -30 M-8 -78 L8 -30 H-42 M30 -78 L22 -96 H44" fill="none" stroke="${c}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/><rect x="-26" y="-92" width="36" height="9" rx="4" fill="#2a2a2e"/></g>`;
  const pot = (x, y, c) => `<g><path d="M${x - 26} ${y} L${x - 20} ${y - 40} H${x + 20} L${x + 26} ${y}Z" fill="#b5654a"/><g fill="${c}"><circle cx="${x - 14}" cy="${y - 56}" r="16"/><circle cx="${x + 10}" cy="${y - 62}" r="18"/><circle cx="${x + 24}" cy="${y - 50}" r="12"/></g></g>`;
  // облако-«сянъюнь»
  const xcloud = (x, y, s, o, fill) => `<g transform="translate(${x} ${y}) scale(${s})" opacity="${o || 0.85}"><path d="M-110 20 Q-132 20 -128 -2 Q-124 -22 -100 -18 Q-98 -50 -64 -48 Q-48 -78 -12 -66 Q22 -86 50 -58 Q92 -62 96 -26 Q130 -22 124 6 Q122 20 100 20 Z" fill="${fill || "#fff"}"/><path d="M-70 -4 q12 -14 24 -2 q-4 10 -14 8 M20 -16 q14 -16 28 -2 q-6 12 -16 8" fill="none" stroke="rgba(160,120,90,.35)" stroke-width="4" stroke-linecap="round"/></g>`;
  const mist = (id, y, h, o) => `<rect x="0" y="${y}" width="100%" height="${h}" fill="url(#ms${id})" opacity="${o}"/>`;

  // ── небо ──
  function sky(id, p) {
    const [a, b, c] = p.sky, [sc, sx, sy, sr, red] = p.sun;
    if (p.indoor) {
      let t = "";
      if (p.theme === "subway") {
        for (let x = 0; x <= W; x += 160) t += `<path d="M${x} 60 V${GY}" stroke="rgba(255,255,255,.12)" stroke-width="3"/>`;
        for (let y = 140; y < GY; y += 90) t += `<path d="M0 ${y} H${W}" stroke="rgba(255,255,255,.10)" stroke-width="3"/>`;
      } else {
        t += `<rect y="0" width="${W}" height="120" fill="#7a1812"/><rect y="110" width="${W}" height="14" fill="${GOLD}"/>` + Array.from({ length: 16 }, (_, i) => `<path d="M${i * 100 + 20} 124 q30 38 60 0" fill="none" stroke="${GOLD2}" stroke-width="4"/>`).join("");
      }
      const lights = [260, 620, 980, 1340].map((x) => (p.theme === "station" ? A().lantern(x, 190, 2.2) : `<rect x="${x}" y="22" width="170" height="16" rx="8" fill="#fffbe0"/><rect x="${x - 10}" y="38" width="190" height="60" fill="#fffbe0" opacity=".07"/>`)).join("");
      return `<defs><linearGradient id="sk${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${a}"/><stop offset="1" stop-color="${c}"/></linearGradient></defs><rect width="${W}" height="${H}" fill="url(#sk${id})"/>${t}${p.theme === "subway" ? `<rect width="${W}" height="56" fill="rgba(0,0,0,.2)"/>` : ""}${lights}`;
    }
    const sun = sr ? `<g class="qsunc" style="transform-origin:${sx}px ${sy}px"><circle cx="${sx}" cy="${sy}" r="${sr * 2.6}" fill="url(#su${id})"/><circle cx="${sx}" cy="${sy}" r="${sr}" fill="${red ? "#f6c46a" : sc}"/>${red ? `<circle cx="${sx}" cy="${sy}" r="${sr * 0.8}" fill="#fff0b0" opacity=".55"/>` : ""}</g>` : "";
    const R = rng("sky" + id);
    let cl = ""; for (let i = 0; i < 5; i++) cl += `<g class="qcl" style="animation-duration:${60 + Math.floor(R() * 50)}s;animation-delay:-${Math.floor(R() * 60)}s">${xcloud(140 + i * 330 + R() * 120, 100 + R() * 230, 0.8 + R() * 0.7, 0.75 + R() * 0.2, "#fff")}</g>`;
    let birds = ""; for (let i = 0; i < 4; i++) { const bx = 420 + i * 90 + R() * 40, by = 200 + R() * 100; birds += `<g class="qbird" style="animation-duration:${22 + i * 3}s;animation-delay:-${i * 5}s"><path class="qwing" style="transform-origin:${bx + 20}px ${by}px" d="M${bx} ${by} q10 -10 20 0 q10 -10 20 0" fill="none" stroke="rgba(60,40,50,.45)" stroke-width="3" stroke-linecap="round"/></g>`; }
    return `<defs><linearGradient id="sk${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${a}"/><stop offset=".55" stop-color="${b}"/><stop offset="1" stop-color="${c}"/></linearGradient>
      <radialGradient id="su${id}"><stop offset="0" stop-color="${sc}" stop-opacity=".9"/><stop offset="1" stop-color="${sc}" stop-opacity="0"/></radialGradient></defs>
      <rect width="${W}" height="${H}" fill="url(#sk${id})"/>${sun}${cl}${birds}`;
  }

  // ── горы в стиле туши, с дымкой ──
  function ridge(R, x0, x1, base, amp, step, c) {
    const pts = []; let x = x0 - step; while (x <= x1 + step) { pts.push([x, base - amp * (0.22 + 0.78 * R())]); x += step * (0.6 + R() * 0.8); }
    let d = `M${f1(pts[0][0])} ${H} L${f1(pts[0][0])} ${f1(pts[0][1])}`;
    for (let i = 1; i < pts.length; i++) { const a = pts[i - 1], b = pts[i], mx = (a[0] + b[0]) / 2; d += ` Q${f1(mx)} ${f1(Math.min(a[1], b[1]) - 24 * R())} ${f1(b[0])} ${f1(b[1])}`; }
    d += ` L${f1(pts[pts.length - 1][0])} ${H}Z`;
    return { d: `<path d="${d}" fill="${c}"/>`, pts };
  }
  function farMountains(id, p, R, w) {
    const a = ridge(R, 0, w, 720, 330, 170, p.far), b = ridge(R, 0, w, 760, 250, 150, p.far2), c = ridge(R, 0, w, 800, 170, 130, p.far3);
    return `<defs><linearGradient id="ms${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".7"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>${a.d}${mist(id, 560, 160, 0.55)}${b.d}${mist(id, 640, 140, 0.5)}${c.d}`;
  }
  // Великая стена на гребне: ломаная линия с башнями
  function wallOnRidge(R, x0, x1, ybase, amp, scale, towerEvery) {
    const pts = []; let x = x0, y = ybase;
    while (x <= x1) { pts.push([x, y]); x += 110 * scale; y = Math.max(ybase - amp, Math.min(ybase + amp * 0.2, y + (R() - 0.55) * amp * 0.7)); }
    let line = `M${pts[0][0]} ${f1(pts[0][1])}`; pts.forEach((q) => { line += ` L${f1(q[0])} ${f1(q[1])}`; });
    let s = `<path d="${line}" fill="none" stroke="#7a6c56" stroke-width="${f1(34 * scale)}" stroke-linejoin="round"/><path d="${line}" fill="none" stroke="#cdbd98" stroke-width="${f1(26 * scale)}" stroke-linejoin="round"/><path d="${line}" fill="none" stroke="#efe2c0" stroke-width="${f1(3 * scale)}" stroke-dasharray="${f1(16 * scale)} ${f1(11 * scale)}" transform="translate(0 ${f1(-6 * scale)})"/>`;
    for (let i = 2; i < pts.length; i += towerEvery) { const q = pts[i], k = scale; s += `<g transform="translate(${f1(q[0])} ${f1(q[1])})"><rect x="${f1(-38 * k)}" y="${f1(-96 * k)}" width="${f1(76 * k)}" height="${f1(96 * k)}" fill="#cdbd98" stroke="#7a6c56" stroke-width="${f1(3 * k)}"/><rect x="${f1(-46 * k)}" y="${f1(-114 * k)}" width="${f1(92 * k)}" height="${f1(20 * k)}" fill="#cdbd98" stroke="#7a6c56" stroke-width="${f1(3 * k)}"/><g fill="#7a6c56">${[-38, -9, 20].map((dx) => `<rect x="${f1(dx * k)}" y="${f1(-130 * k)}" width="${f1(18 * k)}" height="${f1(16 * k)}"/>`).join("")}</g><rect x="${f1(-10 * k)}" y="${f1(-70 * k)}" width="${f1(20 * k)}" height="${f1(34 * k)}" rx="${f1(10 * k)}" fill="#4a3b35"/></g>`; }
    return s;
  }
  function skyline(R, x0, x1, base, c, win) {
    let s = "", x = x0;
    while (x < x1) { const w = 80 + R() * 110, h = 140 + R() * 300; s += `<rect x="${f1(x)}" y="${f1(base - h)}" width="${f1(w)}" height="${f1(h + 120)}" fill="${c}"/>`; if (win) for (let yy = base - h + 22; yy < base - 20; yy += 42) for (let xx = x + 12; xx < x + w - 18; xx += 32) if (R() > 0.45) s += `<rect x="${f1(xx)}" y="${f1(yy)}" width="13" height="19" fill="${win}"/>`; x += w + 6 + R() * 26; }
    return s;
  }

  function farLayer(id, p, screens) {
    const R = rng("far" + id), w = screens * W;
    if (p.indoor) {
      let s = "";
      if (p.theme === "subway") {
        for (let x = 120; x < w; x += 420) s += `<rect x="${x}" y="150" width="120" height="${GY - 150}" fill="${p.far2}"/><rect x="${x - 12}" y="150" width="144" height="24" fill="${p.far}"/><rect x="${x}" y="${GY - 30}" width="120" height="30" fill="#2f6db0" opacity=".6"/>`;
        for (let x = 40; x < w; x += 840) s += `<rect x="${x + 230}" y="210" width="210" height="110" rx="6" fill="#1d2329"/><text x="${x + 335}" y="256" text-anchor="middle" font-size="40" font-weight="800" fill="#f0a73a" font-family="serif">2号线</text><text x="${x + 335}" y="302" text-anchor="middle" font-size="26" fill="#9fb2bd" font-family="sans-serif">Xīzhímén</text>`;
      } else for (let x = 80; x < w; x += 480) s += `<rect x="${x}" y="130" width="46" height="${GY - 130}" fill="#a3281f"/><rect x="${x - 10}" y="130" width="66" height="22" fill="${GOLD2}"/><rect x="${x - 10}" y="${GY - 24}" width="66" height="24" fill="#cfc8b8"/>`;
      return s;
    }
    let s = farMountains(id, p, R, w);
    if (p.theme === "mountain") s += `<g opacity=".92">${wallOnRidge(R, 0, w, 640, 150, 0.62, 3)}</g>`;
    if (p.theme === "wall") s += `<g opacity=".9">${wallOnRidge(R, 0, w, 600, 190, 0.7, 3)}</g>`;
    if (p.theme === "airport" || p.theme === "road") s += `<g opacity=".6">${skyline(R, 0, w, 760, p.far2, "rgba(255,255,255,.5)")}</g>`;
    if (p.theme === "road") for (let i = 0; i < 2; i++) s += `<g opacity=".92">${tower(f1(700 + i * 1900), 770, 0.9)}</g>`;
    if (p.theme !== "wall" && p.theme !== "mountain" && p.theme !== "road") for (let i = 0; i < 2; i++) s += `<g opacity=".85">${pagoda(f1(560 + i * 1700 + R() * 200), 770, 0.9, p.theme === "hotel" || p.theme === "food" ? "#7a5a52" : "#8a7d70", p.far2, 5)}</g>`;
    return s;
  }

  // ── средний план ──
  function wallRed(x0, x1, base) {
    let s = `<rect x="${x0}" y="${base - 230}" width="${x1 - x0}" height="230" fill="#a3281f"/><rect x="${x0}" y="${base - 56}" width="${x1 - x0}" height="56" fill="#cfc8b8"/><rect x="${x0}" y="${base - 262}" width="${x1 - x0}" height="40" fill="${YEL}"/><rect x="${x0}" y="${base - 224}" width="${x1 - x0}" height="10" fill="${YEL2}"/>`;
    for (let x = x0; x < x1; x += 40) s += `<path d="M${x} ${base - 262} q20 -22 40 0" fill="${YEL2}"/>`;
    for (let x = x0 + 60; x < x1; x += 260) s += `<rect x="${x}" y="${base - 190}" width="150" height="90" rx="6" fill="none" stroke="${RED2}" stroke-width="5"/><path d="M${x + 75} ${base - 190} V${base - 100} M${x} ${base - 145} H${x + 150}" stroke="${RED2}" stroke-width="4"/>`;
    return s;
  }
  function hutongRow(R, x0, x1, base) {
    let s = "", x = x0;
    while (x < x1) {
      const w = 260 + R() * 160, h = 120 + R() * 60, tall = R() > 0.6;
      s += `<g><rect x="${f1(x)}" y="${f1(base - h)}" width="${f1(w)}" height="${f1(h)}" fill="#cfc9b8"/><path d="M${f1(x)} ${f1(base - 26)} H${f1(x + w)}" stroke="rgba(0,0,0,.12)" stroke-width="4"/>` +
        `<path d="M${f1(x - 26)} ${f1(base - h)} Q${f1(x + w / 2)} ${f1(base - h - 100 - (tall ? 40 : 0))} ${f1(x + w + 26)} ${f1(base - h)} Q${f1(x + w / 2)} ${f1(base - h - 34)} ${f1(x - 26)} ${f1(base - h)}Z" fill="#5d6571"/>` +
        `<path d="M${f1(x + 10)} ${f1(base - h - 20)} Q${f1(x + w / 2)} ${f1(base - h - 82)} ${f1(x + w - 10)} ${f1(base - h - 20)}" fill="none" stroke="#7b8490" stroke-width="5" stroke-dasharray="10 8"/>` +
        `<rect x="${f1(x + w / 2 - 28)}" y="${f1(base - 96)}" width="56" height="96" rx="6" fill="#a3281f"/><circle cx="${f1(x + w / 2 - 12)}" cy="${f1(base - 48)}" r="5" fill="${GOLD}"/><circle cx="${f1(x + w / 2 + 12)}" cy="${f1(base - 48)}" r="5" fill="${GOLD}"/></g>`;
      if (R() > 0.4) s += A().lantern(f1(x + w * 0.15), base - 120, 1.4);
      if (R() > 0.55) s += ginkgo(f1(x + w * 0.85), base, 0.7);
      x += w + 20;
    }
    return s;
  }
  const plane = () => `<g><path d="M-30 0 Q-30 -8 -18 -8 H24 Q36 -6 38 0 Q36 6 24 6 H-18 Q-30 6 -30 0Z" fill="#fbfbf7"/><path d="M-26 -6 L-34 -22 L-24 -22 L-14 -7Z" fill="#c5413a"/><path d="M-4 4 L8 20 L16 20 L12 4Z" fill="#dfe3e0"/><path d="M-4 -6 L8 -20 L14 -20 L12 -6Z" fill="#e9ecea"/><g fill="#8fb9d6"><rect x="14" y="-5" width="4" height="4" rx="1"/><rect x="21" y="-5" width="4" height="4" rx="1"/><rect x="28" y="-4" width="4" height="3" rx="1"/></g></g>`;
  function midLayer(id, p, screens) {
    const R = rng("mid" + id), w = screens * W;
    let s = "";
    if (p.indoor) {
      if (p.theme === "subway") for (let x = 300; x < w; x += 780) s += `<g><rect x="${x}" y="290" width="380" height="${GY - 290}" fill="#dfe5e8"/><rect x="${x}" y="290" width="380" height="22" fill="#2f6db0"/><rect x="${x}" y="${GY - 38}" width="380" height="14" fill="#2f6db0"/>${[0, 1, 2].map((k) => `<rect x="${x + 18 + k * 118}" y="332" width="100" height="${GY - 400}" rx="6" fill="#2b333b"/><rect x="${x + 24 + k * 118}" y="338" width="88" height="${GY - 412}" fill="#f4e7b8"/><path d="M${x + 68 + k * 118} 338 V${GY - 74}" stroke="#aaa" stroke-width="3"/>`).join("")}</g>`;
      else for (let x = 200; x < w; x += 760) s += `<g><path d="M${x} ${GY} V380 Q${x + 150} 220 ${x + 300} 380 V${GY}Z" fill="#c33a30" stroke="${GOLD}" stroke-width="8"/><path d="M${x + 34} ${GY} V396 Q${x + 150} 256 ${x + 266} 396 V${GY}Z" fill="#f1e7c9"/></g>`;
      return s;
    }
    if (p.theme === "road") s += wallRed(0, w, GY - 8) + [0, 1].map((i) => pailou(f1(1000 + i * 2400), GY - 8, 1.1, { text: i ? "天下为公" : "京" })).join("");
    else if (p.theme === "hotel" || p.theme === "food") s += hutongRow(R, 0, w, GY - 10);
    else if (p.theme === "airport") {
      for (let i = 0; i < 2; i++) s += `<g transform="translate(${f1(500 + i * 1600 + R() * 500)} ${f1(240 + R() * 90)}) scale(2.2)">${plane()}</g>`;
      for (let x = 160; x < w; x += 360) s += ginkgo(f1(x + R() * 80), GY - 12, 0.9 + R() * 0.3);
      for (let x = 340; x < w; x += 720) s += `<g><rect x="${x}" y="${GY - 330}" width="10" height="320" fill="#6b4a2a"/><g class="qflag" style="transform-origin:${x + 10}px ${GY - 270}px"><path d="M${x + 10} ${GY - 320} H${x + 190} V${GY - 220} H${x + 10}Z" fill="#c8302a"/><text x="${x + 100}" y="${GY - 250}" text-anchor="middle" font-size="46" font-weight="900" fill="#f4d675" font-family="${SERIF}">欢迎</text></g></g>`;
    } else if (p.theme === "mountain") {
      s += ridge(R, 0, w, GY - 30, 340, 200, "#6fa58a").d + `<g opacity=".95">${wallOnRidge(R, 0, w, 560, 170, 0.95, 3)}</g>` + ridge(R, 0, w, GY - 10, 160, 180, "#4f8a6e").d;
      for (let x = 100; x < w; x += 240 + R() * 200) s += pine(f1(x), GY - 12, 0.7 + R() * 0.6, p.pine2, p.pine);
    } else if (p.theme === "wall") {
      s += ridge(R, 0, w, GY - 30, 380, 210, "#6b5f96").d + `<g>${wallOnRidge(R, 0, w, 540, 190, 1.35, 2)}</g>` + ridge(R, 0, w, GY - 10, 150, 190, "#52497f").d;
      for (let x = 160; x < w; x += 360 + R() * 240) s += pine(f1(x), GY - 12, 0.8 + R() * 0.5, "#4c8a68", "#366c52");
    }
    return s;
  }

  // ── ориентиры у места диалога (мировые x примерно 520–1500) ──
  function landmark(id, p) {
    switch (id) {
      case "s1": return `<g><rect x="540" y="330" width="780" height="${GY - 330}" rx="6" fill="#ece6d6"/><rect x="540" y="330" width="780" height="26" fill="${RED}"/><rect x="540" y="356" width="780" height="8" fill="${GOLD}"/>
        ${[0, 1, 2, 3].map((k) => `<rect x="${580 + k * 200}" y="370" width="26" height="${GY - 370}" fill="${RED}"/><rect x="${572 + k * 200}" y="${GY - 24}" width="42" height="24" fill="#cfc8b8"/>`).join("")}
        <rect x="640" y="390" width="560" height="250" rx="8" fill="#bfe0f1" stroke="#7f8d95" stroke-width="8"/><path d="M640 590 H1200" stroke="#9aa5ab" stroke-width="54"/><g transform="translate(900 495) scale(3)">${plane()}</g><path d="M780 390 V640 M920 390 V640 M1060 390 V640" stroke="#7f8d95" stroke-width="7"/>
        ${bluesign(790, 250, 330, "到达", "dàodá", "#1f4f8a", 56)}${plaque(770, 148, 370, "欢迎来到北京", "Huānyíng dào Běijīng", 44)}${A().lantern(580, 260, 2.2)}${A().lantern(1280, 260, 2.2)}
        <g><rect x="1340" y="${GY - 190}" width="110" height="190" rx="10" fill="#d9473f"/><rect x="1372" y="${GY - 226}" width="46" height="38" rx="12" fill="none" stroke="#7a2a26" stroke-width="10"/><rect x="1220" y="${GY - 140}" width="100" height="140" rx="10" fill="#2f8f83"/></g></g>`;
      case "s2": return `<g>${plaque(1130, GY - 470, 250, "出租车", "chūzūchē", 50)}<rect x="1248" y="${GY - 360}" width="14" height="360" fill="#4a3b35"/>
        <g transform="translate(600 ${GY - 150}) scale(1.5)"><path d="M0 100 Q0 64 36 58 L66 14 H172 L214 58 Q252 62 252 100 V120 H0Z" fill="#f2c230"/><path d="M82 22 H162 L190 58 H58Z" fill="#cfe9f5"/><path d="M122 22 V58" stroke="#f2c230" stroke-width="8"/><rect x="92" y="-14" width="68" height="26" rx="7" fill="#fff" stroke="#999" stroke-width="2"/><text x="126" y="6" text-anchor="middle" font-size="18" font-weight="800" fill="#222" font-family="serif">出租车</text><rect x="0" y="86" width="252" height="12" fill="#d29f14"/><circle cx="60" cy="124" r="26" fill="#26292c"/><circle cx="60" cy="124" r="10" fill="#bbb"/><circle cx="196" cy="124" r="26" fill="#26292c"/><circle cx="196" cy="124" r="10" fill="#bbb"/><rect x="238" y="74" width="16" height="12" rx="4" fill="#fff6c9"/></g>${bike(1030, GY, "#2f8f83")}${A().lantern(520, GY - 330, 1.6)}</g>`;
      case "s3": return `<g><rect x="520" y="${GY - 30}" width="840" height="30" fill="#8f877a"/><rect x="540" y="${GY - 330}" width="800" height="300" fill="#6d737c"/>${Array.from({ length: 16 }, (_, i) => `<path d="M${540 + i * 50} ${GY - 330} V${GY - 30}" stroke="rgba(0,0,0,.12)" stroke-width="3"/>`).join("")}
        ${roof(940, GY - 520, 900, 200, "#5d6571", "#46505c")}<g><rect x="810" y="${GY - 300}" width="260" height="270" fill="#a3281f"/><rect x="826" y="${GY - 284}" width="228" height="254" fill="#7a1812"/><path d="M940 ${GY - 284} V${GY - 30}" stroke="${GOLD}" stroke-width="5"/>${[0, 1, 2, 3].flatMap((r) => [0, 1, 2].map((c) => `<circle cx="${850 + c * 28}" cy="${GY - 250 + r * 36}" r="7" fill="${GOLD}"/><circle cx="${1030 - c * 28}" cy="${GY - 250 + r * 36}" r="7" fill="${GOLD}"/>`)).join("")}</g>
        ${plaque(700, GY - 440, 480, "清茶酒店", "Qīngchá jiǔdiàn", 68)}${A().lantern(620, GY - 290, 2.2)}${A().lantern(1260, GY - 290, 2.2)}
        <g fill="#c9c2b0">${[600, 1280].map((x) => `<g><rect x="${x - 36}" y="${GY - 90}" width="72" height="90" rx="10"/><circle cx="${x}" cy="${GY - 112}" r="30"/><circle cx="${x - 14}" cy="${GY - 118}" r="5" fill="#4a3b35"/><circle cx="${x + 14}" cy="${GY - 118}" r="5" fill="#4a3b35"/></g>`).join("")}</g></g>`;
      case "s4": return `<g><rect x="520" y="${GY - 330}" width="900" height="330" fill="#9a9488"/>${Array.from({ length: 9 }, (_, r) => `<path d="M520 ${GY - 330 + r * 38} H1420" stroke="rgba(0,0,0,.12)" stroke-width="3"/>`).join("")}
        <path d="M520 ${GY - 330} Q970 ${GY - 480} 1420 ${GY - 330} Q970 ${GY - 400} 520 ${GY - 330}Z" fill="#5d6571"/>
        <rect x="620" y="${GY - 300}" width="760" height="16" fill="#a3281f"/>${Array.from({ length: 19 }, (_, i) => `<path d="M${620 + i * 40} ${GY - 284} q20 30 40 0" fill="#fff" stroke="#e0d6c0" stroke-width="3"/>`).join("")}
        ${plaque(820, GY - 450, 340, "包子铺", "bāozi pù", 60)}<rect x="590" y="${GY - 160}" width="820" height="30" rx="8" fill="#d2a066"/><rect x="606" y="${GY - 130}" width="788" height="130" fill="#b9814a"/>
        ${[0, 1, 2].map((k) => `<g transform="translate(${690 + k * 210} ${GY - 255})"><ellipse cx="62" cy="98" rx="72" ry="16" fill="#d8b878"/><rect x="0" y="52" width="124" height="46" rx="8" fill="#e6c98a"/><ellipse cx="62" cy="52" rx="62" ry="16" fill="#efd8a0"/><path d="M34 30 C20 -4 56 -8 40 -50 M74 30 C60 -4 96 -8 80 -50" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round" opacity=".85" class="qsteam"/></g>`).join("")}
        ${A().lantern(560, GY - 360, 2)}${A().lantern(1380, GY - 360, 2)}</g>`;
      case "s5": return `<g><rect x="540" y="290" width="800" height="${GY - 290}" fill="#cfd6dc"/><rect x="540" y="290" width="800" height="34" fill="#2f6db0"/><rect x="540" y="${GY - 70}" width="800" height="18" fill="#2f6db0"/>
        <rect x="640" y="180" width="320" height="92" rx="10" fill="#fff" stroke="#9aa5ab" stroke-width="6"/><circle cx="702" cy="226" r="30" fill="#c5413a"/><text x="702" y="239" text-anchor="middle" font-size="40" font-weight="800" fill="#fff" font-family="sans-serif">2</text><text x="846" y="226" text-anchor="middle" font-size="46" font-weight="800" fill="#22302b" font-family="serif">西直门</text><text x="846" y="258" text-anchor="middle" font-size="22" fill="#67756f" font-family="sans-serif">Xīzhímén · 2号线</text>
        ${[0, 1, 2].map((k) => `<rect x="${600 + k * 230}" y="350" width="196" height="${GY - 440}" rx="8" fill="#2b333b"/><rect x="${612 + k * 230}" y="362" width="172" height="${GY - 464}" fill="#f4e7b8"/><path d="M${698 + k * 230} 362 V${GY - 102}" stroke="#aaa" stroke-width="4"/>`).join("")}${plaque(1130, 330, 190, "请排队", "qǐng páiduì", 38)}</g>`;
      case "s6": return `<g><rect x="540" y="140" width="800" height="300" rx="14" fill="#1d2329" stroke="${GOLD2}" stroke-width="8"/><text x="940" y="196" text-anchor="middle" font-size="40" font-weight="800" fill="#f0a73a" font-family="serif">车次 · 时间 · 目的地</text>
        ${[["08:00", "票完", "#ff6b5e"], ["09:00", "有票", "#7de08b"], ["10:00", "有票", "#7de08b"]].map((r, i) => `<g font-family="serif" font-size="44" font-weight="800" fill="#ffc86a"><text x="590" y="${268 + i * 62}">S2</text><text x="680" y="${268 + i * 62}">${r[0]}</text><text x="840" y="${268 + i * 62}">八达岭长城</text><text x="1190" y="${268 + i * 62}" fill="${r[2]}">${r[1]}</text></g>`).join("")}
        <rect x="860" y="${GY - 250}" width="440" height="250" rx="10" fill="#f4f8fa" stroke="#6b7882" stroke-width="10"/><rect x="900" y="${GY - 220}" width="360" height="110" rx="6" fill="#bfe0f1" stroke="#6b7882" stroke-width="6"/><rect x="840" y="${GY - 100}" width="480" height="34" rx="8" fill="#6b4a2a"/>${plaque(930, GY - 360, 300, "售票处", "shòupiàochù", 50)}</g>`;
      case "s7": return `<g>${[0, 1, 2, 3, 4, 5, 6].map((k) => `<rect x="${960 + k * 66}" y="${GY - 34 - k * 34}" width="${460 - k * 66}" height="38" fill="#cdbf9f" stroke="#a5946f" stroke-width="3"/>`).join("")}
        <g transform="translate(560 ${GY - 340})"><path d="M0 70 Q150 -70 300 70Z" fill="#c8302a"/><path d="M150 0 V340" stroke="#7a5a2f" stroke-width="10"/><rect x="10" y="200" width="280" height="30" rx="8" fill="#b9814a"/><g fill="#6fb8e8">${[0, 1, 2, 3].map((k) => `<rect x="${24 + k * 66}" y="130" width="30" height="64" rx="12"/>`).join("")}</g></g>${bluesign(580, GY - 520, 130, "水", "shuǐ", "#2f6db0", 58)}${plaque(900, GY - 560, 420, "八达岭长城", "Bādálǐng Chángchéng", 44)}</g>`;
      case "s8": return `<g><rect x="720" y="${GY - 470}" width="300" height="470" fill="#cdbd98" stroke="#7a6c56" stroke-width="6"/><rect x="696" y="${GY - 520}" width="348" height="54" fill="#cdbd98" stroke="#7a6c56" stroke-width="6"/><g fill="#7a6c56">${[0, 1, 2, 3].map((k) => `<rect x="${698 + k * 84}" y="${GY - 568}" width="56" height="50"/>`).join("")}</g><rect x="830" y="${GY - 290}" width="80" height="130" rx="40" fill="#3a2f2a"/><path d="M870 ${GY - 568} V${GY - 700}" stroke="#7a5a2f" stroke-width="8"/><path d="M870 ${GY - 700} L1010 ${GY - 662} L870 ${GY - 624}Z" fill="${RED}"/>${plaque(740, GY - 420, 260, "长城", "Chángchéng", 52)}</g>`;
    }
    return "";
  }

  // ── земля ──
  function ground(id, p, screens) {
    const w = screens * W, R = rng("gr" + id);
    if (p.indoor) {
      let s = `<rect x="0" y="${GY}" width="${w}" height="${H - GY}" fill="${p.floor}"/><rect x="0" y="${GY}" width="${w}" height="12" fill="#f0c53a"/><rect x="0" y="${GY + 12}" width="${w}" height="8" fill="rgba(0,0,0,.12)"/>`;
      for (let x = 0; x < w; x += 160) s += `<path d="M${x} ${GY + 20} V${H}" stroke="rgba(0,0,0,.08)" stroke-width="3"/>`;
      s += `<path d="M0 ${GY + 70} H${w} M0 ${GY + 120} H${w}" stroke="rgba(0,0,0,.07)" stroke-width="3"/>`;
      for (let x = 400; x < w; x += 900) s += `<g><rect x="${x}" y="${GY - 70}" width="150" height="14" rx="5" fill="#6b7882"/><rect x="${x + 12}" y="${GY - 56}" width="10" height="56" fill="#555"/><rect x="${x + 128}" y="${GY - 56}" width="10" height="56" fill="#555"/></g>`;
      return s;
    }
    if (p.theme === "wall") {
      let s = `<rect x="0" y="${GY - 196}" width="${w}" height="196" fill="#a79a80"/>`;
      for (let x = 0; x < w; x += 136) s += `<rect x="${x + 18}" y="${GY - 268}" width="86" height="76" fill="#a79a80"/><rect x="${x + 18}" y="${GY - 268}" width="86" height="10" fill="#c9bc9f"/><rect x="${x + 50}" y="${GY - 150}" width="22" height="64" rx="11" fill="#4a3f36"/>`;
      s += `<rect x="0" y="${GY - 196}" width="${w}" height="12" fill="#c9bc9f"/><rect x="0" y="${GY}" width="${w}" height="${H - GY}" fill="#b8a98a"/>`;
      for (let r = 0; r < 4; r++) for (let x = (r % 2) * 60; x < w; x += 120) s += `<rect x="${x}" y="${GY + 6 + r * 34}" width="116" height="30" rx="3" fill="${r % 2 ? "#b1a182" : "#bcad8e"}" stroke="rgba(0,0,0,.14)" stroke-width="2"/>`;
      return s + `<rect x="0" y="${GY - 4}" width="${w}" height="10" fill="#d6c8a6"/>`;
    }
    if (p.theme === "mountain") {
      let s = `<rect x="0" y="${GY}" width="${w}" height="${H - GY}" fill="#8a8272"/>`;
      for (let x = 0; x < w; x += 150 + R() * 100) s += `<path d="M${f1(x)} ${GY} V${H}" stroke="rgba(0,0,0,.18)" stroke-width="4"/>`;
      for (let r = 0; r < 3; r++) s += `<path d="M0 ${GY + 38 + r * 40} H${w}" stroke="rgba(0,0,0,.12)" stroke-width="3"/>`;
      const n = Math.round(w / 70), sw = w / n; let sc = ""; for (let i = 0; i < n; i++) sc += `q${f1(-sw / 2)} 16 ${f1(-sw)} 0 `;
      return s + `<path d="M0 ${GY - 4} H${w} V${GY + 18} ${sc}Z" fill="#5e9a4e"/><path d="M0 ${GY - 4} H${w}" stroke="rgba(255,255,255,.25)" stroke-width="5"/>`;
    }
    let s = `<rect x="0" y="${GY}" width="${w}" height="46" fill="${p.ground}"/><rect x="0" y="${GY}" width="${w}" height="8" fill="#e9e2d0"/><rect x="0" y="${GY + 46}" width="${w}" height="16" fill="${p.ground2}"/><rect x="0" y="${GY + 62}" width="${w}" height="${H - GY - 62}" fill="${p.road}"/><rect x="0" y="${GY + 62}" width="${w}" height="8" fill="rgba(0,0,0,.18)"/>`;
    for (let x = 0; x < w; x += 128) s += `<path d="M${x} ${GY + 8} V${GY + 46}" stroke="rgba(0,0,0,.14)" stroke-width="3"/>`;
    for (let x = 0; x < w; x += 200) s += `<rect x="${x}" y="${GY + 96}" width="110" height="10" rx="4" fill="#f4f0e0" opacity=".8"/>`;
    return s;
  }
  function decor(id, p, screens, keepOut) {
    const w = screens * W, R = rng("dc" + id); let back = "", front = "";
    const free = (x, r) => keepOut.every((k) => Math.abs(x - k) > r);
    if (p.indoor) return { back, front };
    for (let x = 200; x < w - 100; x += 320 + R() * 420) {
      if (!free(x, 260)) continue;
      if (p.theme === "mountain" || p.theme === "wall") back += pine(f1(x), GY - 4, 0.9 + R() * 0.5, p.pine2, p.pine);
      else if (R() > 0.45) back += lampPost(f1(x), GY - 2); else back += ginkgo(f1(x), GY - 4, 0.9 + R() * 0.4);
    }
    for (let x = 80; x < w; x += 120 + R() * 160) {
      if (!free(x, 70)) continue;
      const k = R();
      if (p.theme === "mountain") front += `<path d="M${f1(x - 14)} ${GY + 2} q4 -26 10 -4 q4 -30 10 0 q6 -22 10 4Z" fill="#4d8a3e"/>`;
      else if (p.theme === "wall") { if (k > 0.7) front += `<path d="M${f1(x - 14)} ${GY + 2} q4 -22 10 -4 q4 -26 10 0 q6 -20 10 4Z" fill="#6f9a52"/>`; }
      else if (k < 0.3) front += pot(f1(x), GY + 2, ["#d9473f", "#f2a6bd", "#f2c230"][Math.floor(R() * 3)]);
      else if (k < 0.45) front += bike(f1(x), GY + 2, ["#2f6db0", "#c5413a", "#2f8f83"][Math.floor(R() * 3)]);
    }
    return { back, front };
  }

  // ── препятствия ──
  const stripes = (x, y, w, h, n, c1, c2) => Array.from({ length: n }, (_, i) => `<rect x="${f1(x + (w / n) * i)}" y="${y}" width="${f1(w / n)}" height="${h}" fill="${i % 2 ? c2 : c1}"/>`).join("");
  function obstacle(kind, x, p) {
    const lab = p.ob || ["", ""];
    const sg = (cx, y, w) => plaque(cx - w / 2, y, w, lab[0], lab[1], 44);
    switch (kind) {
      case "barrier": return `<g class="qob barrier"><rect x="${x - 118}" y="${GY - 190}" width="46" height="190" rx="8" fill="${RED}"/><rect x="${x - 118}" y="${GY - 190}" width="46" height="14" fill="${GOLD}"/><circle cx="${x - 95}" cy="${GY - 206}" r="14" fill="#ffd36b"/>
        <g class="arm" style="transform-origin:${x - 95}px ${GY - 150}px">${stripes(x - 100, GY - 162, 250, 24, 8, "#fff", RED)}<rect x="${x - 100}" y="${GY - 162}" width="250" height="24" fill="none" stroke="rgba(0,0,0,.25)" stroke-width="3"/></g>
        <rect x="${x + 140}" y="${GY - 110}" width="26" height="110" rx="6" fill="#59636b"/>${sg(x, GY - 340, 220)}</g>`;
      case "door": return `<g class="qob door"><rect x="${x - 135}" y="${GY - 300}" width="270" height="300" rx="10" fill="#7f8d95"/><rect x="${x - 118}" y="${GY - 282}" width="236" height="282" fill="#bfe0f1"/>
        <g class="dl"><rect x="${x - 118}" y="${GY - 282}" width="118" height="282" fill="#cfe9f5" stroke="#7f8d95" stroke-width="6"/><path d="M${x - 100} ${GY - 250} l50 0 -50 90Z" fill="#fff" opacity=".5"/></g>
        <g class="dr"><rect x="${x}" y="${GY - 282}" width="118" height="282" fill="#cfe9f5" stroke="#7f8d95" stroke-width="6"/><path d="M${x + 20} ${GY - 250} l50 0 -50 90Z" fill="#fff" opacity=".5"/></g>${sg(x, GY - 390, 220)}</g>`;
      case "crates": return `<g class="qob crates"><rect x="${x - 100}" y="${GY - 110}" width="120" height="110" rx="8" fill="#d9473f"/><rect x="${x - 100}" y="${GY - 110}" width="120" height="16" fill="rgba(0,0,0,.14)"/><path d="M${x - 70} ${GY - 110} v110 M${x - 20} ${GY - 110} v110" stroke="rgba(0,0,0,.14)" stroke-width="4"/>
        <rect x="${x + 24}" y="${GY - 80}" width="96" height="80" rx="8" fill="#2f8f83"/><rect x="${x + 52}" y="${GY - 100}" width="40" height="22" rx="10" fill="none" stroke="#1d5f58" stroke-width="8"/>
        <rect x="${x - 70}" y="${GY - 190}" width="100" height="80" rx="8" fill="#e8a23a"/><path d="M${x - 70} ${GY - 150} h100" stroke="rgba(0,0,0,.14)" stroke-width="4"/>${sg(x + 10, GY - 300, 220)}</g>`;
      default: return `<g class="qob gate"><rect x="${x - 134}" y="${GY - 270}" width="30" height="270" rx="6" fill="${RED2}"/><rect x="${x + 104}" y="${GY - 270}" width="30" height="270" rx="6" fill="${RED2}"/><rect x="${x - 150}" y="${GY - 290}" width="300" height="28" rx="6" fill="${RED}"/><rect x="${x - 150}" y="${GY - 262}" width="300" height="8" fill="${GOLD}"/>
        <g class="leaf" style="transform-origin:${x - 104}px ${GY - 40}px"><rect x="${x - 104}" y="${GY - 250}" width="208" height="210" rx="8" fill="#a3281f" stroke="${GOLD2}" stroke-width="4"/><path d="M${x} ${GY - 250} V${GY - 40}" stroke="${GOLD2}" stroke-width="4"/>${[0, 1, 2].flatMap((r) => [0, 1, 2].map((c) => `<circle cx="${x - 76 + c * 24}" cy="${GY - 214 + r * 48}" r="7" fill="${GOLD}"/><circle cx="${x + 28 + c * 24}" cy="${GY - 214 + r * 48}" r="7" fill="${GOLD}"/>`)).join("")}<circle cx="${x - 14}" cy="${GY - 120}" r="9" fill="#e9c96d"/><circle cx="${x + 14}" cy="${GY - 120}" r="9" fill="#e9c96d"/></g>${sg(x, GY - 390, 220)}</g>`;
    }
  }
  const KINDS = { s1: ["barrier", "gate", "door", "crates", "barrier"], s2: ["crates", "barrier", "gate", "door", "crates"], s3: ["door", "gate", "crates", "barrier", "door"], s4: ["crates", "gate", "barrier", "door", "crates"], s5: ["gate", "barrier", "door", "crates", "gate"], s6: ["barrier", "door", "gate", "crates", "barrier"], s7: ["gate", "crates", "barrier", "door", "gate"], s8: ["gate", "barrier", "crates", "door", "gate"] };
  const OB_AT = (i) => 133 + i * 100;
  const FINISH_AT = (n) => 133 + n * 100;

  // финиш: красные ворота с золотой табличкой и фонариками
  function finish(x) {
    return `<g class="qfin"><rect x="${x - 150}" y="${GY - 350}" width="30" height="350" rx="6" fill="${RED}"/><rect x="${x + 120}" y="${GY - 350}" width="30" height="350" rx="6" fill="${RED}"/>
      <rect x="${x - 170}" y="${GY - 380}" width="340" height="34" rx="6" fill="#1f5f56"/><rect x="${x - 170}" y="${GY - 346}" width="340" height="9" fill="${GOLD}"/>
      <rect x="${x - 110}" y="${GY - 330}" width="220" height="70" rx="8" fill="#7a1812" stroke="${GOLD}" stroke-width="5"/><text x="${x}" y="${GY - 280}" text-anchor="middle" font-size="52" font-weight="900" fill="#f4d675" font-family="${SERIF}">到了!</text>
      ${roof(x, GY - 450, 300, 80, "#2f7a6a", "#1f5f56")}${A().lantern(x - 190, GY - 300, 1.9)}${A().lantern(x + 190, GY - 300, 1.9)}
      <path d="M${x - 110} ${GY} H${x + 110}" stroke="#f6c453" stroke-width="8" stroke-dasharray="14 12"/></g>`;
  }

  function build(id, n) {
    const p = pal(id), screens = n + 2;
    const farS = Math.ceil(1 + (n + 1) * 0.12) + 1, midS = Math.ceil(1 + (n + 1) * 0.42) + 1;
    const obXs = Array.from({ length: n }, (_, i) => OB_AT(i) * 16), finX = FINISH_AT(n) * 16;
    const dec = decor(id, p, screens, obXs.concat([finX, 1000]));
    const kinds = KINDS[id] || KINDS.s1;
    const obs = obXs.map((x, i) => obstacle(kinds[i % kinds.length], x, p)).join("");
    const svg = (cls, w, inner) => `<svg class="qw-svg ${cls}" viewBox="0 0 ${w * W} ${H}" preserveAspectRatio="none" aria-hidden="true">${inner}</svg>`;
    return {
      screens, farS, midS, kinds, obXs, finX, pal: p,
      sky: `<svg class="qw-svg sky" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" aria-hidden="true">${sky(id, p)}</svg>`,
      far: svg("far", farS, farLayer(id, p, farS)),
      mid: svg("mid", midS, midLayer(id, p, midS)),
      near: svg("near", screens, ground(id, p, screens) + dec.back + landmark(id, p) + obs + finish(finX) + dec.front),
    };
  }

  // ── картинка для карты на главной: горы тушью, Великая стена, пагода ──
  function mapArt(w, h) {
    const R = rng("map" + w), sc = h / 900;
    return `<svg class="qmapbg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" aria-hidden="true"><defs><linearGradient id="mpsk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6cf9c"/><stop offset=".6" stop-color="#fbe8c6"/><stop offset="1" stop-color="#eef0dd"/></linearGradient></defs>
      <rect width="${w}" height="${h}" fill="url(#mpsk)"/>
      <g transform="scale(${f1(sc)} ${f1(sc)})">${ridge(R, 0, w / sc, 700, 300, 160, "#cbb7b3").d}${ridge(R, 0, w / sc, 760, 240, 140, "#b49aa4").d}<g opacity=".95">${wallOnRidge(R, 0, w / sc, 640, 120, 0.5, 3)}</g>${ridge(R, 0, w / sc, 820, 150, 130, "#8f8aa0").d}</g>
      <g transform="translate(${f1(w * 0.86)} ${f1(h * 0.78)}) scale(${f1(sc * 0.5)})">${pagoda(0, 0, 1, "#7a5a52", "#a88a7a", 4)}</g>
      <circle cx="${f1(w * 0.1)}" cy="${f1(h * 0.2)}" r="${f1(h * 0.09)}" fill="#f4c26a" opacity=".85"/>
      <g opacity=".85">${xcloud(w * 0.45, h * 0.14, sc * 0.5, 0.9)}${xcloud(w * 0.78, h * 0.24, sc * 0.4, 0.8)}</g></svg>`;
  }

  window.QWORLD = { build, W, H, GY, OB_AT, FINISH_AT, PAL: P, pal, mapArt, xcloud, pagoda, roof };
})();
