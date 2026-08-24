import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database import init_db
from admin_handlers import admin_router
from handlers import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


async def main():
    init_db()
    logger.info("Starting Telegram Emoji Pack Bot...")
    
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(admin_router)
    dp.include_router(router)

    # Delete any pending updates / webhook
    await bot.delete_webhook(drop_pending_updates=True)
    
    me = await bot.get_me()
    logger.info(f"Bot logged in as @{me.username} ({me.first_name})")

    # Set Telegram Menu Button to Mini App
    try:
        from aiogram.types import MenuButtonWebApp, WebAppInfo
        from config import WEBAPP_URL
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="📱 Mini App",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        )
        logger.info(f"Bot chat menu button set to Mini App: {WEBAPP_URL}")
    except Exception as e:
        logger.warning(f"Could not set chat menu button: {e}")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot exited.")
