"""
汉助 HanZhu — Chinese Learning Assistant
Created by Laziza Ropijonova
Phase 1: Onboarding, Daily Content, Translation, CRM
"""

import asyncio
import json
import os
import random
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BOT_TOKEN = "ВСТАВЬ_СЮДА_НОВЫЙ_ТОКЕН"
OWNER_ID = 8594239159  # Твой Telegram ID
CHANNEL_LINK = "https://t.me/chayevnichaem_o_kitayskom"
CHANNEL_NAME = "Чаёвничаем о китайском"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ─── CRM (простая файловая база) ──────────────────────────────────────────────
CRM_FILE = "users.json"

def load_users():
    if os.path.exists(CRM_FILE):
        with open(CRM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(CRM_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def get_user(user_id):
    users = load_users()
    return users.get(str(user_id))

def save_user(user_id, data):
    users = load_users()
    users[str(user_id)] = data
    save_users(users)

# ─── STATES ───────────────────────────────────────────────────────────────────
class OnboardingState(StatesGroup):
    waiting_name = State()
    waiting_source = State()
    waiting_language = State()
    waiting_level = State()

class TranslationState(StatesGroup):
    waiting_word = State()

# ─── LOCALIZATION ─────────────────────────────────────────────────────────────
TEXTS = {
    "ru": {
        "welcome": "你好！👋 Я 汉助 (HanZhu) — твой помощник в изучении китайского языка!\n\nСоздан специально для учеников и подписчиков канала *{channel}*.\n\nДавай познакомимся! Как тебя зовут?",
        "ask_source": "Отлично, {name}! 🌟\n\nОткуда ты узнал(а) о боте?",
        "ask_language": "Понял! Выбери язык общения 🌐",
        "ask_level": "На каком уровне ты сейчас изучаешь китайский?",
        "onboarding_done": "Всё готово, {name}! 🎉\n\nДобро пожаловать в 汉助!\n\nЧто хочешь сделать?",
        "word_of_day": "📚 *Слово дня*",
        "chengyu_of_day": "🧧 *Чэнъюй дня*",
        "fact_of_day": "🌏 *Факт о Китае*",
        "translate_prompt": "Введи слово для перевода (на русском или китайском):",
        "menu": "Главное меню",
        "btn_word": "📚 Слово дня",
        "btn_chengyu": "🧧 Чэнъюй",
        "btn_fact": "🌏 Факт о Китае",
        "btn_translate": "🔤 Перевод",
        "btn_channel": "📢 Канал",
        "btn_help": "❓ Помощь",
        "channel_msg": f"📢 Подписывайся на канал *{CHANNEL_NAME}* — там живой китайский, дорамы, мемы и культура!\n\n👉 {CHANNEL_LINK}",
        "help_msg": "汉助 — Chinese Learning Assistant\n*Создан:* Laziza Ropijonova\n\nКоманды:\n/start — начать заново\n/menu — главное меню\n/word — слово дня\n/chengyu — чэнъюй дня\n/fact — факт о Китае\n/translate — перевод слова",
        "source_options": ["Telegram-канал «Чаёвничаем о китайском»", "От друга/знакомого", "Из группы/чата", "Другое"],
        "level_options": ["Начальный (нет опыта)", "HSK 1", "HSK 2", "HSK 3", "HSK 4", "HSK 5", "HSK 6", "HSK 7-9"],
    },
    "uz": {
        "welcome": "你好！👋 Men 汉助 (HanZhu) — xitoy tilini o'rganishda sizning yordamchingizman!\n\n*{channel}* kanali o'quvchilari va obunachilari uchun maxsus yaratilgan.\n\nKeling, tanishaylik! Ismingiz nima?",
        "ask_source": "Ajoyib, {name}! 🌟\n\nBot haqida qayerdan bildingiz?",
        "ask_language": "Tushunarli! Muloqot tilini tanlang 🌐",
        "ask_level": "Hozir xitoy tilini qaysi darajada o'rganayapsiz?",
        "onboarding_done": "Hammasi tayyor, {name}! 🎉\n\n汉助 ga xush kelibsiz!\n\nNima qilmoqchisiz?",
        "word_of_day": "📚 *Kunning so'zi*",
        "chengyu_of_day": "🧧 *Kunning chengyu'si*",
        "fact_of_day": "🌏 *Xitoy haqida fakt*",
        "translate_prompt": "Tarjima qilish uchun so'z kiriting (o'zbekcha yoki xitoycha):",
        "menu": "Asosiy menyu",
        "btn_word": "📚 Kunning so'zi",
        "btn_chengyu": "🧧 Chengyu",
        "btn_fact": "🌏 Xitoy fakti",
        "btn_translate": "🔤 Tarjima",
        "btn_channel": "📢 Kanal",
        "btn_help": "❓ Yordam",
        "channel_msg": f"📢 *{CHANNEL_NAME}* kanaliga obuna bo'ling — u yerda jonli xitoy tili, dramalar, memlar va madaniyat!\n\n👉 {CHANNEL_LINK}",
        "help_msg": "汉助 — Chinese Learning Assistant\n*Yaratuvchi:* Laziza Ropijonova\n\nBuyruqlar:\n/start — qayta boshlash\n/menu — asosiy menyu\n/word — kunning so'zi\n/chengyu — kunning chengyusi\n/fact — xitoy fakti\n/translate — so'z tarjimasi",
        "source_options": ["«Chayevnichaem o kitayskom» kanali", "Do'st/tanishdan", "Guruh/chatdan", "Boshqa"],
        "level_options": ["Boshlang'ich (tajriba yo'q)", "HSK 1", "HSK 2", "HSK 3", "HSK 4", "HSK 5", "HSK 6", "HSK 7-9"],
    },
    "en": {
        "welcome": "你好！👋 I'm 汉助 (HanZhu) — your Chinese language learning assistant!\n\nCreated for students and followers of the *{channel}* channel.\n\nLet's get acquainted! What's your name?",
        "ask_source": "Great, {name}! 🌟\n\nHow did you find out about this bot?",
        "ask_language": "Got it! Choose your language 🌐",
        "ask_level": "What's your current Chinese level?",
        "onboarding_done": "All set, {name}! 🎉\n\nWelcome to 汉助!\n\nWhat would you like to do?",
        "word_of_day": "📚 *Word of the Day*",
        "chengyu_of_day": "🧧 *Chengyu of the Day*",
        "fact_of_day": "🌏 *Fact about China*",
        "translate_prompt": "Enter a word to translate (in English or Chinese):",
        "menu": "Main Menu",
        "btn_word": "📚 Word of the Day",
        "btn_chengyu": "🧧 Chengyu",
        "btn_fact": "🌏 China Fact",
        "btn_translate": "🔤 Translate",
        "btn_channel": "📢 Channel",
        "btn_help": "❓ Help",
        "channel_msg": f"📢 Subscribe to *{CHANNEL_NAME}* — live Chinese, dramas, memes and culture!\n\n👉 {CHANNEL_LINK}",
        "help_msg": "汉助 — Chinese Learning Assistant\n*Created by:* Laziza Ropijonova\n\nCommands:\n/start — restart\n/menu — main menu\n/word — word of the day\n/chengyu — chengyu of the day\n/fact — China fact\n/translate — translate a word",
        "source_options": ["Telegram channel «Chayevnichaem o kitayskom»", "From a friend", "From a group/chat", "Other"],
        "level_options": ["Beginner (no experience)", "HSK 1", "HSK 2", "HSK 3", "HSK 4", "HSK 5", "HSK 6", "HSK 7-9"],
    },
    "zh": {
        "welcome": "你好！👋 我是汉助 (HanZhu) — 你的汉语学习助手！\n\n专为 *{channel}* 频道的学员和订阅者创建。\n\n让我们认识一下吧！你叫什么名字？",
        "ask_source": "太好了，{name}！🌟\n\n你是怎么知道这个机器人的？",
        "ask_language": "明白了！请选择交流语言 🌐",
        "ask_level": "你目前的汉语水平是什么？",
        "onboarding_done": "一切准备就绪，{name}！🎉\n\n欢迎使用汉助！\n\n你想做什么？",
        "word_of_day": "📚 *今日词汇*",
        "chengyu_of_day": "🧧 *今日成语*",
        "fact_of_day": "🌏 *关于中国的小知识*",
        "translate_prompt": "请输入要翻译的词语（中文或俄文）：",
        "menu": "主菜单",
        "btn_word": "📚 今日词汇",
        "btn_chengyu": "🧧 成语",
        "btn_fact": "🌏 中国小知识",
        "btn_translate": "🔤 翻译",
        "btn_channel": "📢 频道",
        "btn_help": "❓ 帮助",
        "channel_msg": f"📢 订阅 *{CHANNEL_NAME}* 频道 — 那里有生动的汉语、电视剧、表情包和文化内容！\n\n👉 {CHANNEL_LINK}",
        "help_msg": "汉助 — Chinese Learning Assistant\n*创建者：* Laziza Ropijonova\n\n命令：\n/start — 重新开始\n/menu — 主菜单\n/word — 今日词汇\n/chengyu — 今日成语\n/fact — 中国小知识\n/translate — 翻译词语",
        "source_options": ["Telegram频道《Chayevnichaem o kitayskom》", "朋友介绍", "群组/聊天室", "其他"],
        "level_options": ["初级（无基础）", "HSK 1", "HSK 2", "HSK 3", "HSK 4", "HSK 5", "HSK 6", "HSK 7-9"],
    }
}

def t(user_id, key, **kwargs):
    user = get_user(user_id)
    lang = user.get("language", "ru") if user else "ru"
    text = TEXTS.get(lang, TEXTS["ru"]).get(key, key)
    return text.format(**kwargs) if kwargs else text

# ─── CONTENT DATABASE ─────────────────────────────────────────────────────────
WORDS_OF_DAY = [
    {"zh": "你好", "pinyin": "nǐ hǎo", "ru": "Привет", "uz": "Salom", "en": "Hello"},
    {"zh": "谢谢", "pinyin": "xiè xie", "ru": "Спасибо", "uz": "Rahmat", "en": "Thank you"},
    {"zh": "朋友", "pinyin": "péng yǒu", "ru": "Друг", "uz": "Do'st", "en": "Friend"},
    {"zh": "学习", "pinyin": "xué xí", "ru": "Учиться", "uz": "O'qimoq", "en": "To study"},
    {"zh": "漂亮", "pinyin": "piào liang", "ru": "Красивый", "uz": "Chiroyli", "en": "Beautiful"},
    {"zh": "努力", "pinyin": "nǔ lì", "ru": "Усердно стараться", "uz": "Qattiq harakat qilmoq", "en": "To work hard"},
    {"zh": "梦想", "pinyin": "mèng xiǎng", "ru": "Мечта", "uz": "Orzu", "en": "Dream"},
    {"zh": "快乐", "pinyin": "kuài lè", "ru": "Счастливый / радостный", "uz": "Baxtli / quvnoq", "en": "Happy / joyful"},
    {"zh": "坚持", "pinyin": "jiān chí", "ru": "Настойчиво продолжать", "uz": "Davom ettirmoq", "en": "To persist"},
    {"zh": "旅行", "pinyin": "lǚ xíng", "ru": "Путешествие", "uz": "Sayohat", "en": "Travel"},
    {"zh": "文化", "pinyin": "wén huà", "ru": "Культура", "uz": "Madaniyat", "en": "Culture"},
    {"zh": "音乐", "pinyin": "yīn yuè", "ru": "Музыка", "uz": "Musiqa", "en": "Music"},
    {"zh": "电影", "pinyin": "diàn yǐng", "ru": "Фильм", "uz": "Film", "en": "Movie"},
    {"zh": "加油", "pinyin": "jiā yóu", "ru": "Давай! Не сдавайся!", "uz": "Harakating!", "en": "Go for it! Keep going!"},
    {"zh": "缘分", "pinyin": "yuán fèn", "ru": "Судьба / предназначение", "uz": "Taqdir", "en": "Fate / destiny"},
]

CHENGYUS = [
    {
        "zh": "加油", "pinyin": "jiā yóu",
        "ru": "Буквально «добавь масла» — не сдавайся, давай!\nИспользуется как поддержка и ободрение.",
        "uz": "So'zma-so'z «yog' qo'sh» — ber o'zingdan!\nQo'llab-quvvatlash sifatida ishlatiladi.",
        "en": "Literally 'add oil' — don't give up, go for it!\nUsed as encouragement and support.",
    },
    {
        "zh": "半途而废", "pinyin": "bàn tú ér fèi",
        "ru": "Бросить на полпути. Начать дело и не доделать его до конца.",
        "uz": "Yarim yo'lda tashlash. Ishni boshlab, oxiriga yetkazmaslik.",
        "en": "To give up halfway. To start something and not finish it.",
    },
    {
        "zh": "一石二鸟", "pinyin": "yī shí èr niǎo",
        "ru": "Одним камнем двух птиц. Решить две проблемы одним действием.",
        "uz": "Bir tosh bilan ikki qush. Bitta harakat bilan ikki muammoni hal qilish.",
        "en": "Kill two birds with one stone. Solve two problems with one action.",
    },
    {
        "zh": "塞翁失马", "pinyin": "sài wēng shī mǎ",
        "ru": "Старик с границы потерял коня — почём знать, не к счастью ли?\nНеудача может обернуться удачей.",
        "uz": "Chegara choli otini yo'qotdi — baxt emasmi kim bilsin?\nOmadsizlik baxtga aylanishi mumkin.",
        "en": "The old man lost his horse — who knows if it's a blessing?\nMisfortune may turn into good luck.",
    },
    {
        "zh": "功夫不负有心人", "pinyin": "gōngfu bù fù yǒuxīn rén",
        "ru": "Усилия не предадут того, кто искренне старается.\nНастойчивость всегда вознаграждается.",
        "uz": "Mehnat samimiy harakat qiluvchini aldamaydi.\nSabr-toqat doim mukofotlanadi.",
        "en": "Hard work never betrays those who are sincere.\nPersistence is always rewarded.",
    },
    {
        "zh": "马到成功", "pinyin": "mǎ dào chéng gōng",
        "ru": "Конь пришёл — успех достигнут! Пожелание удачи перед важным делом.",
        "uz": "Ot keldi — muvaffaqiyat qo'lga kiritildi! Muhim ish oldidan omad tilash.",
        "en": "The horse arrives — success is achieved! A wish of good luck before an important event.",
    },
]

FACTS = [
    {
        "ru": "🇨🇳 В Китае официально 56 народностей. Жители Шанхая и Гуандуна могут совсем не понимать друг друга на слух — именно поэтому путунхуа (普通话) стал обязательным общим языком.",
        "uz": "🇨🇳 Xitoyda rasman 56 millat bor. Shanxay va Gvandun aholisi bir-birini quloq orqali umuman tushunmasligi mumkin — shuning uchun putunxua (普通话) umumiy majburiy til bo'ldi.",
        "en": "🇨🇳 China officially has 56 ethnic groups. Residents of Shanghai and Guangdong may not understand each other at all by ear — that's why Putonghua (普通话) became the mandatory common language.",
        "zh": "🇨🇳 中国官方有56个民族。上海人和广东人可能完全听不懂对方说话——这就是为什么普通话成为了必须掌握的共同语言。",
    },
    {
        "ru": "🔴 Красный цвет в Китае — символ счастья, удачи и защиты. Деньги в подарок принято давать в красных конвертах 红包. Именно поэтому Chinese New Year весь в красном.",
        "uz": "🔴 Xitoyda qizil rang — baxt, omad va himoyaning ramzi. Sovg'a pul qizil konvertlarga 红包 solinadi. Shu sababli Xitoy Yangi yili qizilga to'lgan.",
        "en": "🔴 Red in China is a symbol of happiness, luck and protection. Gift money is traditionally given in red envelopes 红包. That's why Chinese New Year is all red.",
        "zh": "🔴 红色在中国是幸福、好运和保护的象征。送礼金要装在红包里。这就是为什么春节到处都是红色的。",
    },
    {
        "ru": "4️⃣ В Китае число 4 считается несчастливым — 四 (sì) звучит как 死 (sǐ) — смерть. Во многих зданиях нет 4-го этажа. Зато 8 — счастливое: 八 (bā) похоже на 发 (fā) — богатеть.",
        "uz": "4️⃣ Xitoyda 4 raqami baxtsiz hisoblanadi — 四 (sì) 死 (sǐ) — o'lim kabi eshitiladi. Ko'p binalarda 4-qavat yo'q. Ammo 8 — baxtli: 八 (bā) 发 (fā) — boyish so'ziga o'xshaydi.",
        "en": "4️⃣ In China, the number 4 is considered unlucky — 四 (sì) sounds like 死 (sǐ) — death. Many buildings skip the 4th floor. But 8 is lucky: 八 (bā) sounds like 发 (fā) — to prosper.",
        "zh": "4️⃣ 在中国，数字4被认为不吉利——四(sì)听起来像死(sǐ)。很多楼没有四楼。而8是幸运数字：八(bā)听起来像发(fā)——发财。",
    },
    {
        "ru": "🍵 Слово 'чай' в разных языках пришло из разных диалектов китайского. 'Tea' — из минь-наньского (té), 'чай' и 'чой' — из мандаринского (chá). Зависело от того, с кем торговали.",
        "uz": "🍵 Turli tillardagi 'choy' so'zi xitoy tilining turli lahjalaridan kelgan. 'Tea' — min-nan lahjasidan (té), 'choy' — mandarin lahjasidan (chá). Kimlar bilan savdo qilganiga bog'liq edi.",
        "en": "🍵 The word 'tea' in different languages came from different Chinese dialects. 'Tea' — from Min Nan (té), 'chai' — from Mandarin (chá). It depended on who you traded with.",
        "zh": "🍵 不同语言中的'茶'来自汉语不同方言。'Tea'来自闽南语(té)，'chai'来自普通话(chá)。这取决于当时与谁进行贸易。",
    },
    {
        "ru": "🐉 Дракон на Востоке и Западе — совершенно разные существа. 龙 (lóng) в Китае — символ удачи, силы и императорской власти. Никакого зла. Китайцы называют себя 'потомками дракона'.",
        "uz": "🐉 Sharq va G'arbdagi ajdaho — butunlay boshqa mavjudotlar. 龙 (lóng) Xitoyda — omad, kuch va imperatorlik hokimiyatining ramzi. Hech qanday yovuzlik yo'q. Xitoyliklar o'zlarini 'ajdaho avlodlari' deb ataydi.",
        "en": "🐉 The dragon in the East and West are completely different creatures. 龙 (lóng) in China is a symbol of luck, strength and imperial power. No evil. Chinese people call themselves 'descendants of the dragon'.",
        "zh": "🐉 东方和西方的龙是完全不同的生物。中国的龙(lóng)是好运、力量和皇权的象征，没有任何邪恶。中国人称自己为'龙的传人'。",
    },
]

SIMPLE_DICTIONARY = {
    "привет": {"zh": "你好", "pinyin": "nǐ hǎo", "en": "Hello"},
    "спасибо": {"zh": "谢谢", "pinyin": "xiè xie", "en": "Thank you"},
    "пожалуйста": {"zh": "不客气", "pinyin": "bù kè qi", "en": "You're welcome"},
    "да": {"zh": "是", "pinyin": "shì", "en": "Yes"},
    "нет": {"zh": "不是", "pinyin": "bù shì", "en": "No"},
    "любовь": {"zh": "爱", "pinyin": "ài", "en": "Love"},
    "друг": {"zh": "朋友", "pinyin": "péng yǒu", "en": "Friend"},
    "учиться": {"zh": "学习", "pinyin": "xué xí", "en": "To study"},
    "красивый": {"zh": "漂亮", "pinyin": "piào liang", "en": "Beautiful"},
    "мечта": {"zh": "梦想", "pinyin": "mèng xiǎng", "en": "Dream"},
    "你好": {"ru": "Привет", "uz": "Salom", "pinyin": "nǐ hǎo"},
    "谢谢": {"ru": "Спасибо", "uz": "Rahmat", "pinyin": "xiè xie"},
    "爱": {"ru": "Любовь", "uz": "Muhabbat", "pinyin": "ài"},
    "朋友": {"ru": "Друг", "uz": "Do'st", "pinyin": "péng yǒu"},
    "学习": {"ru": "Учиться", "uz": "O'qimoq", "pinyin": "xué xí"},
    "梦想": {"ru": "Мечта", "uz": "Orzu", "pinyin": "mèng xiǎng"},
    "加油": {"ru": "Давай! Не сдавайся!", "uz": "Harakating!", "pinyin": "jiā yóu"},
}

# ─── KEYBOARDS ────────────────────────────────────────────────────────────────
def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
         InlineKeyboardButton(text="🇨🇳 中文", callback_data="lang_zh")],
    ])

