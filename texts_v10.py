"""
Тексты версии 10: скидочные месяцы за друзей, продление практики без Telegram Stars, ники в рейтинге,
недельная сводка для родителей. Подключается в конце texts.py.
Цена и способ оплаты не вшиты в текст: они берутся из переменных PAY_INFO, PAY_PRICE, PAY_URL (см. README).
"""

P = {}

P["ru"] = {
    "pr_app": "🎮 Открыть игру (Mini App)",
    # ── скидка за друзей ──
    "ref_r3": "💸 друг начал заниматься: скидка 30% на один месяц занятий. Скидки не суммируются, а идут по очереди: "
              "привёл двоих, получишь два скидочных месяца подряд, каждый действует 30 дней",
    "disc_active": "💸 Скидка 30% действует до {end}.",
    "disc_queue": "⏭ Скидочных месяцев в очереди: {n} (они идут подряд, один за другим, каждый 30 дней).",
    "disc_applied": "💸 Скидка 30% применена к твоей оплате и действует до {end}. Скидочных месяцев в очереди: {n}.",
    # ── жизни закончились: продление без Stars ──
    "lx_offer": "Жизни на сегодня закончились 🍵 Утром их снова будет {base}.\n\nЕсли не хочется ждать, можно включить "
                "«расширенную практику»: {pro} жизней в день на {days} дней. Жизни также даются за друга: ссылка в разделе «🤝 Приведи друга».",
    "lx_btn": "💳 Расширенная практика",
    "lx_info": "💳 <b>Расширенная практика</b>\n{pro} жизней в день вместо {base} на {days} дней.\n\n"
               "Стоимость: <b>{price}</b>\n\nКак оплатить:\n{pay}\n\nПосле оплаты нажми «Я оплатил(а)». "
               "Лазиза проверит платёж и включит доступ, я сразу напишу.",
    "lx_paid": "✅ Я оплатил(а)", "lx_url": "💳 Перейти к оплате",
    "lx_sent": "Спасибо! Заявка отправлена. Как только Лазиза подтвердит платёж, я напишу тебе.",
    "lx_dup": "Заявка уже отправлена, осталось дождаться подтверждения 🌿",
    "lx_ok": "Готово! Расширенная практика включена до {until}: {pro} жизней в день. Приятной игры 🍵",
    "lx_no": "Платёж пока не найден. Если ты уже оплатил(а), пришли Лазизе чек или номер операции.",
    "lx_off": "Чтобы продолжить прямо сейчас, напиши Лазизе: она подскажет, как оплатить. Ответ придёт сюда.",
    # ── ники ──
    "top_consent": "Если вступишь в рейтинг, другие игроки увидят в таблице только твой ник и очки. Настоящее имя знает "
                   "только Лазиза: ей нужно знать победителя, чтобы вручить приз. Согласен(на)?",
    "top_consent_yes": "✅ Да, выбрать ник",
    "nk_ask": "Придумай ник для рейтинга ({min}–{max} знаков: буквы, цифры, пробел, _ . -).\n\nНе пиши настоящее имя, "
              "фамилию, телефон и @username. Например: «Зелёный Дракон» или «Tea Fox».",
    "nk_len": "Ник должен быть от {min} до {max} знаков. Попробуй ещё раз.",
    "nk_chars": "Допустимы только буквы, цифры, пробел и знаки _ . -, без ссылок и @. Нужна хотя бы одна буква.",
    "nk_bad": "Этот ник не подходит по правилам игры. Придумай другой.",
    "nk_name": "Ник похож на настоящее имя. Для защиты придумай что-то другое.",
    "nk_taken": "Такой ник уже занят. Придумай другой.",
    "nk_wait": "Ник можно менять раз в {days} дней. Следующая смена: {date}.",
    "nk_ok": "Твой ник «{nick}». Другие видят только его и очки.",
    "top_joined": "Ты в рейтинге под ником «{nick}»! Очки идут за верные ответы в Чайной лавке, не больше {cap} в день. Удачи 🍵",
    "top_left": "Готово, ты вышел(ла) из рейтинга. Твой ник в таблице больше не виден.",
    "top_change": "✏️ Сменить ник",
    "top_you_nick": "Твой ник: «{nick}»",
    "top_need_nick": "Выбери ник, чтобы остаться в таблице: нажми «Сменить ник».",
    # ── родители ──
    "pa_btn": "👨‍👩‍👧 Родителям",
    "pa_new": "👨‍👩‍👧 <b>Ссылка для родителей</b>\n\nПерешли её маме или папе. Раз в неделю, в воскресенье вечером, они будут получать "
              "короткую сводку: занятия, тесты, домашки, активность в практике, расписание на неделю и напоминание об оплате. "
              "Родитель не видит твои слова, ответы и переписку.\n\n{link}\n\nОтключить родителя можно в любой момент: /parents",
    "pa_consent": "Здравствуйте! Вы подключаетесь к недельной сводке по ученику «{child}» (занятия Лазизы Ропижоновой, 清越).\n\n"
                  "Каждое воскресенье вечером я пришлю: сколько было занятий, результаты тестов, домашние задания, активность "
                  "в практике, расписание на следующую неделю и напоминание об оплате. Больше ничего: личные сообщения, "
                  "слова и ответы ребёнка вам не показываются. Данные хранятся по правилам /privacy.\n\n"
                  "Отключить можно в любой момент командой /stop. Подключить?",
    "pa_yes": "✅ Подключить", "pa_no": "Отмена",
    "pa_done": "Готово, сводка подключена ✅ Первая придёт в воскресенье вечером. Вопросы можно писать прямо сюда, "
               "я передам Лазизе. Отключить: /stop",
    "pa_bad": "Ссылка не действует. Попросите ребёнка или Лазизу прислать новую.",
    "pa_stopped": "Сводка отключена. Если захотите вернуть, попросите новую ссылку.",
    "pa_home": "Вы подключены к недельной сводке по ученику «{child}». Любой вопрос можно написать сюда, я передам Лазизе. Отключить: /stop",
    "pa_q_sent": "Передала Лазизе ✅",
    "pa_child_note": "👨‍👩‍👧 К недельной сводке по тебе подключился родитель. Он видит только итоги недели. Отключить: /parents",
    "pa_list_none": "К тебе пока никто из родителей не подключён. Нажми «👨‍👩‍👧 Родителям», чтобы получить ссылку.",
    "pa_list": "Подключено родителей: {n}. Чтобы отключить всех, нажми кнопку.",
    "pa_off_all": "🚫 Отключить всех", "pa_off_done": "Родители отключены.",
    "pw_title": "📊 <b>Итоги недели · {child}</b>\n{start} – {end}",
    "pw_lessons": "🎓 Занятий проведено: <b>{n}</b> ({dates})",
    "pw_nolessons": "🎓 Занятий на этой неделе не было.",
    "pw_abs": " Отмен: {a}.",
    "pw_test": "📝 Тест «{title}»: <b>{pct}%</b>{delta}",
    "pw_notests": "📝 Новых тестов на этой неделе нет.",
    "pw_hw": "📚 Домашние задания: задано {g}, сдано {d}.",
    "pw_nohw": "📚 Новых домашних заданий на этой неделе не было.",
    "pw_late": " Просрочено: {n}.",
    "pw_prac": "🍵 Практика в боте: {days} из 7 дней, очков {pts}, точность {acc}%.",
    "pw_noprac": "🍵 В практике на этой неделе заниматься не начинали.",
    "pw_sched": "🗓 <b>Расписание на следующую неделю</b>\n{rows}",
    "pw_nosched": "🗓 Расписание на следующую неделю не задано, Лазиза напишет отдельно.",
    "pw_pay_ok": "💳 Оплачено занятий в запасе: <b>{left}</b>.",
    "pw_pay_low": "⚠️ Оплаченных занятий осталось: <b>{left}</b>. Скоро понадобится оплатить следующий пакет.",
    "pw_pay_zero": "⚠️ Оплаченные занятия закончились. Пожалуйста, оплатите следующий пакет, чтобы занятия продолжились.",
    "pw_pay_debt": "💬 По оплате есть задолженность за занятия: {n}. Пожалуйста, свяжитесь с Лазизой.",
    "pw_outro": "С уважением, Лазиза · 清越",
}

