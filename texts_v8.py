"""
Тексты версии 8: марафон викторины, сдача домашки, и полный китайский перевод всех новых функций
(в v7 китайский брал английский текст).
Подключается в конце texts.py. Если ключа нет в языке, бот берёт русский (у китайского: английский).
"""

P = {}

P["ru"] = {
    "pr_marathon": "🏁 Марафон (100+ вопросов)",
    "mr_pick": "🏁 <b>Марафон викторины</b>\n\nВыбери уровень HSK. HSK 1–3: по 100 вопросов, HSK 4–6: по 150. "
               "Вопросы не повторяются, прогресс сохраняется, продолжать можно в любой день.\n\n✅ пройден   ▶️ начат",
    "mr_resume": "Ты остановился(ась) на вопросе {n} из {total}. Продолжим?", "mr_resume_btn": "▶️ Продолжить",
    "mr_restart_btn": "🔄 Начать заново", "mr_back": "⬅️ К уровням",
    "mr_again_ask": "Этот уровень ты уже прошёл(ла) 🏅 Хочешь пройти ещё раз? Подарок за уровень выдаётся один раз.",
    "mr_q": "<b>HSK {level}</b> · вопрос {n}/{total}\n<code>{bar}</code>\n{prev}\n\n<b>{zh}</b>\n🔊 <code>{py}</code>\n\nЧто это значит?",
    "mr_prev_ok": "✅ {zh} = {right}", "mr_prev_no": "❌ {zh} = {right}",
    "mr_toast_ok": "✅ Верно!", "mr_toast_no": "❌ Правильно: {right}",
    "mr_pause": "⏸ Пауза", "mr_paused": "Прогресс сохранён: {done}/{total}. Продолжить можно в «🎮 Практика» → «🏁 Марафон».",
    "mr_stale": "Вопрос устарел, даю новый.",
    "mr_done": "🎉 <b>Поздравляю!</b>\n\nТы прошёл(ла) марафон <b>HSK {level}</b>: {total} вопросов!\n"
               "Верно: <b>{correct}/{total}</b> ({pct}%)\n🏅 Твоё звание: <b>{title}</b>\n\n"
               "🧧 <b>Пожелание от 茶茶</b>\n<b>{zh}</b>\n<code>{py}</code>\n<i>{meaning}</i>\n\n{wish}",
    "mr_gift": "\n\n🎁 Подарок: +{n} жизней в Чайной лавке на сегодня.",
    "mr_title_hi": "Мастер иероглифов", "mr_title_mid": "Чайный знаток", "mr_title_low": "Упорный путник",
    "mr_share": "📣 Рассказать другу", "mr_share_text": "Я прошёл(ла) марафон HSK {level} в боте 汉助: {correct}/{total}! 🍵",
    "mr_add": "🃏 Ошибки в карточки ({n})", "mr_more": "🏁 Другие уровни",
    # домашка со сдачей
    "hw_submit_btn": "📤 Отправить ДЗ · 提交作业",
    "hw_fmt": "📎 <b>Как отправить домашку</b>\n\n<b>Принимаю:</b>\n· фото тетради или листа (JPG, PNG), можно несколько, каждое отдельным сообщением\n"
              "· файлы PDF и Word (DOC, DOCX)\n· голосовое сообщение или аудио (для устных заданий)\n· обычный текст\n\n"
              "<b>Не принимаю:</b> видео, «кружки», архивы (ZIP, RAR) и другие форматы.\n\n"
              "💡 Фотографируй при хорошем свете, чтобы всё было видно. Файл не больше 20 МБ.",
    "hw_fmt_ok": "✅ Понятно, отправляю", "hw_cancel": "Отмена",
    "hw_send_now": "Присылай по одному сообщению. Когда всё отправишь, нажми «Готово».",
    "hw_got": "Получила: {n}. Можно прислать ещё или нажать «Готово».", "hw_finish": "✅ Готово",
    "hw_bad_fmt": "Этот формат я не принимаю 🙈 Пришли фото, PDF или Word, голосовое сообщение или текст.",
    "hw_empty": "Пока ничего не пришло. Пришли файл или нажми «Отмена».",
    "hw_sent": "Отправила Лазизе! Она посмотрит и ответит 🌿", "hw_cancelled": "Хорошо, отменила.",
    "hw_stale": "Это задание уже закрыто или устарело.", "hw_hint": "Чтобы сдать домашку, нажми «📤 Отправить ДЗ» под заданием (список: /hw).",
    "hw_accepted": "✅ Лазиза приняла твою домашку «{text}». Молодец 👏",
    "hw_redo": "🔁 Лазиза просит доработать домашку «{text}». Она напишет, что исправить.",
}

