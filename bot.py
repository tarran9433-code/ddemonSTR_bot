"""
Whale Tracker Bot — Main Entry Point
Real-time blockchain whale and smart alert system
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# HTTP API imports
from aiohttp import web
import json
from datetime import datetime

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

import config
from handlers.commands import (
    start_command,
    help_command,
    alerts_command,
    whales_command,
    price_command,
    status_command,
    settings_command,
    subscribe_command,
    demo_command,
)
from handlers.webapp import dashboard_command
from handlers.callbacks import button_callback
from monitors.whale_monitor import WhaleMonitor
from monitors.price_monitor import PriceMonitor
from services.formatters import format_welcome, format_help

# Setup logging
def setup_logging():
    """Configure logging for the bot"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_dir / "bot.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger(__name__)

logger = setup_logging()


# Global monitors storage
class BotMonitors:
    """Container for all bot monitors"""
    whale: WhaleMonitor | None = None
    price: PriceMonitor | None = None
    unlock: None = None  # Placeholder for future

    @classmethod
    async def start_all(cls, app: Application):
        """Initialize and start all monitors"""
        if config.WHALE_CONFIG.enabled:
            cls.whale = WhaleMonitor(app)
            asyncio.create_task(cls.whale.start())
            logger.info("Whale monitor started")

        if config.PRICE_CONFIG.enabled:
            cls.price = PriceMonitor(app)
            asyncio.create_task(cls.price.start())
            logger.info("Price monitor started")

    @classmethod
    async def stop_all(cls):
        """Stop all monitors"""
        if cls.whale:
            await cls.whale.stop()
        if cls.price:
            await cls.price.stop()
        logger.info("All monitors stopped")


async def post_init(application: Application):
    """Run after bot initialization"""
    logger.info("Bot starting post-initialization...")

    # Create necessary directories
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    # Start monitors
    await BotMonitors.start_all(application)
    
    # Запускаем HTTP API сервер
    port = int(os.environ.get("PORT", 8080))
    asyncio.create_task(start_http_server(application, port=port))

    logger.info("Bot initialized successfully!")


# --- HTTP API для Mini App ---
async def api_transactions(request):
    """Возвращает последние транзакции китов в формате JSON"""
    # Получаем whale_monitor из глобального хранилища приложения
    app = request.app["telegram_app"]
    whale_monitor = None
    if hasattr(app, "monitors") and app.monitors and app.monitors.whale:
        whale_monitor = app.monitors.whale
    
    if whale_monitor is None:
        return web.json_response([])
    
    alerts = whale_monitor.recent_alerts[-20:]  # последние 20
    data = []
    for alert in alerts:
        tx = alert.transaction
        data.append({
            "id": alert.id,
            "token": tx.symbol,
            "type": "buy" if alert.alert_type == "exchange_in" else "sell",
            "amount": tx.amount_usd,
            "timestamp": tx.timestamp.isoformat(),
            "hash": tx.tx_hash,
            "from_address": tx.from_address,
            "to_address": tx.to_address,
            "blockchain": tx.blockchain
        })
    return web.json_response(data)

async def start_http_server(telegram_app, port=8080):
    """Запускает aiohttp сервер в фоне"""
    web_app = web.Application()
    web_app["telegram_app"] = telegram_app
    web_app.router.add_get("/api/transactions", api_transactions)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"✅ HTTP API server started on port {port}/api/transactions")
    # держим бесконечно
    await asyncio.Event().wait()


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot"""
    logger.error(f"Exception while handling an update: {context.error}")

    # Try to notify user about error
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Произошла ошибка. Попробуйте позже или используйте /help."
        )


def main():
    """Main function to run the bot"""
    logger.info("=" * 50)
    logger.info("Whale & Smart Alert Tracker Bot - Starting")
    logger.info("=" * 50)

    # Check for bot token
    if config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ BOT_TOKEN not set! Please set your Telegram bot token.")
        logger.error("   Export BOT_TOKEN='your_token_here' before running.")
        sys.exit(1)

    # Create application
    application = Application.builder()\
        .token(config.BOT_TOKEN)\
        .read_timeout(30)\
        .write_timeout(30)\
        .post_init(post_init)\
        .build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("alerts", alerts_command))
    application.add_handler(CommandHandler("whales", whales_command))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("demo", demo_command))
    application.add_handler(CommandHandler("dashboard", dashboard_command))

    # Add callback handler for inline buttons
    application.add_handler(CallbackQueryHandler(button_callback))

    # Add error handler
    application.add_error_handler(error_handler)

    # Add message handler for general text
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        lambda u, c: u.effective_message.reply_text(
            "Используйте команды бота. Нажмите /help для списка команд."
        )
    ))

    # Run the bot
    logger.info("Bot is ready. Starting polling...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
