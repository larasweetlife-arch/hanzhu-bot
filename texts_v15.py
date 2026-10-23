"""
Тексты версии 24 для пользователей (4 языка): объявления (ads.py) и сообщения от 茶茶 (chacha.py).
Отдельно от texts.py, чтобы не пересекаться с остальными ключами. Нужного языка нет → берём русский.
Тексты 茶茶 (BANK) — банк напоминаний: 3 вида (утро, день, вечер) по 4 варианта на язык.
{name} — имя человека; если имени нет, подставляется слово из CC[lang]["friend"].
"""

AD = {}
CC = {}
BANK = {}

# ─── ОБЪЯВЛЕНИЯ ───────────────────────────────────────────────────────────────

AD["ru"] = {
    "label": "Реклама",
    "ask": "📢 Пришли текст объявления (от {min} до {max} знаков). Оно уйдёт пользователям бота с пометкой «Реклама».\n\n"
           "Сначала я покажу, как оно будет выглядеть, и цену. Нельзя рекламировать то, что запрещено законом, товары и услуги 18+, обман и сбор денег без объяснений.",
    "short": "Слишком коротко. Напиши хотя бы пару предложений.",
    "long": "Слишком длинно: до {max} знаков. Сократи, пожалуйста.",
    "head": "Так увидят ваше объявление:",
    "pick": "Кому показать объявление? Выбери аудиторию:",
    "a_all": "Все", "a_stu": "Ученики", "a_non": "Не ученики",
    "zero": "Сейчас в этой аудитории нет получателей. Выбери другую.",
    "price": "Аудитория: <b>{aud}</b>, примерно {n} чел.\nЦена: <b>{price} ⭐</b>{disc}\n\n"
             "Объявление сначала проверяет Лазиза. Если оно не подойдёт, звёзды вернутся.",
    "disc": " (скидка {pct}% для репетиторов на «Про»)",
    "pay": "⭐ Оплатить {price}",
    "cancel": "Отмена",
    "cancelled": "Хорошо, отменено.",
    "inv_title": "Объявление в боте 汉助",
    "inv_desc": "Рассылка вашего объявления пользователям бота",
    "paid": "✅ Оплата получена. Объявление ушло на проверку Лазизе, обычно она отвечает в течение дня. "
            "Как только оно уйдёт, я напишу. Если не подойдёт, звёзды вернутся автоматически.",
    "sent": "📢 Ваше объявление отправлено, дошло до {n} чел.",
    "rejected": "Объявление не прошло проверку, звёзды ({stars} ⭐) возвращены. Если есть вопросы, напиши Лазизе.",
    "nostars": "Оплата звёздами сейчас недоступна. Попробуй позже.",
    "bad": "Не получилось оформить оплату. Попробуй ещё раз позже.",
}
AD["uz"] = {
    "label": "Reklama",
    "ask": "📢 E'lon matnini yuboring ({min}–{max} belgi). U bot foydalanuvchilariga «Reklama» belgisi bilan yuboriladi.\n\n"
           "Avval e'lon qanday ko'rinishini va narxini ko'rsataman. Qonun taqiqlagan narsalar, 18+ mahsulot va xizmatlar, aldov va tushuntirishsiz pul yig'ishni reklama qilib bo'lmaydi.",
    "short": "Juda qisqa. Kamida bir-ikki gap yozing.",
    "long": "Juda uzun: {max} belgigacha. Qisqartiring, iltimos.",
    "head": "E'loningiz shunday ko'rinadi:",
    "pick": "E'lonni kimlarga ko'rsatamiz? Auditoriyani tanlang:",
    "a_all": "Hamma", "a_stu": "O'quvchilar", "a_non": "O'quvchi bo'lmaganlar",
    "zero": "Bu auditoriyada hozircha qabul qiluvchi yo'q. Boshqasini tanlang.",
    "price": "Auditoriya: <b>{aud}</b>, taxminan {n} kishi.\nNarxi: <b>{price} ⭐</b>{disc}\n\n"
             "E'lonni avval Laziza tekshiradi. Mos kelmasa, yulduzlar qaytariladi.",
    "disc": " («Pro» darajasidagi repetitorlar uchun {pct}% chegirma)",
    "pay": "⭐ {price} to'lash",
    "cancel": "Bekor qilish",
    "cancelled": "Xo'p, bekor qilindi.",
    "inv_title": "汉助 botida e'lon",
    "inv_desc": "E'loningizni bot foydalanuvchilariga yuborish",
    "paid": "✅ To'lov qabul qilindi. E'lon Lazizaga tekshiruvga yuborildi, odatda u bir kun ichida javob beradi. "
            "E'lon yuborilgach, sizga yozaman. Mos kelmasa, yulduzlar avtomatik qaytariladi.",
    "sent": "📢 E'loningiz yuborildi, {n} kishiga yetib bordi.",
    "rejected": "E'lon tekshiruvdan o'tmadi, yulduzlar ({stars} ⭐) qaytarildi. Savollar bo'lsa, Lazizaga yozing.",
    "nostars": "Yulduzlar bilan to'lov hozir mavjud emas. Keyinroq urinib ko'ring.",
    "bad": "To'lovni rasmiylashtirib bo'lmadi. Keyinroq yana urinib ko'ring.",
}
AD["en"] = {
    "label": "Ad",
    "ask": "📢 Send the text of your ad ({min}–{max} characters). It will go to the bot's users marked «Ad».\n\n"
           "First I will show how it will look and the price. You cannot advertise anything illegal, 18+ goods or services, scams, or fundraising without explanation.",
    "short": "Too short. Please write at least a couple of sentences.",
    "long": "Too long: up to {max} characters. Please shorten it.",
    "head": "This is how your ad will look:",
    "pick": "Who should see the ad? Choose the audience:",
    "a_all": "Everyone", "a_stu": "Students", "a_non": "Non-students",
    "zero": "There are no recipients in this audience right now. Choose another.",
    "price": "Audience: <b>{aud}</b>, about {n} people.\nPrice: <b>{price} ⭐</b>{disc}\n\n"
             "Laziza reviews the ad before it is sent. If it does not fit, the Stars are refunded.",
    "disc": " ({pct}% discount for tutors on «Pro»)",
    "pay": "⭐ Pay {price}",
    "cancel": "Cancel",
    "cancelled": "Okay, cancelled.",
    "inv_title": "Ad in the 汉助 bot",
    "inv_desc": "Sending your ad to the bot's users",
    "paid": "✅ Payment received. The ad has gone to Laziza for review; she usually answers within a day. "
            "I will write as soon as it is sent. If it does not fit, the Stars are refunded automatically.",
    "sent": "📢 Your ad has been sent and reached {n} people.",
    "rejected": "The ad did not pass review and the Stars ({stars} ⭐) were refunded. If you have questions, write to Laziza.",
    "nostars": "Payment with Stars is unavailable right now. Please try later.",
    "bad": "Could not create the payment. Please try again later.",
}
AD["zh"] = {
    "label": "广告",
    "ask": "📢 请发送广告文字（{min}–{max} 个字符）。它会带着“广告”标记发给机器人的用户。\n\n"
           "我会先给你看效果和价格。不能推广违法内容、18+ 商品或服务、欺诈，以及不说明用途的募捐。",
    "short": "太短了，请至少写两句话。",
    "long": "太长了：最多 {max} 个字符，请精简一下。",
    "head": "你的广告会这样显示：",
    "pick": "要给谁看？请选择受众：",
    "a_all": "所有人", "a_stu": "学生", "a_non": "非学生",
    "zero": "这个受众目前没有可发送的人，请换一个。",
    "price": "受众：<b>{aud}</b>，约 {n} 人。\n价格：<b>{price} ⭐</b>{disc}\n\n"
             "广告发送前由 Laziza 审核。如果不通过，星星会退还。",
    "disc": "（“Pro”级老师享 {pct}% 折扣）",
    "pay": "⭐ 支付 {price}",
    "cancel": "取消",
    "cancelled": "好的，已取消。",
    "inv_title": "汉助机器人广告",
    "inv_desc": "向机器人用户发送你的广告",
    "paid": "✅ 已收到付款。广告已提交给 Laziza 审核，通常一天内回复。发出后我会通知你。如果不通过，星星会自动退还。",
    "sent": "📢 你的广告已发送，共送达 {n} 人。",
    "rejected": "广告未通过审核，星星（{stars} ⭐）已退还。如有疑问请联系 Laziza。",
    "nostars": "目前无法使用星星支付，请稍后再试。",
    "bad": "无法创建付款，请稍后再试。",
}

