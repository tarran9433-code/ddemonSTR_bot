"""
Message Formatters for Whale Tracker Bot
Beautiful, styled notifications for various alert types
"""

from datetime import datetime, timedelta
from typing import Optional
import config
from models import WhaleAlert, PriceAlert, Transaction, PriceData


def format_timestamp(dt: datetime) -> str:
    """Format timestamp for display"""
    now = datetime.now()
    diff = now - dt

    if diff < timedelta(minutes=1):
        return "только что"
    elif diff < timedelta(hours=1):
        mins = int(diff.total_seconds() / 60)
        return f"{mins} мин. назад"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} ч. назад"
    else:
        return dt.strftime("%d.%m.%Y %H:%M")


def truncate_address(address: str, chars: int = 6) -> str:
    """Truncate blockchain address for display"""
    if not address:
        return "Unknown"
    if len(address) <= chars * 2 + 3:
        return address
    return f"{address[:chars]}...{address[-chars:]}"


def format_amount(amount: float, symbol: str = "") -> str:
    """Format amount with appropriate suffix"""
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.2f}B"
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.2f}K"
    else:
        return f"${amount:.2f}"


def format_whale_alert(alert: WhaleAlert) -> str:
    """Format whale alert message with beautiful styling"""

    # Size emoji and label
    size_map = {
        "giant": ("🔴", "Гигантский"),
        "large": ("🟠", "Крупный"),
        "medium": ("🟡", "Средний"),
    }
    size_emoji, size_label = size_map.get(alert.size_category, ("⚪", "Обычный"))

    # Network emoji
    network_map = {
        "ethereum": "🔷",
        "tron": "🔵",
        "bsc": "🟡",
        "polygon": "🟣",
    }
    network_emoji = network_map.get(alert.transaction.blockchain, "⚪")

    # Type emoji
    type_emoji = {
        "exchange_in": "📥",
        "exchange_out": "📤",
        "internal_transfer": "🔄",
        "transfer": "↔️",
    }
    type_emoji_val = type_emoji.get(alert.alert_type, "💸")

    # Format amount
    amount_formatted = format_amount(alert.transaction.amount_usd)

    # Get explorer URL
    explorer_base = config.SUPPORTED_NETWORKS.get(
        alert.transaction.blockchain, {}
    ).get("explorer", "https://etherscan.io")
    tx_url = f"{explorer_base}/tx/{alert.transaction.tx_hash}"

    message = f"""
╔══════════════════════════════════════╗
║  🐋 КИТ 🐋  {size_emoji} {size_label}               ║
╠══════════════════════════════════════╣
║  💰 Сумма: <code>{amount_formatted}</code>
║  📊 Токен: {alert.transaction.symbol}
║  {network_emoji} Сеть: {alert.transaction.blockchain.capitalize()}
║  🕵️ От: <code>{truncate_address(alert.transaction.from_address)}</code>
║  🏛️ Кому: <code>{truncate_address(alert.transaction.to_address)}</code>
║  ⏰ Время: {format_timestamp(alert.transaction.timestamp)}
║  {type_emoji_val} Объём: {size_label}
╠══════════════════════════════════════╣
║  💡 Контекст: {alert.context or "Крупное движение"}
║  🔗 <a href="{tx_url}">Посмотреть транзакцию</a>
╚══════════════════════════════════════╝
"""
    return message


def format_price_alert(
    alert: PriceAlert,
    previous_price: Optional[float] = None
) -> str:
    """Format price alert message"""

    # Direction emoji and color
    if alert.change_percent > 0:
        direction_emoji = "📈"
        direction_text = "РОСТ"
        change_color = "🔺"
    elif alert.change_percent < 0:
        direction_emoji = "📉"
        direction_text = "ПАДЕНИЕ"
        change_color = "🔻"
    else:
        direction_emoji = "➡️"
        direction_text = "СТАБИЛЬНО"
        change_color = "⚪"

    # Volume formatting
    volume = alert.volume_24h
    if volume >= 1_000_000_000:
        volume_str = f"${volume / 1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        volume_str = f"${volume / 1_000_000:.2f}M"
    else:
        volume_str = f"${volume / 1_000:.2f}K"

    # Calculate price change if previous provided
    price_change = ""
    if previous_price:
        diff = alert.price - previous_price
        diff_sign = "+" if diff > 0 else ""
        price_change = f"\n║  📍 Изменение: {diff_sign}${diff:.2f}"

    message = f"""
╔══════════════════════════════════════╗
║  ⚡ PRICE ALERT ⚡                    ║
╠══════════════════════════════════════╣
║  📊 Пара: <code>{alert.symbol}</code>
║  {direction_emoji} Тренд: <b>{direction_text}</b>
║  💵 Цена: <code>${alert.price:,.2f}</code>
║  {change_color} Изменение: <code>{alert.change_percent:+.2f}%</code>{price_change}
║  📊 Объём 24ч: {volume_str}
║  ⏰ Время: {format_timestamp(alert.timestamp)}
╠══════════════════════════════════════╣
║  💡 Анализ: {'бычий импульс' if alert.change_percent > 2 else 'медвежий тренд' if alert.change_percent < -2 else 'боковое движение'}
╚══════════════════════════════════════╝
"""
    return message


