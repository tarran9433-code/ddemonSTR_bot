"""
Utility helpers for the bot
"""

from datetime import datetime
from typing import Optional
import re


def format_number(num: float, decimals: int = 2) -> str:
    """Format number with thousand separators"""
    return f"{num:,.{decimals}f}".replace(",", " ")


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount"""
    if currency == "USD":
        if amount >= 1_000_000_000:
            return f"${amount / 1_000_000_000:.2f}B"
        elif amount >= 1_000_000:
            return f"${amount / 1_000_000:.2f}M"
        elif amount >= 1_000:
            return f"${amount / 1_000:.2f}K"
        else:
            return f"${amount:.2f}"
    return f"{amount:.2f} {currency}"


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def is_valid_address(address: str, blockchain: str = "ethereum") -> bool:
    """Validate blockchain address format"""
    if blockchain == "ethereum":
        # Ethereum addresses: 0x followed by 40 hex characters
        pattern = r"^0x[a-fA-F0-9]{40}$"
    elif blockchain == "tron":
        # Tron addresses: starts with T, 34 characters
        pattern = r"^T[a-zA-Z0-9]{33}$"
    else:
        return len(address) > 10

    return bool(re.match(pattern, address))


def parse_amount(text: str) -> Optional[float]:
    """Parse amount from text (e.g., '1.5M', '100K', '1000000')"""
    text = text.upper().strip().replace(",", "").replace(" ", "")

    multipliers = {
        "K": 1_000,
        "M": 1_000_000,
        "B": 1_000_000_000,
    }

    for suffix, multiplier in multipliers.items():
        if suffix in text:
            try:
                num = float(text.replace(suffix, ""))
                return num * multiplier
            except ValueError:
                return None

    try:
        return float(text)
    except ValueError:
        return None


def get_time_ago(dt: datetime) -> str:
    """Get human-readable time ago string"""
    from datetime import timedelta

    now = datetime.now()
    diff = now - dt

    if diff < timedelta(seconds=10):
        return "только что"
    elif diff < timedelta(minutes=1):
        return f"{int(diff.total_seconds())} сек. назад"
    elif diff < timedelta(hours=1):
        mins = int(diff.total_seconds() / 60)
        return f"{mins} мин. назад"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} ч. назад"
    elif diff < timedelta(days=7):
        days = int(diff.total_seconds() / 86400)
        return f"{days} дн. назад"
    else:
        return dt.strftime("%d.%m.%Y")


def get_network_explorer_url(blockchain: str, address: str = "") -> str:
    """Get explorer URL for blockchain"""
    explorers = {
        "ethereum": "https://etherscan.io",
        "tron": "https://tronscan.io",
        "bsc": "https://bscscan.com",
        "polygon": "https://polygonscan.com",
        "solana": "https://solscan.io",
    }

    base_url = explorers.get(blockchain, "https://etherscan.io")

    if address:
        if blockchain == "tron":
            return f"{base_url}/address/{address}"
        else:
            return f"{base_url}/address/{address}"

    return base_url


def sanitize_markdown(text: str) -> str:
    """Remove or escape problematic markdown characters"""
    # Characters that need escaping in Markdown
    problematic = ["_", "*", "~", "`", ">", "[", "]", "(", ")", "#", "+", "-", ".", "!"]
    for char in problematic:
        text = text.replace(char, f"\\{char}")
    return text


def identify_exchange(address: str) -> tuple[str, str]:
    """
    Определяет биржу по адресу кошелька
    
    Returns:
        tuple: (exchange_name, address_type) 
        address_type: "hot_wallet", "cold_wallet", "unknown"
    """
    import config
    
    address = address.lower()
    
    for exchange, addresses in config.EXCHANGE_ADDRESSES.items():
        for exchange_addr in addresses:
            if exchange_addr.lower() == address:
                # Определяем тип кошелька по номеру
                if "hot" in exchange_addr.lower() or len(exchange_addr) > 20:
                    return exchange, "hot_wallet"
                else:
                    return exchange, "cold_wallet"
    
    return "Unknown", "unknown"


def format_address_display(address: str, exchange_info: tuple = None) -> str:
    """
    Форматирует адрес для отображения с подсветкой биржи
    
    Args:
        address: адрес кошелька
        exchange_info: (exchange_name, address_type) из identify_exchange
    """
    if exchange_info is None:
        exchange_info = identify_exchange(address)
    
    exchange_name, address_type = exchange_info
    
    # Сокращаем адрес для отображения
    if len(address) > 10:
        short_addr = f"{address[:6]}...{address[-4:]}"
    else:
        short_addr = address
    
    # Добавляем подсветку биржи
    if exchange_name != "Unknown":
        exchange_emoji = {
            "Binance": "🟡",
            "Coinbase": "🔵", 
            "Kraken": "🔴",
            "Bybit": "🟠",
            "OKX": "⚫",
            "KuCoin": "🟢"
        }.get(exchange_name, "🏦")
        
        return f"{exchange_emoji} {exchange_name} ({short_addr})"
    else:
        return f"📍 {short_addr}"


def parse_command_args(text: str) -> dict:
    """Parse command arguments from text"""
    parts = text.strip().split()
    args = {}

    # Common argument patterns
    for i, part in enumerate(parts[1:], 1):
        if part.startswith("--"):
            key = part[2:].split("=")[0]
            value = part[2:].split("=")[1] if "=" in part else parts[i + 1] if i + 1 < len(parts) else "true"
            args[key] = value

    return args


class RateLimiter:
    """Simple rate limiter for alerts"""

    def __init__(self, max_per_minute: int = 10):
        self.max_per_minute = max_per_minute
        self._timestamps: list = []

    def is_allowed(self) -> bool:
        """Check if new action is allowed"""
        from datetime import datetime, timedelta

        now = datetime.now()
        cutoff = now - timedelta(minutes=1)

        # Remove old timestamps
        self._timestamps = [ts for ts in self._timestamps if ts > cutoff]

        if len(self._timestamps) >= self.max_per_minute:
            return False

        self._timestamps.append(now)
        return True

    def wait_time(self) -> float:
        """Get seconds to wait before next action"""
        if not self._timestamps:
            return 0

        from datetime import datetime, timedelta

        oldest = min(self._timestamps)
        cutoff = oldest + timedelta(minutes=1)
        now = datetime.now()

        if now >= cutoff:
            return 0

        return (cutoff - now).total_seconds()
