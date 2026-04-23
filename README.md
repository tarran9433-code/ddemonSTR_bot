# Whale & Smart Alert Tracker Bot

Telegram-бот для real-time мониторинга блокчейн-активности и рыночных аномалий.

## Возможности

- 🐋 **Whale Alerts** — мониторинг крупных переводов ($100K+) в реальном времени
- 📊 **Price Alerts** — оповещения о движениях цен криптовалют
- 🔓 **Token Unlocks** — отслеживание разлоков токенов
- 💰 **Exchange Flows** — анализ потоков на биржи
- 📈 **Live Mini App** — интерактивный дашборд прямо в Telegram
- 🚀 **Demo Mode** — демонстрация работы бота в действии
- 🔄 **HTTP API** — доступ к данным для внешних приложений
- 💾 **Offline Cache** — бот работает даже без интернета

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repo-url>
cd whale_tracker
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте переменные окружения:
```bash
# Создайте файл .env в корне проекта
cp .env.example .env

# Получите BOT_TOKEN:
# 1. Найдите @BotFather в Telegram
# 2. Отправьте /newbot
# 3. Следуйте инструкциям для создания бота
# 4. Скопируйте полученный токен

# Отредактируйте .env файл:
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz  # ваш токен
WHALE_ALERT_API_KEY=demo_key  # опционально для демо
DEMO_MODE=true  # включить демо-режим
```

4. Запустите бота:
```bash
python bot.py
```

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Начать работу |
| `/help` | Справка |
| `/alerts` | Управление подписками |
| `/whales` | Настройки китов |
| `/price` | Настройки цен |
| `/status` | Текущий статус и дашборд |
| `/dashboard` | Открыть Mini App с live дашбордом |
| `/settings` | Общие настройки |
| `/subscribe [тип]` | Быстрая подписка |
| `/unsubscribe [тип]` | Быстрая отписка |
| `/demo` | Демонстрация алертов |
| `/test` | Тестовое оповещение |

## Поддерживаемые сети

- 🔷 Ethereum (USDT, USDC, ETH, WBTC)
- 🔵 Tron (USDT)
- 🟡 BSC (USDT, BNB)
- 🟣 Polygon (USDT, USDC)

## Архитектура

```
whale_tracker/
├── bot.py              # Точка входа + HTTP API сервер
├── config.py           # Конфигурация
├── handlers/           # Обработчики команд + WebApp
├── monitors/           # Мониторинг событий + кэш алертов
├── services/           # API и форматирование
├── models/            # Модели данных
├── utils/              # Утилиты + автоопределение бирж
├── static/             # Mini App (HTML/CSS/JS)
├── data/               # Данные пользователей
└── logs/               # Логи работы
```

### 🔄 Интеграция с Mini App

- **HTTP API**: `http://localhost:8080/api/transactions`
- **WebSocket**: Планируется для real-time обновлений
- **ngrok**: HTTPS туннель для продакшена
- **GitHub Pages**: Хостинг Mini App

### 📱 Mini App возможности

- Real-time дашборд с транзакциями
- Автообновление каждые 30 секунд
- Подсветка биржевых адресов
- Интерактивные графики и статистика
- Адаптивный дизайн для мобильных устройств

## Лицензия

MIT
