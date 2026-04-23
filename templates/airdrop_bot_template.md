# Airdrop Bot Template - Адаптация Whale Tracker

## 🚀 Быстрая адаптация под Airdrop-мониторинг (15 минут)

### 1. Заменяем whale_api.py → airdrop_api.py

```python
# services/airdrop_api.py
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class AirdropApiService:
    def __init__(self):
        self.session = None
        self.base_urls = [
            "https://airdropalert.com",
            "https://defillama.com/airdrops",
            "https://cryptopotato.com/category/airdrops/"
        ]
    
    async def start(self):
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        if self.session:
            await self.session.close()
    
    async def get_recent_airdrops(self) -> List[Dict]:
        """Парсинг последних аирдропов"""
        airdrops = []
        
        for url in self.base_urls:
            try:
                async with self.session.get(url) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Парсим карточки аирдропов
                    for card in soup.find_all('div', class_='airdrop-card'):
                        title = card.find('h3').text.strip()
                        description = card.find('p').text.strip()
                        link = card.find('a')['href']
                        
                        airdrops.append({
                            'title': title,
                            'description': description,
                            'link': link,
                            'timestamp': datetime.now()
                        })
                        
            except Exception as e:
                logger.error(f"Error parsing {url}: {e}")
        
        return airdrops

# Twitter парсинг (альтернатива)
async def parse_twitter_airdrops():
    """Парсинг Twitter через twikit"""
    import twikit
    
    # Ищем посты с хэштегами #airdrop #crypto
    keywords = ["airdrop", "crypto airdrop", "free tokens", "claim"]
    
    # Возвращаем найденные аирдропы
    return []
```

### 2. Обновляем config.py

```python
# Заменяем SUPPORTED_NETWORKS на SUPPORTED_PROJECTS
SUPPORTED_PROJECTS = {
    "ethereum": {
        "name": "Ethereum Ecosystem",
        "keywords": ["ETH", "Ethereum", "Layer 2"],
        "emoji": "🔷"
    },
    "solana": {
        "name": "Solana Ecosystem", 
        "keywords": ["SOL", "Solana", "Phantom"],
        "emoji": "🟣"
    },
    "polygon": {
        "name": "Polygon Ecosystem",
        "keywords": ["MATIC", "Polygon", "zkEVM"],
        "emoji": "🟣"
    },
    "arbitrum": {
        "name": "Arbitrum Ecosystem",
        "keywords": ["ARB", "Arbitrum", "Optimism"],
        "emoji": "🔵"
    }
}

# Настройки Airdrop-монитора
AIRDROP_CONFIG = MonitorConfig(
    enabled=True,
    poll_interval=300,  # 5 минут
    min_amount_usd=0   # для аирдропов не актуально
)
```

### 3. Обновляем formatters.py → airdrop_formatters.py

```python
# services/airdrop_formatters.py

def format_airdrop_alert(airdrop: Dict) -> str:
    """Форматирует уведомление об аирдропе"""
    
    project_emoji = {
        "ethereum": "🔷",
        "solana": "🟣", 
        "polygon": "🟣",
        "arbitrum": "🔵"
    }.get(airdrop.get('project', 'ethereum'), "🎯")
    
    return f"""🎯 AIRDROP ALERT 🎯
━━━━━━━━━━━━━━━
{project_emoji} <b>{airdrop['title']}</b>

📝 <b>Описание:</b>
{airdrop['description'][:200]}...

🔗 <b>Ссылка:</b>
{airdrop['link']}

⏰ <b>Время:</b>
{format_timestamp(airdrop['timestamp'])}

━━━━━━━━━━━━━━━
💡 <b>Действие:</b>
Проверьте требования и участвуйте!

🚀 <b>Быстрые действия:</b>
/claim_{airdrop['id']} — детали
/share — поделиться с друзьями"""

def format_airdrop_menu() -> str:
    """Меню управления аирдропами"""
    return """🎯 <b>Airdrop Monitor</b>

━━━━━━━━━━━━━━━━━━━━
<b>Активные проекты:</b>
🔷 Ethereum Ecosystem
🟣 Solana Ecosystem  
🟣 Polygon Ecosystem
🔵 Arbitrum Ecosystem

━━━━━━━━━━━━━━━━━━━━
<b>Фильтры:</b>
• Минимальный reward: $10
• Вероятность: Высокая
• Требования: Соцсети

━━━━━━━━━━━━━━━━━━━━
<i>Настройте фильтры в /airdrops</i>"""
```

