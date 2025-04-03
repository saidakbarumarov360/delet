import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatMemberStatus

# 📌 Bot tokeningizni shu yerga yozing
API_TOKEN = "7833851145:AAEcYEYfCNRrCb2EM6gKkbCc1hvEkdIBkFY"

# 📌 Guruh ID-larini ro‘yxat shaklida yozing
GROUP_IDS = [-1001754111732, -1007833851145]

# 📌 Logging sozlamalari
logging.basicConfig(level=logging.INFO)

# 📌 Bot va Dispatcher obyektlari
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# 📌 /start buyrug‘i
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("Assalomu alaykum! Bu bot sizga yordam berish uchun tayyor.")

# 📌 UNIVERSAL REGEX - Har qanday havolani aniqlaydi
URL_REGEX = re.compile(
    r'(?:(?:https?|ftp):\/\/)?(?:\S+(?::\S*)?@)?(?:'
    r'(?![0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\b)'
    r'[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}'
    r'(?::\d+)?(?:\/[^?#\s]*)?(?:\?[^#\s]*)?(?:#[\S]*)?|'
    r'www\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.[a-z]{2,}'
    r'(?::\d+)?(?:\/[^?#\s]*)?(?:\?[^#\s]*)?(?:#[\S]*)?)',
    re.IGNORECASE
)

# 📌 Ruscha harflarni aniqlash
RUSSIAN_CYRILLIC_LETTERS = set("ёыэъщ")

def is_russian_text(text):
    text_set = set(text.lower())
    return bool(text_set & RUSSIAN_CYRILLIC_LETTERS)

# 📌 Xabarlarni nazorat qilish va o‘chirish
@dp.message_handler(lambda message: message.chat.id in GROUP_IDS)
async def delete_messages(message: types.Message):
    try:
        if not message.text or not message.text.strip():
            return

        # 📌 Anonim adminlarni tekshirish
        if message.sender_chat and message.sender_chat.id == message.chat.id:
            return

        # 📌 Adminlarni tekshirish
        try:
            user_status = await bot.get_chat_member(message.chat.id, message.from_user.id)
            if user_status.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
                return
        except Exception as e:
            logging.warning(f"Admin tekshirishda xatolik: {e}")

        # 📌 UNIVERSAL regex bilan havolalarni o‘chirish
        if URL_REGEX.search(message.text):
            await bot.delete_message(message.chat.id, message.message_id)
            logging.info(f"Havola o‘chirildi: {message.text}")
            return

        # 📌 Rus tilidagi xabarlarni o‘chirish
        if is_russian_text(message.text):
            await bot.delete_message(message.chat.id, message.message_id)
            logging.info(f"Ruscha xabar o‘chirildi: {message.text}")
            return

    except Exception as e:
        logging.error(f"Xatolik yuz berdi: {e}")

# 📌 Guruhga yangi a’zo qo‘shilganda xabarni o‘chirish
@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def delete_new_member_message(message: types.Message):
    if message.chat.id in GROUP_IDS:
        try:
            await bot.delete_message(message.chat.id, message.message_id)
        except Exception as e:
            logging.error(f"Yangi a’zo xabarini o‘chirishda xatolik: {e}")

# 📌 Guruhdan kimdir chiqib ketganda xabarni o‘chirish
@dp.message_handler(content_types=types.ContentType.LEFT_CHAT_MEMBER)
async def delete_left_member_message(message: types.Message):
    if message.chat.id in GROUP_IDS:
        try:
            await bot.delete_message(message.chat.id, message.message_id)
        except Exception as e:
            logging.error(f"Chiqib ketgan a’zo xabarini o‘chirishda xatolik: {e}")

# 📌 Asosiy ishga tushirish
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    loop.run_forever()
        
