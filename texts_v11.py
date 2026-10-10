"""
Тексты версии 11: игра «Путешествие с Чачей», оплата Telegram Stars, поддержка проекта.
Подключается в конце texts.py. Реквизиты для поддержки не вшиты: они берутся из переменных DONATE_INFO и DONATE_URL.
"""

P = {}

P["ru"] = {
    "qt_title": "🏆 <b>Рейтинг игры · эта неделя</b>", "qt_empty": "Пока никого в рейтинге. Пройди сцену в игре, и ты будешь первым(ой) 🍵", "qt_you": "ты",
    "pz_win": "🎉 <b>Ты победил(а) в розыгрыше!</b>\n\nДля тебя нарисуем <b>уникальный наряд</b> для героя в игре «Путешествие с Чачей». Он будет только у тебя.\n\nНапиши мне прямо сюда, каким он должен быть: цвета, образ, детали, любимые мотивы. Сообщение придёт Ларе 🍵",
    "b_donate": "💝 Поддержать проект",
    "pr_quest": "🗺 Путешествие с Чачей",
    "dn_text": "💝 <b>Поддержать проект</b>\n\nЭтого бота и игру делает один человек, чтобы китайский стал ближе и интереснее. "
               "Если они тебе нравятся, можно помочь: тогда появятся новые главы, города и слова.\n\n"
               "Это всегда по желанию, учёба от этого не зависит 🍵",
    "dn_info": "\n\n<b>Перевод на карту:</b>\n{info}",
    "dn_stars": "Или отправь звёзды Telegram:",
    "dn_url_btn": "💳 Перейти к переводу",
    "dn_title": "Поддержать проект", "dn_desc": "Спасибо, что помогаешь проекту «清越» расти 🍵",
    "dn_thanks": "Спасибо тебе огромное! 💝 Твоя поддержка помогает проекту расти 🍵",
    "qs_thanks": "⭐ Оплата получена, спасибо! Загляни в игру: покупка уже там 🍵",
    "qs_coins": "⭐ Оплата получена, спасибо! Такая покупка у тебя уже была, поэтому в игру добавлены монеты на ту же сумму 🍵",
    "pre_err": "Не получилось подготовить платёж. Попробуй ещё раз из игры.",
}

P["uz"] = {
    "qt_title": "🏆 <b>O'yin reytingi · shu hafta</b>", "qt_empty": "Hozircha reytingda hech kim yo'q. O'yinda sahnani o'ting, birinchi bo'lasiz 🍵", "qt_you": "siz",
    "pz_win": "🎉 <b>Siz o'yinda g'olib bo'ldingiz!</b>\n\nSiz uchun «Chacha bilan sayohat» o'yinida qahramonning <b>noyob kiyimini</b> chizamiz. U faqat sizda bo'ladi.\n\nUning qanday bo'lishini shu yerning o'ziga yozing: ranglar, obraz, detallar, sevimli naqshlar. Xabar Laraga boradi 🍵",
    "b_donate": "💝 Loyihani qo'llab-quvvatlash",
    "pr_quest": "🗺 Chacha bilan sayohat",
    "dn_text": "💝 <b>Loyihani qo'llab-quvvatlash</b>\n\nBu bot va o'yinni bir kishi xitoy tilini yaqinroq va qiziqarliroq qilish uchun yaratadi. "
               "Agar yoqsa, yordam berishingiz mumkin: shunda yangi boblar, shaharlar va so'zlar paydo bo'ladi.\n\n"
               "Bu doim ixtiyoriy, o'qishingiz bunga bog'liq emas 🍵",
    "dn_info": "\n\n<b>Kartaga o'tkazma:</b>\n{info}",
    "dn_stars": "Yoki Telegram yulduzlarini yuboring:",
    "dn_url_btn": "💳 O'tkazmaga o'tish",
    "dn_title": "Loyihani qo'llab-quvvatlash", "dn_desc": "«清越» loyihasi o'sishiga yordam berganingiz uchun rahmat 🍵",
    "dn_thanks": "Katta rahmat! 💝 Sizning yordamingiz loyiha o'sishiga ko'maklashadi 🍵",
    "qs_thanks": "⭐ To'lov qabul qilindi, rahmat! O'yinga kiring: xarid u yerda 🍵",
    "qs_coins": "⭐ To'lov qabul qilindi, rahmat! Bu xarid sizda allaqachon bor edi, shuning uchun o'yinga shu summadagi tangalar qo'shildi 🍵",
    "pre_err": "To'lovni tayyorlab bo'lmadi. O'yindan qayta urinib ko'ring.",
}

