"""
Тексты новых функций (практика, пробный урок, друзья, домашки, перенос, отзывы).
Подключаются в texts.py. Награды за друзей (ref_r1, ref_r2, ref_r3) можно спокойно править здесь.
Если какого-то ключа нет в языке, бот берёт русский (у китайского запасной английский).
"""

P = {}

P["ru"] = {
    "b_practice": "🎮 Практика", "b_friend": "🎁 Пригласить друга", "b_trial": "📝 Пробный урок",
    "pr_title": "Что потренируем?",
    "pr_quiz": "❓ Викторина", "pr_cards": "🃏 Карточки", "pr_tea": "🍵 Чайная лавка",
    # викторина
    "qz_q": "<b>Вопрос {n}/{total}</b>\n\n<b>{zh}</b>\n🔊 <code>{py}</code>\n\nЧто это значит?",
    "qz_right": "✅ Верно!", "qz_wrong": "❌ Не совсем. Правильно: <b>{right}</b>",
    "qz_end": "Раунд закончен: <b>{score}/{total}</b> {emoji}", "qz_mistakes": "Над чем ещё поработать:",
    "qz_again": "🔁 Ещё раунд", "qz_add": "🃏 Ошибки в карточки", "qz_added": "Добавила слов в карточки: {n}",
    "qz_stale": "Раунд устарел. Нажми «Викторина» ещё раз.", "qz_fail": "Не получилось составить вопрос, попробуй позже.",
    # карточки
    "fc_front": "🃏 <b>{zh}</b>\n🔊 <code>{py}</code>\n\nВспомни значение, потом нажми «Показать».",
    "fc_show": "👀 Показать", "fc_know": "✅ Знаю", "fc_again": "🔁 Ещё раз",
    "fc_back": "🃏 <b>{zh}</b>  <code>{py}</code>\n📖 {meaning}",
    "fc_done": "На сегодня всё 🎉 Выучено: {known} из {total}. Возвращайся завтра, повторения сами подберутся.",
    "fc_new": "Добавила новые слова в колоду: {n}", "fc_stale": "Карточка устарела. Нажми «Карточки» ещё раз.",
    # чайная лавка
    "tea_intro": "🍵 <b>Чайная лавка</b>\n\nК тебе приходят покупатели и говорят по-китайски, а ты подаёшь нужное. "
                 "Верно: +1 монета. Ошибка: −1 жизнь, и слово вернётся ещё раз.\n\n"
                 "❤️ Жизни на сегодня: {lives}\n🪙 Монет: {coins}\n{emoji} {title}",
    "tea_start": "▶️ Открыть лавку",
    "tea_order": "🏮 <b>Покупатель говорит:</b>\n\n<b>{zh}</b>\n🔊 <code>{py}</code>\n\nЧто подать?   ❤️ {lives}",
    "tea_right": "✅ Верно! +{coins} 🪙", "tea_wrong": "❌ Нет. Нужно было: <b>{right}</b>\n❤️ Осталось жизней: {lives}",
    "tea_closed": "🏮 Лавка закрывается на сегодня: жизни закончились. Завтра их снова {max}. "
                  "А пока можно потренироваться в викторине или карточках.",
    "tea_levelup": "🎉 Новое звание: {emoji} {title}!", "tea_next": "➡️ Следующий покупатель", "tea_stop": "🚪 Выйти",
    "tea_stale": "Заказ устарел. Нажми «Чайная лавка» ещё раз.",
    "title0": "Новичок за стойкой", "title1": "Помощник чайного мастера", "title2": "Хозяин лавки",
    "title3": "Мастер чая", "title4": "Чайный наставник",
    # пробный урок
    "trial_ask": "Первый пробный урок бесплатный 🌿 Напиши, в какие дни и во сколько тебе удобно, "
                 "и коротко о себе: возраст, что хочешь учить (например: «пн–ср после 18:00, взрослый, с нуля»). Я передам Лазизе.",
    "trial_sent": "Передала Лазизе! Она напишет тебе 🌿",
    "trial_students": "Ты уже в списке учеников Лазизы, пробный тебе не нужен 😉 Если хочешь что-то уточнить, просто напиши мне.",
    # друзья
    "friend_text": "🎁 <b>Пригласи друга</b>\n\nТвоя личная ссылка:\n<code>{link}</code>\n\n"
                   "<b>Что получишь ты:</b>\n{rewards}\n\nУ друга первый пробный урок бесплатный.\n\n"
                   "Пришли по ссылке: {joined} · записались на пробный: {trial} · начали заниматься: {paid}",
    "ref_r1": "🎟 друг запустил бота: +3 жизни в Чайной лавке на сегодня",
    "ref_r2": "🖌 друг записался на пробный: китайское имя и открытка с иероглифами от Лазизы",
    "ref_r3": "🎁 друг начал заниматься: бонусный разговорный урок на 30 минут",
    "ref_welcome": "Тебя пригласил(а) {name} 🌿 Первый пробный урок у Лазизы бесплатный: нажми «📝 Пробный урок» в меню.",
    "ref_got1": "🎉 Твой друг {friend} запустил бота!\n{reward}",
    "ref_got2": "🎉 Твой друг {friend} записался на пробный урок!\n{reward}\nЛазиза скоро свяжется с тобой.",
    "ref_got3": "🎉 Твой друг {friend} начал заниматься!\n{reward}\nЛазиза скоро свяжется с тобой.",
    # домашки
    "hw_new": "📚 <b>Новое домашнее задание</b>\n\n{text}\n\nСрок: {due}", "hw_btn": "✅ Сделано",
    "hw_thanks": "Отлично! Лазиза увидит 👏", "hw_none": "Открытых заданий нет 🎉",
    "hw_title": "📚 <b>Домашние задания</b>", "hw_nodue": "без срока",
    "hw_remind": "⏰ Напоминание: домашка «{text}» нужна сегодня.",
    # перенос
    "mv_btn": "🔄 Перенести урок",
    "mv_ask": "Когда тебе удобно? Напиши так: <code>чт 17:30</code> или <code>15.10 17:30</code>.\nПереношу урок: {when}",
    "mv_bad": "Не поняла время. Примеры: <code>чт 17:30</code> или <code>15.10 17:30</code>.",
    "mv_sent": "Отправила Лазизе. Как только она ответит, напишу 🌿",
    "mv_ok": "✅ Урок перенесён: {when}", "mv_no": "На это время не получится. Лазиза напишет, когда можно 🌿",
    "mv_none": "Ближайший урок не нашла.",
    # отзыв
    "rv_ask": "Ты уже позанимался(ась) {n} раз 🌿 Оцени занятия от 1 до 5:",
    "rv_text": "Спасибо! Напиши пару слов: что нравится, что улучшить (или «-», если не хочешь).",
    "rv_public": "Можно показать твой отзыв в постах (без фамилии)?", "rv_yes": "Да", "rv_no": "Нет",
    "rv_thanks": "Спасибо! 💛",
}