def format_welcome_message() -> str:
    """Format welcome message"""
    return f"""
🐋 <b>Whale & Smart Alert Tracker</b> 🐋

━━━━━━━━━━━━━━━━━━━━
🎉 <b>Добро пожаловать!</b>

Я — твой персональный радар для отслеживания крупных движений на блокчейне.

<b>🌟 Что я умею:</b>
━━━━━━━━━━━━━━━━━━━━
🐋 <b>Whale Alerts</b> — мониторинг переводов китов ($100K+)
📊 <b>Price Alerts</b> — оповещения о движениях цен
🔓 <b>Token Unlocks</b> — отслеживание разлоков токенов
💰 <b>Exchange Flows</b> — анализ потоков на биржи

<b>⚡ Быстрый старт:</b>
━━━━━━━━━━━━━━━━━━━━
/alerts — настроить уведомления
/whales — пороги китов
/price — настройки цен
/status — текущий статус
/help — подробная справка

━━━━━━━━━━━━━━━━━━━━
<i>Подпишись на интересующие типы алертов и будь в курсе всех крупных движений!</i>
"""


def format_help_message() -> str:
    """Format help message"""
    return """
📖 <b>Справка по боту</b>

━━━━━━━━━━━━━━━━━━━━
<b>🧭 Основные команды:</b>
━━━━━━━━━━━━━━━━━━━━
/start — Начать работу
/help — Эта справка
/alerts — Управление подписками
/whales — Настройки китов
/price — Настройки цен
/status — Текущий статус
/settings — Общие настройки

━━━━━━━━━━━━━━━━━━━━
<b>🐋 Whale Alerts:</b>
━━━━━━━━━━━━━━━━━━━━
Отслеживаю крупные переводы ($100K+) в сетях:
• Ethereum (USDT, USDC, ETH, WBTC)
• Tron (USDT)
• BSC (USDT, BNB)
• Polygon (USDT, USDC)

<b>📊 Price Alerts:</b>
━━━━━━━━━━━━━━━━━━━━
Настрой оповещения при достижении ценой определённых уровней.

<b>🔓 Token Unlocks:</b>
━━━━━━━━━━━━━━━━━━━━
Мониторинг разлоков токенов от проектов.

<b>⚙️ Фильтры:</b>
━━━━━━━━━━━━━━━━━━━━
• Минимальная сумма перевода
• Выбор сетей
• Quiet hours (тихие часы)

━━━━━━━━━━━━━━━━━━━━
<b>💡 Советы:</b>
━━━━━━━━━━━━━━━━━━━━
• Используй /settings для общих настроек
• Настрой /whales для изменения порогов
• Включи only major для фильтрации мелких транзакций
"""


def format_status_message(
    whale_alerts_enabled: bool,
    price_alerts_enabled: bool,
    min_whale_amount: float,
    networks: list,
    active_users: int = 0,
    api_status: str = "🟢 Отлично",
    offline_cache: bool = True,
    demo_mode: bool = False
) -> str:
    """Format status message"""
    status_emoji = "🟢" if whale_alerts_enabled or price_alerts_enabled else "🔴"

    networks_str = ", ".join([n.capitalize() for n in networks])

    # Формируем строку режимов
    modes = []
    if demo_mode:
        modes.append("🎯 Демо-режим")
    if offline_cache:
        modes.append("💾 Оффлайн-кэш")
    
    modes_str = " | ".join(modes) if modes else "🟢 Реальный режим"

    return f"""
📊 <b>Статус системы</b>

━━━━━━━━━━━━━━━━━━━━
{status_emoji} <b>Мониторинг:</b>
• Whale Alerts: {'✅ Включены' if whale_alerts_enabled else '❌ Отключены'}
• Price Alerts: {'✅ Включены' if price_alerts_enabled else '❌ Отключены'}
• API Статус: {api_status}
• Активных пользователей: {active_users}

━━━━━━━━━━━━━━━━━━━━
<b>⚙️ Текущие настройки:</b>
• Мин. сумма кита: {format_amount(min_whale_amount)}
• Сети: {networks_str}
• Режимы: {modes_str}

━━━━━━━━━━━━━━━━━━━━
<b>🔗 Последняя проверка:</b>
⏰ {datetime.now().strftime('%H:%M:%S')}
"""


def format_alerts_menu() -> str:
    """Format alerts menu"""
    return """
🔔 <b>Управление подписками</b>

━━━━━━━━━━━━━━━━━━━━
Выбери типы уведомлений:

🟢 <b>Whale Alerts</b> — переводы китов
   ($100K+ в USDT, ETH, BTC)

🔵 <b>Price Alerts</b> — движения цен
   (мониторинг курса)

🟣 <b>Token Unlocks</b> — разлоки токенов
   (вестинг, team unlock)

━━━━━━━━━━━━━━━━━━━━
<i>Используй кнопки ниже для управления</i>
"""


def format_whales_menu(current_min: float, networks: list) -> str:
    """Format whales settings menu"""
    networks_str = ", ".join([n.capitalize() for n in networks])
    return f"""
🐋 <b>Настройки Whale Alerts</b>

━━━━━━━━━━━━━━━━━━━━
<b>Текущие параметры:</b>

• Мин. сумма: {format_amount(current_min)}
• Сети: {networks_str}

━━━━━━━━━━━━━━━━━━━━
<b>Выбери действие:</b>

Используй кнопки для изменения порогов или выбора сетей.
"""


def format_subscribe_success(alert_type: str) -> str:
    """Format subscription success message"""
    messages = {
        "whale": "🐋 Подписка на Whale Alerts оформлена!",
        "price": "📊 Подписка на Price Alerts оформлена!",
        "unlock": "🔓 Подписка на Token Unlocks оформлена!",
    }
    return messages.get(alert_type, "✅ Подписка оформлена!")


def format_unsubscribe_success(alert_type: str) -> str:
    """Format unsubscription success message"""
    messages = {
        "whale": "🐋 Подписка на Whale Alerts отменена.",
        "price": "📊 Подписка на Price Alerts отменена.",
        "unlock": "🔓 Подписка на Token Unlocks отменена.",
    }
    return messages.get(alert_type, "✅ Подписка отменена.")
