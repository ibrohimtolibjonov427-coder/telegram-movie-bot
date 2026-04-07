import asyncio
import logging
import sqlite3
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from aiohttp import web

# ===============================
# TOKEN (Renderdan olinadi)
# ===============================
API_TOKEN = os.getenv("BOT_TOKEN")

if not API_TOKEN:
    raise Exception("BOT_TOKEN topilmadi!")

# ===============================
# SOZLAMALAR
# ===============================
ADMINS = [7454731921]  # o'zingni ID
CHANNELS = ["@tolibjonovv_00"]  # kanallar username

# ===============================
# BOT
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
        kb.inline_keyboard.append(
            [InlineKeyboardButton(text=f"Obuna bo'lish {ch}", url=f"https://t.me/{ch[1:]}")]
        )
    kb.inline_keyboard.append(
        [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")]
    )
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
# ADMIN VIDEO
# ===============================
@dp.message(F.video)
async def save_movie(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    if not message.caption:
        await message.answer("❗ Kod yozilmagan")
        return

    code = message.caption.strip()
    file_id = message.video.file_id

    cursor.execute("REPLACE INTO movies VALUES (?, ?)", (code, file_id))
    conn.commit()

    await message.answer(f"✅ Saqlandi: {code}")

# ===============================
# KINO CHIQARISH
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
        await bot.send_video(message.chat.id, result[0])
    else:
        await message.answer("❌ Topilmadi")

# ===============================
# FAKE SERVER (RENDER UCHUN)
# ===============================
PORT = int(os.environ.get("PORT", 10000))

async def handle(request):
    return web.Response(text="Bot ishlayapti")

async def start_web():
    app = web.Application()
    app.router.add_get("/", handle)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

# ===============================
# MAIN
# ===============================
async def main():
    await start_web()
    print("Bot ishga tushdi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())