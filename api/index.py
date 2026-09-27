import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from google import genai
from google.genai import types as genai_types

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "KALIT")

bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = (
    "Siz samimiy, aqlli va muloyim insoniy yordamchisiz. "
    "Foydalanuvchilarga doimo hurmat bilan, 'siz' ohangida, iliq va tushunarli javob bering. "
    "Hech qachon 'sen' deb murojaat qilmang. O'zbek tilida ravon, tabiiy va xushmuomala gapiring."
)

@dp.message(F.text)
async def handle_message(message: types.Message):
    if message.from_user.is_bot:
        return

    user_text = message.text
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_text,
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            ),
        )
        bot_reply = response.text
    await message.answer(bot_reply)
except Exception as e:
    bot_reply = f"Xatolik tafsiloti: {str(e)}"
@app.post("/api/index")
async def webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update=update)
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"status": "Bot Vercel'da ishlamqda!"}