P["en"] = {
    "b_practice": "🎮 Practice", "b_friend": "🎁 Invite a friend", "b_trial": "📝 Trial lesson",
    "pr_title": "What shall we practice?",
    "pr_quiz": "❓ Quiz", "pr_cards": "🃏 Flashcards", "pr_tea": "🍵 Tea shop",
    "qz_q": "<b>Question {n}/{total}</b>\n\n<b>{zh}</b>\n🔊 <code>{py}</code>\n\nWhat does it mean?",
    "qz_right": "✅ Correct!", "qz_wrong": "❌ Not quite. Correct answer: <b>{right}</b>",
    "qz_end": "Round finished: <b>{score}/{total}</b> {emoji}", "qz_mistakes": "Worth another look:",
    "qz_again": "🔁 Another round", "qz_add": "🃏 Mistakes to flashcards", "qz_added": "Words added to flashcards: {n}",
    "qz_stale": "This round has expired. Tap Quiz again.", "qz_fail": "Couldn't build a question, please try later.",
    "fc_front": "🃏 <b>{zh}</b>\n🔊 <code>{py}</code>\n\nRecall the meaning, then tap Show.",
    "fc_show": "👀 Show", "fc_know": "✅ I know it", "fc_again": "🔁 Again",
    "fc_back": "🃏 <b>{zh}</b>  <code>{py}</code>\n📖 {meaning}",
    "fc_done": "That's all for today 🎉 Learned: {known} of {total}. Come back tomorrow, reviews are scheduled automatically.",
    "fc_new": "New words added to your deck: {n}", "fc_stale": "This card has expired. Tap Flashcards again.",
    "tea_intro": "🍵 <b>Tea shop</b>\n\nCustomers come in and speak Chinese, and you serve what they ask for. "
                 "Correct: +1 coin. Mistake: −1 life, and the word comes back later.\n\n"
                 "❤️ Lives today: {lives}\n🪙 Coins: {coins}\n{emoji} {title}",
    "tea_start": "▶️ Open the shop",
    "tea_order": "🏮 <b>The customer says:</b>\n\n<b>{zh}</b>\n🔊 <code>{py}</code>\n\nWhat do you serve?   ❤️ {lives}",
    "tea_right": "✅ Correct! +{coins} 🪙", "tea_wrong": "❌ No. It was: <b>{right}</b>\n❤️ Lives left: {lives}",
    "tea_closed": "🏮 The shop closes for today: no lives left. Tomorrow you get {max} again. "
                  "Meanwhile try the quiz or flashcards.",
    "tea_levelup": "🎉 New rank: {emoji} {title}!", "tea_next": "➡️ Next customer", "tea_stop": "🚪 Leave",
    "tea_stale": "This order has expired. Tap Tea shop again.",
    "title0": "Newcomer behind the counter", "title1": "Tea master's helper", "title2": "Shop owner",
    "title3": "Tea master", "title4": "Tea mentor",
    "trial_ask": "The first trial lesson is free 🌿 Tell me which days and times suit you, plus a few words about you: "
                 "age and what you want to learn (for example: \"Mon–Wed after 6pm, adult, from scratch\"). I'll pass it to Laziza.",
    "trial_sent": "Passed to Laziza! She'll write to you 🌿",
    "trial_students": "You're already on Laziza's student list, no trial needed 😉 If you want to ask something, just write to me.",
    "friend_text": "🎁 <b>Invite a friend</b>\n\nYour personal link:\n<code>{link}</code>\n\n"
                   "<b>What you get:</b>\n{rewards}\n\nYour friend gets a free first trial lesson.\n\n"
                   "Joined via your link: {joined} · booked a trial: {trial} · started lessons: {paid}",
    "ref_r1": "🎟 friend starts the bot: +3 lives in the Tea shop today",
    "ref_r2": "🖌 friend books a trial: a Chinese name and a calligraphy card from Laziza",
    "ref_r3": "🎁 friend starts lessons: a bonus 30-minute speaking lesson",
    "ref_welcome": "{name} invited you 🌿 Laziza's first trial lesson is free: tap \"📝 Trial lesson\" in the menu.",
    "ref_got1": "🎉 Your friend {friend} started the bot!\n{reward}",
    "ref_got2": "🎉 Your friend {friend} booked a trial lesson!\n{reward}\nLaziza will contact you soon.",
    "ref_got3": "🎉 Your friend {friend} started lessons!\n{reward}\nLaziza will contact you soon.",
    "hw_new": "📚 <b>New homework</b>\n\n{text}\n\nDue: {due}", "hw_btn": "✅ Done",
    "hw_thanks": "Great! Laziza will see it 👏", "hw_none": "No open homework 🎉",
    "hw_title": "📚 <b>Homework</b>", "hw_nodue": "no deadline",
    "hw_remind": "⏰ Reminder: the homework \"{text}\" is due today.",
    "mv_btn": "🔄 Reschedule a lesson",
    "mv_ask": "When suits you? Write like this: <code>Thu 17:30</code> (in Russian: <code>чт 17:30</code>) or <code>15.10 17:30</code>.\nLesson to move: {when}",
    "mv_bad": "I couldn't read that time. Examples: <code>чт 17:30</code> or <code>15.10 17:30</code>.",
    "mv_sent": "Sent to Laziza. I'll write as soon as she replies 🌿",
    "mv_ok": "✅ Lesson moved: {when}", "mv_no": "That time doesn't work. Laziza will write when it does 🌿",
    "mv_none": "I couldn't find your next lesson.",
    "rv_ask": "You've had {n} lessons 🌿 Rate them from 1 to 5:",
    "rv_text": "Thank you! Write a few words: what you like, what to improve (or \"-\" to skip).",
    "rv_public": "May we show your review in posts (without your surname)?", "rv_yes": "Yes", "rv_no": "No",
    "rv_thanks": "Thank you! 💛",
}

