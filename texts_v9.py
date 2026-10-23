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
        "📜 <b>Правила и условия игр «Путешествие по Китаю с 茶茶» и «Тренировка слов»</b>\n"
        "<i>Организатор: Лазиза Ропижонова (汉助)</i>\n\n"
        "🗺 <b>1. О чём игра</b>\n"
        "В «Путешествии по Китаю с 茶茶» ты создаёшь героя и идёшь по Китаю вместе с чайным духом 茶茶. Каждая сцена состоит из диалога и заданий на китайском: перевести, выбрать иероглиф, собрать фразу. Первая глава ведёт от Пекина до Великой стены. Есть и дополнительный режим «Тренировка слов»: быстрая викторина, где покупатели заказывают чай и посуду по-китайски. Играть бесплатно, а цель одна: запоминать китайский с удовольствием.\n\n"
        "🎯 <b>2. Как играть</b>\n"
        "· Каждый день открывается одна новая сцена. Ещё одну сцену в тот же день можно открыть за монеты или ⭐.\n"
        "· Верный ответ с первой попытки даёт 10 монет, верный ответ после ошибки 5, а за пройденную сцену ещё 20 (за финал главы 50).\n"
        "· Ошибка в задании стоит одной жизни. Всего их 5, и одна возвращается каждый час. Жизнь можно вернуть, повторив карточки (+1), или купить за монеты.\n"
        "· Монеты тратятся на жизни, наряды героя и дополнительную сцену. Всё, что продаётся за ⭐, можно получить и за монеты, поэтому платить не обязательно. Монеты можно докупить за ⭐, но купленные монеты в рейтинг не идут: очки считаются только по заработанным. Монеты и очки нельзя обменять на деньги.\n"
        "· В «Тренировке слов» верный ответ даёт +1 монету, каждый пятый подряд ещё +3. За ошибку −1 жизнь, в день даётся {lives} жизней, утром они обновляются.\n\n"
        "🏆 <b>3. Рейтинги</b>\n"
        "Рейтингов два, и считаются они отдельно.\n"
        "· <b>Рейтинг путешествия</b> (карточка «Рейтинг» на вкладке «Путь»). Очки равны монетам, которые ты заработал(а) в путешествии за задания и сцены, покупки их не меняют. Есть таблица за неделю и за всё время. В ней видны только имя героя и очки, скрыть себя можно там же. Неделя идёт с понедельника 00:00 до воскресенья 23:59 по Ташкенту. Если очков поровну, выше тот, кто прошёл больше сцен. Чтобы получить оформление победителя, нужно набрать за неделю не меньше 60 очков.\n"
        "· <b>Рейтинг недели «Тренировки слов»</b> (вкладка «Рейтинг»). Участие добровольное: выбери ник и нажми «Участвовать». Очки равны монетам из тренировки, но не больше {cap} в день: выигрывает тот, кто занимается регулярно, а не тот, кто просидел одну ночь. Итоги подводятся в понедельник. Если очков поровну, выше доля верных ответов, а затем тот, кто набрал очки раньше. Чтобы получить оформление победителя, нужно набрать за неделю не меньше {min} очков.\n· В любой таблице можно нажать на игрока и открыть его карточку: имя или ник, оформление, число побед и очки. Монеты других игроков не показываются.\n\n"
        "🎁 <b>4. Призы</b>\n"
        "· Победитель недели получает <b>оформление профиля</b> на неделю: интерфейс игры в особых цветах, подсветку в рейтинге и значок победителя в карточке. Оформления получают победители обоих рейтингов: «Тренировки слов» и путешествия. Каждую неделю оно новое и подряд не повторяется, даже если побеждает один и тот же человек. Оно действует до воскресенья следующей недели, когда подводятся новые итоги, и после этого исчезает. Число твоих побед остаётся в карточке навсегда. Оформления из магазина (за монеты или ⭐) остаются у тебя навсегда.\n"
        "· Розыгрыш наряда: каждый, кто прошёл первую сцену путешествия, участвует в розыгрыше. Победитель выбирается случайно, а Лазиза рисует для него уникальный наряд героя по его пожеланиям. Розыгрыши проводятся время от времени, итоги приходят в бота.\n"
        "· Призы нельзя обменять на деньги.\n\n"
        "🤝 <b>5. Честная игра</b>\n"
        "· Один человек: один аккаунт.\n"
        "· Нельзя использовать боты, скрипты, автоматические нажатия и ошибки в работе игры. "
        "Нашёл(ла) ошибку, напиши Лазизе, это поможет всем.\n"
        "· Если тебе нет 18 лет, участвуй с ведома родителей.\n\n"
        "🚫 <b>6. Что запрещено</b>\n"
        "В имени, нике и сообщениях нельзя:\n"
        "· разжигать ненависть и вражду по признаку национальности, расы, религии, пола, возраста, "
        "происхождения, здоровья и тому подобному;\n"
        "· оскорблять, травить и угрожать людям;\n"
        "· призывать к насилию и экстремизму или оправдывать их;\n"
        "· присылать материалы 18+ и откровенный контент;\n"
        "· рекламировать, рассылать спам и раскрывать чужие личные данные.\n"
        "За нарушение человека исключают из рейтинга, а оформление победителя аннулируется.\n\n"
        "🔒 <b>7. Данные</b>\n"
        "В таблицах видны только ник (в путешествии имя героя) и очки. Выйти из рейтинга можно в любой момент в том же разделе. Подробнее: /privacy.\n\n"
        "🔄 <b>8. Изменения</b>\n"
        "Лазиза может обновлять правила, актуальная версия всегда здесь. Игра не связана с Telegram и не поддерживается им.\n\n"
        "Спасибо, что играешь честно 🌿"),
    "top_title": "🏆 <b>Рейтинг недели</b>\n{start} – {end} · осталось дней: {days}\n\n{rows}",
    "top_empty": "Пока в рейтинге никого. Стань первым: играй в тренировку слов и нажми «Участвовать» 🍵",
    "top_you": "Твоё место: <b>{place}</b> · очков: <b>{pts}</b>",
    "top_you_out": "Ты пока не в рейтинге. Нажми «Участвовать», и твои очки появятся в таблице.",
    "top_you_zero": "Ты в рейтинге, но очков пока нет. Загляни в тренировку слов 🍵",
    "top_prize": "🎁 Приз за 1-е место: оформление профиля на неделю (каждую неделю новое). Минимум очков для приза: {min}.",
    "top_join": "✅ Участвовать", "top_leave": "🚪 Выйти из рейтинга", "top_rules": "📜 Правила",
    "top_consent": "Если ты вступишь в рейтинг, другие игроки увидят в таблице твоё имя «{nick}» и очки. Согласен(на)?",
    "top_consent_yes": "✅ Да, участвую", "top_no": "Отмена",
    "top_joined": "Ты в рейтинге! Очки идут за верные ответы в тренировке слов, не больше {cap} в день. Удачи 🍵",
    "top_left": "Готово, ты вышел(ла) из рейтинга. Твоё имя в таблице больше не видно.",
    "board_result": "🏆 <b>Итоги недели {start} – {end}</b>\n\n{rows}\n\n{you}",
    "board_win": "🥇 <b>Ты победил(а) на этой неделе!</b>\n\nПриз: оформление профиля на неделю. Оно уже у тебя в игре.",
}

