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

# transliterate.py dan olingan lug‘atlar va funksiyalar
LATIN_TO_CYRILLIC = {
    'a': 'а', 'A': 'А', 'b': 'б', 'B': 'Б', 'd': 'д', 'D': 'Д', 'e': 'е', 'E': 'Е',
    'f': 'ф', 'F': 'Ф', 'g': 'г', 'G': 'Г', 'h': 'ҳ', 'H': 'Ҳ', 'i': 'и', 'I': 'И',
    'j': 'ж', 'J': 'Ж', 'k': 'к', 'K': 'К', 'l': 'л', 'L': 'Л', 'm': 'м', 'M': 'М',
    'n': 'н', 'N': 'Н', 'o': 'о', 'O': 'О', 'p': 'п', 'P': 'П', 'q': 'қ', 'Q': 'Қ',
    'r': 'р', 'R': 'Р', 's': 'с', 'S': 'С', 't': 'т', 'T': 'Т', 'u': 'у', 'U': 'У',
    'v': 'в', 'V': 'В', 'x': 'х', 'X': 'Х', 'y': 'й', 'Y': 'Й', 'z': 'з', 'Z': 'З',
    'ʼ': 'ъ',
}

CYRILLIC_TO_LATIN = {
    'а': 'a', 'А': 'A', 'б': 'b', 'Б': 'B', 'в': 'v', 'В': 'V', 'г': 'g', 'Г': 'G',
    'д': 'd', 'Д': 'D', 'е': 'e', 'Е': 'E', 'ё': 'yo', 'Ё': 'Yo', 'ж': 'j', 'Ж': 'J',
    'з': 'z', 'З': 'Z', 'и': 'i', 'И': 'I', 'й': 'y', 'Й': 'Y', 'к': 'k', 'К': 'K',
    'л': 'l', 'Л': 'L', 'м': 'm', 'М': 'M', 'н': 'n', 'Н': 'N', 'о': 'o', 'О': 'O',
    'п': 'p', 'П': 'P', 'р': 'r', 'Р': 'R', 'с': 's', 'С': 'S', 'т': 't', 'Т': 'T',
    'у': 'u', 'У': 'U', 'ф': 'f', 'Ф': 'F', 'х': 'x', 'Х': 'X', 'ц': 's', 'Ц': 'S',
    'ч': 'ch', 'Ч': 'Ch', 'ш': 'sh', 'Ш': 'Sh', 'ъ': 'ʼ', 'ь': '', 'Ь': '',
    'э': 'e', 'Э': 'E', 'ю': 'yu', 'Ю': 'Yu', 'я': 'ya', 'Я': 'Ya', 'ў': 'oʻ', 'Ў': 'Oʻ',
    'қ': 'q', 'Қ': 'Q', 'ғ': 'gʻ', 'Ғ': 'Gʻ', 'ҳ': 'h', 'Ҳ': 'H',
}

LATIN_VOWELS = ('a', 'A', 'e', 'E', 'i', 'I', 'o', 'O', 'u', 'U', 'o‘', 'O‘')
CYRILLIC_VOWELS = ('а', 'А', 'е', 'Е', 'ё', 'Ё', 'и', 'И', 'о', 'О', 'у', 'У', 'э', 'Э', 'ю', 'Ю', 'я', 'Я', 'ў', 'Ў')

# Ruscha harflarga xos belgilar
RUSSIAN_CYRILLIC_SPECIFIC = set("ёыэъщ")

# Start buyrug‘i
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("Assalomu alaykum! Bu bot sizga yordam berish uchun tayyor. 😊")

# Mukammal URL regex
URL_REGEX = re.compile(
    r"(?i)(https?://|www\.)[-\w.]+\.[a-z]{2,}([:/][-a-z0-9@:%._+~#=]*)?(\?[;&a-z0-9%_=-]+)?(#[-\w]+)?"
)

def to_cyrillic(text):
    """Lotin matnni kirillchaga aylantirish"""
    compounds_first = {
        'ch': 'ч', 'Ch': 'Ч', 'CH': 'Ч', 'sh': 'ш', 'Sh': 'Ш', 'SH': 'Ш', 'yo‘': 'йў', 'Yo‘': 'Йў', 'YO‘': 'ЙЎ'
    }
    compounds_second = {
        'yo': 'ё', 'Yo': 'Ё', 'YO': 'Ё', 'yu': 'ю', 'Yu': 'Ю', 'YU': 'Ю', 'ya': 'я', 'Ya': 'Я', 'YA': 'Я',
        'ye': 'е', 'Ye': 'Е', 'YE': 'Е', 'o‘': 'ў', 'O‘': 'Ў', 'oʻ': 'ў', 'Oʻ': 'Ў', 'g‘': 'ғ', 'G‘': 'Ғ', 'gʻ': 'ғ', 'Gʻ': 'Ғ'
    }
    beginning_rules = {'ye': 'е', 'Ye': 'Е', 'YE': 'Е', 'e': 'э', 'E': 'Э'}
    after_vowel_rules = {'ye': 'е', 'Ye': 'Е', 'YE': 'Е', 'e': 'э', 'E': 'Э'}

    text = text.replace('ʻ', '‘')
    
    # Harf birikmalarini almashtirish
    text = re.sub(r'(%s)' % '|'.join(compounds_first.keys()), lambda x: compounds_first[x.group(1)], text, flags=re.U)
    text = re.sub(r'(%s)' % '|'.join(compounds_second.keys()), lambda x: compounds_second[x.group(1)], text, flags=re.U)
    text = re.sub(r'\b(%s)' % '|'.join(beginning_rules.keys()), lambda x: beginning_rules[x.group(1)], text, flags=re.U)
    text = re.sub(r'(%s)(%s)' % ('|'.join(LATIN_VOWELS), '|'.join(after_vowel_rules.keys())), 
                  lambda x: '%s%s' % (x.group(1), after_vowel_rules[x.group(2)]), text, flags=re.U)
    text = re.sub(r'(%s)' % '|'.join(LATIN_TO_CYRILLIC.keys()), lambda x: LATIN_TO_CYRILLIC[x.group(1)], text, flags=re.U)
    
    return text

def is_russian_text(text):
    """
    Matnni kirillchaga aylantirib, ruscha ekanligini tekshiradi.
    Agar ruscha xos harflar (ё, ы, э, ъ, щ) bo‘lsa, True qaytaradi.
    """
    # Agar matn allaqachon kirillcha bo‘lsa, to‘g‘ridan-to‘g‘ri ishlatamiz, aks holda aylantiramiz
    cyrillic_text = text if any(c in text for c in CYRILLIC_TO_LATIN) else to_cyrillic(text)
    
    # Ruscha xos harflar mavjudligini tekshirish
    has_russian_chars = any(char in RUSSIAN_CYRILLIC_SPECIFIC for char in cyrillic_text)
    
    logging.info(f"Matn: {text}, Kirillcha: {cyrillic_text}, Ruscha harflar: {has_russian_chars}")
    return has_russian_chars

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