P["uz"] = {
    "b_practice": "🎮 Mashq", "b_friend": "🎁 Do'stni taklif qilish", "b_trial": "📝 Sinov darsi",
    "pr_title": "Nimani mashq qilamiz?",
    "pr_quiz": "❓ Viktorina", "pr_cards": "🃏 Kartochkalar", "pr_tea": "🍵 Choyxona do'koni",
    "qz_q": "<b>Savol {n}/{total}</b>\n\n<b>{zh}</b>\n🔊 <code>{py}</code>\n\nBu nima degani?",
    "qz_right": "✅ To'g'ri!", "qz_wrong": "❌ Unday emas. To'g'ri javob: <b>{right}</b>",
    "qz_end": "Raund tugadi: <b>{score}/{total}</b> {emoji}", "qz_mistakes": "Yana ko'rib chiqish kerak:",
    "qz_again": "🔁 Yana bir raund", "qz_add": "🃏 Xatolarni kartochkaga", "qz_added": "Kartochkalarga qo'shilgan so'zlar: {n}",
    "qz_stale": "Raund eskirdi. «Viktorina»ni yana bosing.", "qz_fail": "Savol tuzib bo'lmadi, keyinroq urinib ko'ring.",
    "fc_front": "🃏 <b>{zh}</b>\n🔊 <code>{py}</code>\n\nMa'nosini eslang, so'ng «Ko'rsatish»ni bosing.",
    "fc_show": "👀 Ko'rsatish", "fc_know": "✅ Bilaman", "fc_again": "🔁 Yana",
    "fc_back": "🃏 <b>{zh}</b>  <code>{py}</code>\n📖 {meaning}",
    "fc_done": "Bugunga shu 🎉 O'rganilgan: {known}/{total}. Ertaga qaytib keling, takrorlar o'zi tanlanadi.",
    "fc_new": "To'plamga yangi so'zlar qo'shildi: {n}", "fc_stale": "Kartochka eskirdi. «Kartochkalar»ni yana bosing.",
    "tea_intro": "🍵 <b>Choyxona do'koni</b>\n\nXaridorlar xitoycha gapiradi, siz kerakli narsani uzatasiz. "
                 "To'g'ri: +1 tanga. Xato: −1 jon, so'z yana qaytadi.\n\n"
                 "❤️ Bugungi jonlar: {lives}\n🪙 Tangalar: {coins}\n{emoji} {title}",
    "tea_start": "▶️ Do'konni ochish",
    "tea_order": "🏮 <b>Xaridor aytadi:</b>\n\n<b>{zh}</b>\n🔊 <code>{py}</code>\n\nNimani uzatasiz?   ❤️ {lives}",
    "tea_right": "✅ To'g'ri! +{coins} 🪙", "tea_wrong": "❌ Yo'q. To'g'risi: <b>{right}</b>\n❤️ Qolgan jonlar: {lives}",
    "tea_closed": "🏮 Do'kon bugunga yopildi: jonlar tugadi. Ertaga yana {max} ta bo'ladi. "
                  "Hozircha viktorina yoki kartochkalarni mashq qiling.",
    "tea_levelup": "🎉 Yangi unvon: {emoji} {title}!", "tea_next": "➡️ Keyingi xaridor", "tea_stop": "🚪 Chiqish",
    "tea_stale": "Buyurtma eskirdi. «Choyxona do'koni»ni yana bosing.",
    "title0": "Peshtaxta ortidagi yangi xodim", "title1": "Choy ustasining yordamchisi", "title2": "Do'kon egasi",
    "title3": "Choy ustasi", "title4": "Choy murabbiyi",
    "trial_ask": "Birinchi sinov darsi bepul 🌿 Qaysi kun va soatlar qulay ekanini va o'zingiz haqingizda qisqacha yozing: "
                 "yoshingiz, nimani o'rganmoqchisiz (masalan: «du–ch 18:00 dan keyin, kattaman, noldan»). Lazizaga yetkazaman.",
    "trial_sent": "Lazizaga yetkazdim! U sizga yozadi 🌿",
    "trial_students": "Siz allaqachon Laziza o'quvchilari ro'yxatidasiz, sinov darsi kerak emas 😉 Savol bo'lsa, shunchaki yozing.",
    "friend_text": "🎁 <b>Do'stni taklif qiling</b>\n\nShaxsiy havolangiz:\n<code>{link}</code>\n\n"
                   "<b>Siz nima olasiz:</b>\n{rewards}\n\nDo'stingizga birinchi sinov darsi bepul.\n\n"
                   "Havola orqali kelgan: {joined} · sinovga yozilgan: {trial} · o'qishni boshlagan: {paid}",
    "ref_r1": "🎟 do'st botni ishga tushirdi: bugun Choyxona do'konida +3 jon",
    "ref_r2": "🖌 do'st sinov darsiga yozildi: Lazizadan xitoycha ism va ieroglifli otkritka",
    "ref_r3": "🎁 do'st o'qishni boshladi: 30 daqiqalik bonus suhbat darsi",
    "ref_welcome": "Sizni {name} taklif qildi 🌿 Laziza bilan birinchi sinov darsi bepul: menyudagi «📝 Sinov darsi»ni bosing.",
    "ref_got1": "🎉 Do'stingiz {friend} botni ishga tushirdi!\n{reward}",
    "ref_got2": "🎉 Do'stingiz {friend} sinov darsiga yozildi!\n{reward}\nLaziza tez orada siz bilan bog'lanadi.",
    "ref_got3": "🎉 Do'stingiz {friend} o'qishni boshladi!\n{reward}\nLaziza tez orada siz bilan bog'lanadi.",
    "hw_new": "📚 <b>Yangi uy vazifasi</b>\n\n{text}\n\nMuddat: {due}", "hw_btn": "✅ Bajarildi",
    "hw_thanks": "Zo'r! Laziza ko'radi 👏", "hw_none": "Ochiq vazifalar yo'q 🎉",
    "hw_title": "📚 <b>Uy vazifalari</b>", "hw_nodue": "muddatsiz",
    "hw_remind": "⏰ Eslatma: «{text}» uy vazifasi bugun kerak.",
    "mv_btn": "🔄 Darsni ko'chirish",
    "mv_ask": "Qachon qulay? Mana bunday yozing: <code>чт 17:30</code> yoki <code>15.10 17:30</code>.\nKo'chirilayotgan dars: {when}",
    "mv_bad": "Vaqtni tushunmadim. Misollar: <code>чт 17:30</code> yoki <code>15.10 17:30</code>.",
    "mv_sent": "Lazizaga yubordim. U javob bergach, yozaman 🌿",
    "mv_ok": "✅ Dars ko'chirildi: {when}", "mv_no": "Bu vaqt to'g'ri kelmaydi. Laziza qachon mumkinligini yozadi 🌿",
    "mv_none": "Eng yaqin darsni topolmadim.",
    "rv_ask": "Siz {n} marta shug'ullandingiz 🌿 Darslarni 1 dan 5 gacha baholang:",
    "rv_text": "Rahmat! Bir-ikki og'iz yozing: nima yoqadi, nimani yaxshilash kerak (yoki o'tkazib yuborish uchun «-»).",
    "rv_public": "Fikringizni postlarda (familiyasiz) ko'rsatishimiz mumkinmi?", "rv_yes": "Ha", "rv_no": "Yo'q",
    "rv_thanks": "Rahmat! 💛",
}

P["zh"] = {
    "b_practice": "🎮 练习", "b_friend": "🎁 邀请朋友", "b_trial": "📝 试听课",
    "pr_title": "练什么？",
    "pr_quiz": "❓ 小测验", "pr_cards": "🃏 单词卡", "pr_tea": "🍵 茶铺",
}
# китайский: то, чего нет, берём из английского
P["zh"] = {**P["en"], **P["zh"]}

# строка про новые функции в приветствии
WELCOME_LINE = {
    "ru": "🎮 викторина, карточки и Чайная лавка\n",
    "uz": "🎮 viktorina, kartochkalar va Choyxona do'koni\n",
    "en": "🎮 quiz, flashcards and the Tea shop\n",
    "zh": "🎮 小测验、单词卡和茶铺\n",
}
