"""
Telegram Games Bot — main entry point.
Runs FastAPI + aiogram 3.x via webhook for Render.com deployment.
"""

import os
import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from fastapi import FastAPI
from dotenv import load_dotenv

from handlers import games
from keyboards import main_menu_kb

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = "/webhook"
BASE_WEBHOOK_URL = f"{WEBHOOK_URL}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# ─── Start handler ───────────────────────────────────────────────
@dp.message_command("start")
async def cmd_start(message):
    await message.answer(
        "🎮 <b>Добро пожаловать в Игровой Бот!</b>\n\n"
        "Выбери игру из меню ниже:",
        reply_markup=main_menu_kb()
    )


# ─── Register game handlers ──────────────────────────────────────
dp.include_router(games.router)


# ─── Lifespan ────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Set webhook on startup
    await bot.set_webhook(
        url=BASE_WEBHOOK_URL,
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"]
    )
    logger.info(f"Webhook set to: {BASE_WEBHOOK_URL}")
    yield
    await bot.session.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"status": "ok", "message": "Telegram Games Bot is running!"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Mount aiogram webhook
setup_application(app, WEBHOOK_PATH, dispatcher=dp, bot=bot)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8081))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
