"""
Тексты версии 9: правила и условия игры, недельный рейтинг, награда за друга (скидка 30%).
Подключается в конце texts.py. Числа в правилах подставляются из practice.py (жизни, лимит очков в день, минимум очков).
Если захочешь поменять приз или срок, правь здесь строки rules и top_prize во всех четырёх языках.
"""

P = {}

P["ru"] = {
    "b_rules": "📜 Правила игры", "pr_top": "🏆 Рейтинг недели", "pr_rules": "📜 Правила и условия",
    "ref_r3": "💸 друг начал заниматься: скидка 30% на один месяц занятий",
    "rules": (
        "📜 <b>Правила и условия игры «Чайная лавка»</b>\n"
        "<i>Организатор: Лазиза Ропижонова (清越)</i>\n\n"
        "🍵 <b>1. О чём игра</b>\n"
        "Ты хозяин чайной лавки. Покупатели заказывают чай и посуду по-китайски, а ты подаёшь нужное. "
        "Играть бесплатно, а цель одна: запоминать слова с удовольствием.\n\n"
        "🎯 <b>2. Как играть</b>\n"
        "· Верный ответ даёт +1 монету, а каждый пятый подряд ещё +3.\n"
        "· За ошибку −1 жизнь, и слово вернётся позже. В день даётся {lives} жизней, утром они обновляются. "
        "Жизни за друзей и марафон добавляются на этот день.\n"
        "· Монеты и звания нельзя купить или обменять на деньги.\n\n"
        "🏆 <b>3. Рейтинг недели</b>\n"
        "· Участие добровольное: нажми «Участвовать» в разделе «🏆 Рейтинг недели». Другие участники увидят "
        "только твоё первое имя и очки.\n"
        "· Очки недели равны монетам из Чайной лавки, но не больше {cap} в день: выигрывает тот, кто занимается "
        "регулярно, а не тот, кто просидел одну ночь.\n"
        "· Неделя идёт с понедельника 00:00 до воскресенья 23:59 по Ташкенту, итоги подводятся в понедельник.\n"
        "· Если очков поровну, выше тот, у кого больше доля верных ответов, а затем тот, кто набрал очки раньше.\n"
        "· Чтобы получить приз, нужно набрать за неделю не меньше {min} очков.\n\n"
        "🎁 <b>4. Приз</b>\n"
        "· Победитель недели получает один авторский урок от Лазизы на выбранную им тему "
        "(разговор, манхуа, чайная лексика, подготовка к HSK и т. п.).\n"
        "· Тема должна подходить для урока и не нарушать пункт 6: Лазиза может отклонить тему и предложить другую.\n"
        "· Время урока согласуется лично, воспользоваться призом нужно в течение 30 дней. "
        "Приз нельзя обменять на деньги.\n\n"
        "🤝 <b>5. Честная игра</b>\n"
        "· Один человек: один аккаунт.\n"
        "· Нельзя использовать боты, скрипты, автоматические нажатия и ошибки в работе игры. "
        "Нашёл(ла) ошибку, напиши Лазизе, это поможет всем.\n"
        "· Если тебе нет 18 лет, участвуй с ведома родителей.\n\n"
        "🚫 <b>6. Что запрещено</b>\n"
        "В имени, в сообщениях и в теме призового урока нельзя:\n"
        "· разжигать ненависть и вражду по признаку национальности, расы, религии, пола, возраста, "
        "происхождения, здоровья и тому подобному;\n"
        "· оскорблять, травить и угрожать людям;\n"
        "· призывать к насилию и экстремизму или оправдывать их;\n"
        "· присылать материалы 18+ и откровенный контент;\n"
        "· рекламировать, рассылать спам и раскрывать чужие личные данные.\n"
        "За нарушение человека исключают из рейтинга, а приз аннулируется.\n\n"
        "🔒 <b>7. Данные</b>\n"
        "В таблице видно только первое имя и очки. Выйти из рейтинга можно в любой момент в том же разделе. "
        "Подробнее: /privacy.\n\n"
        "🔄 <b>8. Изменения</b>\n"
        "Лазиза может обновлять правила, актуальная версия всегда здесь. Игра не связана с Telegram и не поддерживается им.\n\n"
        "Спасибо, что играешь честно 🌿"),
    "top_title": "🏆 <b>Рейтинг недели</b>\n{start} – {end} · осталось дней: {days}\n\n{rows}",
    "top_empty": "Пока в рейтинге никого. Стань первым: играй в Чайную лавку и нажми «Участвовать» 🍵",
    "top_you": "Твоё место: <b>{place}</b> · очков: <b>{pts}</b>",
    "top_you_out": "Ты пока не в рейтинге. Нажми «Участвовать», и твои очки появятся в таблице.",
    "top_you_zero": "Ты в рейтинге, но очков пока нет. Загляни в Чайную лавку 🍵",
    "top_prize": "🎁 Приз за 1-е место: авторский урок от Лазизы на любую тему (в рамках правил). Минимум очков для приза: {min}.",
    "top_join": "✅ Участвовать", "top_leave": "🚪 Выйти из рейтинга", "top_rules": "📜 Правила",
    "top_consent": "Если ты вступишь в рейтинг, другие игроки увидят в таблице твоё имя «{nick}» и очки. Согласен(на)?",
    "top_consent_yes": "✅ Да, участвую", "top_no": "Отмена",
    "top_joined": "Ты в рейтинге! Очки идут за верные ответы в Чайной лавке, не больше {cap} в день. Удачи 🍵",
    "top_left": "Готово, ты вышел(ла) из рейтинга. Твоё имя в таблице больше не видно.",
    "board_result": "🏆 <b>Итоги недели {start} – {end}</b>\n\n{rows}\n\n{you}",
    "board_win": "🥇 <b>Ты победил(а) на этой неделе!</b>\n\nПриз: авторский урок от Лазизы на любую тему (в рамках правил игры). "
                 "Лазиза скоро напишет тебе, чтобы выбрать тему и время.",
}