P["uz"] = {
    "pr_app": "🎮 O'yinni ochish (Mini App)",
    "ref_r3": "💸 do'st o'qishni boshladi: bir oylik darslarga 30% chegirma. Chegirmalar qo'shilmaydi, navbat bilan beriladi: "
              "ikki do'st olib kelsangiz, ketma-ket ikki chegirmali oy olasiz, har biri 30 kun amal qiladi",
    "disc_active": "💸 30% chegirma {end} gacha amal qiladi.",
    "disc_queue": "⏭ Navbatdagi chegirmali oylar: {n} (ular ketma-ket, birin-ketin ishlaydi, har biri 30 kun).",
    "disc_applied": "💸 30% chegirma to'lovingizga qo'llandi va {end} gacha amal qiladi. Navbatdagi chegirmali oylar: {n}.",
    "lx_offer": "Bugungi jonlar tugadi 🍵 Ertalab yana {base} ta bo'ladi.\n\nKutishni istamasangiz, «kengaytirilgan mashq»ni yoqishingiz "
                "mumkin: {days} kun davomida kuniga {pro} ta jon. Do'st uchun ham jon beriladi: «🤝 Do'stingni olib kel» bo'limidagi havola.",
    "lx_btn": "💳 Kengaytirilgan mashq",
    "lx_info": "💳 <b>Kengaytirilgan mashq</b>\nKuniga {base} o'rniga {pro} ta jon, {days} kun.\n\n"
               "Narxi: <b>{price}</b>\n\nQanday to'lash:\n{pay}\n\nTo'lagandan keyin «To'ladim»ni bosing. "
               "Laziza to'lovni tekshirib, kirishni yoqadi, men darhol yozaman.",
    "lx_paid": "✅ To'ladim", "lx_url": "💳 To'lovga o'tish",
    "lx_sent": "Rahmat! So'rov yuborildi. Laziza to'lovni tasdiqlashi bilan sizga yozaman.",
    "lx_dup": "So'rov allaqachon yuborilgan, tasdiqlashni kutish qoldi 🌿",
    "lx_ok": "Tayyor! Kengaytirilgan mashq {until} gacha yoqildi: kuniga {pro} ta jon. O'yin zavqi bilan 🍵",
    "lx_no": "To'lov hozircha topilmadi. Agar to'lagan bo'lsangiz, Lazizaga chek yoki operatsiya raqamini yuboring.",
    "lx_off": "Hoziroq davom etish uchun Lazizaga yozing: u qanday to'lashni aytadi. Javob shu yerga keladi.",
    "top_consent": "Reytingga qo'shilsangiz, boshqa o'yinchilar jadvalda faqat taxallusingiz va ochkolaringizni ko'radi. Haqiqiy ismingizni "
                   "faqat Laziza biladi: g'olibga sovg'a berish uchun unga kerak. Rozimisiz?",
    "top_consent_yes": "✅ Ha, taxallus tanlayman",
    "nk_ask": "Reyting uchun taxallus o'ylab toping ({min}–{max} belgi: harf, raqam, bo'sh joy, _ . -).\n\nHaqiqiy ism, "
              "familiya, telefon va @username yozmang. Masalan: «Yashil Ajdar» yoki «Tea Fox».",
    "nk_len": "Taxallus {min} tadan {max} tagacha belgidan iborat bo'lishi kerak. Yana urinib ko'ring.",
    "nk_chars": "Faqat harf, raqam, bo'sh joy va _ . - belgilari mumkin, havola va @ bo'lmasin. Kamida bitta harf kerak.",
    "nk_bad": "Bu taxallus o'yin qoidalariga mos kelmaydi. Boshqasini o'ylab toping.",
    "nk_name": "Taxallus haqiqiy ismga o'xshayapti. Himoya uchun boshqa narsa o'ylab toping.",
    "nk_taken": "Bu taxallus band. Boshqasini o'ylab toping.",
    "nk_wait": "Taxallusni {days} kunda bir marta o'zgartirish mumkin. Keyingi o'zgartirish: {date}.",
    "nk_ok": "Taxallusingiz «{nick}». Boshqalar faqat uni va ochkolaringizni ko'radi.",
    "top_joined": "Siz reytingdasiz, taxallusingiz «{nick}»! Ochkolar Choyxona do'konidagi to'g'ri javoblar uchun beriladi, kuniga {cap} tagacha. Omad 🍵",
    "top_left": "Tayyor, reytingdan chiqdingiz. Taxallusingiz jadvalda endi ko'rinmaydi.",
    "top_change": "✏️ Taxallusni o'zgartirish",
    "top_you_nick": "Taxallusingiz: «{nick}»",
    "top_need_nick": "Jadvalda qolish uchun taxallus tanlang: «Taxallusni o'zgartirish»ni bosing.",
    "pa_btn": "👨‍👩‍👧 Ota-onaga",
    "pa_new": "👨‍👩‍👧 <b>Ota-ona uchun havola</b>\n\nUni dadangiz yoki onangizga yuboring. Haftada bir marta, yakshanba kechqurun ular qisqa "
              "xulosa oladi: darslar, testlar, uy vazifalari, mashqdagi faollik, haftalik jadval va to'lov eslatmasi. "
              "Ota-ona sizning so'zlaringiz, javoblaringiz va yozishmangizni ko'rmaydi.\n\n{link}\n\nOta-onani istalgan vaqtda o'chirish mumkin: /parents",
    "pa_consent": "Assalomu alaykum! Siz «{child}» o'quvchisi bo'yicha haftalik xulosaga ulanyapsiz (Laziza Ropijonova, 清越 darslari).\n\n"
                  "Har yakshanba kechqurun yuboraman: nechta dars bo'lgani, test natijalari, uy vazifalari, mashqdagi faollik, "
                  "keyingi hafta jadvali va to'lov eslatmasi. Boshqa hech narsa: bolaning shaxsiy xabarlari, so'zlari va javoblari "
                  "sizga ko'rsatilmaydi. Ma'lumotlar /privacy qoidalariga ko'ra saqlanadi.\n\n"
                  "Istalgan vaqtda /stop bilan o'chirish mumkin. Ulaymizmi?",
    "pa_yes": "✅ Ulash", "pa_no": "Bekor qilish",
    "pa_done": "Tayyor, xulosa ulandi ✅ Birinchisi yakshanba kechqurun keladi. Savollarni shu yerga yozishingiz mumkin, "
               "Lazizaga yetkazaman. O'chirish: /stop",
    "pa_bad": "Havola amal qilmaydi. Bolangizdan yoki Lazizadan yangisini yuborishni so'rang.",
    "pa_stopped": "Xulosa o'chirildi. Qayta ulamoqchi bo'lsangiz, yangi havola so'rang.",
    "pa_home": "Siz «{child}» o'quvchisi bo'yicha haftalik xulosaga ulangansiz. Istalgan savolni shu yerga yozing, Lazizaga yetkazaman. O'chirish: /stop",
    "pa_q_sent": "Lazizaga yetkazdim ✅",
    "pa_child_note": "👨‍👩‍👧 Siz haqingizdagi haftalik xulosaga ota-onangiz ulandi. U faqat hafta yakunlarini ko'radi. O'chirish: /parents",
    "pa_list_none": "Sizga hozircha hech bir ota-ona ulanmagan. Havola olish uchun «👨‍👩‍👧 Ota-onaga»ni bosing.",
    "pa_list": "Ulangan ota-onalar: {n}. Hammasini o'chirish uchun tugmani bosing.",
    "pa_off_all": "🚫 Hammasini o'chirish", "pa_off_done": "Ota-onalar o'chirildi.",
    "pw_title": "📊 <b>Hafta yakunlari · {child}</b>\n{start} – {end}",
    "pw_lessons": "🎓 O'tkazilgan darslar: <b>{n}</b> ({dates})",
    "pw_nolessons": "🎓 Bu hafta dars bo'lmadi.",
    "pw_abs": " Bekor qilishlar: {a}.",
    "pw_test": "📝 «{title}» testi: <b>{pct}%</b>{delta}",
    "pw_notests": "📝 Bu hafta yangi testlar yo'q.",
    "pw_hw": "📚 Uy vazifalari: berildi {g}, topshirildi {d}.",
    "pw_nohw": "📚 Bu hafta yangi uy vazifasi berilmadi.",
    "pw_late": " Muddati o'tgan: {n}.",
    "pw_prac": "🍵 Botdagi mashq: 7 kundan {days} kun, ochko {pts}, aniqlik {acc}%.",
    "pw_noprac": "🍵 Bu hafta mashq boshlanmadi.",
    "pw_sched": "🗓 <b>Keyingi hafta jadvali</b>\n{rows}",
    "pw_nosched": "🗓 Keyingi hafta jadvali belgilanmagan, Laziza alohida yozadi.",
    "pw_pay_ok": "💳 To'langan darslar zaxirasi: <b>{left}</b>.",
    "pw_pay_low": "⚠️ To'langan darslar qoldi: <b>{left}</b>. Tez orada keyingi paketni to'lash kerak bo'ladi.",
    "pw_pay_zero": "⚠️ To'langan darslar tugadi. Darslar davom etishi uchun keyingi paketni to'lang.",
    "pw_pay_debt": "💬 Darslar uchun qarzdorlik bor: {n}. Iltimos, Laziza bilan bog'laning.",
    "pw_outro": "Hurmat bilan, Laziza · 清越",
}

