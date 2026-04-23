"""
Inline keyboard builders for the bot
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

import config


def main_menu_keyboard():
    """Main menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🐋 Whale Alerts", callback_data="menu_whales"),
            InlineKeyboardButton("📊 Price Alerts", callback_data="menu_price"),
        ],
        [
            InlineKeyboardButton("🔓 Token Unlocks", callback_data="menu_unlocks"),
            InlineKeyboardButton("⚙️ Настройки", callback_data="menu_settings"),
        ],
        [
            InlineKeyboardButton("📖 Справка", callback_data="menu_help"),
            InlineKeyboardButton("🧪 Тест", callback_data="menu_test"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def alerts_menu_keyboard():
    """Alerts subscription keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🐋 Whale Alerts", callback_data="toggle_whale"),
        ],
        [
            InlineKeyboardButton("📊 Price Alerts", callback_data="toggle_price"),
        ],
        [
            InlineKeyboardButton("🔓 Token Unlocks", callback_data="toggle_unlock"),
        ],
        [
            InlineKeyboardButton("🔙 Назад", callback_data="menu_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def whales_menu_keyboard():
    """Whale alerts settings keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("💰 $100K", callback_data="whale_100k"),
            InlineKeyboardButton("💰 $500K", callback_data="whale_500k"),
            InlineKeyboardButton("💰 $1M", callback_data="whale_1m"),
        ],
        [
            InlineKeyboardButton("🔷 Ethereum", callback_data="net_ethereum"),
            InlineKeyboardButton("🔵 Tron", callback_data="net_tron"),
        ],
        [
            InlineKeyboardButton("🟡 BSC", callback_data="net_bsc"),
            InlineKeyboardButton("🟣 Polygon", callback_data="net_polygon"),
        ],
        [
            InlineKeyboardButton("🔙 Назад", callback_data="menu_alerts"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def price_menu_keyboard():
    """Price alerts settings keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("₿ BTC/USDT", callback_data="price_BTC"),
            InlineKeyboardButton("Ξ ETH/USDT", callback_data="price_ETH"),
        ],
        [
            InlineKeyboardButton("🔷 BNB/USDT", callback_data="price_BNB"),
            InlineKeyboardButton("🌙 SOL/USDT", callback_data="price_SOL"),
        ],
        [
            InlineKeyboardButton("🔙 Назад", callback_data="menu_alerts"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def settings_menu_keyboard():
    """General settings keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("📱 Уведомления", callback_data="settings_notifications"),
        ],
        [
            InlineKeyboardButton("🌙 Тихие часы", callback_data="settings_quiet"),
        ],
        [
            InlineKeyboardButton("📝 Формат сообщений", callback_data="settings_format"),
        ],
        [
            InlineKeyboardButton("🔙 Назад", callback_data="menu_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def confirm_keyboard(action: str):
    """Confirmation keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_{action}"),
            InlineKeyboardButton("❌ Отмена", callback_data="cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def network_filter_keyboard(selected_networks: list):
    """Network filter selection keyboard"""
    all_networks = ["ethereum", "tron", "bsc", "polygon"]
    network_emojis = {
        "ethereum": "🔷",
        "tron": "🔵",
        "bsc": "🟡",
        "polygon": "🟣",
    }

    keyboard = []
    row = []

    for i, network in enumerate(all_networks):
        emoji = network_emojis.get(network, "⚪")
        selected = "✅" if network in selected_networks else "⬜"
        row.append(
            InlineKeyboardButton(
                f"{emoji} {selected}",
                callback_data=f"net_toggle_{network}"
            )
        )

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("💾 Сохранить", callback_data="networks_save"),
        InlineKeyboardButton("🔙 Отмена", callback_data="menu_whales"),
    ])

    return InlineKeyboardMarkup(keyboard)


def amount_filter_keyboard(current_min: float):
    """Amount threshold selection keyboard"""
    amounts = [
        (100000, "$100K"),
        (250000, "$250K"),
        (500000, "$500K"),
        (1000000, "$1M"),
        (5000000, "$5M"),
        (10000000, "$10M"),
    ]

    keyboard = []
    row = []

    for value, label in amounts:
        selected = "✅" if abs(current_min - value) < 1000 else "⬜"
        row.append(
            InlineKeyboardButton(
                f"{selected} {label}",
                callback_data=f"amount_set_{int(value)}"
            )
        )

        if len(row) == 3:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("🔙 Назад", callback_data="menu_whales"),
    ])

    return InlineKeyboardMarkup(keyboard)


def subscribe_confirmation_keyboard(alert_type: str):
    """Subscribe confirmation keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Включить", callback_data=f"subscribe_{alert_type}"),
            InlineKeyboardButton("❌ Отключить", callback_data=f"unsubscribe_{alert_type}"),
        ],
        [
            InlineKeyboardButton("🔙 Назад", callback_data="menu_alerts"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def status_keyboard():
    """Status page keyboard with dashboard button"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Дашборд", callback_data="open_dashboard"),
        ],
        [
            InlineKeyboardButton("🔄 Обновить", callback_data="status_refresh"),
            InlineKeyboardButton("🧪 Тест", callback_data="menu_test"),
        ],
        [
            InlineKeyboardButton("🔙 Главное меню", callback_data="menu_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