P["uz"] = {
    "b_rules": "📜 O'yin qoidalari", "pr_top": "🏆 Hafta reytingi", "pr_rules": "📜 Qoidalar va shartlar",
    "ref_r3": "💸 do'st o'qishni boshladi: bir oylik darslarga 30% chegirma",
    "rules": (
        "📜 <b>«Choyxona do'koni» o'yinining qoidalari va shartlari</b>\n"
        "<i>Tashkilotchi: Laziza Ropijonova (清越)</i>\n\n"
        "🍵 <b>1. O'yin nima haqida</b>\n"
        "Siz choyxona do'koni egasisiz. Xaridorlar xitoycha choy va idish buyurtma qiladi, siz kerakli narsani uzatasiz. "
        "O'ynash bepul, maqsad bitta: so'zlarni zavq bilan yodlash.\n\n"
        "🎯 <b>2. Qanday o'ynaladi</b>\n"
        "· To'g'ri javob +1 tanga beradi, ketma-ket har beshinchisi yana +3.\n"
        "· Xato uchun −1 jon, so'z keyinroq qaytadi. Kuniga {lives} ta jon beriladi, ertalab yangilanadi. "
        "Do'stlar va marafon uchun jonlar shu kunga qo'shiladi.\n"
        "· Tanga va unvonlarni sotib olib yoki pulga almashtirib bo'lmaydi.\n\n"
        "🏆 <b>3. Hafta reytingi</b>\n"
        "· Qatnashish ixtiyoriy: «🏆 Hafta reytingi» bo'limida «Qatnashish»ni bosing. Boshqa ishtirokchilar "
        "faqat ismingizning birinchi so'zini va ochkolaringizni ko'radi.\n"
        "· Hafta ochkolari Choyxona do'konidagi tangalarga teng, lekin kuniga {cap} tadan oshmaydi: g'olib bo'lish uchun "
        "bir kechada o'tirish emas, muntazam shug'ullanish kerak.\n"
        "· Hafta dushanba 00:00 dan yakshanba 23:59 gacha (Toshkent vaqti), natijalar dushanba kuni chiqadi.\n"
        "· Ochkolar teng bo'lsa, to'g'ri javoblar ulushi yuqori bo'lgan, so'ng ochkoni oldinroq to'plagan yuqoriroq turadi.\n"
        "· Sovg'a olish uchun hafta davomida kamida {min} ochko to'plash kerak.\n\n"
        "🎁 <b>4. Sovg'a</b>\n"
        "· Hafta g'olibi o'zi tanlagan mavzuda Lazizadan bitta mualliflik darsini oladi "
        "(suhbat, manhua, choy lug'ati, HSKga tayyorgarlik va hokazo).\n"
        "· Mavzu dars uchun mos bo'lishi va 6-bandni buzmasligi kerak: Laziza mavzuni rad etib, boshqasini taklif qilishi mumkin.\n"
        "· Dars vaqti shaxsan kelishiladi, sovg'adan 30 kun ichida foydalanish kerak. "
        "Sovg'ani pulga almashtirib bo'lmaydi.\n\n"
        "🤝 <b>5. Halol o'yin</b>\n"
        "· Bitta odam: bitta akkaunt.\n"
        "· Botlar, skriptlar, avtomatik bosishlar va o'yindagi xatolardan foydalanish mumkin emas. "
        "Xato topsangiz, Lazizaga yozing, bu hammaga foyda.\n"
        "· Agar 18 yoshga to'lmagan bo'lsangiz, ota-onangiz xabari bilan qatnashing.\n\n"
        "🚫 <b>6. Nima taqiqlanadi</b>\n"
        "Ismda, xabarlarda va sovg'a darsi mavzusida quyidagilar mumkin emas:\n"
        "· millat, irq, din, jins, yosh, kelib chiqish, sog'liq va shu kabilar bo'yicha nafrat va adovatni qo'zg'atish;\n"
        "· odamlarni haqorat qilish, ta'qib qilish va ularga tahdid qilish;\n"
        "· zo'ravonlik va ekstremizmga chaqirish yoki ularni oqlash;\n"
        "· 18+ materiallar va ochiq-oydin kontent yuborish;\n"
        "· reklama, spam va boshqalarning shaxsiy ma'lumotlarini oshkor qilish.\n"
        "Qoidabuzarlik uchun odam reytingdan chiqariladi, sovg'a bekor qilinadi.\n\n"
        "🔒 <b>7. Ma'lumotlar</b>\n"
        "Jadvalda faqat birinchi ism va ochkolar ko'rinadi. Reytingdan istalgan vaqtda shu bo'limda chiqish mumkin. "
        "Batafsil: /privacy.\n\n"
        "🔄 <b>8. O'zgarishlar</b>\n"
        "Laziza qoidalarni yangilashi mumkin, dolzarb versiya doim shu yerda. O'yin Telegram bilan bog'liq emas va u tomonidan qo'llab-quvvatlanmaydi.\n\n"
        "Halol o'ynaganingiz uchun rahmat 🌿"),
    "top_title": "🏆 <b>Hafta reytingi</b>\n{start} – {end} · qolgan kunlar: {days}\n\n{rows}",
    "top_empty": "Hozircha reytingda hech kim yo'q. Birinchi bo'ling: Choyxona do'konida o'ynang va «Qatnashish»ni bosing 🍵",
    "top_you": "Sizning o'rningiz: <b>{place}</b> · ochko: <b>{pts}</b>",
    "top_you_out": "Siz hali reytingda emassiz. «Qatnashish»ni bosing, ochkolaringiz jadvalda ko'rinadi.",
    "top_you_zero": "Siz reytingdasiz, lekin hozircha ochko yo'q. Choyxona do'koniga kiring 🍵",
    "top_prize": "🎁 1-o'rin sovg'asi: Lazizadan istalgan mavzuda mualliflik darsi (qoidalar doirasida). Sovg'a uchun minimal ochko: {min}.",
    "top_join": "✅ Qatnashish", "top_leave": "🚪 Reytingdan chiqish", "top_rules": "📜 Qoidalar",
    "top_consent": "Reytingga qo'shilsangiz, boshqa o'yinchilar jadvalda «{nick}» ismingiz va ochkolaringizni ko'radi. Rozimisiz?",
    "top_consent_yes": "✅ Ha, qatnashaman", "top_no": "Bekor qilish",
    "top_joined": "Siz reytingdasiz! Ochkolar Choyxona do'konidagi to'g'ri javoblar uchun beriladi, kuniga {cap} tagacha. Omad 🍵",
    "top_left": "Tayyor, reytingdan chiqdingiz. Ismingiz jadvalda endi ko'rinmaydi.",
    "board_result": "🏆 <b>{start} – {end} hafta natijalari</b>\n\n{rows}\n\n{you}",
    "board_win": "🥇 <b>Siz bu hafta g'olib bo'ldingiz!</b>\n\nSovg'a: Lazizadan istalgan mavzuda mualliflik darsi (o'yin qoidalari doirasida). "
                 "Laziza tez orada mavzu va vaqtni tanlash uchun sizga yozadi.",
}

