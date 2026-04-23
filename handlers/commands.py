"""
Command handlers for the Whale Tracker Bot
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.formatters import (
    format_welcome_message,
    format_help_message,
    format_status_message,
    format_alerts_menu,
    format_whales_menu,
    format_subscribe_success,
    format_unsubscribe_success,
)
from utils.keyboard import (
    main_menu_keyboard,
    alerts_menu_keyboard,
    whales_menu_keyboard,
    price_menu_keyboard,
    settings_menu_keyboard,
    amount_filter_keyboard,
    network_filter_keyboard,
    status_keyboard,
)
from utils.helpers import format_amount

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    user_id = user.id

    logger.info(f"User {user_id} started the bot")

    # Register user if new
    if hasattr(context.application, "monitors"):
        monitors = context.application.monitors
        if hasattr(monitors, "whale") and monitors.whale:
            monitors.whale.user_storage.register_user(user_id)

    # Welcome message
    welcome_text = format_welcome_message()

    await update.message.reply_text(
        welcome_text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=main_menu_keyboard(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = format_help_message()

    await update.message.reply_text(
        help_text,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


async def alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /alerts command - manage subscriptions"""
    user_id = update.effective_user.id

    alerts_text = format_alerts_menu()

    await update.message.reply_text(
        alerts_text,
        parse_mode="HTML",
        reply_markup=alerts_menu_keyboard(),
    )