P["uz"] = {
    "pr_marathon": "🏁 Marafon (100+ savol)",
    "mr_pick": "🏁 <b>Viktorina marafoni</b>\n\nHSK darajasini tanlang. HSK 1–3: 100 tadan, HSK 4–6: 150 tadan savol. "
               "Savollar takrorlanmaydi, natija saqlanadi, istalgan kuni davom ettirish mumkin.\n\n✅ tugatilgan   ▶️ boshlangan",
    "mr_resume": "Siz {total} tadan {n}-savolda to'xtagansiz. Davom etamizmi?", "mr_resume_btn": "▶️ Davom etish",
    "mr_restart_btn": "🔄 Qaytadan boshlash", "mr_back": "⬅️ Darajalarga",
    "mr_again_ask": "Bu darajani allaqachon tugatgansiz 🏅 Yana o'tmoqchimisiz? Daraja uchun sovg'a bir marta beriladi.",
    "mr_q": "<b>HSK {level}</b> · savol {n}/{total}\n<code>{bar}</code>\n{prev}\n\n<b>{zh}</b>\n🔊 <code>{py}</code>\n\nBu nima degani?",
    "mr_prev_ok": "✅ {zh} = {right}", "mr_prev_no": "❌ {zh} = {right}",
    "mr_toast_ok": "✅ To'g'ri!", "mr_toast_no": "❌ To'g'ri javob: {right}",
    "mr_pause": "⏸ Pauza", "mr_paused": "Natija saqlandi: {done}/{total}. «🎮 Mashq» → «🏁 Marafon» orqali davom ettirishingiz mumkin.",
    "mr_stale": "Savol eskirdi, yangisini beraman.",
    "mr_done": "🎉 <b>Tabriklayman!</b>\n\nSiz <b>HSK {level}</b> marafonini tugatdingiz: {total} ta savol!\n"
               "To'g'ri: <b>{correct}/{total}</b> ({pct}%)\n🏅 Unvoningiz: <b>{title}</b>\n\n"
               "🧧 <b>茶茶dan tilak</b>\n<b>{zh}</b>\n<code>{py}</code>\n<i>{meaning}</i>\n\n{wish}",
    "mr_gift": "\n\n🎁 Sovg'a: bugun Choyxona do'konida +{n} jon.",
    "mr_title_hi": "Ieroglif ustasi", "mr_title_mid": "Choy bilimdoni", "mr_title_low": "Sabrli yo'lovchi",
    "mr_share": "📣 Do'stga aytish", "mr_share_text": "Men 汉助 botida HSK {level} marafonini tugatdim: {correct}/{total}! 🍵",
    "mr_add": "🃏 Xatolarni kartochkaga ({n})", "mr_more": "🏁 Boshqa darajalar",
    "hw_submit_btn": "📤 Uy vazifasini yuborish · 提交作业",
    "hw_fmt": "📎 <b>Uy vazifasini qanday yuborish kerak</b>\n\n<b>Qabul qilaman:</b>\n· daftar yoki varaq surati (JPG, PNG), bir nechta bo'lishi mumkin, har biri alohida xabarda\n"
              "· PDF va Word fayllari (DOC, DOCX)\n· ovozli xabar yoki audio (og'zaki topshiriqlar uchun)\n· oddiy matn\n\n"
              "<b>Qabul qilmayman:</b> video, «dumaloq video», arxivlar (ZIP, RAR) va boshqa formatlar.\n\n"
              "💡 Hammasi ko'rinishi uchun yorug'da suratga oling. Fayl 20 MB dan oshmasin.",
    "hw_fmt_ok": "✅ Tushundim, yuboraman", "hw_cancel": "Bekor qilish",
    "hw_send_now": "Bittadan xabar qilib yuboring. Hammasini yuborgach, «Tayyor»ni bosing.",
    "hw_got": "Qabul qildim: {n}. Yana yuborishingiz yoki «Tayyor»ni bosishingiz mumkin.", "hw_finish": "✅ Tayyor",
    "hw_bad_fmt": "Bu formatni qabul qilmayman 🙈 Surat, PDF yoki Word, ovozli xabar yoki matn yuboring.",
    "hw_empty": "Hozircha hech narsa kelmadi. Fayl yuboring yoki «Bekor qilish»ni bosing.",
    "hw_sent": "Lazizaga yubordim! U ko'rib chiqib, javob beradi 🌿", "hw_cancelled": "Mayli, bekor qildim.",
    "hw_stale": "Bu topshiriq yopilgan yoki eskirgan.", "hw_hint": "Uy vazifasini topshirish uchun topshiriq ostidagi «📤 Uy vazifasini yuborish» tugmasini bosing (ro'yxat: /hw).",
    "hw_accepted": "✅ Laziza «{text}» uy vazifangizni qabul qildi. Barakalla 👏",
    "hw_redo": "🔁 Laziza «{text}» uy vazifasini qayta ishlashni so'raydi. Nimani to'g'rilashni yozadi.",
}