P["en"] = {
    "pr_app": "🎮 Open the game (Mini App)",
    "ref_r3": "💸 friend starts lessons: 30% off one month of lessons. Discounts do not stack, they run one after another: "
              "bring two friends and you get two discounted months in a row, each valid for 30 days",
    "disc_active": "💸 Your 30% discount is valid until {end}.",
    "disc_queue": "⏭ Discounted months in the queue: {n} (they run back to back, each for 30 days).",
    "disc_applied": "💸 Your 30% discount has been applied to your payment and is valid until {end}. Discounted months in the queue: {n}.",
    "lx_offer": "Today's lives are used up 🍵 You will have {base} again in the morning.\n\nIf you do not want to wait, you can turn on "
                "“extended practice”: {pro} lives a day for {days} days. Friends also earn lives: the link is in “🤝 Bring a friend”.",
    "lx_btn": "💳 Extended practice",
    "lx_info": "💳 <b>Extended practice</b>\n{pro} lives a day instead of {base}, for {days} days.\n\n"
               "Price: <b>{price}</b>\n\nHow to pay:\n{pay}\n\nAfter paying, tap “I have paid”. "
               "Laziza will check the payment and switch it on, and I will message you right away.",
    "lx_paid": "✅ I have paid", "lx_url": "💳 Go to payment",
    "lx_sent": "Thank you! The request is sent. I will message you as soon as Laziza confirms the payment.",
    "lx_dup": "The request is already sent, now we just wait for confirmation 🌿",
    "lx_ok": "Done! Extended practice is on until {until}: {pro} lives a day. Enjoy the game 🍵",
    "lx_no": "The payment has not been found yet. If you have already paid, send Laziza the receipt or the transaction number.",
    "lx_off": "To continue right now, write to Laziza: she will tell you how to pay. The reply will come here.",
    "top_consent": "If you join the ranking, other players will see only your nickname and points in the table. Only Laziza knows your real "
                   "name: she needs it to hand over the prize to the winner. Do you agree?",
    "top_consent_yes": "✅ Yes, choose a nickname",
    "nk_ask": "Make up a nickname for the ranking ({min}–{max} characters: letters, digits, space, _ . -).\n\nDo not write your real name, "
              "surname, phone or @username. For example: “Green Dragon” or “Tea Fox”.",
    "nk_len": "The nickname must be {min} to {max} characters. Try again.",
    "nk_chars": "Only letters, digits, space and _ . - are allowed, with no links or @. At least one letter is needed.",
    "nk_bad": "This nickname does not fit the game rules. Please pick another one.",
    "nk_name": "The nickname looks like a real name. For your protection, please pick something else.",
    "nk_taken": "This nickname is already taken. Please pick another one.",
    "nk_wait": "You can change the nickname once every {days} days. Next change: {date}.",
    "nk_ok": "Your nickname is “{nick}”. Others see only it and your points.",
    "top_joined": "You are in the ranking as “{nick}”! Points come from correct answers in the Tea shop, up to {cap} a day. Good luck 🍵",
    "top_left": "Done, you have left the ranking. Your nickname is no longer visible in the table.",
    "top_change": "✏️ Change nickname",
    "top_you_nick": "Your nickname: “{nick}”",
    "top_need_nick": "Pick a nickname to stay in the table: tap “Change nickname”.",
    "pa_btn": "👨‍👩‍👧 For parents",
    "pa_new": "👨‍👩‍👧 <b>Link for parents</b>\n\nForward it to your mum or dad. Once a week, on Sunday evening, they will get a short "
              "summary: lessons, tests, homework, practice activity, next week's schedule and a payment reminder. "
              "Parents do not see your words, answers or chats.\n\n{link}\n\nYou can disconnect a parent at any time: /parents",
    "pa_consent": "Hello! You are connecting to the weekly summary for the student “{child}” (lessons with Laziza Ropijonova, 清越).\n\n"
                  "Every Sunday evening I will send: how many lessons took place, test results, homework, practice activity, "
                  "next week's schedule and a payment reminder. Nothing else: the child's private messages, words and answers "
                  "are not shown to you. Data is kept under the /privacy rules.\n\n"
                  "You can disconnect at any time with /stop. Connect?",
    "pa_yes": "✅ Connect", "pa_no": "Cancel",
    "pa_done": "Done, the summary is connected ✅ The first one arrives on Sunday evening. You can write any question here, "
               "I will pass it to Laziza. Disconnect: /stop",
    "pa_bad": "This link is no longer valid. Please ask your child or Laziza for a new one.",
    "pa_stopped": "The summary is switched off. If you want it back, ask for a new link.",
    "pa_home": "You are connected to the weekly summary for the student “{child}”. Write any question here and I will pass it to Laziza. Disconnect: /stop",
    "pa_q_sent": "Passed to Laziza ✅",
    "pa_child_note": "👨‍👩‍👧 A parent has connected to the weekly summary about you. They see only the week's results. Disconnect: /parents",
    "pa_list_none": "No parent is connected to you yet. Tap “👨‍👩‍👧 For parents” to get a link.",
    "pa_list": "Connected parents: {n}. Tap the button to disconnect all of them.",
    "pa_off_all": "🚫 Disconnect all", "pa_off_done": "Parents disconnected.",
    "pw_title": "📊 <b>Week summary · {child}</b>\n{start} – {end}",
    "pw_lessons": "🎓 Lessons held: <b>{n}</b> ({dates})",
    "pw_nolessons": "🎓 There were no lessons this week.",
    "pw_abs": " Cancellations: {a}.",
    "pw_test": "📝 Test “{title}”: <b>{pct}%</b>{delta}",
    "pw_notests": "📝 No new tests this week.",
    "pw_hw": "📚 Homework: assigned {g}, handed in {d}.",
    "pw_nohw": "📚 No new homework this week.",
    "pw_late": " Overdue: {n}.",
    "pw_prac": "🍵 Practice in the bot: {days} of 7 days, {pts} points, accuracy {acc}%.",
    "pw_noprac": "🍵 No practice in the bot this week.",
    "pw_sched": "🗓 <b>Schedule for next week</b>\n{rows}",
    "pw_nosched": "🗓 Next week's schedule is not set, Laziza will write separately.",
    "pw_pay_ok": "💳 Paid lessons in reserve: <b>{left}</b>.",
    "pw_pay_low": "⚠️ Paid lessons left: <b>{left}</b>. The next package will need paying soon.",
    "pw_pay_zero": "⚠️ The paid lessons have run out. Please pay for the next package so the lessons can continue.",
    "pw_pay_debt": "💬 There is an outstanding balance for lessons: {n}. Please contact Laziza.",
    "pw_outro": "Best regards, Laziza · 清越",
}