P["uz"] = {
    "b_rules": "📜 O'yin qoidalari", "pr_top": "🏆 Hafta reytingi", "pr_rules": "📜 Qoidalar va shartlar",
    "ref_r3": "💸 do'st o'qishni boshladi: bir oylik darslarga 30% chegirma",
    "rules": (
        "📜 <b>«茶茶 bilan Xitoy bo'ylab sayohat» va «So'z mashqi» o'yinlarining qoidalari va shartlari</b>\n"
        "<i>Tashkilotchi: Laziza Ropijonova (汉助)</i>\n\n"
        "🗺 <b>1. O'yin nima haqida</b>\n"
        "«茶茶 bilan Xitoy bo'ylab sayohat»da qahramon yaratasiz va choy ruhi 茶茶 bilan Xitoy bo'ylab yo'lga chiqasiz. Har bir sahna dialog va xitoycha topshiriqlardan iborat: tarjima qilish, ieroglif tanlash, ibora tuzish. Birinchi bob Pekindan Buyuk devorgacha. Qo'shimcha «So'z mashqi» ham bor: xaridorlar xitoycha choy va idish buyurtma qiladigan tezkor viktorina. O'ynash bepul, maqsad bitta: xitoy tilini zavq bilan yodlash.\n\n"
        "🎯 <b>2. Qanday o'ynaladi</b>\n"
        "· Har kuni bitta yangi sahna ochiladi. Shu kuni yana bir sahnani tanga yoki ⭐ evaziga ochish mumkin.\n"
        "· Birinchi urinishdagi to'g'ri javob 10 tanga, xatodan keyingi to'g'ri javob 5 tanga beradi, o'tilgan sahna uchun yana 20 tanga (bob finali uchun 50).\n"
        "· Topshiriqdagi xato bitta jonga tushadi. Jami 5 jon, bittasi har soatda qaytadi. Jonni kartochkalarni takrorlab (+1) yoki tanga evaziga qaytarish mumkin.\n"
        "· Tangalar jon, qahramon kiyimlari va qo'shimcha sahna uchun sarflanadi. ⭐ ga sotiladigan hamma narsani tanga evaziga ham olish mumkin, shuning uchun to'lash shart emas. Tangalarni ⭐ evaziga sotib olish mumkin, lekin sotib olingan tangalar reytingga kirmaydi: ochkolar faqat topilgan tangalar bo'yicha hisoblanadi. Tangalar va ochkolarni pulga almashtirib bo'lmaydi.\n"
        "· «So'z mashqi»da to'g'ri javob +1 tanga beradi, ketma-ket har beshinchisi yana +3. Xato uchun −1 jon, kuniga {lives} ta jon beriladi, ertalab yangilanadi.\n\n"
        "🏆 <b>3. Reytinglar</b>\n"
        "Reyting ikkita va ular alohida hisoblanadi.\n"
        "· <b>Sayohat reytingi</b> («Yo'l» sahifasidagi «Reyting» kartochkasi). Ochkolar sayohatda topshiriq va sahnalar uchun topgan tangalaringizga teng, xaridlar ularni o'zgartirmaydi. Hafta va butun vaqt jadvallari bor. Jadvalda faqat qahramon ismi va ochkolar ko'rinadi, o'zingizni shu yerning o'zida yashirish mumkin. Hafta dushanba 00:00 dan yakshanba 23:59 gacha (Toshkent vaqti). Ochkolar teng bo'lsa, ko'proq sahna o'tgan yuqori turadi. G'olib bezagini olish uchun hafta davomida kamida 60 ochko kerak.\n"
        "· <b>«So'z mashqi» hafta reytingi</b> («Reyting» sahifasi). Qatnashish ixtiyoriy: taxallus tanlab «Qatnashish»ni bosing. Ochkolar mashqdagi tangalarga teng, lekin kuniga {cap} tadan oshmaydi: g'olib bo'lish uchun bir kechada o'tirish emas, muntazam shug'ullanish kerak. Natijalar dushanba kuni chiqadi. Ochkolar teng bo'lsa, to'g'ri javoblar ulushi yuqori turadi, keyin ochkoni oldinroq yig'gan. G'olib bezagini olish uchun hafta davomida kamida {min} ochko kerak.\n· Istalgan jadvalda o'yinchini bosib, uning kartochkasini ochish mumkin: ism yoki nik, bezak, g'alabalar soni va ochkolar. Boshqa o'yinchilarning tangalari ko'rsatilmaydi.\n\n"
        "🎁 <b>4. Sovg'alar</b>\n"
        "· Hafta g'olibi bir haftaga <b>profil bezagi</b> oladi: o'yin interfeysi maxsus ranglarda, reytingda yorqin ajratilish va kartochkada g'olib belgisi. Bezakni ikkala reyting g'olibi oladi: «So'z mashqi» va sayohat. Har hafta bezak yangi bo'ladi va ketma-ket takrorlanmaydi, hatto g'olib bir kishi bo'lsa ham. U keyingi haftaning yakshanbasigacha amal qiladi, keyin yangi natijalar chiqib, yo'qoladi. G'alabalar soni kartochkada abadiy qoladi. Do'kondagi bezaklar (tanga yoki ⭐ evaziga) sizda abadiy qoladi.\n"
        "· Kiyim o'yini: sayohatning birinchi sahnasini o'tgan har bir kishi o'yinda qatnashadi. G'olib tasodifiy tanlanadi, Laziza esa unga qahramon uchun noyob kiyimni uning xohishlariga ko'ra chizadi. O'yinlar vaqti-vaqti bilan o'tkaziladi, natijalar botga keladi.\n"
        "· Sovg'alarni pulga almashtirib bo'lmaydi.\n\n"
        "🤝 <b>5. Halol o'yin</b>\n"
        "· Bitta odam: bitta akkaunt.\n"
        "· Botlar, skriptlar, avtomatik bosishlar va o'yindagi xatolardan foydalanish mumkin emas. "
        "Xato topsangiz, Lazizaga yozing, bu hammaga foyda.\n"
        "· Agar 18 yoshga to'lmagan bo'lsangiz, ota-onangiz xabari bilan qatnashing.\n\n"
        "🚫 <b>6. Nima taqiqlanadi</b>\n"
        "Ism, nik va xabarlarda quyidagilar mumkin emas:\n"
        "· millat, irq, din, jins, yosh, kelib chiqish, sog'liq va shu kabilar bo'yicha nafrat va adovatni qo'zg'atish;\n"
        "· odamlarni haqorat qilish, ta'qib qilish va ularga tahdid qilish;\n"
        "· zo'ravonlik va ekstremizmga chaqirish yoki ularni oqlash;\n"
        "· 18+ materiallar va ochiq-oydin kontent yuborish;\n"
        "· reklama, spam va boshqalarning shaxsiy ma'lumotlarini oshkor qilish.\n"
        "Qoidabuzarlik uchun odam reytingdan chiqariladi, sovg'a bekor qilinadi.\n\n"
        "🔒 <b>7. Ma'lumotlar</b>\n"
        "Jadvallarda faqat taxallus (sayohatda qahramon ismi) va ochkolar ko'rinadi. Reytingdan istalgan vaqtda shu bo'limda chiqish mumkin. Batafsil: /privacy.\n\n"
        "🔄 <b>8. O'zgarishlar</b>\n"
        "Laziza qoidalarni yangilashi mumkin, dolzarb versiya doim shu yerda. O'yin Telegram bilan bog'liq emas va u tomonidan qo'llab-quvvatlanmaydi.\n\n"
        "Halol o'ynaganingiz uchun rahmat 🌿"),
    "top_title": "🏆 <b>Hafta reytingi</b>\n{start} – {end} · qolgan kunlar: {days}\n\n{rows}",
    "top_empty": "Hozircha reytingda hech kim yo'q. Birinchi bo'ling: So'z mashqida o'ynang va «Qatnashish»ni bosing 🍵",
    "top_you": "Sizning o'rningiz: <b>{place}</b> · ochko: <b>{pts}</b>",
    "top_you_out": "Siz hali reytingda emassiz. «Qatnashish»ni bosing, ochkolaringiz jadvalda ko'rinadi.",
    "top_you_zero": "Siz reytingdasiz, lekin hozircha ochko yo'q. So'z mashqiga kiring 🍵",
    "top_prize": "🎁 1-o'rin sovg'asi: bir haftalik profil bezagi (har hafta yangi). Sovg'a uchun minimal ochko: {min}.",
    "top_join": "✅ Qatnashish", "top_leave": "🚪 Reytingdan chiqish", "top_rules": "📜 Qoidalar",
    "top_consent": "Reytingga qo'shilsangiz, boshqa o'yinchilar jadvalda «{nick}» ismingiz va ochkolaringizni ko'radi. Rozimisiz?",
    "top_consent_yes": "✅ Ha, qatnashaman", "top_no": "Bekor qilish",
    "top_joined": "Siz reytingdasiz! Ochkolar So'z mashqidagi to'g'ri javoblar uchun beriladi, kuniga {cap} tagacha. Omad 🍵",
    "top_left": "Tayyor, reytingdan chiqdingiz. Ismingiz jadvalda endi ko'rinmaydi.",
    "board_result": "🏆 <b>{start} – {end} hafta natijalari</b>\n\n{rows}\n\n{you}",
    "board_win": "🥇 <b>Siz bu hafta g'olib bo'ldingiz!</b>\n\nSovg'a: bir haftalik profil bezagi. U allaqachon o'yinda sizda.",
}