async def whales_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /whales command - whale alert settings"""
    user_id = update.effective_user.id

    # Get user preferences
    user_prefs = None
    if hasattr(context.application, "monitors"):
        monitors = context.application.monitors
        if hasattr(monitors, "whale") and monitors.whale:
            user_prefs = monitors.whale.user_storage.get_prefs(user_id)

    if user_prefs:
        menu_text = format_whales_menu(
            user_prefs.min_whale_amount,
            user_prefs.networks
        )
        reply_markup = amount_filter_keyboard(user_prefs.min_whale_amount)
    else:
        menu_text = format_whales_menu(100000, ["ethereum", "tron"])
        reply_markup = amount_filter_keyboard(100000)

    await update.message.reply_text(
        menu_text,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /price command - price alert settings"""
    price_text = """
📊 <b>Price Alerts</b>

━━━━━━━━━━━━━━━━━━━━
Настройка оповещений о ценах:

Доступные пары:
• BTC/USDT
• ETH/USDT
• BNB/USDT
• SOL/USDT
• XRP/USDT
• ADA/USDT

━━━━━━━━━━━━━━━━━━━━
<i>Используйте кнопки для управления подписками</i>
"""

    await update.message.reply_text(
        price_text,
        parse_mode="HTML",
        reply_markup=price_menu_keyboard(),
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - show current status"""
    user_id = update.effective_user.id

    # Get user preferences
    whale_enabled = True
    price_enabled = True
    min_amount = 100000
    networks = ["ethereum", "tron"]
    active_users = 0
    api_status = "🟢 Отлично"
    offline_cache = True
    demo_mode = False

    if hasattr(context.application, "monitors"):
        monitors = context.application.monitors
        if hasattr(monitors, "whale") and monitors.whale:
            user_prefs = monitors.whale.user_storage.get_prefs(user_id)
            whale_enabled = user_prefs.whale_alerts
            price_enabled = user_prefs.price_alerts
            min_amount = user_prefs.min_whale_amount
            networks = user_prefs.networks
            active_users = len(monitors.whale.user_storage.get_all_user_ids())
            
            # Получаем статус монитора
            monitor_status = monitors.whale.get_status()
            api_status = monitor_status["api_status"]
            offline_cache = monitor_status["offline_cache"]
            demo_mode = monitor_status["demo_mode"]

    status_text = format_status_message(
        whale_enabled,
        price_enabled,
        min_amount,
        networks,
        active_users,
        api_status,
        offline_cache,
        demo_mode
    )

    await update.message.reply_text(
        status_text,
        parse_mode="HTML",
        reply_markup=status_keyboard(),
    )


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command - general settings"""
    settings_text = """
⚙️ <b>Общие настройки</b>

━━━━━━━━━━━━━━━━━━━━
Управление настройками бота:

• Уведомления — включить/выключить
• Тихие часы — период без алертов
• Формат сообщений — детальный/компактный

━━━━━━━━━━━━━━━━━━━━
<i>Используйте кнопки для настройки</i>
"""

    await update.message.reply_text(
        settings_text,
        parse_mode="HTML",
        reply_markup=settings_menu_keyboard(),
    )


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /subscribe command - quick subscribe"""
    user_id = update.effective_user.id

    if len(context.args) > 0:
        alert_type = context.args[0].lower()

        if hasattr(context.application, "monitors"):
            monitors = context.application.monitors
            if hasattr(monitors, "whale") and monitors.whale:
                prefs = monitors.whale.user_storage.get_prefs(user_id)

                if "whale" in alert_type:
                    prefs.whale_alerts = True
                    monitors.whale.user_storage.set_prefs(user_id, prefs)
                    await update.message.reply_text(format_subscribe_success("whale"))
                elif "price" in alert_type:
                    prefs.price_alerts = True
                    monitors.whale.user_storage.set_prefs(user_id, prefs)
                    await update.message.reply_text(format_subscribe_success("price"))
                else:
                    await update.message.reply_text(
                        "❌ Неизвестный тип алерта. Доступно: whale, price"
                    )
            else:
                await update.message.reply_text(format_subscribe_success("whale"))
        else:
            await update.message.reply_text(format_subscribe_success("whale"))
    else:
        await update.message.reply_text(
            "📝 <b>Быстрая подписка</b>\n\n"
            "Использование: /subscribe [тип]\n\n"
            "Типы: whale, price, unlock\n\n"
            "Пример: /subscribe whale",
            parse_mode="HTML"
        )


async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unsubscribe command - quick unsubscribe"""
    user_id = update.effective_user.id

    if len(context.args) > 0:
        alert_type = context.args[0].lower()

        if hasattr(context.application, "monitors"):
            monitors = context.application.monitors
            if hasattr(monitors, "whale") and monitors.whale:
                prefs = monitors.whale.user_storage.get_prefs(user_id)

                if "whale" in alert_type:
                    prefs.whale_alerts = False
                    monitors.whale.user_storage.set_prefs(user_id, prefs)
                    await update.message.reply_text(format_unsubscribe_success("whale"))
                elif "price" in alert_type:
                    prefs.price_alerts = False
                    monitors.whale.user_storage.set_prefs(user_id, prefs)
                    await update.message.reply_text(format_unsubscribe_success("price"))
                else:
                    await update.message.reply_text(
                        "❌ Неизвестный тип алерта. Доступно: whale, price"
                    )
        else:
            await update.message.reply_text(format_unsubscribe_success("whale"))
    else:
        await update.message.reply_text(
            "📝 <b>Быстрая отписка</b>\n\n"
            "Использование: /unsubscribe [тип]\n\n"
            "Типы: whale, price, unlock\n\n"
            "Пример: /unsubscribe whale",
            parse_mode="HTML"
        )


async def demo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /demo command - simulate real alerts"""
    user_id = update.effective_user.id
    
    # Отправляем начальное сообщение
    await update.message.reply_text(
        "🚀 <b>DEMO MODE</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Показываю как работают реальные уведомления...\n"
        "━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML"
    )
    
    # Ждем 1 секунду перед первым алертом
    await asyncio.sleep(1)
    
    # Демо алерты
    alerts = [
        {
            "title": "🐋 КИТ 🐋",
            "description": "Binance Hot Wallet получил крупный перевод",
            "details": "💰 Сумма: $2,500,000 USDT\n"
                     "📊 Токен: USDT\n"
                     "🔗 Сеть: Ethereum\n"
                     "📍 От: 0x7a25...3f8c\n"
                     "📍 Кому: Binance Hot Wallet\n"
                     "🎯 Объём: 🔴 Крупный\n"
                     "💡 Контекст: Крупный вывод на биржу",
            "delay": 2
        },
        {
            "title": "⚡ PRICE ALERT ⚡",
            "description": "Резкий рост BTC",
            "details": "📊 BTC/USDT\n"
                     "📈 $67,450 → $69,615\n"
                     "🔺 +3.2% (5 минут)\n"
                     "🎯 Объём: Высокий\n"
                     "💡 Движение: Бычий импульс после новости ETF",
            "delay": 2
        },
        {
            "title": "🔓 TOKEN UNLOCK 🔓",
            "description": "Предстоящий разлок токенов",
            "details": "🎯 Проект: EigenLayer\n"
                     "💎 Токен: EIGEN\n"
                     "📊 Разлок: $12.5M\n"
                     "📅 Дата: 15.04.2025\n"
                     "⏰ Через 3 дня\n"
                     "💡 Источник: @ tokenomics_hunter",
            "delay": 2
        },
        {
            "title": "🐋 КИТ 🐋",
            "description": "Крупная транзакция в сети Tron",
            "details": "💰 Сумма: $1,800,000 USDT\n"
                     "📊 Токен: USDT\n"
                     "🔗 Сеть: Tron\n"
                     "📍 От: Unknown Whale\n"
                     "📍 Кому: Another Whale\n"
                     "🎯 Объём: 🔴 Средний\n"
                     "💡 Контекст: Межкошельковый перевод",
            "delay": 2
        }
    ]
    
    # Отправляем алерты с задержкой
    for alert in alerts:
        alert_text = f"""{alert['title']}
━━━━━━━━━━━━━━━
{alert['description']}
━━━━━━━━━━━━━━━
{alert['details']}
━━━━━━━━━━━━━━━
⏰ только что"""
        
        await update.message.reply_text(alert_text, parse_mode="HTML")
        await asyncio.sleep(alert['delay'])
    
    # Финальное сообщение
    await update.message.reply_text(
        "✅ <b>Демо завершено!</b>\n\n"
        "Вот так выглядят реальные уведомления от бота.\n"
        "Хотите получать такие же алерты?\n\n"
        "🚀 <b>Начните сейчас:</b>\n"
        "/subscribe whale — подписаться на китов\n"
        "/subscribe price — подписаться на цены\n"
        "/alerts — все настройки\n\n"
        "<i>Настройте пороги и сети в /whales</i>",
        parse_mode="HTML",
        reply_markup=None
    )


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /test command - send test alert"""
    user_id = update.effective_user.id

    if hasattr(context.application, "monitors"):
        monitors = context.application.monitors
        if hasattr(monitors, "whale") and monitors.whale:
            await monitors.whale.test_alert(user_id)
        if hasattr(monitors, "price") and monitors.price:
            await monitors.price.test_alert(user_id)
    else:
        await update.message.reply_text(
            "🧪 Тест временно недоступен. Попробуйте позже."
        )
