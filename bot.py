# ===============================
# TELEGRAM MOVIE BOT (AIROGRAM 3 VERSION)
# ===============================

# 📌 O'RNATISH:
# pip install aiogram

import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# ===============================
# ⚠️ O'ZGARTIRISH KERAK
# ===============================
API_TOKEN = "8631701404:AAEOTBfU9niY8x_G-iToyMPK6lJX5nb0tnE"
ADMINS = [7454731921]  # O'z ID
CHANNELS = ["@tolibjonovv_00"]  # faqat @username

# ===============================

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# ===============================
# DATABASE
# ===============================
conn = sqlite3.connect("movies.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS movies (
    code TEXT PRIMARY KEY,
    file_id TEXT
)
""")
conn.commit()

# ===============================
# OBUNA TEKSHIRISH
# ===============================
async def check_sub(user_id):
    for channel in CHANNELS:
        member = await bot.get_chat_member(channel, user_id)
        if member.status in ["left", "kicked"]:
            return False
    return True

# ===============================
# BUTTON
# ===============================
def sub_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for ch in CHANNELS:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f"Obuna bo'lish {ch}", url=f"https://t.me/{ch[1:]}")
        ])
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")
    ])
    return kb

# ===============================
# START
# ===============================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    if not await check_sub(message.from_user.id):
        await message.answer("❗ Avval obuna bo'ling:", reply_markup=sub_keyboard())
        return

    await message.answer("🎬 Kino kodini yuboring:")

# ===============================
# CHECK BUTTON
# ===============================
@dp.callback_query(F.data == "check_sub")
async def check_callback(callback: types.CallbackQuery):
    if await check_sub(callback.from_user.id):
        await callback.message.answer("✅ Obuna tasdiqlandi!")
    else:
        await callback.answer("❌ Obuna bo'lmagansiz", show_alert=True)

# ===============================
# ADMIN ADD
# ===============================
@dp.message(Command("add"))
async def add_movie(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    await message.answer("Videoni yuboring va captionga kod yozing")

# ===============================
# VIDEO SAVE
# ===============================
@dp.message(F.video)
async def save_movie(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    if not message.caption:
        await message.answer("❗ Kod yozing")
        return

    code = message.caption.strip()
    file_id = message.video.file_id

    cursor.execute("REPLACE INTO movies VALUES (?, ?)", (code, file_id))
    conn.commit()

    await message.answer(f"✅ Saqlandi: {code}")

# ===============================
# SEND MOVIE
# ===============================
@dp.message()
async def send_movie(message: types.Message):
    if not await check_sub(message.from_user.id):
        await message.answer("❗ Obuna bo'ling", reply_markup=sub_keyboard())
        return

    code = message.text.strip()

    cursor.execute("SELECT file_id FROM movies WHERE code=?", (code,))
    result = cursor.fetchone()

    if result:
        await message.answer_video(result[0])
    else:
        await message.answer("❌ Topilmadi")

# ===============================
# STAT
# ===============================
@dp.message(Command("stat"))
async def stat(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    cursor.execute("SELECT COUNT(*) FROM movies")
    count = cursor.fetchone()[0]

    await message.answer(f"🎬 Kinolar: {count}")

# ===============================
# RUN
# ===============================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