P["en"] = {
    "qt_title": "🏆 <b>Game ranking · this week</b>", "qt_empty": "Nobody is on the board yet. Finish a scene in the game and you will be first 🍵", "qt_you": "you",
    "pz_win": "🎉 <b>You won the draw!</b>\n\nWe will draw a <b>unique outfit</b> for your hero in “Journey with Chacha”. Only you will have it.\n\nWrite to me right here what it should be like: colours, style, details, favourite motifs. The message goes to Lara 🍵",
    "b_donate": "💝 Support the project",
    "pr_quest": "🗺 Journey with Chacha",
    "dn_text": "💝 <b>Support the project</b>\n\nThis bot and the game are made by one person, to make Chinese closer and more fun. "
               "If you like them, you can help: that way new chapters, cities and words appear.\n\n"
               "It is always optional, and your learning does not depend on it 🍵",
    "dn_info": "\n\n<b>Card transfer:</b>\n{info}",
    "dn_stars": "Or send Telegram Stars:",
    "dn_url_btn": "💳 Go to the transfer",
    "dn_title": "Support the project", "dn_desc": "Thank you for helping 清越 grow 🍵",
    "dn_thanks": "Thank you so much! 💝 Your support helps the project grow 🍵",
    "qs_thanks": "⭐ Payment received, thank you! Open the game: your purchase is already there 🍵",
    "qs_coins": "⭐ Payment received, thank you! You already had this purchase, so coins of the same value were added to the game 🍵",
    "pre_err": "Could not prepare the payment. Please try again from the game.",
}

P["zh"] = {
    "qt_title": "🏆 <b>游戏排行榜 · 本周</b>", "qt_empty": "榜单上还没有人。在游戏里完成一幕，你就是第一名 🍵", "qt_you": "你",
    "pz_win": "🎉 <b>你赢得了抽奖！</b>\n\n我们会为你在《茶茶的旅行》里的主角设计一套<b>独一无二的装扮</b>，只属于你。\n\n请直接在这里写下你想要的样子：颜色、风格、细节、喜欢的图案。消息会发给 Lara 🍵",
    "b_donate": "💝 支持项目",
    "pr_quest": "🗺 茶茶的旅行",
    "dn_text": "💝 <b>支持项目</b>\n\n这个机器人和游戏由一个人制作，希望让中文更亲近、更有趣。"
               "如果你喜欢，可以帮帮我：这样就会有新的章节、城市和词语。\n\n"
               "一切自愿，你的学习不受影响 🍵",
    "dn_info": "\n\n<b>银行卡转账：</b>\n{info}",
    "dn_stars": "或者发送 Telegram 星星：",
    "dn_url_btn": "💳 前往转账",
    "dn_title": "支持项目", "dn_desc": "感谢你帮助「清越」成长 🍵",
    "dn_thanks": "非常感谢！💝 你的支持让项目不断成长 🍵",
    "qs_thanks": "⭐ 已收到付款，谢谢！打开游戏看看：购买已到账 🍵",
    "qs_coins": "⭐ 已收到付款，谢谢！这项购买你已拥有，所以按同等价值给游戏补了金币 🍵",
    "pre_err": "无法准备付款，请从游戏里再试一次。",
}
