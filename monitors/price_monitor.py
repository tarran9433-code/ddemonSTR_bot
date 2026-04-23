"""
Price Monitor — Real-time cryptocurrency price monitoring
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional, List
from telegram.ext import Application

import config
from models import PriceAlert, UserPreferences
from services.price_api import PriceApiService, PriceData, create_price_api
from services.formatters import format_price_alert

logger = logging.getLogger(__name__)


class PriceMonitor:
    """Real-time cryptocurrency price monitor"""

    def __init__(self, app: Application):
        self.app = app
        self.api: Optional[PriceApiService] = None
        self.running = False
        self.last_prices: Dict[str, float] = {}  # Store last known prices
        self.last_alert_prices: Dict[str, float] = {}  # Store prices at last alert
        self.user_storage = None  # Will be set by bot
        self._task: Optional[asyncio.Task] = None

        # Price change thresholds (percentage)
        self.alert_threshold_percent = 2.0  # Alert on 2%+ changes

        # Default pairs to monitor
        self.default_pairs = ["BTC/USDT", "ETH/USDT"]

    def set_user_storage(self, storage):
        """Set user storage reference"""
        self.user_storage = storage

    async def start(self):
        """Start the price monitor"""
        self.running = True
        self.api = await create_price_api()
        logger.info("PriceMonitor: Started")

        # Initial price fetch
        await self._fetch_initial_prices()

        # Run monitoring loop
        while self.running:
            try:
                await self._check_for_price_changes()
            except Exception as e:
                logger.error(f"PriceMonitor: Error in loop: {e}")

            # Wait before next check
            await asyncio.sleep(config.PRICE_CONFIG.poll_interval)

    async def stop(self):
        """Stop the price monitor"""
        self.running = False
        if self._task:
            self._task.cancel()

        if self.api:
            await self.api.close()

        logger.info("PriceMonitor: Stopped")

    async def _fetch_initial_prices(self):
        """Fetch initial prices for all pairs"""
        prices = await self.api.get_prices(self.default_pairs)

        for symbol, price_data in prices.items():
            self.last_prices[symbol] = price_data.price
            self.last_alert_prices[symbol] = price_data.price

        logger.info(f"PriceMonitor: Initial prices fetched: {list(prices.keys())}")

    async def _check_for_price_changes(self):
        """Check for significant price changes"""
        if not self.api:
            return

        # Get current prices
        prices = await self.api.get_prices(self.default_pairs)

        for symbol, price_data in prices.items():
            previous_price = self.last_prices.get(symbol)

            if previous_price is None:
                self.last_prices[symbol] = price_data.price
                continue

            # Calculate percentage change
            change_percent = abs(
                ((price_data.price - previous_price) / previous_price) * 100
            )

            # Check if significant change
            if change_percent >= self.alert_threshold_percent:
                # Check if we already alerted at similar level
                last_alert_price = self.last_alert_prices.get(symbol, 0)
                alert_threshold = self.last_alert_prices.get(f"{symbol}_threshold", 0)

                # Only alert if change since last alert is significant
                if abs(price_data.price - last_alert_price) / last_alert_price * 100 >= self.alert_threshold_percent:
                    await self._send_price_alert(price_data, previous_price)
                    self.last_alert_prices[symbol] = price_data.price
                    self.last_alert_prices[f"{symbol}_threshold"] = self.alert_threshold_percent

            # Update last known price
            self.last_prices[symbol] = price_data.price

    async def _send_price_alert(
        self,
        price_data: PriceData,
        previous_price: float
    ):
        """Send price alert to all subscribed users"""
        # Create price alert
        alert = self.api.create_price_alert(price_data, previous_price)
        formatted_message = format_price_alert(alert, previous_price)

        if not self.user_storage:
            logger.warning("PriceMonitor: User storage not set")
            return

        # Get all users with price alerts enabled
        user_ids = self.user_storage.get_all_user_ids()

        for user_id in user_ids:
            prefs = self.user_storage.get_prefs(user_id)

            # Skip if price alerts disabled
            if not prefs.price_alerts:
                continue

            # Skip if quiet time
            if prefs.is_quiet_time():
                continue

            # Check if pair is in user's subscriptions
            if alert.symbol not in prefs.price_pairs:
                continue

            try:
                await self.app.bot.send_message(
                    chat_id=user_id,
                    text=formatted_message,
                    parse_mode="HTML",
                )
                logger.info(f"PriceMonitor: Sent alert to {user_id}")
            except Exception as e:
                logger.error(f"PriceMonitor: Failed to send to {user_id}: {e}")

    async def test_alert(self, user_id: int):
        """Send a test price alert to specific user"""
        # Create demo price data
        demo_data = PriceData(
            symbol="BTC/USDT",
            price=67450.00,
            change_1h=1.25,
            change_24h=3.45,
            volume_24h=1_234_567_890,
            market_cap=1_320_000_000_000,
            timestamp=datetime.now(),
        )

        formatted_message = format_price_alert(
            self.api.create_price_alert(demo_data, 67000.00),
            67000.00
        )

        await self.app.bot.send_message(
            chat_id=user_id,
            text="🧪 <b>Тестовое оповещение цены</b>\n\n" + formatted_message,
            parse_mode="HTML",
        )
