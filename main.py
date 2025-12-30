import asyncio
import logging
import json
import os
import pandas as pd
from collections import defaultdict
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- SOZLAMALAR ---
BOT_TOKEN = "8520261546:AAH5T7iXPFyoRTSBuMqskXuI07_P85RDCGc"
CHANNEL_ID = -1003269835561
CHANNEL_LINK = "https://t.me/yangiyoltmmtb" 
RESULTS_FILE = "poll_results.json" 
VOTED_USERS_FILE = "voted_users.json"

# --- RAHBARLAR (MA'NAVIYATCHILAR) RO'YXATI ---
DMTT = {
    1: "Ташева Гулчехра",
    2: "Кенжаева Мухаррам ",
    3: "Хакимова Шоира",
    4: "Иброхимова Хуснорабону",
    5: "Нурматова Саида ",
    6: "Ўринбоева Муборак",
    7: "Дадахўжаева Шарифа",
    8: "Суванова Соҳиба",
    9: "Заирова Мавлуда",
    10: "Шароббаева Муҳайё ",
    11: "Бадалбаева Нодира",
    12: "Ибрагимова Гавҳар",
    13: "Исакова Бахринисо",
    14: "Султонова Дилбар",
    15: "Умурова Навруза",
    17: "Бутаева Малика",
    18: "Арзимбетова Жулдуз",
    19: "Махаматова Фируза",
    20: "Куралбаева Роза",
    21: "Саматова Захро",
    22: "Жураева Маҳлиё",
    23: "Махаматиллаева Шахноза",
    24: "Назарова Шарафатхан",
    25: "Тўйчибекова Гўзал ",
    26: "Ахунова Фотима",
    27: "Жумабоева Хатирахон",
    28: "Усмонова Дилдора",
    29: "Холматова Дилафруз",
}

logging.basicConfig(level=logging.INFO)
poll_results = defaultdict(int)
voted_users = set()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- FAYLLAR ---
def load_data():
    global poll_results, voted_users
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for k, v in data.items(): poll_results[int(k)] = v
    if os.path.exists(VOTED_USERS_FILE):
        with open(VOTED_USERS_FILE, 'r', encoding='utf-8') as f:
            voted_users = set(json.load(f))

def save_data():
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(dict(poll_results), f, indent=4)
    with open(VOTED_USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(voted_users), f, indent=4)

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except: return False

# --- TUGMALAR (F.I.Sh BILAN) ---
def create_keyboard():
    builder = InlineKeyboardBuilder()
    for i in sorted(DMTT.keys()):
        fio = DMTT[i]
        votes = poll_results[i]
        # Tugmada maktab va ism sharif chiqadi
        builder.button(text=f"🏠 {i}-DMTT | {fio} ({votes})", callback_data=f"vote_{i}")
    builder.adjust(1)
    return builder.as_markup()

# --- HANDLERLAR ---
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    photo_url = "https://raintree.ac.th/wp-content/uploads/2024/05/what-kindergarten-looks-like-in-southeast-asian-countries.jpeg"
    poll_description = (
        "<b>«YILNING ENG NAMUNALI DMTT RAHBARI — 2025»</b>\n\n"
        "Yilning eng namunali «DMTT RAHBARI» nominatsiyasi uchun jamoatchilik so‘rovnomasi e’lon qilinmoqda.\n\n"
        "2025-yilda eng faol ishlagan, soha rivojida munosib hissasini qo‘shgan, tizimda yetakchi bo‘lgan DMTT RAHBARINI овоз бериш орқали  аниқлаб беринг!\n\n"
        "<i>Qaysi rahbar qanday ishlaganini — sizning e’tirofingiz aniqlab beradi.</i>\n\n"
        "<b>⏰ Tanlov 5-yanvar kuni 10:00 da yakunlanadi.</b>\n\n"
        "<b>🛑 ҚОИДАЛАР:</b>\n"
        "1️⃣ Фақат 1 марта овоз бериш мумкин.\n"
        "2️⃣ Каналга аъзо бўлиш мажбурий.\n\n"
        "<b>👇 ПАСTДАГИ РЎЙХАТДАН МАКТАБНИ ТАНЛАНГ:</b>"
    )
    try:
        await message.answer_photo(photo=photo_url, caption=poll_description, reply_markup=create_keyboard(), parse_mode="HTML")
    except:
        await message.answer(poll_description, reply_markup=create_keyboard(), parse_mode="HTML")

@dp.message(Command("results"))
async def export_to_excel(message: types.Message):
    data_for_excel = [{"DMTT": i, "F.I.Sh": DMTT[i], "Ovozlar": poll_results[i]} for i in sorted(DMTT.keys())]
    df = pd.DataFrame(data_for_excel)
    file_path = "Natijalar.xlsx"
    df.to_excel(file_path, index=False)
    await message.answer_document(FSInputFile(file_path), caption="📊 Ovoz berish natijalari (Excel)")
    if os.path.exists(file_path): os.remove(file_path)

@dp.callback_query(F.data.startswith("vote_"))
async def process_vote(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id in voted_users:
        await callback_query.answer("⚠️ Siz allaqachon ovoz bergansiz!", show_alert=True)
        return

    if not await check_subscription(user_id):
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="➕ Kanalga a'zo bo'lish", url=CHANNEL_LINK))
        kb.row(InlineKeyboardButton(text="✅ Tekshirish", callback_data=callback_query.data))
        await callback_query.answer("❌ Avval kanalga a'zo bo'ling!", show_alert=True)
        await callback_query.message.answer("Ovoz berish uchun kanalga a'zo bo'lishingiz shart:", reply_markup=kb.as_markup())
        return

    m_id = int(callback_query.data.split('_')[1])
    poll_results[m_id] += 1
    voted_users.add(user_id)
    save_data()
    
    await callback_query.answer(f"✅ {DMTT[m_id]}ga ovoz berildi!", show_alert=True)
    await callback_query.message.edit_reply_markup(reply_markup=create_keyboard())

async def main():
    load_data()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
