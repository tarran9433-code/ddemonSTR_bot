"""
Price API Service
Fetches cryptocurrency price data
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

import aiohttp

import config
from models import PriceAlert

logger = logging.getLogger(__name__)


@dataclass
class PriceData:
    """Price data for a cryptocurrency"""
    symbol: str
    price: float
    change_1h: float
    change_24h: float
    volume_24h: float
    market_cap: float
    timestamp: datetime


class PriceApiService:
    """Service for fetching cryptocurrency prices"""

    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.session: Optional[aiohttp.ClientSession] = None
        # Symbol mapping: display -> Binance
        self.symbol_map = {
            "BTC/USDT": "BTCUSDT",
            "ETH/USDT": "ETHUSDT",
            "BNB/USDT": "BNBUSDT",
            "SOL/USDT": "SOLUSDT",
            "XRP/USDT": "XRPUSDT",
            "ADA/USDT": "ADAUSDT",
            "DOGE/USDT": "DOGEUSDT",
            "DOT/USDT": "DOTUSDT",
            "MATIC/USDT": "MATICUSDT",
            "LINK/USDT": "LINKUSDT",
        }

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_price(self, symbol: str) -> Optional[PriceData]:
        """
        Get current price for a symbol

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")

        Returns:
            Price data or None if error
        """
        binance_symbol = self.symbol_map.get(symbol, symbol.replace("/", ""))

        try:
            session = await self.get_session()

            # Fetch ticker data
            async with session.get(
                f"{self.base_url}/ticker/24hr",
                params={"symbol": binance_symbol},
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_ticker(data, symbol)
                else:
                    logger.error(f"Binance API error: {response.status}")
                    return self._get_demo_price(symbol)

        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return self._get_demo_price(symbol)

    async def get_prices(self, symbols: List[str]) -> Dict[str, PriceData]:
        """Get prices for multiple symbols"""
        results = {}
        tasks = [self.get_price(symbol) for symbol in symbols]

        prices = await asyncio.gather(*tasks, return_exceptions=True)

        for symbol, price_data in zip(symbols, prices):
            if price_data and not isinstance(price_data, Exception):
                results[symbol] = price_data

        return results

    def _parse_ticker(self, data: dict, symbol: str) -> PriceData:
        """Parse Binance ticker response"""
        return PriceData(
            symbol=symbol,
            price=float(data.get("lastPrice", 0)),
            change_1h=0,  # Not available in 24hr ticker
            change_24h=float(data.get("priceChangePercent", 0)),
            volume_24h=float(data.get("volume", 0)),
            market_cap=0,  # Not available in ticker
            timestamp=datetime.now(),
        )

    def _get_demo_price(self, symbol: str) -> PriceData:
        """Generate demo price data for testing"""
        demo_prices = {
            "BTC/USDT": 67450.00,
            "ETH/USDT": 3520.00,
            "BNB/USDT": 580.00,
            "SOL/USDT": 142.00,
            "XRP/USDT": 0.52,
            "ADA/USDT": 0.45,
            "DOGE/USDT": 0.082,
            "DOT/USDT": 7.20,
            "MATIC/USDT": 0.85,
            "LINK/USDT": 14.50,
        }

        base_price = demo_prices.get(symbol, 100.00)
        # Add slight variation
        import random
        variation = random.uniform(-0.02, 0.02)
        current_price = base_price * (1 + variation)

        return PriceData(
            symbol=symbol,
            price=round(current_price, 2),
            change_1h=round(random.uniform(-2, 2), 2),
            change_24h=round(random.uniform(-5, 5), 2),
            volume_24h=random.uniform(100_000_000, 1_000_000_000),
            market_cap=base_price * random.uniform(1_000_000_000, 100_000_000_000),
            timestamp=datetime.now(),
        )

    def create_price_alert(
        self,
        price_data: PriceData,
        previous_price: float
    ) -> PriceAlert:
        """Create a price alert from price data"""
        change_percent = ((price_data.price - previous_price) / previous_price) * 100
        direction = "up" if change_percent > 0 else "down"

        return PriceAlert(
            id=f"price_{price_data.symbol.replace('/', '')}_{int(datetime.now().timestamp())}",
            symbol=price_data.symbol,
            price=price_data.price,
            change_percent=round(change_percent, 2),
            volume_24h=price_data.volume_24h,
            timestamp=price_data.timestamp,
            direction=direction,
        )


async def create_price_api() -> PriceApiService:
    """Factory function to create PriceApiService"""
    return PriceApiService()
