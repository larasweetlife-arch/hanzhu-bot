/* Тексты оболочки 2.0 (v28): вкладки «Сегодня», «Практика», «Шкафчик», «Прогресс». Правишь здесь. */
(() => {
  const H = {
    ru: {
      tab_today: "Сегодня", tab_practice: "Практика", tab_locker: "Шкафчик", tab_progress: "Прогресс",
      td_goal: "Цель дня", td_level: "Звание", td_hanzi: "Иероглиф дня", td_road: "Дорога дня", td_go: "Начать", td_done: "Готово", td_open: "Открыть", td_cont: "Продолжить",
      td_s_words: "Потренировать слова", td_s_words_sub: "Верных ответов сегодня: {a} из {b}", td_s_quest: "Путешествие 茶茶", td_s_quest_new: "Создай героя и отправляйся в путь",
      td_s_quest_sub: "{t} · сцен {a} из {b}", td_s_hanzi: "Посмотри и обведи иероглиф дня", td_s_hanzi_sub: "Порядок черт и разбор",
      pr_title: "Практика", pr_back: "Практика", pr_quest: "Путешествие 茶茶", pr_quest_sub: "Сцены, диалоги и задания по главам", pr_words: "Тренировка слов", pr_words_sub: "Чайная лавка: отвечай и копи очки",
      pr_qrating: "Рейтинг путешествия", pr_qrating_sub: "Кто дальше прошёл путь",
      lk_title: "Шкафчик", lk_soon: "Скоро", lk_text: "Здесь появится каталог всех слов: поиск, ящички по уровням HSK и отметки «Учу», «Помню», «Повторить».",
      pg_mine: "Мой прогресс", pg_about: "О проекте", pg_words: "Мои слова", pg_known: "Выучено", pg_total: "В карточках", pg_due: "Повторить", pg_words_empty: "Пока пусто. Слова попадают сюда, когда повторяешь их в «Практике» бота.",
    },
    uz: {
      tab_today: "Bugun", tab_practice: "Mashq", tab_locker: "Javon", tab_progress: "Natija",
      td_goal: "Kun maqsadi", td_level: "Unvon", td_hanzi: "Kun ieroglifi", td_road: "Kun yo‘li", td_go: "Boshlash", td_done: "Tayyor", td_open: "Ochish", td_cont: "Davom etish",
      td_s_words: "So‘zlarni mashq qilish", td_s_words_sub: "Bugungi to‘g‘ri javoblar: {a} / {b}", td_s_quest: "茶茶 sayohati", td_s_quest_new: "Qahramon yarating va yo‘lga chiqing",
      td_s_quest_sub: "{t} · sahnalar {a} / {b}", td_s_hanzi: "Kun ieroglifini ko‘ring va yozing", td_s_hanzi_sub: "Chiziqlar tartibi va tahlil",
      pr_title: "Mashq", pr_back: "Mashq", pr_quest: "茶茶 sayohati", pr_quest_sub: "Boblar bo‘yicha sahnalar, dialoglar va topshiriqlar", pr_words: "So‘z mashqi", pr_words_sub: "Choyxona: javob bering va ochko to‘plang",
      pr_qrating: "Sayohat reytingi", pr_qrating_sub: "Kim ko‘proq yo‘l bosdi",
      lk_title: "Javon", lk_soon: "Tez orada", lk_text: "Bu yerda barcha so‘zlar katalogi paydo bo‘ladi: qidiruv, HSK darajalari bo‘yicha tortmalar va «O‘rganyapman», «Eslab qoldim», «Takrorlash» belgilari.",
      pg_mine: "Mening natijam", pg_about: "Loyiha haqida", pg_words: "Mening so‘zlarim", pg_known: "O‘rganilgan", pg_total: "Kartochkalarda", pg_due: "Takrorlash", pg_words_empty: "Hozircha bo‘sh. So‘zlar botdagi «Mashq»da takrorlaganingizda shu yerga tushadi.",
    },
    en: {
      tab_today: "Today", tab_practice: "Practice", tab_locker: "Locker", tab_progress: "Progress",
      td_goal: "Daily goal", td_level: "Rank", td_hanzi: "Character of the day", td_road: "Today’s road", td_go: "Start", td_done: "Done", td_open: "Open", td_cont: "Continue",
      td_s_words: "Practise words", td_s_words_sub: "Correct answers today: {a} of {b}", td_s_quest: "茶茶’s journey", td_s_quest_new: "Create a hero and set off",
      td_s_quest_sub: "{t} · scenes {a} of {b}", td_s_hanzi: "Look at and trace today’s character", td_s_hanzi_sub: "Stroke order and breakdown",
      pr_title: "Practice", pr_back: "Practice", pr_quest: "茶茶’s journey", pr_quest_sub: "Scenes, dialogues and tasks by chapter", pr_words: "Word practice", pr_words_sub: "The tea shop: answer and earn points",
      pr_qrating: "Journey ranking", pr_qrating_sub: "Who has travelled the furthest",
      lk_title: "Locker", lk_soon: "Coming soon", lk_text: "A catalogue of all words will appear here: search, drawers by HSK level and the marks “Learning”, “Known” and “Review”.",
      pg_mine: "My progress", pg_about: "About", pg_words: "My words", pg_known: "Learned", pg_total: "In cards", pg_due: "To review", pg_words_empty: "Nothing yet. Words appear here when you review them in the bot’s “Practice”.",
    },
    zh: {
      tab_today: "今天", tab_practice: "练习", tab_locker: "柜子", tab_progress: "进度",
      td_goal: "今日目标", td_level: "称号", td_hanzi: "每日一字", td_road: "今日之路", td_go: "开始", td_done: "完成", td_open: "打开", td_cont: "继续",
      td_s_words: "练习单词", td_s_words_sub: "今天答对：{a} / {b}", td_s_quest: "茶茶的旅程", td_s_quest_new: "创建角色，出发吧",
      td_s_quest_sub: "{t} · 场景 {a} / {b}", td_s_hanzi: "看看并描一描今天的字", td_s_hanzi_sub: "笔顺与拆解",
      pr_title: "练习", pr_back: "练习", pr_quest: "茶茶的旅程", pr_quest_sub: "按章节的场景、对话和任务", pr_words: "单词练习", pr_words_sub: "茶铺：答题赚积分",
      pr_qrating: "旅程排行榜", pr_qrating_sub: "看谁走得最远",
      lk_title: "柜子", lk_soon: "即将推出", lk_text: "这里会有所有单词的目录：搜索、按 HSK 等级分类的抽屉，以及“在学”“记住了”“待复习”标记。",
      pg_mine: "我的进度", pg_about: "关于", pg_words: "我的单词", pg_known: "已学会", pg_total: "卡片中", pg_due: "待复习", pg_words_empty: "还没有内容。你在机器人的“练习”里复习的单词会出现在这里。",
    },
  };
  for (const l of Object.keys(H)) Object.assign(window.I18N[l], H[l]);
})();
