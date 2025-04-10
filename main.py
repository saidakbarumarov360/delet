from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ChatMemberStatus
import logging
import re

# Bot token va guruh ID’lari
API_TOKEN = "7833851145:AAEcYEYfCNRrCb2EM6gKkbCc1hvEkdIBkFY"
GROUP_IDS = [-1001754111732, -1002520242281]  # Ikkala guruh ID

# Logging sozlamalari
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Start buyrug‘i
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("Assalomu alaykum! Bu bot sizga yordam berish uchun tayyor. 😊")

# Mukammal URL regex
URL_REGEX = re.compile(
    r"(?i)(https?://|www\.)"  # Protokol yoki www (case-insensitive)
    r"[-\w.]+\.[a-z]{2,}"     # Domen nomi
    r"([:/][-a-z0-9@:%._+~#=]*)?"  # Yo‘l
    r"(\?[;&a-z0-9%_=-]+)?"  # Parametrlar
    r"(#[-\w]+)?"            # Fragment
)

# O‘zbekcha va ruscha harflar
UZBEK_CYRILLIC_LETTERS = set("ўқғҳ")
RUSSIAN_CYRILLIC_LETTERS = set("ёыэъщ")
RUSSIAN_COMMON_LETTERS = set("абвгдежзийклмнопрстуфхцчшщъыьэюяё")  # Ruscha umumiy harflar

def is_russian_text(text, threshold=0.7):
    """
    Matnni so‘zlar bo‘yicha tahlil qilib, ruscha so‘zlar foizini hisoblaydi.
    Agar ruscha so‘zlar 70% dan oshsa, True qaytaradi.
    """
    # Matnni so‘zlarga ajratish (bo‘shliq va tinish belgilari bo‘yicha)
    words = re.split(r"\s+|[.,!?;]", text.lower())
    words = [word for word in words if word]  # Bo‘sh so‘zlarni olib tashlash
    
    if not words:  # Agar matnda so‘z bo‘lmasa
        return False

    russian_word_count = 0
    total_words = len(words)

    for word in words:
        word_set = set(word)
        
        # Agar so‘zda ruscha xos harflar bo‘lsa, ruscha deb hisoblaymiz
        if word_set & RUSSIAN_CYRILLIC_LETTERS:
            russian_word_count += 1
            continue
        
        # Agar so‘z faqat ruscha harflardan iborat bo‘lsa va o‘zbekcha harflar yo‘q bo‘lsa
        if word_set.issubset(RUSSIAN_COMMON_LETTERS) and not (word_set & UZBEK_CYRILLIC_LETTERS):
            if len(word) > 1:  # 1 harfli so‘zlarni hisoblamaymiz
                russian_word_count += 1

    # Ruscha so‘zlar foizini hisoblash
    russian_percentage = russian_word_count / total_words
    logging.info(f"Ruscha so‘zlar foizi: {russian_percentage:.2%} ({russian_word_count}/{total_words}) - {text}")
    
    return russian_percentage >= threshold

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

        # Ruscha matn tekshiruvi (70% threshold bilan)
        if is_russian_text(message.text, threshold=0.7):
            await bot.delete_message(message.chat.id, message.message_id)
            logging.info(f"Ruscha xabar o‘chirildi (70%+): {message.text}, Guruh: {message.chat.id}")
            return

    except Exception as e:
        logging.error(f"Xatolik yuz berdi: {e}, Guruh: {message.chat.id}")

# Botni ishga tushirish
if __name__ == "__main__":
    logging.info("Bot ishga tushdi!")
    executor.start_polling(dp, skip_updates=True)