P["en"] = {
    "pr_marathon": "🏁 Marathon (100+ questions)",
    "mr_pick": "🏁 <b>Quiz marathon</b>\n\nPick an HSK level. HSK 1–3: 100 questions each, HSK 4–6: 150 each. "
               "Questions never repeat, progress is saved, and you can continue on any day.\n\n✅ completed   ▶️ started",
    "mr_resume": "You stopped at question {n} of {total}. Continue?", "mr_resume_btn": "▶️ Continue",
    "mr_restart_btn": "🔄 Start over", "mr_back": "⬅️ Back to levels",
    "mr_again_ask": "You've already completed this level 🏅 Want to run it again? The level gift is given only once.",
    "mr_q": "<b>HSK {level}</b> · question {n}/{total}\n<code>{bar}</code>\n{prev}\n\n<b>{zh}</b>\n🔊 <code>{py}</code>\n\nWhat does it mean?",
    "mr_prev_ok": "✅ {zh} = {right}", "mr_prev_no": "❌ {zh} = {right}",
    "mr_toast_ok": "✅ Correct!", "mr_toast_no": "❌ Correct answer: {right}",
    "mr_pause": "⏸ Pause", "mr_paused": "Progress saved: {done}/{total}. Continue from “🎮 Practice” → “🏁 Marathon”.",
    "mr_stale": "That question expired, here is a new one.",
    "mr_done": "🎉 <b>Congratulations!</b>\n\nYou finished the <b>HSK {level}</b> marathon: {total} questions!\n"
               "Correct: <b>{correct}/{total}</b> ({pct}%)\n🏅 Your title: <b>{title}</b>\n\n"
               "🧧 <b>A wish from 茶茶</b>\n<b>{zh}</b>\n<code>{py}</code>\n<i>{meaning}</i>\n\n{wish}",
    "mr_gift": "\n\n🎁 Gift: +{n} lives in the Tea shop today.",
    "mr_title_hi": "Master of characters", "mr_title_mid": "Tea connoisseur", "mr_title_low": "Persistent traveller",
    "mr_share": "📣 Tell a friend", "mr_share_text": "I finished the HSK {level} marathon in the 汉助 bot: {correct}/{total}! 🍵",
    "mr_add": "🃏 Mistakes to flashcards ({n})", "mr_more": "🏁 Other levels",
    "hw_submit_btn": "📤 Submit homework · 提交作业",
    "hw_fmt": "📎 <b>How to submit homework</b>\n\n<b>Accepted:</b>\n· photos of a notebook or sheet (JPG, PNG), several are fine, one per message\n"
              "· PDF and Word files (DOC, DOCX)\n· a voice message or audio (for speaking tasks)\n· plain text\n\n"
              "<b>Not accepted:</b> video, round video messages, archives (ZIP, RAR) and other formats.\n\n"
              "💡 Take photos in good light so everything is readable. File size up to 20 MB.",
    "hw_fmt_ok": "✅ Got it, sending", "hw_cancel": "Cancel",
    "hw_send_now": "Send them one message at a time. When you're done, tap “Done”.",
    "hw_got": "Received: {n}. You can send more or tap “Done”.", "hw_finish": "✅ Done",
    "hw_bad_fmt": "I can't accept that format 🙈 Please send a photo, PDF or Word file, a voice message or text.",
    "hw_empty": "Nothing has arrived yet. Send a file or tap “Cancel”.",
    "hw_sent": "Sent to Laziza! She'll take a look and reply 🌿", "hw_cancelled": "OK, cancelled.",
    "hw_stale": "This task is closed or has expired.", "hw_hint": "To submit homework, tap “📤 Submit homework” under the task (list: /hw).",
    "hw_accepted": "✅ Laziza accepted your homework “{text}”. Well done 👏",
    "hw_redo": "🔁 Laziza asks you to rework the homework “{text}”. She'll write what to fix.",
}