P["zh"] = {
    "pr_app": "🎮 打开游戏（Mini App）",
    "ref_r3": "💸 朋友开始上课：一个月课程 7 折（优惠 30%）。优惠不叠加，而是依次使用：带来两位朋友，就连续获得两个优惠月，每个有效期 30 天",
    "disc_active": "💸 你的 30% 优惠有效期至 {end}。",
    "disc_queue": "⏭ 排队中的优惠月：{n} 个（依次连续使用，每个 30 天）。",
    "disc_applied": "💸 30% 优惠已用于你这次付款，有效期至 {end}。排队中的优惠月：{n} 个。",
    "lx_offer": "今天的命用完了 🍵 明早会恢复到 {base} 条。\n\n不想等的话，可以开通“加强练习”：{days} 天内每天 {pro} 条命。"
                "带朋友来也能获得命：见“🤝 带朋友来”里的链接。",
    "lx_btn": "💳 加强练习",
    "lx_info": "💳 <b>加强练习</b>\n{days} 天内每天 {pro} 条命（原为 {base} 条）。\n\n价格：<b>{price}</b>\n\n付款方式：\n{pay}\n\n"
               "付款后请点“我已付款”。Laziza 核实后会为你开通，我会马上通知你。",
    "lx_paid": "✅ 我已付款", "lx_url": "💳 去付款",
    "lx_sent": "谢谢！申请已发送。Laziza 确认付款后我会通知你。",
    "lx_dup": "申请已发送，请等待确认 🌿",
    "lx_ok": "好了！加强练习已开通至 {until}：每天 {pro} 条命。玩得开心 🍵",
    "lx_no": "暂时没有找到这笔付款。如果你已经付款，请把收据或交易号发给 Laziza。",
    "lx_off": "想立刻继续的话，请给 Laziza 留言，她会告诉你如何付款。回复会发到这里。",
    "top_consent": "加入排行榜后，其他玩家只会在榜上看到你的昵称和积分。你的真实姓名只有 Laziza 知道：她需要知道冠军是谁才能发奖。你同意吗？",
    "top_consent_yes": "✅ 同意，去取昵称",
    "nk_ask": "为排行榜取个昵称（{min}–{max} 个字符：字母、数字、空格、_ . -）。\n\n不要写真实姓名、姓氏、电话和 @用户名。例如：“绿色小龙”或“Tea Fox”。",
    "nk_len": "昵称需要 {min} 到 {max} 个字符，请再试一次。",
    "nk_chars": "只能使用字母、数字、空格和 _ . -，不能含链接或 @，且至少要有一个字母。",
    "nk_bad": "这个昵称不符合游戏规则，请换一个。",
    "nk_name": "昵称看起来像真实姓名。为了保护你，请换一个。",
    "nk_taken": "这个昵称已被占用，请换一个。",
    "nk_wait": "昵称每 {days} 天只能更改一次。下次可改：{date}。",
    "nk_ok": "你的昵称是“{nick}”。其他人只能看到它和你的积分。",
    "top_joined": "你已以“{nick}”加入排行榜！积分来自茶铺里的正确回答，每天最多 {cap} 分。祝你好运 🍵",
    "top_left": "好的，你已退出排行榜。榜上不再显示你的昵称。",
    "top_change": "✏️ 更改昵称",
    "top_you_nick": "你的昵称：“{nick}”",
    "top_need_nick": "请选择一个昵称才能留在榜上：点“更改昵称”。",
    "pa_btn": "👨‍👩‍👧 家长入口",
    "pa_new": "👨‍👩‍👧 <b>家长链接</b>\n\n请转发给爸爸或妈妈。每周日晚上，他们会收到一份简短总结：上课情况、测验、作业、练习活跃度、下周课表和付款提醒。"
              "家长看不到你的单词、答案和聊天内容。\n\n{link}\n\n你可以随时取消家长的连接：/parents",
    "pa_consent": "您好！您正在连接学生“{child}”的每周总结（Laziza Ropijonova 的课程，清越）。\n\n"
                  "每周日晚上我会发送：上了几节课、测验成绩、作业、练习活跃度、下周课表和付款提醒。仅此而已：孩子的私人消息、单词和答案不会展示给您。"
                  "数据按 /privacy 规则保存。\n\n您可以随时用 /stop 取消。确认连接吗？",
    "pa_yes": "✅ 连接", "pa_no": "取消",
    "pa_done": "好了，周总结已连接 ✅ 第一份将在周日晚上送达。您有问题可以直接写在这里，我会转告 Laziza。取消：/stop",
    "pa_bad": "链接已失效。请让孩子或 Laziza 重新发送一个。",
    "pa_stopped": "周总结已关闭。如需恢复，请索取新的链接。",
    "pa_home": "您已连接学生“{child}”的每周总结。有任何问题请写在这里，我会转告 Laziza。取消：/stop",
    "pa_q_sent": "已转告 Laziza ✅",
    "pa_child_note": "👨‍👩‍👧 有家长连接了关于你的每周总结。他们只能看到一周的结果。取消：/parents",
    "pa_list_none": "还没有家长连接到你。点“👨‍👩‍👧 家长入口”获取链接。",
    "pa_list": "已连接的家长：{n}。点按钮可全部取消。",
    "pa_off_all": "🚫 全部取消", "pa_off_done": "家长已取消连接。",
    "pw_title": "📊 <b>本周总结 · {child}</b>\n{start} – {end}",
    "pw_lessons": "🎓 本周上课：<b>{n}</b> 节（{dates}）",
    "pw_nolessons": "🎓 本周没有上课。",
    "pw_abs": " 请假：{a} 次。",
    "pw_test": "📝 测验“{title}”：<b>{pct}%</b>{delta}",
    "pw_notests": "📝 本周没有新的测验。",
    "pw_hw": "📚 作业：布置 {g} 份，已交 {d} 份。",
    "pw_nohw": "📚 本周没有新作业。",
    "pw_late": " 逾期：{n} 份。",
    "pw_prac": "🍵 机器人练习：7 天中练了 {days} 天，{pts} 分，正确率 {acc}%。",
    "pw_noprac": "🍵 本周没有进行机器人练习。",
    "pw_sched": "🗓 <b>下周课表</b>\n{rows}",
    "pw_nosched": "🗓 下周课表尚未确定，Laziza 会另行通知。",
    "pw_pay_ok": "💳 已付费剩余课时：<b>{left}</b>。",
    "pw_pay_low": "⚠️ 已付费课时还剩 <b>{left}</b> 节，很快需要支付下一期。",
    "pw_pay_zero": "⚠️ 已付费课时已用完。请支付下一期以便继续上课。",
    "pw_pay_debt": "💬 课程有欠费：{n} 节。请联系 Laziza。",
    "pw_outro": "此致，Laziza · 清越",
}