def level_keyboard(lang):
    levels = TEXTS[lang]["level_options"]
    buttons = [[InlineKeyboardButton(text=lvl, callback_data=f"level_{i}")] for i, lvl in enumerate(levels)]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def source_keyboard(lang):
    sources = TEXTS[lang]["source_options"]
    buttons = [[InlineKeyboardButton(text=s, callback_data=f"source_{i}")] for i, s in enumerate(sources)]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def main_menu_keyboard(lang):
    t_lang = TEXTS.get(lang, TEXTS["ru"])
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t_lang["btn_word"]), KeyboardButton(text=t_lang["btn_chengyu"])],
            [KeyboardButton(text=t_lang["btn_fact"]), KeyboardButton(text=t_lang["btn_translate"])],
            [KeyboardButton(text=t_lang["btn_channel"]), KeyboardButton(text=t_lang["btn_help"])],
        ],
        resize_keyboard=True
    )

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def format_word(word, lang):
    return (
        f"*{word['zh']}*\n"
        f"🔊 Пиньинь: `{word['pinyin']}`\n"
        f"📖 {word.get(lang, word.get('ru', ''))}"
    )

def format_chengyu(cy, lang):
    return (
        f"*{cy['zh']}*\n"
        f"🔊 `{cy['pinyin']}`\n\n"
        f"{cy.get(lang, cy.get('ru', ''))}"
    )

