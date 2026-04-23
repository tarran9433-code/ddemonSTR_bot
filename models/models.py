"""
Data models for the Whale Tracker Bot
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum
import json


class AlertType(Enum):
    """Types of alerts supported by the bot"""
    WHALE_TRANSFER = "whale_transfer"
    PRICE_CHANGE = "price_change"
    TOKEN_UNLOCK = "token_unlock"
    EXCHANGE_FLOW = "exchange_flow"


class Network(Enum):
    """Supported blockchain networks"""
    ETHEREUM = "ethereum"
    TRON = "tron"
    BSC = "bsc"
    POLYGON = "polygon"
    SOLANA = "solana"
    AVALANCHE = "avalanche"


@dataclass
class Transaction:
    """Represents a blockchain transaction"""
    tx_hash: str
    blockchain: str
    symbol: str
    amount: float
    amount_usd: float
    from_address: str
    to_address: str
    timestamp: datetime
    confirmed: bool = True

    def to_dict(self) -> dict:
        return {
            "tx_hash": self.tx_hash,
            "blockchain": self.blockchain,
            "symbol": self.symbol,
            "amount": self.amount,
            "amount_usd": self.amount_usd,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "timestamp": self.timestamp.isoformat(),
            "confirmed": self.confirmed,
        }


@dataclass
class WhaleAlert:
    """Represents a whale alert"""
    id: str
    transaction: Transaction
    alert_type: str  # "transfer", "exchange_in", "exchange_out"
    size_category: str  # "medium", "large", "giant"
    context: Optional[str] = None

    def __post_init__(self):
        if self.transaction.amount_usd >= 10_000_000:
            self.size_category = "giant"
        elif self.transaction.amount_usd >= 1_000_000:
            self.size_category = "large"
        else:
            self.size_category = "medium"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "transaction": self.transaction.to_dict(),
            "alert_type": self.alert_type,
            "size_category": self.size_category,
            "context": self.context,
        }


@dataclass
class PriceAlert:
    """Represents a price alert"""
    id: str
    symbol: str
    price: float
    change_percent: float
    volume_24h: float
    timestamp: datetime
    direction: str  # "up", "down"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "price": self.price,
            "change_percent": self.change_percent,
            "volume_24h": self.volume_24h,
            "timestamp": self.timestamp.isoformat(),
            "direction": self.direction,
        }


@dataclass
class UserPreferences:
    """User preferences and settings"""
    user_id: int
    whale_alerts: bool = True
    price_alerts: bool = True
    unlock_alerts: bool = False
    networks: List[str] = field(default_factory=lambda: ["ethereum", "tron"])
    min_whale_amount: float = 100_000
    price_pairs: List[str] = field(default_factory=lambda: ["BTC/USDT", "ETH/USDT"])
    alert_format: str = "detailed"
    quiet_hours_enabled: bool = False
    quiet_hours_start: int = 22  # 10 PM
    quiet_hours_end: int = 8     # 8 AM
    notifications_enabled: bool = True

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "whale_alerts": self.whale_alerts,
            "price_alerts": self.price_alerts,
            "unlock_alerts": self.unlock_alerts,
            "networks": self.networks,
            "min_whale_amount": self.min_whale_amount,
            "price_pairs": self.price_pairs,
            "alert_format": self.alert_format,
            "quiet_hours_enabled": self.quiet_hours_enabled,
            "quiet_hours_start": self.quiet_hours_start,
            "quiet_hours_end": self.quiet_hours_end,
            "notifications_enabled": self.notifications_enabled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserPreferences":
        """Create UserPreferences from dictionary"""
        return cls(
            user_id=data.get("user_id", 0),
            whale_alerts=data.get("whale_alerts", True),
            price_alerts=data.get("price_alerts", True),
            unlock_alerts=data.get("unlock_alerts", False),
            networks=data.get("networks", ["ethereum", "tron"]),
            min_whale_amount=data.get("min_whale_amount", 100_000),
            price_pairs=data.get("price_pairs", ["BTC/USDT", "ETH/USDT"]),
            alert_format=data.get("alert_format", "detailed"),
            quiet_hours_enabled=data.get("quiet_hours_enabled", False),
            quiet_hours_start=data.get("quiet_hours_start", 22),
            quiet_hours_end=data.get("quiet_hours_end", 8),
            notifications_enabled=data.get("notifications_enabled", True),
        )

    def is_quiet_time(self) -> bool:
        """Check if current time is in quiet hours"""
        if not self.quiet_hours_enabled:
            return False

        current_hour = datetime.now().hour

        if self.quiet_hours_start < self.quiet_hours_end:
            # Normal range (e.g., 22-23)
            return self.quiet_hours_start <= current_hour < self.quiet_hours_end
        else:
            # Overnight range (e.g., 22-08)
            return current_hour >= self.quiet_hours_start or current_hour < self.quiet_hours_end


@dataclass
class Subscription:
    """User subscription for specific alerts"""
    user_id: int
    alert_type: AlertType
    params: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = True

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "alert_type": self.alert_type.value,
            "params": self.params,
            "created_at": self.created_at.isoformat(),
            "active": self.active,
        }


@dataclass
class PriceData:
    """Represents price data for a token"""
    symbol: str
    price: float
    change_24h: float
    change_1h: float
    volume_24h: float
    market_cap: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "change_24h": self.change_24h,
            "change_1h": self.change_1h,
            "volume_24h": self.volume_24h,
            "market_cap": self.market_cap,
            "timestamp": self.timestamp.isoformat(),
        }


class AlertHistory:
    """In-memory storage for alert history"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.alerts: List[dict] = []

    def add(self, alert: dict):
        """Add an alert to history"""
        self.alerts.append({
            "timestamp": datetime.now().isoformat(),
            **alert
        })

        # Trim if needed
        if len(self.alerts) > self.max_size:
            self.alerts = self.alerts[-self.max_size:]

    def get_recent(self, limit: int = 20) -> List[dict]:
        """Get recent alerts"""
        return self.alerts[-limit:]

    def clear(self):
        """Clear all alerts"""
        self.alerts = []

    def save_to_file(self, filepath: str):
        """Save history to file"""
        with open(filepath, "w") as f:
            json.dump(self.alerts, f, indent=2)

    def load_from_file(self, filepath: str):
        """Load history from file"""
        try:
            with open(filepath, "r") as f:
                self.alerts = json.load(f)
        except FileNotFoundError:
            self.alerts = []