P["en"] = {
    "b_rules": "📜 Game rules", "pr_top": "🏆 Weekly ranking", "pr_rules": "📜 Rules and terms",
    "ref_r3": "💸 friend starts lessons: 30% off one month of lessons",
    "rules": (
        "📜 <b>Rules and terms of the “Tea shop” game</b>\n"
        "<i>Organiser: Laziza Ropijonova (清越)</i>\n\n"
        "🍵 <b>1. What the game is</b>\n"
        "You run a tea shop. Customers order tea and teaware in Chinese, and you serve what they ask for. "
        "It is free to play and has one purpose: to learn words with pleasure.\n\n"
        "🎯 <b>2. How to play</b>\n"
        "· A correct answer gives +1 coin, and every fifth in a row gives another +3.\n"
        "· A mistake costs 1 life and the word comes back later. You get {lives} lives a day, refreshed each morning. "
        "Lives earned through friends and the marathon are added for that day.\n"
        "· Coins and ranks cannot be bought or exchanged for money.\n\n"
        "🏆 <b>3. Weekly ranking</b>\n"
        "· Taking part is voluntary: tap “Join” in the “🏆 Weekly ranking” section. Other players will see "
        "only your first name and your points.\n"
        "· Weekly points equal the coins earned in the Tea shop, but no more than {cap} a day: the winner is the one who "
        "practises regularly, not the one who sat up for a single night.\n"
        "· The week runs from Monday 00:00 to Sunday 23:59 Tashkent time, and results are announced on Monday.\n"
        "· If points are equal, the player with the higher share of correct answers ranks higher, then the one who scored earlier.\n"
        "· To win the prize you need at least {min} points in the week.\n\n"
        "🎁 <b>4. The prize</b>\n"
        "· The weekly winner receives one custom lesson from Laziza on a topic of their choice "
        "(conversation, manhua, tea vocabulary, HSK preparation and so on).\n"
        "· The topic must suit a lesson and comply with section 6: Laziza may decline a topic and suggest another.\n"
        "· The time is agreed personally and the prize must be used within 30 days. "
        "It cannot be exchanged for money.\n\n"
        "🤝 <b>5. Fair play</b>\n"
        "· One person, one account.\n"
        "· No bots, scripts, automated taps or exploiting bugs in the game. "
        "If you find a bug, tell Laziza, it helps everyone.\n"
        "· If you are under 18, take part with your parents' knowledge.\n\n"
        "🚫 <b>6. What is not allowed</b>\n"
        "In your name, your messages and the topic of the prize lesson, you may not:\n"
        "· incite hatred or hostility on grounds of nationality, race, religion, sex, age, origin, health and the like;\n"
        "· insult, harass or threaten people;\n"
        "· call for or justify violence or extremism;\n"
        "· send 18+ material or explicit content;\n"
        "· advertise, spam or reveal other people's personal data.\n"
        "A violation means removal from the ranking and cancellation of the prize.\n\n"
        "🔒 <b>7. Data</b>\n"
        "The table shows only your first name and points. You can leave the ranking at any time in the same section. "
        "More: /privacy.\n\n"
        "🔄 <b>8. Changes</b>\n"
        "Laziza may update these rules; the current version is always here. The game is not affiliated with or endorsed by Telegram.\n\n"
        "Thank you for playing fair 🌿"),
    "top_title": "🏆 <b>Weekly ranking</b>\n{start} – {end} · days left: {days}\n\n{rows}",
    "top_empty": "Nobody is in the ranking yet. Be the first: play the Tea shop and tap “Join” 🍵",
    "top_you": "Your place: <b>{place}</b> · points: <b>{pts}</b>",
    "top_you_out": "You are not in the ranking yet. Tap “Join” and your points will appear in the table.",
    "top_you_zero": "You are in the ranking but have no points yet. Visit the Tea shop 🍵",
    "top_prize": "🎁 Prize for 1st place: a custom lesson from Laziza on any topic (within the rules). Minimum points for the prize: {min}.",
    "top_join": "✅ Join", "top_leave": "🚪 Leave the ranking", "top_rules": "📜 Rules",
    "top_consent": "If you join, other players will see your name “{nick}” and your points in the table. Do you agree?",
    "top_consent_yes": "✅ Yes, join", "top_no": "Cancel",
    "top_joined": "You are in the ranking! Points come from correct answers in the Tea shop, up to {cap} a day. Good luck 🍵",
    "top_left": "Done, you have left the ranking. Your name is no longer visible in the table.",
    "board_result": "🏆 <b>Results for the week {start} – {end}</b>\n\n{rows}\n\n{you}",
    "board_win": "🥇 <b>You won this week!</b>\n\nPrize: a custom lesson from Laziza on any topic (within the game rules). "
                 "Laziza will write to you soon to choose the topic and time.",
}