# Правки уже существующих текстов: имя → ник. (старое → новое), применяются в texts.py
RULES_PATCH = {
    "ru": [("только твоё первое имя и очки", "только твой ник и очки. Ник придумываешь ты, настоящее имя не показывается, его знает только Лазиза "
                                             "(ей нужно знать победителя, чтобы вручить приз). Ник можно менять раз в 7 дней, а неподходящий ник Лазиза вправе сбросить"),
           ("В имени, в сообщениях", "В нике, в сообщениях"),
           ("В таблице видно только первое имя и очки.", "В таблице видны только ник и очки, настоящее имя знает только Лазиза.")],
    "uz": [("faqat ismingizning birinchi so'zini va ochkolaringizni ko'radi", "faqat taxallusingiz va ochkolaringizni ko'radi. Taxallusni o'zingiz o'ylab topasiz, haqiqiy ism "
                                                                              "ko'rsatilmaydi, uni faqat Laziza biladi (g'olibga sovg'a berish uchun). Taxallusni 7 kunda bir marta o'zgartirish mumkin, "
                                                                              "mos kelmaydigan taxallusni Laziza bekor qilishi mumkin"),
           ("Ismda, xabarlarda", "Taxallusda, xabarlarda"),
           ("Jadvalda faqat birinchi ism va ochkolar ko'rinadi.", "Jadvalda faqat taxallus va ochkolar ko'rinadi, haqiqiy ismni faqat Laziza biladi.")],
    "en": [("only your first name and your points", "only your nickname and your points. You make the nickname up yourself, your real name is not shown and only Laziza knows it "
                                                   "(she needs it to hand the prize to the winner). You can change the nickname once every 7 days, and Laziza may reset an unsuitable one"),
           ("In your name, your messages", "In your nickname, your messages"),
           ("The table shows only your first name and points.", "The table shows only your nickname and points; only Laziza knows your real name.")],
    "zh": [("其他玩家只会看到你名字的第一个词和你的积分", "其他玩家只会看到你的昵称和你的积分。昵称由你自己取，真实姓名不会显示，只有 Laziza 知道（她需要知道冠军是谁才能发奖）。"
                                                  "昵称每 7 天可更改一次，不合适的昵称 Laziza 有权重置"),
           ("在名字、消息和奖品课主题中", "在昵称、消息和奖品课主题中"),
           ("排行榜上只显示名字的第一个词和积分。", "排行榜上只显示昵称和积分，真实姓名只有 Laziza 知道。")],
}