P["en"] = {
    "b_rules": "📜 Game rules", "pr_top": "🏆 Weekly ranking", "pr_rules": "📜 Rules and terms",
    "ref_r3": "💸 friend starts lessons: 30% off one month of lessons",
    "rules": (
        "📜 <b>Rules and terms of the games “Journey Through China with 茶茶” and “Word practice”</b>\n"
        "<i>Organizer: Laziza Ropijonova (汉助)</i>\n\n"
        "🗺 <b>1. What the game is</b>\n"
        "In “Journey Through China with 茶茶” you create a hero and travel through China with the tea spirit 茶茶. Each scene is a dialogue plus tasks in Chinese: translate, pick a character, build a phrase. Chapter 1 leads from Beijing to the Great Wall. There is also an extra mode, “Word practice”: a quick quiz where customers order tea and teaware in Chinese. Playing is free, and the goal is one: to remember Chinese with pleasure.\n\n"
        "🎯 <b>2. How to play</b>\n"
        "· One new scene opens every day. One more scene on the same day can be unlocked with coins or ⭐.\n"
        "· A correct answer on the first try earns 10 coins, a correct answer after a mistake 5, and finishing a scene adds 20 more (50 for a chapter finale).\n"
        "· A mistake in a task costs one life. You have 5, and one comes back every hour. A life can be restored by reviewing flashcards (+1) or bought with coins.\n"
        "· Coins are spent on lives, outfits for your hero and an extra scene. Everything sold for ⭐ can also be bought with coins, so paying is never required. Coins can also be topped up for ⭐, but purchased coins do not count towards the ranking: points come only from coins you earn. Coins and points cannot be exchanged for money.\n"
        "· In “Word practice” a correct answer earns +1 coin and every fifth in a row +3 more. A mistake costs 1 life; you get {lives} lives a day, refreshed each morning.\n\n"
        "🏆 <b>3. Rankings</b>\n"
        "There are two rankings, and they are counted separately.\n"
        "· <b>Journey ranking</b> (the “Ranking” card on the “Journey” tab). Points equal the coins you earned in the journey for tasks and scenes; purchases do not change them. There is a weekly and an all-time table. It shows only hero names and points, and you can hide yourself there. The week runs from Monday 00:00 to Sunday 23:59 Tashkent time. If points are equal, the player who has finished more scenes ranks higher. To receive the winner's theme you need at least 60 points in the week.\n"
        "· <b>“Word practice” weekly ranking</b> (the “Ranking” tab). Taking part is voluntary: choose a nickname and tap “Join”. Points equal the coins earned in the practice, but no more than {cap} a day: the winner is whoever plays regularly, not whoever sat up one night. Results are announced on Monday. If points are equal, the higher share of correct answers wins, then whoever scored first. To receive the winner's theme you need at least {min} points in the week.\n· In any table you can tap a player to open their card: name or nickname, theme, number of wins and points. Other players' coins are never shown.\n\n"
        "🎁 <b>4. Prizes</b>\n"
        "· The weekly winner receives a <b>profile theme</b> for one week: the game interface in special colours, a highlight in the rankings and a winner badge on their card. Themes go to the winners of both rankings: “Word practice” and the journey. The theme is new every week and never repeats back to back, even if the same person wins again. It lasts until the end of the following week, when new results are announced, and then disappears. Your number of wins stays on your card for good. Themes bought in the shop (for coins or ⭐) stay with you forever.\n"
        "· Outfit draw: everyone who finishes the first scene of the journey takes part. The winner is chosen at random, and Laziza draws a unique outfit for their hero based on their wishes. Draws are held from time to time, and results arrive in the bot.\n"
        "· There are no prizes yet for places in the journey ranking.\n"
        "· Prizes cannot be exchanged for money.\n\n"
        "🤝 <b>5. Fair play</b>\n"
        "· One person, one account.\n"
        "· No bots, scripts, automated taps or exploiting bugs in the game. "
        "If you find a bug, tell Laziza, it helps everyone.\n"
        "· If you are under 18, take part with your parents' knowledge.\n\n"
        "🚫 <b>6. What is not allowed</b>\n"
        "In your name, nickname and messages, you may not:\n"
        "· incite hatred or hostility on grounds of nationality, race, religion, sex, age, origin, health and the like;\n"
        "· insult, harass or threaten people;\n"
        "· call for or justify violence or extremism;\n"
        "· send 18+ material or explicit content;\n"
        "· advertise, spam or reveal other people's personal data.\n"
        "A violation means removal from the ranking and cancellation of the prize.\n\n"
        "🔒 <b>7. Data</b>\n"
        "The tables show only a nickname (in the journey, the hero's name) and points. You can leave the ranking at any time in the same section. More: /privacy.\n\n"
        "🔄 <b>8. Changes</b>\n"
        "Laziza may update these rules; the current version is always here. The game is not affiliated with or endorsed by Telegram.\n\n"
        "Thank you for playing fair 🌿"),
    "top_title": "🏆 <b>Weekly ranking</b>\n{start} – {end} · days left: {days}\n\n{rows}",
    "top_empty": "Nobody is in the ranking yet. Be the first: play Word practice and tap “Join” 🍵",
    "top_you": "Your place: <b>{place}</b> · points: <b>{pts}</b>",
    "top_you_out": "You are not in the ranking yet. Tap “Join” and your points will appear in the table.",
    "top_you_zero": "You are in the ranking but have no points yet. Visit Word practice 🍵",
    "top_prize": "🎁 Prize for 1st place: a profile theme for one week (new every week). Minimum points for the prize: {min}.",
    "top_join": "✅ Join", "top_leave": "🚪 Leave the ranking", "top_rules": "📜 Rules",
    "top_consent": "If you join, other players will see your name “{nick}” and your points in the table. Do you agree?",
    "top_consent_yes": "✅ Yes, join", "top_no": "Cancel",
    "top_joined": "You are in the ranking! Points come from correct answers in Word practice, up to {cap} a day. Good luck 🍵",
    "top_left": "Done, you have left the ranking. Your name is no longer visible in the table.",
    "board_result": "🏆 <b>Results for the week {start} – {end}</b>\n\n{rows}\n\n{you}",
    "board_win": "🥇 <b>You won this week!</b>\n\nPrize: a profile theme for one week. It is already in your game.",
}

