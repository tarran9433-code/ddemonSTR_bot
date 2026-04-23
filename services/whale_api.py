"""
Whale Alert API Service
Fetches whale transaction data from various sources
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

import aiohttp

import config
from models import Transaction, WhaleAlert, AlertType

logger = logging.getLogger(__name__)


@dataclass
class WhaleTransaction:
    """Raw whale transaction from API"""
    blockchain: str
    symbol: str
    amount: float
    amount_usd: float
    from_address: str
    to_address: str
    timestamp: int  # Unix timestamp
    tx_hash: str


class WhaleApiService:
    """Service for fetching whale transactions"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.WHALE_ALERT_API_KEY
        self.base_url = "https://api.whale-alert.io/v1"
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_recent_transactions(
        self,
        min_value: float = 100000,
        symbols: List[str] = None
    ) -> List[WhaleTransaction]:
        """
        Fetch recent whale transactions

        Args:
            min_value: Minimum USD value
            symbols: List of symbols to filter (default: all)

        Returns:
            List of whale transactions
        """
        if symbols is None:
            symbols = list(config.SUPPORTED_TOKENS.keys())

        try:
            session = await self.get_session()
            params = {
                "key": self.api_key,
                "min_value": min_value,
                "symbols": ",".join(symbols),
            }

            async with session.get(
                f"{self.base_url}/transactions",
                params=params,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_transactions(data)
                elif response.status == 401:
                    logger.warning("Invalid API key, using demo data")
                    return self._get_demo_transactions()
                else:
                    logger.error(f"API error: {response.status}")
                    return []

        except asyncio.TimeoutError:
            logger.error("Whale Alert API timeout")
            return self._get_demo_transactions()
        except Exception as e:
            logger.error(f"Error fetching transactions: {e}")
            return self._get_demo_transactions()

    def _parse_transactions(self, data: dict) -> List[WhaleTransaction]:
        """Parse API response into WhaleTransaction objects"""
        transactions = []

        for tx in data.get("transactions", []):
            try:
                transactions.append(WhaleTransaction(
                    blockchain=tx.get("blockchain", "unknown"),
                    symbol=tx.get("symbol", "unknown"),
                    amount=tx.get("amount", 0),
                    amount_usd=tx.get("amount_usd", 0),
                    from_address=tx.get("from", {}).get("address", ""),
                    to_address=tx.get("to", {}).get("address", ""),
                    timestamp=tx.get("timestamp", 0),
                    tx_hash=tx.get("hash", ""),
                ))
            except Exception as e:
                logger.warning(f"Failed to parse transaction: {e}")

        return transactions

    def _get_demo_transactions(self) -> List[WhaleTransaction]:
        """Generate demo transactions for testing"""
        return [
            WhaleTransaction(
                blockchain="ethereum",
                symbol="USDT",
                amount=2_500_000,
                amount_usd=2_500_000,
                from_address="0x7a25e8d4e54c8b13df3d8ddfa8b4e3f0c5b5f1a8",
                to_address="0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0b4",
                timestamp=int(datetime.now().timestamp()),
                tx_hash="0x8a7c3b2e1d9f0c5a6b4e3f2d1c0b9a8e7f6d5c4b3a2918273645506172",
            ),
            WhaleTransaction(
                blockchain="tron",
                symbol="USDT",
                amount=5_000_000,
                amount_usd=5_000_000,
                from_address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
                to_address="TMuA6YqfCeX8EhbfYEg5y7S4DqzSJireY9",
                timestamp=int(datetime.now().timestamp()),
                tx_hash="a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0",
            ),
            WhaleTransaction(
                blockchain="ethereum",
                symbol="ETH",
                amount=500,
                amount_usd=1_250_000,
                from_address="0x28c6c06298d514db2099347b5b495eabfb9f5a8",
                to_address="0x21a31ee1afc51d94c2efccaa2092ad1028285549",
                timestamp=int(datetime.now().timestamp()),
                tx_hash="0x1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a",
            ),
        ]

    @staticmethod
    def is_exchange_address(address: str) -> Optional[str]:
        """Check if address belongs to known exchange"""
        address_lower = address.lower()

        for exchange, addresses in config.EXCHANGE_ADDRESSES.items():
            for addr in addresses:
                if addr.lower() == address_lower:
                    return exchange

        # Simple heuristics for exchange addresses
        if "binance" in address_lower or "0x3f5c" in address_lower:
            return "Binance"
        if "coinbase" in address_lower or "0x503" in address_lower:
            return "Coinbase"

        return None

    def get_alert_context(self, tx: WhaleTransaction) -> str:
        """Generate human-readable context for transaction"""
        from_exchange = self.is_exchange_address(tx.from_address)
        to_exchange = self.is_exchange_address(tx.to_address)

        if from_exchange and to_exchange:
            return f"Перевод между биржами ({from_exchange} → {to_exchange})"
        elif from_exchange:
            return f"Крупный вывод с {from_exchange}"
        elif to_exchange:
            return f"Крупный депозит на {to_exchange}"
        else:
            return "Крупный перевод между кошельками"

    def transactions_to_alerts(
        self,
        transactions: List[WhaleTransaction]
    ) -> List[WhaleAlert]:
        """Convert transactions to WhaleAlert objects"""
        alerts = []

        for tx in transactions:
            alert_type = "transfer"

            # Determine alert type based on addresses
            from_exchange = self.is_exchange_address(tx.from_address)
            to_exchange = self.is_exchange_address(tx.to_address)

            if from_exchange and to_exchange:
                alert_type = "internal_transfer"
            elif from_exchange:
                alert_type = "exchange_out"
            elif to_exchange:
                alert_type = "exchange_in"

            transaction = Transaction(
                tx_hash=tx.tx_hash,
                blockchain=tx.blockchain,
                symbol=tx.symbol,
                amount=tx.amount,
                amount_usd=tx.amount_usd,
                from_address=tx.from_address,
                to_address=tx.to_address,
                timestamp=datetime.fromtimestamp(tx.timestamp),
            )

            alert = WhaleAlert(
                id=f"whale_{tx.tx_hash[:16]}",
                transaction=transaction,
                alert_type=alert_type,
                size_category="giant" if tx.amount_usd >= 10_000_000 else "large" if tx.amount_usd >= 1_000_000 else "medium",
                context=self.get_alert_context(tx),
            )

            alerts.append(alert)

        return alerts


async def create_whale_api() -> WhaleApiService:
    """Factory function to create WhaleApiService"""
    return WhaleApiService()
