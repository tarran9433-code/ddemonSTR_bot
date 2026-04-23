"""
WebApp handlers for Whale Tracker Bot
Mini App integration with Telegram
"""

import logging
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет кнопку для открытия Mini App"""
    # Railway URL - замени на свой проект
    webapp_url = "https://ВАШ-ПРОЕКТ.up.railway.app"   # 👈 Сюда вставишь Railway URL
    
    # GitHub Pages для Mini App
    webapp_url = "https://your-username.github.io/whale-tracker/static/miniapp.html"
    
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text="📊 Дашборд китов",
            web_app=WebAppInfo(url=webapp_url)
        )
    ]])
    
    await update.message.reply_text(
        "🐋 <b>Live Dashboard</b>\n\n"
        "Нажми на кнопку, чтобы открыть дашборд с последними транзакциями китов в реальном времени.\n\n"
        "📈 <b>Что вы увидите:</b>\n"
        "• Последние 20 транзакций китов\n"
        "• Автоопределение бирж\n"
        "• Реальное обновление данных\n"
        "• Красивые графики и статистика",
        parse_mode="HTML",
        reply_markup=keyboard
    )
