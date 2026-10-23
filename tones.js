/* Проверка тона голосом (v26). Всё считается на телефоне: звук с микрофона не отправляется и не сохраняется,
   в память попадает только линия высоты голоса, и она исчезает, когда закрываешь карточку.
   Часть 1 (чистые функции) проверяется тестами в node, часть 2 — экран внутри карточки иероглифа. */
(function (root) {
  "use strict";
  // ── часть 1: расчёты ──
  const F_MIN = 70, F_MAX = 500, HOP_MS = 25;
  const MARKS = { ā: 1, á: 2, ǎ: 3, à: 4, ē: 1, é: 2, ě: 3, è: 4, ī: 1, í: 2, ǐ: 3, ì: 4, ō: 1, ó: 2, ǒ: 3, ò: 4, ū: 1, ú: 2, ǔ: 3, ù: 4, ǖ: 1, ǘ: 2, ǚ: 3, ǜ: 4 };
  function expectedTone(py) {
    const s = String(py || "").trim().toLowerCase();
    if (!s || /[\s\/,;·]/.test(s)) return 0;           // несколько слогов или чтений: не проверяем
    for (const ch of s) if (MARKS[ch]) return MARKS[ch];
    return 0;                                            // лёгкий тон
  }
  function rms(b) { let s = 0; for (let i = 0; i < b.length; i++) s += b[i] * b[i]; return Math.sqrt(s / b.length); }
  /** Высота основного тона: нормированная автокорреляция. buf — не меньше 1.7 периода самого низкого голоса. */
  function detectPitch(buf, sr) {
    const W = Math.floor(buf.length / 2), lmin = Math.floor(sr / F_MAX), lmax = Math.min(Math.ceil(sr / F_MIN), buf.length - W - 1);
    if (lmax <= lmin + 2) return { f0: 0, clarity: 0 };
    const nsdf = new Float32Array(lmax + 2);
    let e0 = 0; for (let j = 0; j < W; j++) e0 += buf[j] * buf[j];
    let eT = 0; for (let j = 0; j < W; j++) eT += buf[j + lmin - 1] * buf[j + lmin - 1];
    let best = 0;
    for (let t = lmin; t <= lmax; t++) {
      let r = 0; for (let j = 0; j < W; j++) r += buf[j] * buf[j + t];
      eT += buf[W - 1 + t] * buf[W - 1 + t] - buf[t - 1] * buf[t - 1];
      const m = e0 + eT;
      nsdf[t] = m > 1e-12 ? (2 * r) / m : 0;
      if (nsdf[t] > best) best = nsdf[t];
    }
    if (best < 0.5) return { f0: 0, clarity: best };
    // первый локальный максимум, близкий к лучшему: так не берём октаву ниже
    let pick = 0;
    for (let t = lmin + 1; t < lmax; t++) {
      if (nsdf[t] >= 0.9 * best && nsdf[t] >= nsdf[t - 1] && nsdf[t] >= nsdf[t + 1]) { pick = t; break; }
    }
    if (!pick) return { f0: 0, clarity: best };
    const a = nsdf[pick - 1], b = nsdf[pick], c = nsdf[pick + 1], d = a - 2 * b + c;
    const shift = d !== 0 ? (0.5 * (a - c)) / d : 0;
    return { f0: sr / (pick + shift), clarity: b };
  }
  const median = (a) => { const s = a.slice().sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
  /** Ряд частот по кадрам (0 = нет голоса) → линия в полутонах без среднего; null, если голоса мало. */
  function contour(f0s) {
    // самый длинный участок с голосом, дырки до 2 кадров заполняем
    const f = f0s.slice();
    for (let i = 1; i < f.length - 1; i++) if (!f[i]) { let j = i; while (j < f.length && !f[j]) j++; if (j - i <= 2 && f[i - 1] && f[j]) for (let k = i; k < j; k++) f[k] = f[i - 1] + ((f[j] - f[i - 1]) * (k - i + 1)) / (j - i + 1); }
    let bs = 0, bl = 0, s = -1;
    for (let i = 0; i <= f.length; i++) {
      if (i < f.length && f[i]) { if (s < 0) s = i; } else if (s >= 0) { if (i - s > bl) { bl = i - s; bs = s; } s = -1; }
    }
    if (bl < 8) return null;
    const run = f.slice(bs, bs + bl), ref = median(run);
    let st = run.map((x) => 12 * Math.log2(x / ref));
    // скачки на октаву и выбросы
    st = st.map((x, i) => { const nb = st.slice(Math.max(0, i - 3), i + 4); return Math.abs(x - median(nb)) > 4 ? median(nb) : x; });
    st = st.map((x, i) => { const w = [st[i - 1], x, st[i + 1]].filter((v) => v !== undefined); return median(w); });
    // края слога часто «плывут»: отрезаем по 10%
    const cut = Math.floor(st.length * 0.1);
    st = st.slice(cut, st.length - cut);
    if (st.length < 6) return null;
    const mean = st.reduce((p, q) => p + q, 0) / st.length;
    return st.map((x) => x - mean);
  }
  function resample(a, n) {
    const out = [];
    for (let i = 0; i < n; i++) { const p = (i * (a.length - 1)) / (n - 1), k = Math.floor(p), fr = p - k; out.push(a[k] * (1 - fr) + (a[Math.min(k + 1, a.length - 1)] * fr)); }
    return out;
  }
  const zero = (a) => { const m = a.reduce((p, q) => p + q, 0) / a.length; return a.map((x) => x - m); };
  /** Образцы четырёх тонов в полутонах (по схеме Чао: 55, 35, 214, 51). */
  function template(tone, n) {
    const pts = { 1: [[0, 0], [1, 0]], 2: [[0, -2.5], [1, 2.5]], 3: [[0, -0.5], [0.4, -3], [1, 2.5]], 4: [[0, 4], [1, -4]] }[tone];
    const out = [];
    for (let i = 0; i < n; i++) {
      const x = i / (n - 1); let k = 0; while (k < pts.length - 2 && x > pts[k + 1][0]) k++;
      const [x0, y0] = pts[k], [x1, y1] = pts[k + 1];
      out.push(y0 + ((y1 - y0) * (x - x0)) / (x1 - x0));
    }
    return zero(out);
  }
  /** Сравнение с четырьмя образцами. ok — «достаточно похоже на ожидаемый тон» (мягко: небольшая разница в пользу другого тона прощается). */
  function classify(st, expected) {
    const N = 10, x = zero(resample(st, N)), d = {};
    for (let t = 1; t <= 4; t++) { const tm = template(t, N); let s = 0; for (let i = 0; i < N; i++) s += (x[i] - tm[i]) ** 2; d[t] = Math.sqrt(s / N); }
    let best = 1; for (let t = 2; t <= 4; t++) if (d[t] < d[best]) best = t;
    const ok = !expected || best === expected || d[expected] <= d[best] + 0.7;
    return { best, ok, dist: d };
  }
  const api = { expectedTone, detectPitch, contour, classify, template, resample, rms, HOP_MS, F_MIN, F_MAX };
  if (typeof module !== "undefined" && module.exports) { module.exports = api; return; }
  root.TONES = api;

  // ── часть 2: запись с микрофона ──
  let live = null;
  function stop() {
    if (!live) return;
    const l = live; live = null;
    try { clearInterval(l.timer); } catch (e) { /* ок */ }
    try { l.stream.getTracks().forEach((t) => t.stop()); } catch (e) { /* ок */ }
    try { l.ctx.close(); } catch (e) { /* ок */ }
    if (l.done) l.done(l.result);
  }
  /** Запись одного слога. Колбэки: onState("wait"|"hear"), onLevel(0..1), onDone({f0s}|{error}). */
  async function listen(cb) {
    stop();
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { cb.onDone({ error: "unsupported" }); return; }
    let stream;
    try { stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false } }); }
    catch (e) { cb.onDone({ error: e && (e.name === "NotFoundError" || e.name === "OverconstrainedError") ? "nomic" : "denied" }); return; }
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) { stream.getTracks().forEach((t) => t.stop()); cb.onDone({ error: "unsupported" }); return; }
    const ctx = new AC();
    try { await ctx.resume(); } catch (e) { /* ок */ }
    const src = ctx.createMediaStreamSource(stream), an = ctx.createAnalyser();
    an.fftSize = 4096; src.connect(an);
    const buf = new Float32Array(4096), f0s = [], noise = [];
    const l = live = { stream, ctx, timer: null, done: null, result: null };
    let t0 = Date.now(), started = false, quiet = 0, thr = 0.01;
    l.done = (r) => cb.onDone(r || { error: "none" });
    l.timer = setInterval(() => {
      if (live !== l) return;
      an.getFloatTimeDomainData(buf);
      const frame = buf.subarray(4096 - 2048), lvl = rms(frame), el = Date.now() - t0;
      if (el < 350) { noise.push(lvl); thr = Math.max(0.01, median(noise) * 3); }
      cb.onLevel && cb.onLevel(Math.min(1, lvl / 0.15));
      let f = 0;
      if (el >= 350 && lvl > thr) { const p = detectPitch(frame, ctx.sampleRate); if (p.f0 >= F_MIN && p.f0 <= F_MAX && p.clarity > 0.6) f = p.f0; }
      if (f) { if (!started) { started = true; cb.onState && cb.onState("hear"); } quiet = 0; } else if (started) quiet++;
      if (started) f0s.push(f);
      const fin = started && (quiet >= 20 || f0s.length > 160);
      if (fin || el > 7000) { l.result = started ? { f0s } : { error: "silence" }; stop(); }
    }, HOP_MS);
    cb.onState && cb.onState("wait");
  }
  root.TONES.listen = listen; root.TONES.stop = stop;
})(typeof window !== "undefined" ? window : globalThis);
