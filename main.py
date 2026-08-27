import sys
import asyncio
import logging
import uvicorn

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, SERVER_HOST, SERVER_PORT, WEBAPP_URL
from database import init_db
from admin_handlers import admin_router
from handlers import router
from server import app, set_bot

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("main")


async def run_bot():
    """Runs the Aiogram Telegram Bot polling loop with automatic reconnection"""
    while True:
        logger.info("Initializing Telegram Bot...")
        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        set_bot(bot)

        dp = Dispatcher()
        dp.include_router(admin_router)
        dp.include_router(router)

        try:
            # Delete webhook if any, keep pending updates
            try:
                await bot.delete_webhook(drop_pending_updates=False)
            except Exception as w_err:
                logger.warning(f"delete_webhook notice: {w_err}")
            
            me = await bot.get_me()
            logger.info(f"Telegram Bot connected: @{me.username} ({me.first_name})")

            try:
                from aiogram.types import MenuButtonWebApp, WebAppInfo
                await bot.set_chat_menu_button(
                    menu_button=MenuButtonWebApp(
                        text="📱 Mini App",
                        web_app=WebAppInfo(url=WEBAPP_URL)
                    )
                )
                logger.info(f"Bot chat menu button configured: {WEBAPP_URL}")
            except Exception as e:
                logger.warning(f"Could not set chat menu button: {e}")

            logger.info("Starting Telegram Bot polling loop...")
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        except (KeyboardInterrupt, SystemExit):
            logger.info("Bot polling stopped by system.")
            await bot.session.close()
            break
        except Exception as e:
            logger.error(f"Bot polling encountered error: {e}", exc_info=True)
            try:
                await bot.session.close()
            except:
                pass
            logger.info("Reconnecting bot in 3 seconds...")
            await asyncio.sleep(3)


async def run_web_server():
    """Runs the FastAPI / Uvicorn server for Mini App"""
    logger.info(f"Starting Mini App Web Server on http://{SERVER_HOST}:{SERVER_PORT} (Public URL: {WEBAPP_URL})...")
    config = uvicorn.Config(
        app=app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info",
        access_log=False
    )
    server = uvicorn.Server(config)
    try:
        await server.serve()
    except Exception as e:
        logger.error(f"Web server error: {e}", exc_info=True)


async def main():
    # 1. Initialize SQLite Database
    init_db()
    
    # 2. Run both Bot and Web Server concurrently
    logger.info("🚀 GnEmoji Bot & Mini App Server ishga tushmoqda...")
    await asyncio.gather(
        run_bot(),
        run_web_server(),
        return_exceptions=True
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Dastur to'xtatildi.")
