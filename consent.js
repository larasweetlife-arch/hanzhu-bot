/* Согласие на обработку данных (v31): полноэкранный экран при первом открытии мини-аппа. Текст приходит с сервера (content_consent.txt). */
(function () {
  "use strict";
  const T = {
    ru: { accept: "Принимаю", decline: "Не согласен(на)", declined: "Без согласия приложение не работает. Можно закрыть его или передумать и нажать «Принимаю».", err: "Не получилось сохранить. Попробуй ещё раз.", load: "Загрузка…" },
    uz: { accept: "Qabul qilaman", decline: "Rozi emasman", declined: "Rozilik bo‘lmasa, ilova ishlamaydi. Uni yopishingiz yoki fikringizni o‘zgartirib, «Qabul qilaman»ni bosishingiz mumkin.", err: "Saqlab bo‘lmadi. Qayta urinib ko‘ring.", load: "Yuklanmoqda…" },
    en: { accept: "Accept", decline: "I do not agree", declined: "The app does not work without consent. You can close it, or change your mind and press “Accept”.", err: "Could not save. Please try again.", load: "Loading…" },
    zh: { accept: "同意", decline: "不同意", declined: "不同意则无法使用本应用。你可以关闭它，或改变主意点击“同意”。", err: "保存失败，请重试。", load: "加载中…" },
  };
  const NAMES = [["ru", "Русский"], ["uz", "O'zbekcha"], ["en", "English"], ["zh", "中文"]];
  const post = (path, body) => window.QY.api(path, body);

  // Показывает экран согласия и ждёт «Принимаю». Если человек отказался, приложение закрывается.
  function ask(first) {
    const { h, S } = window.QY, app = document.getElementById("app");
    let data = first, lang = first.lang, declined = false, busy = false;
    const sp = document.getElementById("splash"); if (sp) sp.classList.add("off");
    return new Promise((resolve) => {
      async function setLang(l) {
        if (l === lang || busy) return;
        busy = true; lang = l; S.lang = l; draw();
        try { data = await post("/api/consent", { lang: l }); } catch (e) { /* оставим прежний текст */ }
        busy = false; draw();
      }
      async function accept() {
        if (busy) return;
        busy = true; draw();
        try { await post("/api/consent/accept", { lang }); S.lang = lang; app.replaceChildren(); resolve(); }
        catch (e) { busy = false; draw(); window.QY.toast(T[lang].err); }
      }
      function decline() {
        declined = true; draw();
        try { window.Telegram.WebApp.close(); } catch (e) { /* в браузере просто покажем сообщение */ }
      }
      function draw() {
        const d = T[lang] || T.ru;
        const body = (data.blocks || []).map((b) => b.t === "h" ? h("h3", { class: "cs-h" }, b.x) : b.t === "li" ? h("div", { class: "cs-li" }, h("span", {}, "·"), h("span", {}, b.x)) : h("p", { class: "cs-p" }, b.x));
        app.replaceChildren(h("div", { class: "cs" },
          h("div", { class: "cs-top" }, h("div", { class: "seal", style: "width:46px;height:46px;font-size:18px" }, "汉\n助"),
            h("div", { class: "seg fill cs-lang" }, NAMES.map(([c, n]) => h("button", { class: c === lang ? "on" : "", onclick: () => setLang(c) }, n)))),
          h("div", { class: "card cs-card" }, body),
          declined ? h("div", { class: "muted cs-note" }, d.declined) : null,
          h("div", { class: "cs-bar" },
            h("button", { class: "btn jade", disabled: busy ? "" : null, onclick: accept }, d.accept),
            h("button", { class: "btn line", onclick: decline }, d.decline))));
      }
      draw();
    });
  }
  window.CONSENT = { ask };
})();