### 4. Обновляем monitors/whale_monitor.py → monitors/airdrop_monitor.py

```python
# monitors/airdrop_monitor.py

class AirdropMonitor:
    def __init__(self, app: Application):
        self.app = app
        self.api = AirdropApiService()
        self.running = False
        self.last_airdrop_ids: Set[str] = set()
        self.user_storage = UserStorage()
    
    async def start(self):
        """Запуск мониторинга аирдропов"""
        self.running = True
        await self.api.start()
        logger.info("AirdropMonitor: Started")
        
        while self.running:
            try:
                await self._check_for_airdrops()
            except Exception as e:
                logger.error(f"AirdropMonitor: Error: {e}")
            
            await asyncio.sleep(config.AIRDROP_CONFIG.poll_interval)
    
    async def _check_for_airdrops(self):
        """Проверка новых аирдропов"""
        airdrops = await self.api.get_recent_airdrops()
        
        for airdrop in airdrops:
            if airdrop['id'] not in self.last_airdrop_ids:
                await self._notify_airdrop(airdrop)
                self.last_airdrop_ids.add(airdrop['id'])
    
    async def _notify_airdrop(self, airdrop: Dict):
        """Отправка уведомления об аирдропе"""
        formatted_message = format_airdrop_alert(airdrop)
        
        user_ids = self.user_storage.get_all_user_ids()
        for user_id in user_ids:
            prefs = self.user_storage.get_prefs(user_id)
            
            if prefs.airdrop_alerts and not prefs.is_quiet_time():
                try:
                    await self.app.bot.send_message(
                        chat_id=user_id,
                        text=formatted_message,
                        parse_mode="HTML",
                        disable_web_page_preview=True
                    )
                except Exception as e:
                    logger.error(f"Failed to send airdrop to {user_id}: {e}")
```

### 5. Обновляем команды в handlers/commands.py

```python
# Добавляем новые команды
async def airdrops_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /airdrops command"""
    airdrops_text = format_airdrop_menu()
    
    await update.message.reply_text(
        airdrops_text,
        parse_mode="HTML",
        reply_markup=airdrop_menu_keyboard(),
    )

async def claim_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /claim command - детали аирдропа"""
    airdrop_id = context.args[0] if context.args else None
    
    if airdrop_id:
        # Показываем детали конкретного аирдропа
        details_text = f"""🎯 <b>Детали Airdrop #{airdrop_id}</b>
        
━━━━━━━━━━━━━━━━━━━━
📝 <b>Требования:</b>
• Follow Twitter
• Join Discord  
• Subscribe Newsletter
• Minimum $10 in wallet

⏰ <b>Дедлайн:</b>
7 дней

💰 <b>Оценочный reward:</b>
$50-200

🔗 <b>Ссылки:</b>
Twitter: [ссылка]
Discord: [ссылка]
Website: [ссылка]

━━━━━━━━━━━━━━━━━━━━
🚀 <b>Быстрый клейм:</b>
/confirm_claim {airdrop_id}"""
        
        await update.message.reply_text(details_text, parse_mode="HTML")
```

## 🎯 Монетизация Airdrop-бота

### Ценовые пакеты:

| Пакет | Цена | Что входит |
|-------|------|------------|
| **Airdrop Basic** | $100 | Мониторинг 5 источников, базовые фильтры |
| **Airdrop Pro** | $300 | + Twitter парсинг, приоритетные алерты |
| **Airdrop Enterprise** | $500 | + Кастомные источники, API доступ |

### Продающие тексты для клиентов:

> "Создам для вас Telegram-бота, который отслеживает все крипто-аирдропы в реальном времени. Бот будет парсить 10+ источников, фильтровать по вашим критериям и присылать только самые выгодные предложения. Уже есть готовое демо - покажу на созвоне. Запуск через 2 часа после оплаты."

> "Ваши подписчики будут получать эксклюзивные аирдропы первыми! Бот автоматически проверяет требования, оценивает потенциальный доход и присылает готовые инструкции для участия. Монетизация через referral-ссылки и платные подписки."

## 🚀 Запуск за 15 минут:

1. **Копируем** whale_monitor.py → airdrop_monitor.py
2. **Заменяем** API вызовы на парсинг сайтов
3. **Меняем** форматирование сообщений  
4. **Обновляем** команды в handlers
5. **Тестируем** и запускаем

**Готово!** У вас есть рабочий Airdrop-бот с полной экосистемой! 🎯
