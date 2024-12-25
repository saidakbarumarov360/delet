from aiogram import Bot, Dispatcher, executor, types
import logging
import re
from langdetect import detect

API_TOKEN = "7833851145:AAFiKeE_jHhAhFBgeRbEzZ-Or4JwIDN00cI"
GROUP_ID = -1001754111732

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("Assalomu alaykum! Bu bot sizga yordam berish uchun tayyor. 😊")

# Havolalarni aniqlash uchun regex
URL_REGEX = re.compile(r"http[s]?://|www\\.|@[a-zA-Z0-9_]+")

@dp.message_handler(lambda message: message.chat.id == GROUP_ID)
async def delete_messages(message: types.Message):
    try:
        # Agar xabar bo'sh bo'lsa, uni o'tkazib yuborish
        if not message.text.strip():
            logging.info("Bo'sh xabar, o'chirishni o'tkazib yuborish.")
            return

        # Havolalar uchun tekshirish
        url_match = URL_REGEX.search(message.text)
        if url_match:  # Havola aniqlanganda
            await bot.delete_message(message.chat.id, message.message_id)
            logging.info(f"Havola o'chirildi: {message.text}")
            return

        # Tilni aniqlash va ruscha xabarlarni o'chirish
        detected_lang = detect(message.text)
        if detected_lang == 'ru':
            await bot.delete_message(message.chat.id, message.message_id)
            logging.info(f"Ruscha xabar o'chirildi: {message.text}")
            return

        logging.info(f"Til aniqlanmadi yoki ruscha emas: {message.text}")
    except Exception as e:
        logging.error(f"Xatolik: {e}")

# Guruhga qo'shilgan yoki tark etgan a'zolar haqida habarlarni o'chirish
@dp.message_handler(lambda message: message.chat.id == GROUP_ID and message.content_type == "new_chat_members")
async def delete_join_messages(message: types.Message):
    try:
        await bot.delete_message(message.chat.id, message.message_id)
        logging.info("Qo'shilish haqida xabar o'chirildi")
    except Exception as e:
        logging.error(f"Xatolik: {e}")

@dp.message_handler(lambda message: message.chat.id == GROUP_ID and message.content_type == "left_chat_member")
async def delete_leave_messages(message: types.Message):
    try:
        await bot.delete_message(message.chat.id, message.message_id)
        logging.info("Tark etish haqida xabar o'chirildi")
    except Exception as e:
        logging.error(f"Xatolik: {e}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