P["zh"] = {
    "b_rules": "📜 游戏规则", "pr_top": "🏆 每周排行榜", "pr_rules": "📜 规则与条款",
    "ref_r3": "💸 朋友开始上课：一个月课程 7 折（优惠 30%）",
    "rules": (
        "📜 <b>“茶铺”游戏规则与条款</b>\n"
        "<i>主办人：Laziza Ropijonova（清越）</i>\n\n"
        "🍵 <b>1. 游戏简介</b>\n"
        "你是茶铺老板。顾客用中文点茶和茶具，你来上对应的东西。游戏免费，目的只有一个：开开心心地记单词。\n\n"
        "🎯 <b>2. 玩法</b>\n"
        "· 答对 +1 金币，连续答对每第 5 次再 +3。\n"
        "· 答错 −1 条命，这个词稍后会再出现。每天 {lives} 条命，每天早上恢复。通过朋友和马拉松获得的命会加到当天。\n"
        "· 金币和称号不能购买，也不能兑换成钱。\n\n"
        "🏆 <b>3. 每周排行榜</b>\n"
        "· 自愿参加：在“🏆 每周排行榜”里点“参加”。其他玩家只会看到你名字的第一个词和你的积分。\n"
        "· 每周积分等于在茶铺赚到的金币，但每天最多计 {cap} 分：赢的是坚持练习的人，而不是只熬一晚上的人。\n"
        "· 每周从周一 00:00 到周日 23:59（塔什干时间），周一公布结果。\n"
        "· 积分相同时，答对率高的排名靠前，再比谁先拿到这些积分。\n"
        "· 想获得奖品，一周至少需要 {min} 分。\n\n"
        "🎁 <b>4. 奖品</b>\n"
        "· 每周冠军可获得一节 Laziza 的原创课，主题由冠军自选（口语、漫画、茶词汇、HSK 备考等）。\n"
        "· 主题必须适合上课，并且不违反第 6 条：Laziza 有权婉拒某个主题并建议另一个。\n"
        "· 上课时间当面商定，奖品需在 30 天内使用，不能兑换成钱。\n\n"
        "🤝 <b>5. 公平游戏</b>\n"
        "· 一人一个账号。\n"
        "· 不得使用机器人、脚本、自动点击，也不得利用游戏漏洞。发现漏洞请告诉 Laziza，这对大家都有帮助。\n"
        "· 未满 18 岁请在家长知情的情况下参加。\n\n"
        "🚫 <b>6. 禁止事项</b>\n"
        "在名字、消息和奖品课主题中，不得：\n"
        "· 因民族、种族、宗教、性别、年龄、出身、健康状况等煽动仇恨或敌意；\n"
        "· 辱骂、骚扰或威胁他人；\n"
        "· 鼓吹或为暴力和极端主义辩护；\n"
        "· 发送 18+ 内容或露骨内容；\n"
        "· 打广告、发垃圾信息或泄露他人个人信息。\n"
        "违规者将被移出排行榜，奖品作废。\n\n"
        "🔒 <b>7. 数据</b>\n"
        "排行榜上只显示名字的第一个词和积分。你可以随时在同一栏目里退出排行榜。详见 /privacy。\n\n"
        "🔄 <b>8. 变更</b>\n"
        "Laziza 可能更新规则，最新版本始终在这里。本游戏与 Telegram 无关，也未获其认可。\n\n"
        "感谢你公平游戏 🌿"),
    "top_title": "🏆 <b>每周排行榜</b>\n{start} – {end} · 剩余天数：{days}\n\n{rows}",
    "top_empty": "排行榜上还没有人。来当第一个吧：玩茶铺，然后点“参加” 🍵",
    "top_you": "你的名次：<b>{place}</b> · 积分：<b>{pts}</b>",
    "top_you_out": "你还没有加入排行榜。点“参加”，你的积分就会出现在榜上。",
    "top_you_zero": "你已加入排行榜，但还没有积分。去茶铺看看吧 🍵",
    "top_prize": "🎁 第一名奖品：Laziza 的一节原创课，主题不限（在规则范围内）。获奖最低积分：{min}。",
    "top_join": "✅ 参加", "top_leave": "🚪 退出排行榜", "top_rules": "📜 规则",
    "top_consent": "加入排行榜后，其他玩家会在榜上看到你的名字“{nick}”和积分。你同意吗？",
    "top_consent_yes": "✅ 同意，参加", "top_no": "取消",
    "top_joined": "你已加入排行榜！积分来自茶铺里的正确回答，每天最多 {cap} 分。祝你好运 🍵",
    "top_left": "好的，你已退出排行榜。榜上不再显示你的名字。",
    "board_result": "🏆 <b>{start} – {end} 本周结果</b>\n\n{rows}\n\n{you}",
    "board_win": "🥇 <b>你赢得了本周冠军！</b>\n\n奖品：Laziza 的一节原创课，主题不限（在游戏规则范围内）。Laziza 很快会联系你，商定主题和时间。",
}
