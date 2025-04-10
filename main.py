from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ChatMemberStatus
import logging
import re
import transliterate  # transliterate.py faylini import qilamiz

# Bot token va guruh ID’lari
API_TOKEN = "7833851145:AAEcYEYfCNRrCb2EM6gKkbCc1hvEkdIBkFY"
GROUP_IDS = [-1001754111732, -1007833851145]  # Ikkala guruh ID

# Logging sozlamalari
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Mukammal URL regex
URL_REGEX = re.compile(
    r"(?i)(https?://|www\.)[-\w.]+\.[a-z]{2,}([:/][-a-z0-9@:%._+~#=]*)?(\?[;&a-z0-9%_=-]+)?(#[-\w]+)?"
)

# Ruscha xos harflar
RUSSIAN_CYRILLIC_SPECIFIC = set("ёыэъщ")
UZBEK_CYRILLIC_SPECIFIC = set("ўқғҳ")

def is_cyrillic_or_latin(text):
    """
    Matn kirillcha yoki lotincha ekanligini tekshiradi.
    Agar ikkalasi ham bo‘lmasa, False qaytaradi.
    """
    # Kirillcha harflar mavjudligini tekshirish
    has_cyrillic = any(char in transliterate.CYRILLIC_TO_LATIN for char in text)
    
    # Lotincha harflar mavjudligini tekshirish
    has_latin = any(char in transliterate.LATIN_TO_CYRILLIC for char in text)
    
    # Agar hech biri bo‘lmasa, False qaytaradi
    is_valid = has_cyrillic or has_latin
    
    logging.info(f"Matn: {text}, Kirillcha: {has_cyrillic}, Lotincha: {has_latin}, To‘g‘ri: {is_valid}")
    return is_valid

def is_russian_text(text):
    """
    Matnni kirillchaga aylantirib, ruscha ekanligini tekshiradi.
    Agar ruscha xos harflar bo‘lsa va o‘zbekcha harflar bo‘lmasa, True qaytaradi.
    """
    cyrillic_text = text if any(c in text for c in transliterate.CYRILLIC_TO_LATIN) else transliterate.to_cyrillic(text)
    
    has_russian_chars = any(char in RUSSIAN_CYRILLIC_SPECIFIC for char in cyrillic_text)
    has_uzbek_chars = any(char in UZBEK_CYRILLIC_SPECIFIC for char in cyrillic_text)
    
    is_russian = has_russian_chars and not has_uzbek_chars
    
    logging.info(f"Matn: {text}, Kirillcha: {cyrillic_text}, Ruscha harflar: {has_russian_chars}, O‘zbekcha harflar: {has_uzbek_chars}, Ruscha: {is_russian}")
    return is_russian

# Start buyrug‘i
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("Assalomu alaykum! Bu bot sizga yordam berish uchun tayyor. 😊")

# Yangi a’zo qo‘shilganda xabarni o‘chirish
@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def delete_new_member_message(message: types.Message):
    if message.chat.id in GROUP_IDS:
        try:
            await bot.delete_message(message.chat.id, message.message_id)
            logging.info(f"Yangi a’zo xabari o‘chirildi: Guruh ID {message.chat.id}")
        except Exception as e:
            logging.error(f"Yangi a’zo xabarini o‘chirishda xatolik: {e}, Guruh: {message.chat.id}")

# A’zo chiqib ketganda xabarni o‘chirish
@dp.message_handler(content_types=types.ContentType.LEFT_CHAT_MEMBER)
async def delete_left_member_message(message: types.Message):
    if message.chat.id in GROUP_IDS:
        try:
            await bot.delete_message(message.chat.id, message.message_id)
            logging.info(f"Chiqib ketgan a’zo xabari o‘chirildi: Guruh ID {message.chat.id}")
        except Exception as e:
            logging.error(f"Chiqib ketgan a’zo xabarini o‘chirishda xatolik: {e}, Guruh: {message.chat.id}")

# Oddiy xabarlar uchun handler
@dp.message_handler(lambda message: message.chat.id in GROUP_IDS)
async def delete_messages(message: types.Message):
    try:
        # Bo‘sh xabar yoki maxsus eventlarni o‘tkazib yuborish
        if not message.text or message.new_chat_members or message.left_chat_member:
            return

        # Admin tekshiruvi
        if message.from_user:
            user_status = await bot.get_chat_member(message.chat.id, message.from_user.id)
            if user_status.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
                logging.info(f"Admin xabari: {message.from_user.id} - {message.text}")
                return

        # Havola tekshiruvi
        if URL_REGEX.search(message.text):
            await bot.delete_message(message.chat.id, message.message_id)
            logging.info(f"Havola o‘chirildi: {message.text}, Guruh: {message.chat.id}")
            return

        # Kirillcha yoki lotincha ekanligini tekshirish
        if not is_cyrillic_or_latin(message.text):
            await bot.delete_message(message.chat.id, message.message_id)
            logging.info(f"Kirillcha yoki lotincha emas, o‘chirildi: {message.text}, Guruh: {message.chat.id}")
            return

        # Ruscha matn tekshiruvi
        if is_russian_text(message.text):
            await bot.delete_message(message.chat.id, message.message_id)
            logging.info(f"Ruscha xabar o‘chirildi: {message.text}, Guruh: {message.chat.id}")
            return

    except Exception as e:
        logging.error(f"Xatolik yuz berdi: {e}, Guruh: {message.chat.id}")

# Botni ishga tushirish
if __name__ == "__main__":
    logging.info("Bot ishga tushdi!")
    executor.start_polling(dp, skip_updates=True)
