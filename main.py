from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ChatMemberStatus
import logging
import re

# Bot token va guruh ID’lari
API_TOKEN = "7833851145:AAEcYEYfCNRrCb2EM6gKkbCc1hvEkdIBkFY"
GROUP_IDS = [-1001754111732, -1007833851145]  # Ikkala guruh ID

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

# Mukammal qo‘shilish/chiqish regex (ko‘p tilli qo‘llab-quvvatlash)
JOIN_LEFT_REGEX = re.compile(
    r"(joined the group|left the group|was added by|"
    r"группага қўшилди|гуруҳдан чиқди|томонидан қўшилди|"
    r"присоединился к группе|покинул группу|был добавлен)", 
    re.IGNORECASE
)

# O‘zbekcha va ruscha harflar
UZBEK_CYRILLIC_LETTERS = set("ўқғҳ")
RUSSIAN_CYRILLIC_LETTERS = set("ёыэъщ")

def is_russian_text(text):
    text_set = set(text.lower())
    if text_set & UZBEK_CYRILLIC_LETTERS:
        return False
    if text_set & RUSSIAN_CYRILLIC_LETTERS:
        return True
    return False

# Guruh xabarlarini boshqarish
@dp.message_handler(lambda message: message.chat.id in GROUP_IDS)
async def delete_messages(message: types.Message):
    try:
        # Bo‘sh xabarni o‘tkazib yuborish
        if not message.text and not message.new_chat_members and not message.left_chat_member:
            return

        # Admin tekshiruvi
        if message.from_user:
            user_status = await bot.get_chat_member(message.chat.id, message.from_user.id)
            if user_status.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
                logging.info(f"Admin xabari: {message.from_user.id} - {message.text}")
                return

        # Yangi a’zo yoki chiqib ketish xabarlari (content_types o‘rniga)
        if message.new_chat_members or message.left_chat_member or JOIN_LEFT_REGEX.search(message.text or ""):
            await bot.delete_message(message.chat.id, message.message_id)
            logging.info(f"Qo‘shilish/chiqish xabari o‘chirildi: {message.chat.id}")
            return

        # Havola tekshiruvi
        if URL_REGEX.search(message.text or ""):
            await bot.delete_message(message.chat.id, message.message_id)
            logging.info(f"Havola o‘chirildi: {message.text}")
            return

        # Ruscha matn tekshiruvi
        if is_russian_text(message.text or ""):
            await bot.delete_message(message.chat.id, message.message_id)
            logging.info(f"Ruscha xabar o‘chirildi: {message.text}")
            return

    except Exception as e:
        logging.error(f"Xatolik yuz berdi: {e}")
        # Bot guruhda ishlay olishini tekshirish uchun
        if "Forbidden" in str(e):
            logging.error(f"Botda {message.chat.id} guruhida ruxsat yo‘q!")

# Botni ishga tushirish
if __name__ == "__main__":
    logging.info("Bot ishga tushdi!")
    executor.start_polling(dp, skip_updates=True)