# ─── 茶茶: интерфейс ──────────────────────────────────────────────────────────

CC["ru"] = {
    "friend": "друг",
    "ask": "Привет! Я 茶茶 🍵 Хочу иногда напоминать тебе о китайском, но так, чтобы не надоедать. "
           "Ночью (с 22:00 до 09:00) я не пишу.\n\nКак часто мне заглядывать?",
    "f0": "Не писать", "f1": "1 раз в день", "f2": "2 раза в день", "f3": "3 раза в день",
    "cfg_title": "⚙️ <b>Как часто писать</b>\n\nСейчас: <b>{cur}</b>. Ночью (с 22:00 до 09:00) я не пишу.",
    "saved": "Хорошо, запомнил: {cur} 🌿",
    "go": "🍵 Позаниматься", "cfg": "⚙️ Как часто писать",
    "cut": "Кажется, сейчас не до меня. Буду писать реже 🌿 Если захочешь иначе, нажми /chacha.",
    "stop": "Хорошо, я помолчу. Захочешь, чтобы я снова напоминал о себе, нажми /chacha 🍵",
}
CC["uz"] = {
    "friend": "do'st",
    "ask": "Salom! Men 茶茶 🍵 Ba'zan sizga xitoy tilini eslatib turmoqchiman, lekin zeriktirmasdan. "
           "Kechasi (22:00 dan 09:00 gacha) yozmayman.\n\nQanchalik tez-tez yozay?",
    "f0": "Yozma", "f1": "Kuniga 1 marta", "f2": "Kuniga 2 marta", "f3": "Kuniga 3 marta",
    "cfg_title": "⚙️ <b>Qanchalik tez-tez yozay</b>\n\nHozir: <b>{cur}</b>. Kechasi (22:00 dan 09:00 gacha) yozmayman.",
    "saved": "Xo'p, eslab qoldim: {cur} 🌿",
    "go": "🍵 Mashq qilish", "cfg": "⚙️ Qanchalik tez-tez yozay",
    "cut": "Hozir menga vaqt yo'qdek. Kamroq yozaman 🌿 Boshqacha xohlasangiz, /chacha ni bosing.",
    "stop": "Xo'p, jim turaman. Yana eslatib turishimni xohlasangiz, /chacha ni bosing 🍵",
}
CC["en"] = {
    "friend": "friend",
    "ask": "Hi! I'm 茶茶 🍵 I'd like to remind you about Chinese now and then, without being annoying. "
           "I don't write at night (22:00 to 09:00).\n\nHow often should I drop by?",
    "f0": "Don't write", "f1": "Once a day", "f2": "Twice a day", "f3": "3 times a day",
    "cfg_title": "⚙️ <b>How often I write</b>\n\nNow: <b>{cur}</b>. I don't write at night (22:00 to 09:00).",
    "saved": "Got it: {cur} 🌿",
    "go": "🍵 Practice", "cfg": "⚙️ How often to write",
    "cut": "Looks like you're busy right now. I'll write less often 🌿 If you'd like it differently, press /chacha.",
    "stop": "Okay, I'll stay quiet. If you want me to remind you again, press /chacha 🍵",
}
CC["zh"] = {
    "friend": "朋友",
    "ask": "你好！我是茶茶 🍵 我想偶尔提醒你学中文，但不会打扰你。晚上（22:00 到 09:00）我不发消息。\n\n我多久来看你一次？",
    "f0": "不要发", "f1": "每天 1 次", "f2": "每天 2 次", "f3": "每天 3 次",
    "cfg_title": "⚙️ <b>提醒频率</b>\n\n当前：<b>{cur}</b>。晚上（22:00 到 09:00）我不发消息。",
    "saved": "好的，记住了：{cur} 🌿",
    "go": "🍵 去练习", "cfg": "⚙️ 提醒频率",
    "cut": "你现在好像比较忙，我会少发一些 🌿 想改的话，点 /chacha。",
    "stop": "好的，我先安静。想让我再提醒你，点 /chacha 🍵",
}

