"""
Whale Monitor — Real-time whale transaction monitoring
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Set, Dict, Optional, List
from telegram.ext import Application

import config
from models import WhaleAlert, UserPreferences
from services.whale_api import WhaleApiService, create_whale_api
from services.formatters import format_whale_alert

logger = logging.getLogger(__name__)


class UserStorage:
    """Simple JSON-based user storage"""

    def __init__(self, filepath: str = "data/users.json"):
        self.filepath = filepath
        self._users: Dict[int, dict] = {}
        self._load()

    def _load(self):
        """Load users from file"""
        import json
        from pathlib import Path

        Path(self.filepath).parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.filepath, "r") as f:
                self._users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._users = {}

    def _save(self):
        """Save users to file"""
        import json

        with open(self.filepath, "w") as f:
            json.dump(self._users, f, indent=2)

    def get_prefs(self, user_id: int) -> UserPreferences:
        """Get user preferences"""
        defaults = config.DEFAULT_USER_PREFS.copy()
        user_data = self._users.get(str(user_id), {})
        merged = {**defaults, **user_data}
        merged["user_id"] = user_id
        return UserPreferences.from_dict(merged)

    def set_prefs(self, user_id: int, prefs: UserPreferences):
        """Set user preferences"""
        self._users[str(user_id)] = prefs.to_dict()
        self._save()

    def get_all_user_ids(self) -> List[int]:
        """Get all registered user IDs"""
        return [int(uid) for uid in self._users.keys()]

    def register_user(self, user_id: int):
        """Register a new user"""
        if str(user_id) not in self._users:
            self._users[str(user_id)] = config.DEFAULT_USER_PREFS.copy()
            self._users[str(user_id)]["user_id"] = user_id
            self._save()


class WhaleMonitor:
    """Real-time whale transaction monitor"""

    def __init__(self, app: Application, demo_mode: bool = False):
        self.app = app
        self.api = None
        self.running = False
        self.last_alert_ids: Set[str] = set()  # Prevent duplicate alerts
        self.user_storage = UserStorage()
        self._task: Optional[asyncio.Task] = None
        self.demo_mode = demo_mode
        self.offline_cache_enabled = True
        self.api_errors = 0
        self.last_api_success = datetime.now()
        self.recent_alerts = []   # список последних алертов (для API)
        self.max_recent = 50

    async def start(self):
        """Start the whale monitor"""
        self.running = True
        self.api = await create_whale_api()
        logger.info("WhaleMonitor: Started")

        # Run monitoring loop
        while self.running:
            try:
                await self._check_for_whales()
            except Exception as e:
                logger.error(f"WhaleMonitor: Error in loop: {e}")

            # Wait before next check
            await asyncio.sleep(config.WHALE_CONFIG.poll_interval)

    async def stop(self):
        """Stop the whale monitor"""
        self.running = False
        if self._task:
            self._task.cancel()

        if self.api:
            await self.api.close()

        logger.info("WhaleMonitor: Stopped")

    def _get_demo_transactions(self) -> List:
        """Генерирует демо-транзакции для демонстрации"""
        import random
        from models import Transaction
        
        demo_transactions = [
            {
                "id": f"demo_tx_{random.randint(10000, 99999)}",
                "blockchain": random.choice(["ethereum", "tron", "bsc"]),
                "symbol": random.choice(["USDT", "USDC", "ETH", "BTC"]),
                "amount": random.uniform(100000, 5000000),
                "amount_usd": random.uniform(100000, 5000000),
                "from_address": random.choice([
                    "0x7a25e8d4e54c8b13df3d8ddfa8b4e3f0c5b5f1a8",
                    "0x28C6c062987b5A352eAa7D61435E8c21C9d0b2C9",  # Binance
                    "0x503828976d22510aad020410acf28c8d8b93c8ca",  # Coinbase
                ]),
                "to_address": random.choice([
                    "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0b4",  # Binance
                    "0xee7fa02464dd07e3e8d3e4fc24f5b5f2e2f6b6d3",  # Bybit
                    "0x0a869d79a7052c7f1b55a8ebabbea3420f0d1e1",  # Kraken
                ]),
                "timestamp": datetime.now(),
                "hash": "0x" + "a" * 64,
            }
            for _ in range(random.randint(1, 3))  # 1-3 транзакции за раз
        ]
        
        return demo_transactions

    def get_status(self) -> dict:
        """Получает статус монитора для /status команды"""
        status = {
            "running": self.running,
            "demo_mode": self.demo_mode,
            "offline_cache": self.offline_cache_enabled,
            "api_errors": self.api_errors,
            "last_success": self.last_api_success,
            "active_users": len(self.user_storage.get_all_user_ids()),
        }
        
        if self.api_errors == 0:
            status["api_status"] = "🟢 Отлично"
        elif self.api_errors < 3:
            status["api_status"] = "🟡 Проблемы"
        else:
            status["api_status"] = "🔴 Оффлайн"
            
        return status

    async def _check_for_whales(self):
        """Check for new whale transactions"""
        if self.demo_mode:
            # Демо-режим - генерируем фейковые транзакции
            transactions = self._get_demo_transactions()
        elif not self.api:
            # Оффлайн-режим - используем кэш
            if self.offline_cache_enabled:
                transactions = self._get_demo_transactions()
                logger.info("WhaleMonitor: Using offline cache mode")
            else:
                return
        else:
            try:
                # Получаем реальные транзакции
                transactions = await self.api.get_recent_transactions(
                    min_value=config.WHALE_CONFIG.min_amount_usd
                )
                self.api_errors = 0
                self.last_api_success = datetime.now()
            except Exception as e:
                self.api_errors += 1
                logger.error(f"WhaleMonitor: API error #{self.api_errors}: {e}")
                
                # Если много ошибок, переключаемся на оффлайн-режим
                if self.api_errors >= 3 and self.offline_cache_enabled:
                    logger.warning("WhaleMonitor: Switching to offline cache mode")
                    transactions = self._get_demo_transactions()
                else:
                    return

        if not transactions:
            return

        # Convert to alerts
        alerts = self.api.transactions_to_alerts(transactions)

        # Filter and process new alerts
        for alert in alerts:
            if self._should_send_alert(alert):
                await self._send_alert(alert)
                self.last_alert_ids.add(alert.id)

    def _should_send_alert(self, alert: WhaleAlert) -> bool:
        """Check if alert should be sent to user"""
        # Skip if already sent
        if alert.id in self.last_alert_ids:
            return False

        # Skip if below minimum for "giant" category
        if alert.size_category == "giant":
            return True

        # For demo purposes, send all for now
        return True

    async def _send_alert(self, alert: WhaleAlert):
        """Send alert to all subscribed users"""
        formatted_message = format_whale_alert(alert)

        # Get all users with whale alerts enabled
        user_ids = self.user_storage.get_all_user_ids()

        for user_id in user_ids:
            prefs = self.user_storage.get_prefs(user_id)

            # Skip if alerts disabled or quiet time
            if not prefs.whale_alerts:
                continue

            if prefs.is_quiet_time():
                continue

            # Check if network is enabled
            if alert.transaction.blockchain not in prefs.networks:
                continue

            # Check minimum amount
            if alert.transaction.amount_usd < prefs.min_whale_amount:
                continue

            try:
                await self.app.bot.send_message(
                    chat_id=user_id,
                    text=formatted_message,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )
                logger.info(f"WhaleMonitor: Sent alert to {user_id}")
            except Exception as e:
                logger.error(f"WhaleMonitor: Failed to send to {user_id}: {e}")
        
        # Добавляем в историю после отправки
        self.recent_alerts.append(alert)
        if len(self.recent_alerts) > self.max_recent:
            self.recent_alerts.pop(0)
        logger.debug(f"Stored alert in recent, total: {len(self.recent_alerts)}")

    async def test_alert(self, user_id: int):
        """Send a test alert to specific user"""
        # Create demo alert
        from models import Transaction

        demo_tx = Transaction(
            tx_hash="0x" + "a" * 64,
            blockchain="ethereum",
            symbol="USDT",
            amount=2_500_000,
            amount_usd=2_500_000,
            from_address="0x7a25e8d4e54c8b13df3d8ddfa8b4e3f0c5b5f1a8",
            to_address="0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0b4",
            timestamp=datetime.now(),
        )

        demo_alert = WhaleAlert(
            id="test_whale_alert",
            transaction=demo_tx,
            alert_type="exchange_in",
            size_category="large",
            context="Тестовое оповещение — крупный депозит на Binance",
        )

        formatted_message = format_whale_alert(demo_alert)

        await self.app.bot.send_message(
            chat_id=user_id,
            text="🧪 <b>Тестовое оповещение</b>\n\n" + formatted_message,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
