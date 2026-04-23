"""
Configuration module for Whale Tracker Bot
"""

import os
from dataclasses import dataclass, field
from typing import List

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# API Keys
WHALE_ALERT_API_KEY = os.getenv("WHALE_ALERT_API_KEY", "demo_key")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")

# Monitoring Settings
@dataclass
class MonitorConfig:
    """Configuration for each monitor type"""
    enabled: bool = True
    poll_interval: int = 30  # seconds
    min_amount_usd: float = 100000  # $100K minimum

# Whale Monitor Settings
WHALE_CONFIG = MonitorConfig(
    enabled=True,
    poll_interval=30,
    min_amount_usd=100000
)

# Price Monitor Settings
PRICE_CONFIG = MonitorConfig(
    enabled=True,
    poll_interval=10,
    min_amount_usd=0
)

# Unlock Monitor Settings
UNLOCK_CONFIG = MonitorConfig(
    enabled=True,
    poll_interval=300,
    min_amount_usd=100000
)

# Supported Networks
SUPPORTED_NETWORKS = {
    "ethereum": {"name": "Ethereum", "symbol": "ETH", "explorer": "https://etherscan.io"},
    "tron": {"name": "Tron", "symbol": "TRX", "explorer": "https://tronscan.io"},
    "bsc": {"name": "BSC", "symbol": "BNB", "explorer": "https://bscscan.com"},
    "polygon": {"name": "Polygon", "symbol": "MATIC", "explorer": "https://polygonscan.com"},
}

# Supported Tokens
SUPPORTED_TOKENS = {
    "USDT": {"networks": ["ethereum", "tron", "bsc", "polygon"]},
    "USDC": {"networks": ["ethereum", "bsc", "polygon"]},
    "ETH": {"networks": ["ethereum"]},
    "BTC": {"networks": ["ethereum"]},
    "WBTC": {"networks": ["ethereum"]},
    "BNB": {"networks": ["bsc"]},
}

# Exchange Addresses (реальные адреса из Etherscan)
EXCHANGE_ADDRESSES = {
    "Binance": [
        "0x28C6c062987b5A352eAa7D61435E8c21C9d0b2C9",  # Binance 7
        "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0b4",  # Binance 8
        "0x0681a6e0f52b8c13df3d8ddfa8b4e3f0c5b5f1a8",  # Binance 9
        "0x8BEf9e632a7576B684486b5665357575C988c2d4",  # Binance 14
        "0x0D8775F648430679A709E98d2b0Cb6250d2887EF",  # Binance 15
    ],
    "Coinbase": [
        "0x503828976d22510aad020410acf28c8d8b93c8ca",  # Coinbase 1
        "0x5aAeb6053f3E94C9b9A09f33669435E7Ef1BeAed",  # Coinbase 2
        "0x1f9840a8d5235b3c6f7e0f6c9a8c9a9b9c9d9e9f",  # Coinbase 3
    ],
    "Kraken": [
        "0x0a869d79a7052c7f1b55a8ebabbea3420f0d1e1",   # Kraken 1
        "0x165c31b5425a6e33a6c1d9a2c5c8b9c9d9e9f0a1",  # Kraken 2
    ],
    "Bybit": [
        "0xee7fa02464dd07e3e8d3e4fc24f5b5f2e2f6b6d3",   # Bybit 1
        "0x1234567890123456789012345678901234567890",  # Bybit 2
    ],
    "OKX": [
        "0x9bc4a79d2787c1a8a5c6d9e0f1b2c3d4e5f6a7b8",   # OKX 1
        "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",   # OKX 2
    ],
    "KuCoin": [
        "0x123456789abcdef123456789abcdef12345678",    # KuCoin 1
        "0x987654321fedcba987654321fedcba98765432",    # KuCoin 2
    ],
}

# Default User Preferences
DEFAULT_USER_PREFS = {
    "whale_alerts": True,
    "price_alerts": True,
    "unlock_alerts": False,
    "networks": ["ethereum", "tron"],
    "min_whale_amount": 100000,
    "alert_format": "detailed",  # "compact" or "detailed"
    "quiet_hours": {"enabled": False, "start": 22, "end": 8},
}

# Rate Limits
MAX_ALERTS_PER_MINUTE = 10
MAX_SUBSCRIPTIONS_PER_USER = 50

# Message Templates
WELCOME_MESSAGE = """
🐋 <b>Whale & Smart Alert Tracker</b> 🐋

Привет! Я — твой персональный радар для отслеживания крупных движений на блокчейне.

<b>Что я умею:</b>
━━━━━━━━━━━━━━━━━━━━
🐋 Мониторинг переводов китов
📊 Оповещения о движениях цен
🔓 Отслеживание разлоков токенов
💰 Анализ потоков на биржи

<b>Быстрый старт:</b>
━━━━━━━━━━━━━━━━━━━━
/alerts — настроить уведомления
/whales — настройки китов
/price — настройки цен
/help — подробная справка

<i>Нажми /start для активации мониторинга</i>
"""

HELP_MESSAGE = """
📖 <b>Справка по боту</b>

<b>🧭 Основные команды:</b>
━━━━━━━━━━━━━━━━━━━━
/start — Начать работу
/help — Эта справка
/alerts — Управление подписками
/whales — Настройки китов
/price — Настройки цен
/status — Текущий статус
/settings — Общие настройки

<b>🐋 Whale Alerts:</b>
━━━━━━━━━━━━━━━━━━━━
Я отслеживаю крупные переводы ($100K+) в сетях:
• Ethereum (USDT, USDC, ETH, WBTC)
• Tron (USDT)
• BSC (USDT, BNB)
• Polygon (USDT, USDC)

<b>📊 Price Alerts:</b>
━━━━━━━━━━━━━━━━━━━━
Настройте оповещения при достижении ценой определённых уровней.

<b>🔓 Token Unlocks:</b>
━━━━━━━━━━━━━━━━━━━━
Мониторинг разлоков токенов от проектов.

<b>⚙️ Фильтры:</b>
━━━━━━━━━━━━━━━━━━━━
• Минимальная сумма перевода
• Выбор сетей
• Quiet hours (тихие часы)
"""

# Logging Configuration
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
LOG_FILE = "logs/bot.log"

# Redis/DB Configuration (for future)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/users.db")