P["zh"] = {
    # --- v8: марафон и сдача домашки ---
    "pr_marathon": "🏁 马拉松（100+ 题）",
    "mr_pick": "🏁 <b>测验马拉松</b>\n\n选择 HSK 等级。HSK 1–3 各 100 题，HSK 4–6 各 150 题。题目不会重复，进度会保存，随时可以接着做。\n\n✅ 已完成   ▶️ 已开始",
    "mr_resume": "你停在第 {n}/{total} 题。继续吗？", "mr_resume_btn": "▶️ 继续",
    "mr_restart_btn": "🔄 重新开始", "mr_back": "⬅️ 返回等级",
    "mr_again_ask": "这个等级你已经完成了 🏅 想再做一遍吗？每个等级的礼物只发一次。",
    "mr_q": "<b>HSK {level}</b> · 第 {n}/{total} 题\n<code>{bar}</code>\n{prev}\n\n<b>{zh}</b>\n🔊 <code>{py}</code>\n\n这是什么意思？",
    "mr_prev_ok": "✅ {zh} = {right}", "mr_prev_no": "❌ {zh} = {right}",
    "mr_toast_ok": "✅ 答对了！", "mr_toast_no": "❌ 正确答案：{right}",
    "mr_pause": "⏸ 暂停", "mr_paused": "进度已保存：{done}/{total}。在“🎮 练习” → “🏁 马拉松”里可以继续。",
    "mr_stale": "这道题已过期，给你一道新的。",
    "mr_done": "🎉 <b>恭喜你！</b>\n\n你完成了 <b>HSK {level}</b> 马拉松：共 {total} 题！\n"
               "答对：<b>{correct}/{total}</b>（{pct}%）\n🏅 你的称号：<b>{title}</b>\n\n"
               "🧧 <b>茶茶的祝福</b>\n<b>{zh}</b>\n<code>{py}</code>\n<i>{meaning}</i>\n\n{wish}",
    "mr_gift": "\n\n🎁 礼物：今天茶铺里 +{n} 条命。",
    "mr_title_hi": "汉字大师", "mr_title_mid": "品茶行家", "mr_title_low": "坚持的旅人",
    "mr_share": "📣 告诉朋友", "mr_share_text": "我在汉助机器人里完成了 HSK {level} 马拉松：{correct}/{total}！🍵",
    "mr_add": "🃏 错题加入单词卡（{n}）", "mr_more": "🏁 其他等级",
    "hw_submit_btn": "📤 提交作业",
    "hw_fmt": "📎 <b>如何提交作业</b>\n\n<b>可以接收：</b>\n· 笔记本或试卷的照片（JPG、PNG），可以发多张，每张单独一条消息\n"
              "· PDF 和 Word 文件（DOC、DOCX）\n· 语音消息或音频（口语作业）\n· 普通文字\n\n"
              "<b>不能接收：</b>视频、圆形视频、压缩包（ZIP、RAR）和其他格式。\n\n"
              "💡 请在光线好的地方拍照，保证看得清楚。文件不超过 20 MB。",
    "hw_fmt_ok": "✅ 明白了，开始发送", "hw_cancel": "取消",
    "hw_send_now": "请一条消息发一个。全部发完后，点“完成”。",
    "hw_got": "已收到：{n}。可以继续发送，或点“完成”。", "hw_finish": "✅ 完成",
    "hw_bad_fmt": "这个格式我不能接收 🙈 请发照片、PDF 或 Word 文件、语音消息或文字。",
    "hw_empty": "还没有收到任何内容。请发送文件，或点“取消”。",
    "hw_sent": "已发给 Laziza！她看完会回复你 🌿", "hw_cancelled": "好的，已取消。",
    "hw_stale": "这个作业已关闭或已过期。", "hw_hint": "要提交作业，请点作业下方的“📤 提交作业”（列表：/hw）。",
    "hw_accepted": "✅ Laziza 已收到并通过了你的作业“{text}”。做得好 👏",
    "hw_redo": "🔁 Laziza 请你修改作业“{text}”。她会告诉你要改哪里。",
    # --- v7: полный перевод (раньше был английский) ---
    "pr_title": "练点什么？",
    "qz_q": "<b>第 {n}/{total} 题</b>\n\n<b>{zh}</b>\n🔊 <code>{py}</code>\n\n这是什么意思？",
    "qz_right": "✅ 答对了！", "qz_wrong": "❌ 不太对。正确答案：<b>{right}</b>",
    "qz_end": "本轮结束：<b>{score}/{total}</b> {emoji}", "qz_mistakes": "还需要再看看：",
    "qz_again": "🔁 再来一轮", "qz_add": "🃏 错题加入单词卡", "qz_added": "已加入单词卡的词：{n}",
    "qz_stale": "这一轮已过期，请再点一次“小测验”。", "qz_fail": "暂时出不了题，请稍后再试。",
    "fc_front": "🃏 <b>{zh}</b>\n🔊 <code>{py}</code>\n\n先回忆意思，再点“显示”。",
    "fc_show": "👀 显示", "fc_know": "✅ 我会了", "fc_again": "🔁 再来一次",
    "fc_back": "🃏 <b>{zh}</b>  <code>{py}</code>\n📖 {meaning}",
    "fc_done": "今天就到这里 🎉 记住了：{known}/{total}。明天再来，复习会自动安排。",
    "fc_new": "已为你的卡组添加新词：{n}", "fc_stale": "这张卡已过期，请再点一次“单词卡”。",
    "tea_intro": "🍵 <b>茶铺</b>\n\n顾客用中文点单，你来上对应的茶和茶具。"
                 "答对：+1 金币。答错：−1 条命，这个词稍后会再出现。\n\n"
                 "❤️ 今天的命数：{lives}\n🪙 金币：{coins}\n{emoji} {title}",
    "tea_start": "▶️ 开门营业",
    "tea_order": "🏮 <b>顾客说：</b>\n\n<b>{zh}</b>\n🔊 <code>{py}</code>\n\n上什么？   ❤️ {lives}",
    "tea_right": "✅ 答对了！+{coins} 🪙", "tea_wrong": "❌ 不对。应该是：<b>{right}</b>\n❤️ 剩余命数：{lives}",
    "tea_closed": "🏮 今天茶铺打烊了：命用完了。明天又有 {max} 条。现在可以去做小测验或单词卡。",
    "tea_levelup": "🎉 新称号：{emoji} {title}！", "tea_next": "➡️ 下一位顾客", "tea_stop": "🚪 离开",
    "tea_stale": "这个订单已过期，请再点一次“茶铺”。",
    "title0": "柜台新手", "title1": "茶师助手", "title2": "茶铺老板", "title3": "茶艺大师", "title4": "茶道导师",
    "trial_ask": "第一节试听课免费 🌿 请告诉我你方便的日期和时间，再简单介绍一下自己：年龄、想学什么"
                 "（例如：“周一到周三 18:00 以后，成人，零基础”）。我会转告 Laziza。",
    "trial_sent": "已转告 Laziza！她会联系你 🌿",
    "trial_students": "你已经在 Laziza 的学员名单里了，不需要试听课 😉 有问题直接给我留言就行。",
    "friend_text": "🎁 <b>邀请朋友</b>\n\n你的专属链接：\n<code>{link}</code>\n\n"
                   "<b>你可以得到：</b>\n{rewards}\n\n你的朋友第一节试听课免费。\n\n"
                   "通过你的链接加入：{joined} · 预约试听：{trial} · 开始上课：{paid}",
    "ref_r1": "🎟 朋友启动机器人：今天茶铺里 +3 条命",
    "ref_r2": "🖌 朋友预约试听课：Laziza 送你一个中文名和一张书法卡片",
    "ref_r3": "🎁 朋友开始上课：赠送一节 30 分钟的口语课",
    "ref_welcome": "{name} 邀请了你 🌿 Laziza 的第一节试听课免费：点菜单里的“📝 试听课”。",
    "ref_got1": "🎉 你的朋友 {friend} 启动了机器人！\n{reward}",
    "ref_got2": "🎉 你的朋友 {friend} 预约了试听课！\n{reward}\nLaziza 很快会联系你。",
    "ref_got3": "🎉 你的朋友 {friend} 开始上课了！\n{reward}\nLaziza 很快会联系你。",
    "hw_new": "📚 <b>新作业</b>\n\n{text}\n\n截止：{due}", "hw_btn": "✅ 已完成",
    "hw_thanks": "太棒了！Laziza 会看到的 👏", "hw_none": "没有未完成的作业 🎉",
    "hw_title": "📚 <b>作业</b>", "hw_nodue": "无截止日期",
    "hw_remind": "⏰ 提醒：作业“{text}”今天截止。",
    "mv_btn": "🔄 调整上课时间",
    "mv_ask": "你什么时候方便？请这样写：<code>чт 17:30</code>（周四 17:30）或 <code>15.10 17:30</code>。\n要调整的课：{when}",
    "mv_bad": "没看懂这个时间。例如：<code>чт 17:30</code> 或 <code>15.10 17:30</code>。",
    "mv_sent": "已发给 Laziza。她回复后我会告诉你 🌿",
    "mv_ok": "✅ 课程已调整：{when}", "mv_no": "这个时间不行。Laziza 会告诉你可以改到什么时候 🌿",
    "mv_none": "没有找到最近的课。",
    "rv_ask": "你已经上了 {n} 节课 🌿 请给课程打个分（1 到 5）：",
    "rv_text": "谢谢！再写几句：喜欢什么，哪里可以更好（不想写就发“-”）。",
    "rv_public": "可以在帖子里展示你的评价吗（不带姓氏）？", "rv_yes": "可以", "rv_no": "不可以",
    "rv_thanks": "谢谢！💛",
}

