"""
Message handlers for non-command text
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.helpers import parse_amount, format_amount

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle non-command text messages"""

    text = update.message.text.strip()

    # Check for amount input
    amount = parse_amount(text)
    if amount and amount > 0:
        await update.message.reply_text(
            f"💰 Понял! Сумма: {format_amount(amount)}\n"
            f"Используйте /whales для настройки порогов.",
            parse_mode="HTML",
        )
        return

    # Default response
    await update.message.reply_text(
        "🤖 Используйте команды бота:\n\n"
        "/start — Начать\n"
        "/help — Справка\n"
        "/alerts — Уведомления\n"
        "/whales — Настройки китов\n"
        "/status — Статус\n\n"
        "Или выберите действие в меню.",
        parse_mode="HTML",
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document uploads (future: import settings)"""
    await update.message.reply_text(
        "📄 Функция импорта настроек скоро будет доступна!",
        parse_mode="HTML",
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads"""
    await update.message.reply_text(
        "📷 Спасибо за фото! Пока не поддерживается.",
        parse_mode="HTML",
    )
