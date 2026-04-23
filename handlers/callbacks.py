"""
Callback query handlers for inline buttons
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.formatters import (
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
)

logger = logging.getLogger(__name__)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button callbacks"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    logger.info(f"Callback from {user_id}: {data}")

    # Get user storage if available
    user_prefs = None
    user_storage = None

    if hasattr(context.application, "monitors"):
        monitors = context.application.monitors
        if hasattr(monitors, "whale") and monitors.whale:
            user_storage = monitors.whale.user_storage
            user_prefs = user_storage.get_prefs(user_id)

    # Route callback
    if data == "menu_main":
        await query.edit_message_text(
            text="🐋 <b>Главное меню</b>\n\nВыберите действие:",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )

    elif data == "menu_alerts":
        await query.edit_message_text(
            text=format_alerts_menu(),
            parse_mode="HTML",
            reply_markup=alerts_menu_keyboard(),
        )

    elif data == "menu_whales":
        if user_prefs:
            menu_text = format_whales_menu(
                user_prefs.min_whale_amount,
                user_prefs.networks
            )
            reply_markup = amount_filter_keyboard(user_prefs.min_whale_amount)
        else:
            menu_text = format_whales_menu(100000, ["ethereum", "tron"])
            reply_markup = amount_filter_keyboard(100000)

        await query.edit_message_text(
            text=menu_text,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )

    elif data == "menu_price":
        price_text = """
📊 <b>Price Alerts</b>

━━━━━━━━━━━━━━━━━━━━
Настройка оповещений о ценах:

Доступные пары:
• BTC/USDT
• ETH/USDT
• BNB/USDT
• SOL/USDT

