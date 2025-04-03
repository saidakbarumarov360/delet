from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ChatMemberStatus
import logging
import re

# Bot tokeni (asl token saqlanadi)
API_TOKEN = "7833851145:AAFiKeE_jHhAhFBgeRbEzZ-Or4JwIDN00cI"

# Guruh IDlari ro'yxat shaklida
GROUP_IDS = [
    -1001754111732,  # Birinchi guruh IDsi (avvalgi)
    -1007833851145       # Siz bergan guruh IDsi
]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("Assalomu alaykum! Bu bot sizga yordam berish uchun tayyor. 😊")

# To'g'ri regex
# To'g'ri regex (yangi universal RegEx)
URL_REGEX = re.compile(
    r'(?:(?:https?|ftp):\/\/)?(?:\S+(?::\S*)?@)?(?:'
    r'(?![0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\b)'
    r'[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}'
    r'(?::\d+)?(?:\/[^?#\s]*)?(?:\?[^#\s]*)?(?:#[\S]*)?|'
    r'www\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.[a-z]{2,}'
    r'(?::\d+)?(?:\/[^?#\s]*)?(?:\?[^#\s]*)?(?:#[\S]*)?)',
    re.IGNORECASE
)
UZBEK_CYRILLIC_LETTERS = set("ўқғҳ")  # O‘zbek tiliga xos harflar
RUSSIAN_CYRILLIC_LETTERS = set("ёыэъщ")  # Rus tiliga xos harflar

def is_russian_text(text):
    """
    Matn ruscha ekanligini tekshiradi:
    - Agar rus tiliga xos harflar bo‘lsa, u ruscha bo‘lishi ehtimoli yuqori.
    - Agar o‘zbekcha krill harflari bo‘lsa, bu o‘zbek tilidagi matn.
    """
    text_set = set(text.lower())
    
    # Agar o‘zbekcha krill harflari bo‘lsa, matn o‘zbekcha deb hisoblanadi
    if text_set & UZBEK_CYRILLIC_LETTERS:
        return False
    
    # Agar ruscha harflar mavjud bo‘lsa, matn ruscha bo‘lishi mumkin
    if text_set & RUSSIAN_CYRILLIC_LETTERS:
        return True

    return False  # Agar hech narsa aniqlanmasa, ruscha deb hisoblamaymiz

@dp.message_handler(lambda message: message.chat.id in GROUP_IDS)
async def delete_messages(message: types.Message):
    try:
        if not message.text or not message.text.strip():
            logging.info("Bo'sh xabar, o'tkazib yuborildi.")
            return

        # Anonim admin tekshirish
        if message.sender_chat and message.sender_chat.id == message.chat.id:
            logging.info(f"Anonim admin xabarini o'tkazib yuborish: {message.text}")
            return

        # Oddiy adminlarni tekshirish
        if message.from_user:
            user_status = await bot.get_chat_member(message.chat.id, message.from_user.id)
            if user_status.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
                logging.info(f"Admin xabarini o'tkazib yuborish: {message.text}")
                return

        # Havolalarni tekshirish
        if URL_REGEX.search(message.text):
            await bot.delete_message(message.chat.id, message.message_id)
            logging.info(f"Havola o'chirildi: {message.text}")
            return

        # Rus tilidagi xabarlarni aniqlash
        if is_russian_text(message.text):
            await bot.delete_message(message.chat.id, message.message_id)
            logging.info(f"Ruscha xabar o'chirildi: {message.text}")
            return

        logging.info(f"Til aniqlanmadi yoki o‘zbekcha: {message.text}")

    except Exception as e:
        logging.error(f"Xatolik: {e}")

# Guruhga kimdir qoʻshilganda chiqadigan xabarni oʻchirish
@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def delete_new_member_message(message: types.Message):
    try:
        if message.chat.id in GROUP_IDS:
            await bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print(f"Yangi a'zo xabarini oʻchirishda xatolik: {e}")

# Guruhdan kimdir chiqib ketganda chiqadigan xabarni oʻchirish
@dp.message_handler(content_types=types.ContentType.LEFT_CHAT_MEMBER)
async def delete_left_member_message(message: types.Message):
    try:
        if message.chat.id in GROUP_IDS:
            await bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print(f"Chiqib ketgan a'zo xabarini oʻchirishda xatolik: {e}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)  # Agar muhim xabarlar o‘tkazib yuborilishini xohlamasangiz, False qo‘ying.
