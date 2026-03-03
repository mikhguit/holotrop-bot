import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Словарь для хранения ID сообщений
user_messages = {}

# Пути к текстовым файлам
TEXTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "texts")
FAQ_DIR = os.path.join(TEXTS_DIR, "faq")

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def save_message_id(user_id: int, message_id: int):
    """Сохраняет ID сообщения бота для пользователя"""
    if user_id not in user_messages:
        user_messages[user_id] = []
    user_messages[user_id].append(message_id)
    if len(user_messages[user_id]) > 50:
        user_messages[user_id].pop(0)

def load_text(filename: str) -> str:
    """Загружает текст из файла"""
    filepath = os.path.join(TEXTS_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"Файл не найден: {filepath}")
        return "⚠️ Текст временно недоступен"

def load_faq_text(filename: str) -> str:
    """Загружает текст FAQ из файла"""
    filepath = os.path.join(FAQ_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"Файл не найден: {filepath}")
        return "⚠️ Текст временно недоступен"

# ============================================================
# КЛАВИАТУРЫ
# ============================================================

def get_main_keyboard():
    """Главное меню"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🌬 Холотропное дыхание"))
    builder.add(KeyboardButton(text="👤 О Ведущем"))
    builder.add(KeyboardButton(text="💰 Стоимость участия"))
    builder.add(KeyboardButton(text="❓ Частые вопросы"))
    builder.add(KeyboardButton(text="📅 Расписание мероприятий"))
    builder.add(KeyboardButton(text="📚 Больше информации"))
    builder.add(KeyboardButton(text="✍️ Записаться"))
    builder.add(KeyboardButton(text="🗑 Очистить чат"))
    builder.adjust(1, 1, 1, 1, 1, 1, 1, 1)
    return builder.as_markup(resize_keyboard=True)

def get_hd_keyboard():
    """Клавиатура для Холотропного дыхания"""
    builder = InlineKeyboardBuilder()
    builder.button(text="❓ Частые вопросы", callback_data="faq_menu")
    builder.button(text="✍️ Записаться", url="https://t.me/alla_ananeva")
    builder.button(text="🏠 В главное меню", callback_data="menu")
    builder.adjust(3)
    return builder.as_markup()

def get_leader_keyboard():
    """Клавиатура для О Ведущем"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✍️ Записаться", url="https://t.me/alla_ananeva")
    builder.button(text="🏠 В главное меню", callback_data="menu")
    builder.adjust(2)
    return builder.as_markup()

def get_schedule_keyboard():
    """Клавиатура для Расписания"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✍️ Записаться", url="https://t.me/alla_ananeva")
    builder.button(text="🌬 Холотропное", callback_data="event_holo")
    builder.button(text="🏕 Другая реальность", callback_data="event_weekend")
    builder.button(text="🏔 Алтай", callback_data="event_altai")
    builder.button(text="🌊 Тургояк", callback_data="event_turgoyak")
    builder.button(text="⚰ Закапывание", callback_data="event_burial")
    builder.button(text="🏠 В главное меню", callback_data="menu")
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup()

def get_faq_keyboard():
    """Клавиатура для Частых вопросов"""
    builder = InlineKeyboardBuilder()
    faq_questions = [
        ("🔄 Как проходит тренинг", "faq_1"),
        ("📚 Нужна ли подготовка", "faq_2"),
        ("👥 Почему в группе", "faq_3"),
        ("⏱ Можно ли 1 день", "faq_4"),
        ("😰 А если мне страшно", "faq_5"),
    ]
    for text, callback in faq_questions:
        builder.button(text=text, callback_data=callback)
    builder.button(text="🏠 В главное меню", callback_data="menu")
    builder.adjust(1)
    return builder.as_markup()

def get_info_keyboard():
    """Клавиатура для Больше информации"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🌐 Сайт", url="https://www.sergeyananyev.ru")
    builder.button(text="🏠 В главное меню", callback_data="menu")
    builder.adjust(2)
    return builder.as_markup()

# ============================================================
# ХЕНДЛЕРЫ
# ============================================================

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Команда /start"""
    msg = await message.answer(
        f"Привет, {message.from_user.first_name}! 🙏\n\n"
        f"Я бот-помощник по Холотропному дыханию.\n"
        f"Выберите раздел в меню 👇",
        reply_markup=get_main_keyboard()
    )
    save_message_id(message.chat.id, msg.message_id)

@dp.message(F.text == "🌬 Холотропное дыхание")
async def show_hd(message: types.Message):
    """Холотропное дыхание"""
    text = load_text("hd_description.txt")
    msg = await message.answer(text, parse_mode="HTML", reply_markup=get_hd_keyboard())
    save_message_id(message.chat.id, msg.message_id)

@dp.message(F.text == "👤 О Ведущем")
async def show_leader(message: types.Message):
    """О Ведущем"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    photo_path = os.path.join(base_dir, "leader_photo.jpg")
    text = load_text("about_leader.txt")
    
    if os.path.exists(photo_path):
        msg = await message.answer_photo(
            photo=types.FSInputFile(photo_path),
            caption=text,
            parse_mode="HTML",
            reply_markup=get_leader_keyboard()
        )
    else:
        msg = await message.answer("⚠️ Фото недоступно\n\n" + text, parse_mode="HTML", reply_markup=get_leader_keyboard())
    save_message_id(message.chat.id, msg.message_id)