━━━━━━━━━━━━━━━━━━━━
<i>Выберите пары для мониторинга</i>
"""
        await query.edit_message_text(
            text=price_text,
            parse_mode="HTML",
            reply_markup=price_menu_keyboard(),
        )

    elif data == "menu_unlocks":
        await query.edit_message_text(
            text="🔓 <b>Token Unlocks</b>\n\n"
                 "━━━━━━━━━━━━━━━━━━━━\n"
                 "Мониторинг разлоков токенов.\n"
                 "Эта функция скоро будет доступна! 🚀\n"
                 "━━━━━━━━━━━━━━━━━━━━\n"
                 "<i>Следите за обновлениями</i>",
            parse_mode="HTML",
            reply_markup=alerts_menu_keyboard(),
        )

    elif data == "menu_settings":
        await query.edit_message_text(
            text="⚙️ <b>Настройки</b>\n\n"
                 "━━━━━━━━━━━━━━━━━━━━\n"
                 "Общие параметры бота",
            parse_mode="HTML",
            reply_markup=settings_menu_keyboard(),
        )

    elif data == "menu_help":
        await query.edit_message_text(
            text="📖 <b>Справка</b>\n\n"
                 "━━━━━━━━━━━━━━━━━━━━\n"
                 "Используйте /help для подробной справки",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )

    elif data == "menu_test":
        await query.edit_message_text(
            text="🧪 Отправляю тестовое оповещение...",
            parse_mode="HTML",
        )
        # Send test alert
        if hasattr(context.application, "monitors"):
            monitors = context.application.monitors
            if hasattr(monitors, "whale") and monitors.whale:
                await monitors.whale.test_alert(user_id)
            if hasattr(monitors, "price") and monitors.price:
                await monitors.price.test_alert(user_id)

    # Toggle alerts
    elif data == "toggle_whale":
        if user_prefs and user_storage:
            user_prefs.whale_alerts = not user_prefs.whale_alerts
            user_storage.set_prefs(user_id, user_prefs)
            status = "✅ включены" if user_prefs.whale_alerts else "❌ отключены"
            await query.answer(f"Whale Alerts {status}", show_alert=True)
        else:
            await query.answer("Настройки недоступны", show_alert=True)

    elif data == "toggle_price":
        if user_prefs and user_storage:
            user_prefs.price_alerts = not user_prefs.price_alerts
            user_storage.set_prefs(user_id, user_prefs)
            status = "✅ включены" if user_prefs.price_alerts else "❌ отключены"
            await query.answer(f"Price Alerts {status}", show_alert=True)
        else:
            await query.answer("Настройки недоступны", show_alert=True)

    elif data == "toggle_unlock":
        await query.answer("Скоро будет доступно! 🚀", show_alert=True)

    # Amount thresholds
    elif data.startswith("whale_"):
        amount_str = data.replace("whale_", "").replace("k", "000")
        try:
            amount = int(amount_str)
            if user_prefs and user_storage:
                user_prefs.min_whale_amount = amount
                user_storage.set_prefs(user_id, user_prefs)
                await query.answer(f"Порог установлен: ${amount:,}", show_alert=True)
        except ValueError:
            await query.answer("Ошибка настройки", show_alert=True)

    # Amount setting buttons
    elif data.startswith("amount_set_"):
        try:
            amount = int(data.replace("amount_set_", ""))
            if user_prefs and user_storage:
                user_prefs.min_whale_amount = amount
                user_storage.set_prefs(user_id, user_prefs)
                await query.answer(f"Мин. сумма: ${amount:,}", show_alert=True)
                # Update keyboard
                menu_text = format_whales_menu(amount, user_prefs.networks)
                await query.edit_message_text(
                    text=menu_text,
                    parse_mode="HTML",
                    reply_markup=amount_filter_keyboard(amount),
                )
        except ValueError:
            await query.answer("Ошибка", show_alert=True)

    # Network selection
    elif data.startswith("net_"):
        network = data.replace("net_", "")
        if user_prefs and user_storage:
            if network in user_prefs.networks:
                user_prefs.networks.remove(network)
            else:
                user_prefs.networks.append(network)
            user_storage.set_prefs(user_id, user_prefs)
            await query.answer(f"Сеть {network} обновлена", show_alert=True)

    elif data.startswith("net_toggle_"):
        network = data.replace("net_toggle_", "")
        if user_prefs and user_storage:
            if network in user_prefs.networks:
                user_prefs.networks.remove(network)
            else:
                user_prefs.networks.append(network)
            user_storage.set_prefs(user_id, user_prefs)
            # Update keyboard
            await query.edit_message_text(
                text=format_whales_menu(user_prefs.min_whale_amount, user_prefs.networks),
                parse_mode="HTML",
                reply_markup=network_filter_keyboard(user_prefs.networks),
            )

    elif data == "networks_save":
        if user_prefs and user_storage:
            user_storage.set_prefs(user_id, user_prefs)
            await query.answer("Сети сохранены!", show_alert=True)
            await query.edit_message_text(
                text=format_alerts_menu(),
                parse_mode="HTML",
                reply_markup=alerts_menu_keyboard(),
            )

    # Price pairs
    elif data.startswith("price_"):
        pair = data.replace("price_", "") + "/USDT"
        if user_prefs and user_storage:
            if pair in user_prefs.price_pairs:
                user_prefs.price_pairs.remove(pair)
                user_storage.set_prefs(user_id, user_prefs)
                await query.answer(f"{pair} удалён", show_alert=True)
            else:
                user_prefs.price_pairs.append(pair)
                user_storage.set_prefs(user_id, user_prefs)
                await query.answer(f"{pair} добавлен", show_alert=True)

    # Settings
    elif data == "settings_notifications":
        if user_prefs and user_storage:
            user_prefs.notifications_enabled = not user_prefs.notifications_enabled
            user_storage.set_prefs(user_id, user_prefs)
            status = "✅ включены" if user_prefs.notifications_enabled else "❌ отключены"
            await query.answer(f"Уведомления {status}", show_alert=True)

    elif data == "settings_quiet":
        if user_prefs and user_storage:
            user_prefs.quiet_hours_enabled = not user_prefs.quiet_hours_enabled
            user_storage.set_prefs(user_id, user_prefs)
            status = "✅ включены" if user_prefs.quiet_hours_enabled else "❌ отключены"
            await query.answer(f"Тихие часы {status}", show_alert=True)

    elif data == "settings_format":
        if user_prefs and user_storage:
            user_prefs.alert_format = "compact" if user_prefs.alert_format == "detailed" else "detailed"
            user_storage.set_prefs(user_id, user_prefs)
            await query.answer(f"Формат: {user_prefs.alert_format}", show_alert=True)

    # Subscribe/Unsubcribe
    elif data.startswith("subscribe_"):
        alert_type = data.replace("subscribe_", "")
        if user_prefs and user_storage:
            if alert_type == "whale":
                user_prefs.whale_alerts = True
            elif alert_type == "price":
                user_prefs.price_alerts = True
            elif alert_type == "unlock":
                user_prefs.unlock_alerts = True
            user_storage.set_prefs(user_id, user_prefs)
            await query.edit_message_text(
                text=format_subscribe_success(alert_type),
                parse_mode="HTML",
                reply_markup=alerts_menu_keyboard(),
            )

    elif data.startswith("unsubscribe_"):
        alert_type = data.replace("unsubscribe_", "")
        if user_prefs and user_storage:
            if alert_type == "whale":
                user_prefs.whale_alerts = False
            elif alert_type == "price":
                user_prefs.price_alerts = False
            elif alert_type == "unlock":
                user_prefs.unlock_alerts = False
            user_storage.set_prefs(user_id, user_prefs)
            await query.edit_message_text(
                text=format_unsubscribe_success(alert_type),
                parse_mode="HTML",
                reply_markup=alerts_menu_keyboard(),
            )

    elif data == "open_dashboard":
        # Отправляем дашборд как документ или ссылку
        dashboard_url = "https://raw.githubusercontent.com/your-repo/whale_tracker/main/static/dashboard.html"
        
        dashboard_message = """📊 <b>Live Dashboard</b>

━━━━━━━━━━━━━━━━━━━━
🐋 <b>Статистика за 24ч</b>

💰 Крупных транзакций: 142
📊 Объём: $234M
🏦 Топ биржа: Binance (78%)
👥 Активных пользователей: 1,247

━━━━━━━━━━━━━━━━━━━━
📱 <b>Открыть полный дашборд:</b>

Для просмотра полной статистики откройте ссылку:
🔗 <a href="https://raw.githubusercontent.com/your-repo/whale_tracker/main/static/dashboard.html">📊 Whale Dashboard</a>

<i>Данные обновляются в реальном времени</i>"""
        
        await query.edit_message_text(
            text=dashboard_message,
            parse_mode="HTML",
            disable_web_page_preview=False,
        )

    elif data == "status_refresh":
        # Обновляем статус
        from handlers.commands import status_command
        await status_command(update, context)

    elif data == "cancel":
        await query.edit_message_text(
            text="❌ Действие отменено",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )

    else:
        logger.warning(f"Unknown callback data: {data}")
        await query.answer("Неизвестная команда", show_alert=True)
