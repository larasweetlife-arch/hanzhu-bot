"""
Тексты версии 34: оплата расширенной практики звёздами, отмены и переносы уроков, кабинеты.
Подключается в конце texts.py.
"""

P = {}

P["ru"] = {
    "lx_title": "Расширенная практика",
    "lx_desc": "{pro} жизней в день на {days} дней. Включится сразу после оплаты.",
    # отмены и переносы занятий
    "att_ask": "Жаль 😔 Выбери причину, я передам Лазизе.",
    "att_late": "Занятие {when} отменено позже чем за 6 часов, по условиям оно засчитывается. "
                "Если случилось что-то непредвиденное, Лазиза это учтёт 🤍",
    "cr_sick": "🤒 Болезнь", "cr_family": "👨‍👩‍👧 Семья", "cr_work": "💼 Работа или учёба",
    "cr_tech": "💻 Техника или связь", "cr_force": "🆘 Форс-мажор", "cr_other": "✏️ Другое",
    "cr_dup": "Это занятие уже отменено 🤍",
    "cr_text": "Напиши одним сообщением, что случилось, я передам Лазизе.",
    "cr_free": "Передала Лазизе: занятие {when} отменено, оно не списывается 🤍\nНовое время можно попросить через /lessons, кнопка «Перенести».",
    "cr_support": "Мне очень жаль, что так получилось. Сейчас главное ты и твои близкие. Об уроках не переживай, мы всё решим 🤍",
    "cr_force_wait": "{support}\n\nЛазиза увидит твоё сообщение и решит, не списывать ли урок. Береги себя 🤍",
    "cr_force_free": "{support}\n\nЗанятие {when} отменено, оно не списывается 🤍",
    "cf_ok_student": "{support}\n\nЗанятие {when} не списано. Вернёмся к урокам, когда будет возможность 🤍",
    "cf_no_student": "Лазиза не отметила это как форс-мажор, поэтому занятие {when} засчитано. Если это недоразумение, напиши ей 🤍",
    "tc_notice": "Лазиза отменила занятие {when}.\nПричина: {reason}\nУрок не списывается 🤍",
    "mvt_notice": "🔄 Занятие перенесено: {old} → <b>{new}</b>.\n{by}",
    "mvby_student": "Перенос по твоей просьбе.", "mvby_teacher": "Перенос по просьбе преподавателя.",
    "mv_dup": "Запрос на перенос этого занятия уже отправлен, дождись ответа Лазизы 🌿",
    "left1": "ℹ️ У тебя остался 1 оплаченный урок. Когда будет удобно, напиши Лазизе насчёт продления 🤍",
}
P["uz"] = {
    "lx_title": "Kengaytirilgan mashq",
    "lx_desc": "{days} kun davomida kuniga {pro} ta jon. To'lovdan so'ng darhol yoqiladi.",
    "att_ask": "Afsus 😔 Sababni tanlang, Lazizaga yetkazaman.",
    "att_late": "{when} dars 6 soatdan kech bekor qilindi, shartlarga ko'ra u hisobga olinadi. "
                "Kutilmagan holat yuz bergan bo'lsa, Laziza buni inobatga oladi 🤍",
    "cr_sick": "🤒 Kasallik", "cr_family": "👨‍👩‍👧 Oila", "cr_work": "💼 Ish yoki o'qish",
    "cr_tech": "💻 Texnika yoki aloqa", "cr_force": "🆘 Fors-major", "cr_other": "✏️ Boshqa",
    "cr_dup": "Bu dars allaqachon bekor qilingan 🤍",
    "cr_text": "Nima bo'lganini bitta xabarda yozing, Lazizaga yetkazaman.",
    "cr_free": "Lazizaga yetkazdim: {when} dars bekor qilindi, u hisobdan yechilmaydi 🤍\nYangi vaqtni /lessons orqali «Ko'chirish» tugmasi bilan so'rashingiz mumkin.",
    "cr_support": "Bunday bo'lganidan juda afsusdaman. Hozir eng muhimi siz va yaqinlaringiz. Darslar haqida tashvishlanmang, hammasini hal qilamiz 🤍",
    "cr_force_wait": "{support}\n\nLaziza xabaringizni ko'radi va darsni hisobdan yechmaslikni hal qiladi. O'zingizni asrang 🤍",
    "cr_force_free": "{support}\n\n{when} dars bekor qilindi, u hisobdan yechilmaydi 🤍",
    "cf_ok_student": "{support}\n\n{when} dars hisobdan yechilmadi. Imkon bo'lganda darslarga qaytamiz 🤍",
    "cf_no_student": "Laziza buni fors-major deb belgilamadi, shuning uchun {when} dars hisobga olindi. Agar bu tushunmovchilik bo'lsa, unga yozing 🤍",
    "tc_notice": "Laziza {when} darsni bekor qildi.\nSabab: {reason}\nDars hisobdan yechilmaydi 🤍",
    "mvt_notice": "🔄 Dars ko'chirildi: {old} → <b>{new}</b>.\n{by}",
    "mvby_student": "Siz so'raganingiz bo'yicha ko'chirildi.", "mvby_teacher": "O'qituvchi so'rovi bo'yicha ko'chirildi.",
    "mv_dup": "Bu dars uchun ko'chirish so'rovi allaqachon yuborilgan, Lazizaning javobini kuting 🌿",
    "left1": "ℹ️ Sizda 1 ta to'langan dars qoldi. Qulay payt Lazizaga yozing, davom ettiramiz 🤍",
}
P["en"] = {
    "lx_title": "Extended practice",
    "lx_desc": "{pro} lives a day for {days} days. Turns on right after payment.",
    "att_ask": "Sorry to hear 😔 Please choose a reason, I'll pass it to Laziza.",
    "att_late": "The lesson on {when} was cancelled less than 6 hours before, so under the terms it counts as held. "
                "If something unexpected happened, Laziza will take that into account 🤍",
    "cr_sick": "🤒 Illness", "cr_family": "👨‍👩‍👧 Family", "cr_work": "💼 Work or study",
    "cr_tech": "💻 Tech or connection", "cr_force": "🆘 Emergency", "cr_other": "✏️ Other",
    "cr_dup": "This lesson is already cancelled 🤍",
    "cr_text": "Please write in one message what happened, I'll pass it to Laziza.",
    "cr_free": "Passed to Laziza: the lesson on {when} is cancelled and will not be counted 🤍\nYou can ask for a new time via /lessons, the “Reschedule” button.",
    "cr_support": "I'm so sorry this happened. Right now you and your loved ones come first. Don't worry about lessons, we'll sort it out 🤍",
    "cr_force_wait": "{support}\n\nLaziza will see your message and decide not to count the lesson. Take care 🤍",
    "cr_force_free": "{support}\n\nThe lesson on {when} is cancelled and will not be counted 🤍",
    "cf_ok_student": "{support}\n\nThe lesson on {when} is not counted. We'll get back to lessons when you can 🤍",
    "cf_no_student": "Laziza did not mark this as an emergency, so the lesson on {when} counts as held. If this is a misunderstanding, please write to her 🤍",
    "tc_notice": "Laziza cancelled the lesson on {when}.\nReason: {reason}\nThe lesson is not counted 🤍",
    "mvt_notice": "🔄 Lesson rescheduled: {old} → <b>{new}</b>.\n{by}",
    "mvby_student": "Rescheduled at your request.", "mvby_teacher": "Rescheduled at the teacher's request.",
    "mv_dup": "A reschedule request for this lesson is already sent, please wait for Laziza's answer 🌿",
    "left1": "ℹ️ You have 1 paid lesson left. When convenient, write to Laziza about renewing 🤍",
}
P["zh"] = {
    "lx_title": "加强练习",
    "lx_desc": "{days} 天内每天 {pro} 条命。付款后立即生效。",
    "att_ask": "真遗憾 😔 请选择原因，我会转告 Laziza。",
    "att_late": "{when} 的课在开课前不足 6 小时取消，按约定将计为已上课。如果发生了无法预料的情况，Laziza 会酌情考虑 🤍",
    "cr_sick": "🤒 生病", "cr_family": "👨‍👩‍👧 家里有事", "cr_work": "💼 工作或学习",
    "cr_tech": "💻 设备或网络", "cr_force": "🆘 突发情况", "cr_other": "✏️ 其他",
    "cr_dup": "这节课已经取消了 🤍",
    "cr_text": "请用一条消息说明发生了什么，我会转告 Laziza。",
    "cr_free": "已转告 Laziza：{when} 的课已取消，不会扣课时 🤍\n想改时间可以通过 /lessons 点“改期”。",
    "cr_support": "很抱歉发生了这样的事。现在最重要的是你和家人。课的事不用担心，我们会处理好 🤍",
    "cr_force_wait": "{support}\n\nLaziza 会看到你的消息，并决定是否不扣这节课。请照顾好自己 🤍",
    "cr_force_free": "{support}\n\n{when} 的课已取消，不会扣课时 🤍",
    "cf_ok_student": "{support}\n\n{when} 的课没有扣课时。等你方便时我们再继续上课 🤍",
    "cf_no_student": "Laziza 没有把这次标记为突发情况，所以 {when} 的课按已上课计算。如有误会，请直接联系她 🤍",
    "tc_notice": "Laziza 取消了 {when} 的课。\n原因：{reason}\n这节课不会扣课时 🤍",
    "mvt_notice": "🔄 课程已改期：{old} → <b>{new}</b>。\n{by}",
    "mvby_student": "按你的请求改期。", "mvby_teacher": "按老师的请求改期。",
    "mv_dup": "这节课的改期请求已发送，请等待 Laziza 回复 🌿",
    "left1": "ℹ️ 你还剩 1 节已付费的课。方便时请联系 Laziza 续费 🤍",
}