PRIVACY_PATCH = {
    "ru": ("· если вступишь в рейтинг недели: твоё первое имя и очки видны другим участникам (выйти можно в любой момент)\n",
           "· если вступишь в рейтинг недели: другим участникам видны только твой ник и очки, настоящее имя знает только Лазиза (выйти можно в любой момент)\n"
           "· если подключишь родителя: раз в неделю он получает итоги (занятия, тесты, домашки, активность в практике, расписание, остаток оплаченных занятий), но не твои слова и переписку; отключить можно в любой момент (/parents)\n"),
    "uz": ("· hafta reytingiga qo'shilsangiz: ismingizning birinchi so'zi va ochkolaringiz boshqa ishtirokchilarga ko'rinadi (istalgan vaqtda chiqish mumkin)\n",
           "· hafta reytingiga qo'shilsangiz: boshqa ishtirokchilarga faqat taxallusingiz va ochkolaringiz ko'rinadi, haqiqiy ismni faqat Laziza biladi (istalgan vaqtda chiqish mumkin)\n"
           "· ota-onani ulasangiz: u haftada bir marta xulosa oladi (darslar, testlar, uy vazifalari, mashqdagi faollik, jadval, to'langan darslar qoldig'i), lekin so'zlaringiz va yozishmangizni ko'rmaydi; istalgan vaqtda o'chirish mumkin (/parents)\n"),
    "en": ("· if you join the weekly ranking: your first name and points are visible to other participants (you can leave at any time)\n",
           "· if you join the weekly ranking: other participants see only your nickname and points, and only Laziza knows your real name (you can leave at any time)\n"
           "· if you connect a parent: once a week they get a summary (lessons, tests, homework, practice activity, schedule, balance of paid lessons) but not your words or chats; you can disconnect them at any time (/parents)\n"),
    "zh": ("· 如果你加入每周排行榜：你名字的第一个词和积分会被其他参与者看到（可随时退出）\n",
           "· 如果你加入每周排行榜：其他参与者只能看到你的昵称和积分，真实姓名只有 Laziza 知道（可随时退出）\n"
           "· 如果你连接了家长：家长每周会收到一份总结（上课、测验、作业、练习活跃度、课表、已付费课时余额），看不到你的单词和聊天内容；可随时取消（/parents）\n"),
}