# ─── 茶茶: банк сообщений ─────────────────────────────────────────────────────

BANK["ru"] = {
    "morning": [
        "Доброе утро, {name}! Я 茶茶 🍵 Заварил чай. Давай одно слово на сегодня?",
        "{name}, утро — лучшее время для пары новых слов. Две минуты, и день уже не зря 🌿",
        "Чай готов ☕ Загляни на пару минут, {name}: слово дня уже ждёт.",
        "Доброе утро 🌞 Иероглиф сам себя не выучит, но я рядом. Минутка найдётся?",
    ],
    "day": [
        "Небольшая пауза на чай? Одна карточка, и можно дальше по делам 🍵",
        "{name}, лучше всего запоминаются короткие повторы. Давай одну минутку?",
        "Я тут немного скучаю без твоих слов 🙈 Загляни ненадолго.",
        "Помнишь слово, которое учили в прошлый раз? Давай проверим, как оно читается 🍵",
    ],
    "evening": [
        "Добрый вечер, {name}! Если сегодня ещё не было занятий, хватит и пяти минут 🌙",
        "Чай ещё тёплый. Пять минут повторения, и сегодняшний день засчитан 🍵",
        "Пара слов перед сном запоминается особенно хорошо 🌙 Заглянешь, {name}?",
        "{name}, я загляну завтра. А сегодня успеем быструю минутку повторения?",
    ],
}
BANK["uz"] = {
    "morning": [
        "Xayrli tong, {name}! Men 茶茶 🍵 Choy damladim. Bugun bitta so'z o'rganamizmi?",
        "{name}, ertalab bir-ikki yangi so'z o'rganish uchun eng yaxshi vaqt. Ikki daqiqa, kun bejiz o'tmaydi 🌿",
        "Choy tayyor ☕ {name}, bir-ikki daqiqaga kirib o'ting: kun so'zi kutyapti.",
        "Xayrli tong 🌞 Ieroglif o'zi yodlanmaydi, lekin men yoningizdaman. Bir daqiqa topiladimi?",
    ],
    "day": [
        "Choy uchun biroz tanaffus qilamizmi? Bitta kartochka va ishingizni davom ettirishingiz mumkin 🍵",
        "{name}, eng yaxshi qisqa takrorlar yodda qoladi. Bir daqiqa mashq qilamizmi?",
        "Men sizning so'zlaringizni sog'indim 🙈 Biroz kirib o'ting.",
        "Oxirgi marta o'rgangan so'zingiz esingizdami? Qanday o'qilishini tekshirib ko'ramiz 🍵",
    ],
    "evening": [
        "Xayrli kech, {name}! Bugun hali mashq qilmagan bo'lsangiz, besh daqiqa ham yetadi 🌙",
        "Choy hali iliq. Besh daqiqa takrorlash, va bugungi kun hisobga olinadi 🍵",
        "Uxlashdan oldin bir-ikki so'z ayniqsa yaxshi yodda qoladi 🌙 Kirasizmi, {name}?",
        "{name}, ertaga yana kelaman. Bugun esa tez bir daqiqa takrorlashga ulguramizmi?",
    ],
}
BANK["en"] = {
    "morning": [
        "Good morning, {name}! I'm 茶茶 🍵 I've brewed some tea. Shall we learn one word today?",
        "{name}, morning is the best time for a couple of new words. Two minutes and the day is already well spent 🌿",
        "The tea is ready ☕ Drop in for a couple of minutes, {name}: the word of the day is waiting.",
        "Good morning 🌞 A character won't learn itself, but I'm here. Got a minute?",
    ],
    "day": [
        "A little tea break? One card and you can get back to your day 🍵",
        "{name}, short reviews stick best. Want to do one minute?",
        "I'm missing your words a little 🙈 Drop by for a moment.",
        "Remember the word you learned last time? Let's check how it's read 🍵",
    ],
    "evening": [
        "Good evening, {name}! If you haven't practiced today, five minutes is enough 🌙",
        "The tea is still warm. Five minutes of review and today counts 🍵",
        "A couple of words before bed stick especially well 🌙 Will you drop by, {name}?",
        "{name}, I'll stop by tomorrow. But can we squeeze in a quick minute of review today?",
    ],
}
BANK["zh"] = {
    "morning": [
        "早上好，{name}！我是茶茶 🍵 茶已经泡好了，今天学一个词好吗？",
        "{name}，早晨最适合学几个新词。两分钟，这一天就没白过 🌿",
        "茶好了 ☕ {name}，来坐几分钟吧，今日一词在等你。",
        "早上好 🌞 汉字不会自己跑进脑子里，不过我陪着你。有一分钟吗？",
    ],
    "day": [
        "喝杯茶休息一下？做一张卡片，然后继续忙你的 🍵",
        "{name}，短时间的复习最容易记住。来一分钟好吗？",
        "没有你的词我有点想念 🙈 来看看吧。",
        "还记得上次学的那个词吗？我们看看怎么读 🍵",
    ],
    "evening": [
        "晚上好，{name}！如果今天还没学习，五分钟就够了 🌙",
        "茶还是温的。复习五分钟，今天就算完成 🍵",
        "睡前学几个词，特别容易记住 🌙 {name}，来一下吗？",
        "{name}，我明天再来。不过今天能不能先复习一分钟？",
    ],
}