def format_fact(fact, lang):
    return fact.get(lang, fact.get("ru", ""))

def get_user_lang(user_id):
    user = get_user(user_id)
    return user.get("language", "ru") if user else "ru"

# ─── HANDLERS ─────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if user:
        lang = user.get("language", "ru")
        await message.answer(
            t(message.from_user.id, "onboarding_done", name=user.get("name", ""))  + "\n\n" +
            t(message.from_user.id, "menu"),
            reply_markup=main_menu_keyboard(lang),
            parse_mode="Markdown"
        )
        return

    await state.set_state(OnboardingState.waiting_name)
    await message.answer(
        TEXTS["ru"]["welcome"].format(channel=CHANNEL_NAME),
        parse_mode="Markdown"
    )

@dp.message(OnboardingState.waiting_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(name=name)
    await state.set_state(OnboardingState.waiting_source)
    await message.answer(
        TEXTS["ru"]["ask_source"].format(name=name),
        reply_markup=source_keyboard("ru"),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("source_"))
async def process_source(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split("_")[1])
    sources = TEXTS["ru"]["source_options"]
    source = sources[idx] if idx < len(sources) else "Другое"
    await state.update_data(source=source)
    await state.set_state(OnboardingState.waiting_language)
    await callback.message.edit_text(
        TEXTS["ru"]["ask_language"],
        reply_markup=language_keyboard()
    )

@dp.callback_query(F.data.startswith("lang_"))
async def process_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(language=lang)
    await state.set_state(OnboardingState.waiting_level)
    await callback.message.edit_text(
        TEXTS[lang]["ask_level"],
        reply_markup=level_keyboard(lang)
    )

@dp.callback_query(F.data.startswith("level_"))
async def process_level(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split("_")[1])
    data = await state.get_data()
    lang = data.get("language", "ru")
    levels = TEXTS[lang]["level_options"]
    level = levels[idx] if idx < len(levels) else "Начальный"

    user_data = {
        "name": data.get("name", ""),
        "source": data.get("source", ""),
        "language": lang,
        "level": level,
        "registered_at": datetime.now().isoformat(),
        "user_id": callback.from_user.id,
        "username": callback.from_user.username or "",
    }
    save_user(callback.from_user.id, user_data)
    await state.clear()

    # Notify owner
    try:
        await bot.send_message(
            OWNER_ID,
            f"🆕 *Новый пользователь!*\n"
            f"👤 {user_data['name']} (@{user_data['username']})\n"
            f"🌐 Язык: {lang}\n"
            f"📊 Уровень: {level}\n"
            f"📢 Источник: {user_data['source']}",
            parse_mode="Markdown"
        )
    except Exception:
        pass

    await callback.message.edit_text(
        TEXTS[lang]["onboarding_done"].format(name=user_data["name"])
    )
    await callback.message.answer(
        TEXTS[lang]["menu"],
        reply_markup=main_menu_keyboard(lang)
    )

# ─── MENU HANDLERS ────────────────────────────────────────────────────────────

@dp.message(Command("menu"))
async def cmd_menu(message: Message):
    lang = get_user_lang(message.from_user.id)
    await message.answer(TEXTS[lang]["menu"], reply_markup=main_menu_keyboard(lang))

@dp.message(Command("word"))
async def cmd_word(message: Message):
    await send_word(message)

@dp.message(Command("chengyu"))
async def cmd_chengyu(message: Message):
    await send_chengyu(message)

@dp.message(Command("fact"))
async def cmd_fact(message: Message):
    await send_fact(message)

@dp.message(Command("translate"))
async def cmd_translate(message: Message, state: FSMContext):
    await start_translate(message, state)

@dp.message(Command("help"))
async def cmd_help(message: Message):
    lang = get_user_lang(message.from_user.id)
    await message.answer(TEXTS[lang]["help_msg"], parse_mode="Markdown")

# ─── BUTTON HANDLERS ──────────────────────────────────────────────────────────

async def send_word(message: Message):
    lang = get_user_lang(message.from_user.id)
    word = random.choice(WORDS_OF_DAY)
    text = TEXTS[lang]["word_of_day"] + "\n\n" + format_word(word, lang)
    await message.answer(text, parse_mode="Markdown")

async def send_chengyu(message: Message):
    lang = get_user_lang(message.from_user.id)
    cy = random.choice(CHENGYUS)
    text = TEXTS[lang]["chengyu_of_day"] + "\n\n" + format_chengyu(cy, lang)
    await message.answer(text, parse_mode="Markdown")

async def send_fact(message: Message):
    lang = get_user_lang(message.from_user.id)
    fact = random.choice(FACTS)
    text = TEXTS[lang]["fact_of_day"] + "\n\n" + format_fact(fact, lang)
    await message.answer(text, parse_mode="Markdown")

async def start_translate(message: Message, state: FSMContext):
    lang = get_user_lang(message.from_user.id)
    await state.set_state(TranslationState.waiting_word)
    await message.answer(TEXTS[lang]["translate_prompt"])

@dp.message(TranslationState.waiting_word)
async def process_translation(message: Message, state: FSMContext):
    lang = get_user_lang(message.from_user.id)
    word = message.text.strip().lower()
    result = SIMPLE_DICTIONARY.get(word)

    if result:
        if "zh" in result:
            text = f"🔤 *{word}* → *{result['zh']}*\n🔊 `{result['pinyin']}`"
        else:
            text = f"🔤 *{word}*\n🔊 `{result['pinyin']}`\n🇷🇺 {result.get('ru', '')}\n🇺🇿 {result.get('uz', '')}"
    else:
        msgs = {
            "ru": f"Слово *{word}* пока не найдено в базе. База пополняется! 🔄",
            "uz": f"*{word}* so'zi hozircha bazada topilmadi. Baza to'ldirilmoqda! 🔄",
            "en": f"Word *{word}* not found in the database yet. Database is growing! 🔄",
            "zh": f"词语 *{word}* 暂时在数据库中找不到。数据库正在更新中！🔄",
        }
        text = msgs.get(lang, msgs["ru"])

    await state.clear()
    await message.answer(text, parse_mode="Markdown")

@dp.message()
async def handle_menu_buttons(message: Message, state: FSMContext):
    lang = get_user_lang(message.from_user.id)
    tl = TEXTS.get(lang, TEXTS["ru"])
    text = message.text

    if text == tl["btn_word"]:
        await send_word(message)
    elif text == tl["btn_chengyu"]:
        await send_chengyu(message)
    elif text == tl["btn_fact"]:
        await send_fact(message)
    elif text == tl["btn_translate"]:
        await start_translate(message, state)
    elif text == tl["btn_channel"]:
        await message.answer(tl["channel_msg"], parse_mode="Markdown")
    elif text == tl["btn_help"]:
        await message.answer(tl["help_msg"], parse_mode="Markdown")
    else:
        user = get_user(message.from_user.id)
        if not user:
            await cmd_start(message, state)

# ─── MAIN ─────────────────────────────────────────────────────────────────────
async def main():
    print("🤖 汉助 HanZhu bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