@dp.message(F.text == "💰 Стоимость участия")
async def show_price(message: types.Message):
    """Стоимость участия"""
    text = "💰 <b>Стоимость участия</b>\n\nИнформация о стоимости доступна на сайте или у организатора.\n\n📞 +7-922-108-83-23\n✏️ @alla_ananeva"
    msg = await message.answer(text, parse_mode="HTML", reply_markup=get_leader_keyboard())
    save_message_id(message.chat.id, msg.message_id)

@dp.message(F.text == "❓ Частые вопросы")
async def show_faq_menu(message: types.Message):
    """Меню Частых вопросов"""
    msg = await message.answer("Выберите вопрос 👇", reply_markup=get_faq_keyboard())
    save_message_id(message.chat.id, msg.message_id)

@dp.message(F.text == "📅 Расписание мероприятий")
async def show_schedule(message: types.Message):
    """Расписание"""
    text = load_text("schedule.txt")
    msg = await message.answer(text, parse_mode="HTML", reply_markup=get_schedule_keyboard())
    save_message_id(message.chat.id, msg.message_id)

@dp.message(F.text == "📚 Больше информации")
async def show_info(message: types.Message):
    """Больше информации"""
    text = load_text("contacts.txt")
    msg = await message.answer(text, parse_mode="HTML", reply_markup=get_info_keyboard())
    save_message_id(message.chat.id, msg.message_id)

@dp.message(F.text == "✍️ Записаться")
async def show_signup(message: types.Message):
    """Записаться"""
    text = "✍️ <b>Запись на мероприятия</b>\n\nДля записи свяжитесь с организатором:\n\n📞 +7-922-108-83-23\n✏️ @alla_ananeva\n🌐 www.sergeyananyev.ru"
    msg = await message.answer(text, parse_mode="HTML", reply_markup=get_leader_keyboard())
    save_message_id(message.chat.id, msg.message_id)

@dp.message(F.text == "🗑 Очистить чат")
async def clear_chat(message: types.Message):
    """Очистка чата"""
    user_id = message.chat.id
    deleted_count = 0
    message_ids = user_messages.get(user_id, [])
    
    for msg_id in message_ids:
        try:
            await bot.delete_message(chat_id=user_id, message_id=msg_id)
            deleted_count += 1
            await asyncio.sleep(0.1)
        except:
            pass
    
    user_messages[user_id] = []
    try:
        await message.delete()
    except:
        pass
    
    msg = await message.answer(
        f"✅ Чат очищен! Удалено: {deleted_count}\n\n"
        f"Привет, {message.from_user.first_name}! 🙏\nВыберите раздел 👇",
        reply_markup=get_main_keyboard()
    )
    save_message_id(user_id, msg.message_id)

@dp.callback_query(F.data == "menu")
async def back_to_menu(callback: types.CallbackQuery):
    """В главное меню"""
    msg = await callback.message.answer("Главное меню:", reply_markup=get_main_keyboard())
    save_message_id(callback.message.chat.id, msg.message_id)
    await callback.message.delete()
    await callback.answer()

@dp.callback_query(F.data == "faq_menu")
async def back_to_faq(callback: types.CallbackQuery):
    """К FAQ"""
    msg = await callback.message.edit_text("Выберите вопрос 👇", reply_markup=get_faq_keyboard())
    save_message_id(callback.message.chat.id, msg.message_id)
    await callback.answer()

@dp.callback_query(F.data.startswith("faq_"))
async def process_faq(callback: types.CallbackQuery):
    """Ответы на вопросы FAQ"""
    num = callback.data.replace("faq_", "")
    text = load_faq_text(f"question{num}.txt")
    msg = await callback.message.answer(text, parse_mode="HTML")
    save_message_id(callback.message.chat.id, msg.message_id)
    await callback.answer()

@dp.callback_query(F.data.startswith("event_"))
async def process_event(callback: types.CallbackQuery):
    """Переход к мероприятиям"""
    await callback.message.answer("ℹ️ Подробная информация в разделе «Расписание мероприятий»", reply_markup=get_schedule_keyboard())
    await callback.answer()

# ============================================================
# ЗАПУСК
# ============================================================

async def main():
    logging.info("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())