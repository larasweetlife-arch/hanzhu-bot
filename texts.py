"""Тексты интерфейса на четырёх языках."""

LANG_PROMPT = "🌐 Выбери язык · Tilni tanlang · Choose language · 选择语言"

WEEKDAYS = {
    "ru": ["пн", "вт", "ср", "чт", "пт", "сб", "вс"],
    "uz": ["du", "se", "ch", "pa", "ju", "sh", "ya"],
    "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "zh": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
}

T = {
"ru": {
 "ask_name": "你好！👋 Я 汉助 (HanZhu), помощник по китайскому от Лазизы.\n\nКак тебя зовут?",
 "ask_source": "Приятно познакомиться, {name}!\n\nОткуда ты про меня узнал(а)?",
 "ask_level": "И последнее: какой у тебя уровень китайского?",
 "done": "Готово, {name}! Добро пожаловать 🐉",
 "menu": "Что делаем?",
 "sources": ["Канал «Чаёвничаем о китайском»", "От друга", "Из группы или чата", "Занимаюсь с Лазизой", "Другое"],
 "levels": ["Только начинаю", "HSK 1", "HSK 2", "HSK 3", "HSK 4", "HSK 5", "HSK 6", "HSK 7–9"],
 "b_word": "📚 Слово дня", "b_chengyu": "🧧 Чэнъюй", "b_fact": "🌏 Факт о Китае",
 "b_tr": "🔤 Перевод", "b_progress": "📊 Мой прогресс", "b_lang": "🌐 Язык",
 "b_channel": "📢 Канал", "b_help": "❓ Помощь",
 "word": "📚 Слово дня", "chengyu": "🧧 Чэнъюй дня", "fact": "🌏 Факт о Китае",
 "tr_ask": "Напиши слово, на русском или на китайском:",
 "tr_none": "Такого слова пока нет в словаре. Я его пополняю 🔄",
 "channel": "📢 Мой канал о китайском языке и культуре:\nhttps://t.me/qing_laoshi",
 "help": ("汉助, помощник по китайскому\nСоздан Лазизой Ропижоновой\n\n"
          "/menu меню\n/word слово дня\n/chengyu чэнъюй\n/fact факт о Китае\n"
          "/translate перевод\n/progress мой прогресс\n/lang сменить язык\n\n"
          "Если напишешь мне что-то своё, я передам это Лазизе, и она ответит сама."),
 "no_progress": ("Пока тут пусто 🌱\n\nЭтот раздел заполняется, когда ты занимаешься с Лазизой: "
                 "видно пройденные уроки, оплату и результаты тестов.\n\n"
                 "Хочешь заниматься, напиши ей, первый урок бесплатный."),
 "p_title": "📊 Твой прогресс", "p_lessons": "Уроков пройдено", "p_paid": "Оплачено",
 "p_left": "Осталось", "p_renew": "Пора продлить занятия, напиши Лазизе",
 "p_tests": "📈 Результаты тестов", "p_first": "Первый", "p_last": "Последний",
 "p_growth": "Динамика", "p_pp": "п.п.", "p_no_tests": "Тестов пока не было.",
 "p_recent": "🗓 Последние занятия", "p_sched": "Расписание",
 "lang_pick": "Выбери язык общения", "lang_changed": "Готово, общаемся по-русски 🐉",
 "day_today": "сегодня", "day_tomorrow": "завтра",
 "remind24": "🗓 Занятие {day} в <b>{time}</b>.\nВсё в силе?",
 "remind1": "⏰ Через час занятие ({time}).", "remind1_link": "\n\nСсылка: {link}",
 "btn_yes": "✅ Буду", "btn_no": "❌ Не смогу",
 "att_yes": "Отлично, жду 🐉",
 "att_ask": "Жаль 😔 Напиши одним сообщением причину, я передам Лазизе.",
 "att_ok": "Передала Лазизе, она свяжется насчёт переноса 🤍",
 "att_late": "Передала Лазизе, она свяжется 🤍\nНапоминаю: по условиям отмена позже чем за 3 часа считается проведённым уроком.",
 "att_past": "Это занятие уже прошло.",
 "pay_nudge": "Привет! Оплаченные занятия подходят к концу. Когда будет удобно, напиши Лазизе насчёт продления 🤍",
 "q_sent": "Передала твоё сообщение Лазизе, она ответит сама 🤍",
},
"uz": {
 "ask_name": "你好！👋 Men 汉助 (HanZhu), Lazizaning xitoy tili yordamchisiman.\n\nIsmingiz nima?",
 "ask_source": "Tanishganimdan xursandman, {name}!\n\nMen haqimda qayerdan bildingiz?",
 "ask_level": "Oxirgi savol: xitoy tili darajangiz qanday?",
 "done": "Tayyor, {name}! Xush kelibsiz 🐉",
 "menu": "Nima qilamiz?",
 "sources": ["«Chayevnichaem o kitayskom» kanali", "Do'stdan", "Guruh yoki chatdan", "Laziza bilan shug'ullanaman", "Boshqa"],
 "levels": ["Endi boshlayapman", "HSK 1", "HSK 2", "HSK 3", "HSK 4", "HSK 5", "HSK 6", "HSK 7–9"],
 "b_word": "📚 Kunning so'zi", "b_chengyu": "🧧 Chengyu", "b_fact": "🌏 Xitoy fakti",
 "b_tr": "🔤 Tarjima", "b_progress": "📊 Natijam", "b_lang": "🌐 Til",
 "b_channel": "📢 Kanal", "b_help": "❓ Yordam",
 "word": "📚 Kunning so'zi", "chengyu": "🧧 Kunning chengyusi", "fact": "🌏 Xitoy haqida fakt",
 "tr_ask": "So'z yozing, o'zbekcha yoki xitoycha:",
 "tr_none": "Bu so'z hozircha lug'atda yo'q. Men uni to'ldiryapman 🔄",
 "channel": "📢 Xitoy tili va madaniyati haqidagi kanalim:\nhttps://t.me/qing_laoshi",
 "help": ("汉助, xitoy tili yordamchisi\nLaziza Ropijonova yaratgan\n\n"
          "/menu menyu\n/word kunning so'zi\n/chengyu chengyu\n/fact fakt\n"
          "/translate tarjima\n/progress natijam\n/lang tilni almashtirish\n\n"
          "O'zingizdan biror narsa yozsangiz, uni Lazizaga yetkazaman, u o'zi javob beradi."),
 "no_progress": ("Hozircha bo'sh 🌱\n\nBu bo'lim Laziza bilan darslar boshlanganda to'ladi: "
                 "o'tilgan darslar, to'lov va test natijalari ko'rinadi."),
 "p_title": "📊 Sizning natijangiz", "p_lessons": "O'tilgan darslar", "p_paid": "To'langan",
 "p_left": "Qoldi", "p_renew": "Darslarni uzaytirish vaqti, Lazizaga yozing",
 "p_tests": "📈 Test natijalari", "p_first": "Birinchi", "p_last": "Oxirgi",
 "p_growth": "O'sish", "p_pp": "f.p.", "p_no_tests": "Hozircha testlar bo'lmagan.",
 "p_recent": "🗓 Oxirgi darslar", "p_sched": "Dars jadvali",
 "lang_pick": "Muloqot tilini tanlang", "lang_changed": "Tayyor, endi o'zbek tilida gaplashamiz 🐉",
 "day_today": "bugun", "day_tomorrow": "ertaga",
 "remind24": "🗓 Dars {day} soat <b>{time}</b> da.\nHammasi o'z kuchidami?",
 "remind1": "⏰ Bir soatdan keyin dars ({time}).", "remind1_link": "\n\nHavola: {link}",
 "btn_yes": "✅ Kelaman", "btn_no": "❌ Kela olmayman",
 "att_yes": "Ajoyib, kutaman 🐉",
 "att_ask": "Afsus 😔 Sababini bitta xabarda yozing, Lazizaga yetkazaman.",
 "att_ok": "Lazizaga yetkazdim, u ko'chirish haqida bog'lanadi 🤍",
 "att_late": "Lazizaga yetkazdim 🤍\nEslatma: shartlarga ko'ra, 3 soatdan kech bekor qilingan dars o'tilgan hisoblanadi.",
 "att_past": "Bu dars allaqachon o'tib ketdi.",
 "pay_nudge": "Salom! To'langan darslar tugab qoldi. Qulay payt Lazizaga yozing, davom ettiramiz 🤍",
 "q_sent": "Xabaringizni Lazizaga yetkazdim, u o'zi javob beradi 🤍",
},
"en": {
 "ask_name": "你好！👋 I'm 汉助 (HanZhu), Laziza's Chinese learning assistant.\n\nWhat's your name?",
 "ask_source": "Nice to meet you, {name}!\n\nHow did you find out about me?",
 "ask_level": "Last one: what's your Chinese level?",
 "done": "All set, {name}! Welcome 🐉",
 "menu": "What would you like?",
 "sources": ["Telegram channel", "From a friend", "From a group or chat", "I study with Laziza", "Other"],
 "levels": ["Just starting", "HSK 1", "HSK 2", "HSK 3", "HSK 4", "HSK 5", "HSK 6", "HSK 7–9"],
 "b_word": "📚 Word of the day", "b_chengyu": "🧧 Chengyu", "b_fact": "🌏 China fact",
 "b_tr": "🔤 Translate", "b_progress": "📊 My progress", "b_lang": "🌐 Language",
 "b_channel": "📢 Channel", "b_help": "❓ Help",
 "word": "📚 Word of the Day", "chengyu": "🧧 Chengyu of the Day", "fact": "🌏 Fact about China",
 "tr_ask": "Type a word, in English or Chinese:",
 "tr_none": "Not in the dictionary yet. I'm still adding words 🔄",
 "channel": "📢 My channel about Chinese language and culture:\nhttps://t.me/qing_laoshi",
 "help": ("汉助, Chinese learning assistant\nCreated by Laziza Ropijonova\n\n"
          "/menu menu\n/word word of the day\n/chengyu chengyu\n/fact China fact\n"
          "/translate translate\n/progress my progress\n/lang change language\n\n"
          "If you write me something of your own, I'll pass it to Laziza and she'll reply herself."),
 "no_progress": ("Nothing here yet 🌱\n\nThis section fills up once you start lessons with Laziza: "
                 "lessons completed, payments and test results."),
 "p_title": "📊 Your progress", "p_lessons": "Lessons completed", "p_paid": "Paid for",
 "p_left": "Remaining", "p_renew": "Time to renew, message Laziza",
 "p_tests": "📈 Test results", "p_first": "First", "p_last": "Latest",
 "p_growth": "Change", "p_pp": "pp", "p_no_tests": "No tests yet.",
 "p_recent": "🗓 Recent lessons", "p_sched": "Schedule",
 "lang_pick": "Choose your language", "lang_changed": "Done, we'll talk in English now 🐉",
 "day_today": "today", "day_tomorrow": "tomorrow",
 "remind24": "🗓 Lesson {day} at <b>{time}</b>.\nStill good?",
 "remind1": "⏰ Lesson in one hour ({time}).", "remind1_link": "\n\nLink: {link}",
 "btn_yes": "✅ I'll be there", "btn_no": "❌ Can't make it",
 "att_yes": "Great, see you 🐉",
 "att_ask": "Sorry to hear 😔 Please write the reason in one message, I'll pass it to Laziza.",
 "att_ok": "Passed to Laziza, she'll contact you about rescheduling 🤍",
 "att_late": "Passed to Laziza 🤍\nReminder: under the terms, cancelling less than 3 hours before counts as a held lesson.",
 "att_past": "That lesson has already passed.",
 "pay_nudge": "Hi! Your paid lessons are almost used up. Whenever it's convenient, message Laziza about renewing 🤍",
 "q_sent": "Passed your message to Laziza, she'll reply herself 🤍",
},
"zh": {
 "ask_name": "你好！👋 我是汉助，Laziza 老师的汉语学习助手。\n\n你叫什么名字？",
 "ask_source": "很高兴认识你，{name}！\n\n你是怎么知道我的？",
 "ask_level": "最后一个问题：你的汉语水平是？",
 "done": "都准备好了，{name}！欢迎 🐉",
 "menu": "想做什么？",
 "sources": ["电报频道", "朋友介绍", "群聊", "我在跟 Laziza 学习", "其他"],
 "levels": ["刚开始", "HSK 1", "HSK 2", "HSK 3", "HSK 4", "HSK 5", "HSK 6", "HSK 7–9"],
 "b_word": "📚 今日词汇", "b_chengyu": "🧧 成语", "b_fact": "🌏 中国小知识",
 "b_tr": "🔤 翻译", "b_progress": "📊 我的进度", "b_lang": "🌐 语言",
 "b_channel": "📢 频道", "b_help": "❓ 帮助",
 "word": "📚 今日词汇", "chengyu": "🧧 今日成语", "fact": "🌏 关于中国",
 "tr_ask": "请输入要翻译的词：",
 "tr_none": "词典里还没有这个词，我还在补充 🔄",
 "channel": "📢 我的汉语和文化频道：\nhttps://t.me/qing_laoshi",
 "help": ("汉助，汉语学习助手\n由 Laziza Ropijonova 创建\n\n"
          "/menu 菜单\n/word 今日词汇\n/chengyu 成语\n/fact 小知识\n"
          "/translate 翻译\n/progress 我的进度\n/lang 切换语言\n\n"
          "你写给我的其他内容，我会转给 Laziza，她会亲自回复。"),
 "no_progress": "这里还是空的 🌱\n\n开始上课后，这里会显示课时、付款和测试成绩。",
 "p_title": "📊 你的进度", "p_lessons": "已上课时", "p_paid": "已付课时",
 "p_left": "剩余", "p_renew": "该续费了，请联系 Laziza",
 "p_tests": "📈 测试成绩", "p_first": "第一次", "p_last": "最近",
 "p_growth": "变化", "p_pp": "个百分点", "p_no_tests": "还没有测试记录。",
 "p_recent": "🗓 最近的课", "p_sched": "课程时间",
 "lang_pick": "请选择语言", "lang_changed": "好的，现在用中文交流 🐉",
 "day_today": "今天", "day_tomorrow": "明天",
 "remind24": "🗓 {day} <b>{time}</b> 有课。\n时间没问题吗？",
 "remind1": "⏰ 一小时后上课（{time}）。", "remind1_link": "\n\n链接：{link}",
 "btn_yes": "✅ 我会来", "btn_no": "❌ 来不了",
 "att_yes": "好的，等你 🐉",
 "att_ask": "太遗憾了 😔 请用一条消息写下原因，我会转告 Laziza。",
 "att_ok": "已转告 Laziza，她会联系你改期 🤍",
 "att_late": "已转告 Laziza 🤍\n提醒：按约定，提前不足3小时取消的课按已上课计算。",
 "att_past": "这节课已经结束了。",
 "pay_nudge": "你好！已付费的课快上完了。方便的时候请联系 Laziza 续费 🤍",
 "q_sent": "已把你的消息转给 Laziza，她会亲自回复 🤍",
},
}


def t(lang, key, **kw):
    s = T.get(lang, T["ru"]).get(key) or T["ru"].get(key, key)
    return s.format(**kw) if kw else s