# Пожелания в конце марафона: чэнъюй уровня + значение + пожелание на каждом языке
WISHES = {
    1: ("千里之行，始于足下", "qiān lǐ zhī xíng, shǐ yú zú xià",
        {"ru": ("Путь в тысячу ли начинается с первого шага.", "Первый уровень позади, и самый трудный шаг сделан. Пусть дальше идётся легко 🍵"),
         "uz": ("Ming li yo'l birinchi qadamdan boshlanadi.", "Birinchi daraja ortda, eng qiyin qadam tashlandi. Davomi oson bo'lsin 🍵"),
         "en": ("A journey of a thousand miles begins with a single step.", "Level one is behind you, and the hardest step is done. May the rest come easily 🍵"),
         "zh": ("千里的路程，是从第一步开始的。", "第一关已经过去，最难的一步你已经迈出。愿接下来一路顺利 🍵")}),
    2: ("持之以恒", "chí zhī yǐ héng",
        {"ru": ("Упорно и неуклонно, не бросая начатое.", "Упорство делает своё дело: слова уже начинают складываться во фразы 🌿"),
         "uz": ("Qat'iyat bilan, boshlaganni tashlamay.", "Qat'iyat o'z ishini qiladi: so'zlar endi iboralarga aylana boshladi 🌿"),
         "en": ("To persevere steadily without giving up.", "Perseverance pays off: words are already starting to become phrases 🌿"),
         "zh": ("坚持不懈，长久地做下去。", "坚持是有回报的：单词已经开始连成句子了 🌿")}),
    3: ("学而不厌", "xué ér bù yàn",
        {"ru": ("Учиться и не уставать от учения.", "Ты любишь учиться, и это видно. Пусть эта любовь остаётся с тобой 🍃"),
         "uz": ("O'rganib, o'rganishdan charchamaslik.", "Siz o'rganishni yaxshi ko'rasiz, bu seziladi. Bu muhabbat doim siz bilan bo'lsin 🍃"),
         "en": ("To learn and never tire of learning.", "You love learning, and it shows. May that love stay with you 🍃"),
         "zh": ("学习而不厌倦。", "你爱学习，这一点看得出来。愿这份热爱一直陪着你 🍃")}),
    4: ("日积月累", "rì jī yuè lěi",
        {"ru": ("День за днём, месяц за месяцем: понемногу накапливается многое.", "Слово за словом, день за днём. Из этих маленьких шагов складывается свободная речь 🏮"),
         "uz": ("Kun sayin, oy sayin: oz-ozdan ko'p narsa to'planadi.", "So'zma-so'z, kunma-kun. Mana shu kichik qadamlardan erkin nutq tug'iladi 🏮"),
         "en": ("Day by day, month by month: little by little, much is gathered.", "Word by word, day by day. Free speech is built from these small steps 🏮"),
         "zh": ("一天一天、一月一月地积累。", "一个词一个词，一天一天。自如的表达就是由这些小步子积累出来的 🏮")}),
    5: ("融会贯通", "róng huì guàn tōng",
        {"ru": ("Соединить знания воедино и понять предмет насквозь.", "Ты уже глубоко чувствуешь язык. Пусть всё выученное сложится в одну цельную картину 🍵"),
         "uz": ("Bilimlarni birlashtirib, mavzuni to'liq anglash.", "Siz tilni chuqur his qilyapsiz. O'rganganlaringiz bir butun manzaraga aylansin 🍵"),
         "en": ("To combine everything you know and understand it thoroughly.", "You already feel the language deeply. May everything you've learned come together as one picture 🍵"),
         "zh": ("把所学的知识融合起来，彻底弄懂。", "你已经对这门语言有了很深的体会。愿所学的一切汇成一幅完整的画面 🍵")}),
    6: ("学无止境", "xué wú zhǐ jìng",
        {"ru": ("У учения нет предела.", "У учёбы нет конца, и в этом её радость. Пусть в китайском тебе всегда будет интересно 🏆"),
         "uz": ("O'rganishning chegarasi yo'q.", "O'rganishning oxiri yo'q, quvonchi ham shunda. Xitoy tili sizga doim qiziq bo'lsin 🏆"),
         "en": ("There is no limit to learning.", "Learning has no end, and that is its joy. May Chinese always stay interesting for you 🏆"),
         "zh": ("学习没有止境。", "学无止境，这正是学习的乐趣。愿汉语永远让你觉得有趣 🏆")}),
}