P["zh"] = {
    "b_rules": "📜 游戏规则", "pr_top": "🏆 每周排行榜", "pr_rules": "📜 规则与条款",
    "ref_r3": "💸 朋友开始上课：一个月课程 7 折（优惠 30%）",
    "rules": (
        "📜 <b>《和茶茶游中国》与“单词练习”游戏规则与条款</b>\n"
        "<i>组织者：Laziza Ropijonova（汉助）</i>\n\n"
        "🗺 <b>1. 游戏简介</b>\n"
        "在《和茶茶游中国》中，你创建一个主角，和茶灵茶茶一起游览中国。每一幕包括一段对话和中文练习：翻译、选汉字、组句子。第一章从北京一路到长城。另有一个附加模式“单词练习”：顾客用中文点茶和茶具的快速小测验。游戏免费，目的只有一个：轻松愉快地记住中文。\n\n"
        "🎯 <b>2. 玩法</b>\n"
        "· 每天解锁一幕新剧情。当天想再玩一幕，可以用金币或 ⭐ 解锁。\n"
        "· 第一次就答对得 10 金币，答错后再答对得 5 金币，通关一幕再奖励 20 金币（章节终幕 50）。\n"
        "· 练习中答错扣 1 条命。最多 5 条，每小时恢复 1 条。可以通过复习卡片回 1 条命，也可以用金币购买。\n"
        "· 金币可用来买命、给主角换装和解锁额外一幕。凡是用 ⭐ 买的东西也能用金币换到，所以不必付费。金币也可以用 ⭐ 补充，但购买的金币不计入排行榜：积分只按赚到的金币计算。金币和积分不能兑换成钱。\n"
        "· 在“单词练习”中，答对得 1 金币，连续答对第 5 次再加 3。答错 −1 条命，每天 {lives} 条命，每天早上恢复。\n\n"
        "🏆 <b>3. 排行榜</b>\n"
        "排行榜有两个，分别计算。\n"
        "· <b>旅行排行榜</b>（“旅行”页里的“排行榜”卡片）。积分等于你在旅行中通过练习和通关赚到的金币，购买不会改变积分。有每周榜和总榜。榜上只显示主角名字和积分，你也可以在那里隐藏自己。每周从周一 00:00 到周日 23:59（塔什干时间）。积分相同时，通关幕数多的排名靠前。要获得冠军主题，每周至少需要 60 分。\n"
        "· <b>“单词练习”每周排行榜</b>（“排行榜”页）。自愿参加：选择昵称并点“参加”。积分等于练习中赚到的金币，但每天最多计 {cap} 分：赢的是坚持练习的人，而不是只熬一晚上的人。周一公布结果。积分相同时，正确率高者靠前，再按先得分者排序。要获得冠军主题，每周至少需要 {min} 分。\n· 在任何榜单里都可以点击玩家，查看他的名片：名字或昵称、主题、夺冠次数和积分。其他玩家的金币不会显示。\n\n"
        "🎁 <b>4. 奖品</b>\n"
        "· 每周冠军可获得为期一周的<b>个人主页主题</b>：游戏界面变成特别的配色，在排行榜里高亮显示，名片上有冠军徽章。两个排行榜（“单词练习”和旅行）的冠军都有。主题每周都是新的，即使同一个人连续夺冠也不会重复。它会持续到下周日，新一轮结果公布后消失。你的夺冠次数会永久留在名片上。商店里买的主题（用金币或 ⭐）永久属于你。\n"
        "· 装扮抽奖：完成旅行第一幕的玩家都会参加。获奖者随机抽取，Laziza 会根据对方的想法为其主角画一套独一无二的装扮。抽奖不定期进行，结果会发到机器人里。\n"
        "· 奖品不能兑换成钱。\n\n"
        "🤝 <b>5. 公平游戏</b>\n"
        "· 一人一个账号。\n"
        "· 不得使用机器人、脚本、自动点击，也不得利用游戏漏洞。发现漏洞请告诉 Laziza，这对大家都有帮助。\n"
        "· 未满 18 岁请在家长知情的情况下参加。\n\n"
        "🚫 <b>6. 禁止事项</b>\n"
        "在名字、昵称和消息中，不得：\n"
        "· 因民族、种族、宗教、性别、年龄、出身、健康状况等煽动仇恨或敌意；\n"
        "· 辱骂、骚扰或威胁他人；\n"
        "· 鼓吹或为暴力和极端主义辩护；\n"
        "· 发送 18+ 内容或露骨内容；\n"
        "· 打广告、发垃圾信息或泄露他人个人信息。\n"
        "违规者将被移出排行榜，奖品作废。\n\n"
        "🔒 <b>7. 数据</b>\n"
        "榜单上只显示昵称（旅行中显示主角名字）和积分。你可以随时在同一栏目里退出排行榜。详见 /privacy。\n\n"
        "🔄 <b>8. 变更</b>\n"
        "Laziza 可能更新规则，最新版本始终在这里。本游戏与 Telegram 无关，也未获其认可。\n\n"
        "感谢你公平游戏 🌿"),
    "top_title": "🏆 <b>每周排行榜</b>\n{start} – {end} · 剩余天数：{days}\n\n{rows}",
    "top_empty": "排行榜上还没有人。来当第一个吧：玩单词练习，然后点“参加” 🍵",
    "top_you": "你的名次：<b>{place}</b> · 积分：<b>{pts}</b>",
    "top_you_out": "你还没有加入排行榜。点“参加”，你的积分就会出现在榜上。",
    "top_you_zero": "你已加入排行榜，但还没有积分。去单词练习看看吧 🍵",
    "top_prize": "🎁 第一名奖品：为期一周的个人主页主题（每周都不同）。获奖最低积分：{min}。",
    "top_join": "✅ 参加", "top_leave": "🚪 退出排行榜", "top_rules": "📜 规则",
    "top_consent": "加入排行榜后，其他玩家会在榜上看到你的名字“{nick}”和积分。你同意吗？",
    "top_consent_yes": "✅ 同意，参加", "top_no": "取消",
    "top_joined": "你已加入排行榜！积分来自单词练习里的正确回答，每天最多 {cap} 分。祝你好运 🍵",
    "top_left": "好的，你已退出排行榜。榜上不再显示你的名字。",
    "board_result": "🏆 <b>{start} – {end} 本周结果</b>\n\n{rows}\n\n{you}",
    "board_win": "🥇 <b>你赢得了本周冠军！</b>\n\n奖品：为期一周的个人主页主题。它已经在你的游戏里了。",
}
