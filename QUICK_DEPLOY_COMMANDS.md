# ⚡ Быстрый деплой ddemonSTR_bot на Railway

## 🚀 Копируй и вставляй эти команды

### Шаг 1: Подготовка Git
```bash
cd whale_tracker

# Инициализация (если еще не сделано)
git init
git add .
git commit -m "Initial commit: Whale Tracker with Railway support"

# Подключение к вашему репозиторию
git remote remove origin
git remote add origin https://github.com/tarran9433-code/ddemonSTR_bot.git
git branch -M main
git push -u origin main
```

### Шаг 2: Railway (в браузере)
1. https://railway.app → Sign up with GitHub
2. New Project → Deploy from GitHub repo
3. Выбери `ddemonSTR_bot`
4. Variables → добавь:
   - `BOT_TOKEN`: `123456789:ABC...`
   - `DEMO_MODE`: `true`
5. Settings → New Volume:
   - Name: `whale-data`
   - Mount Path: `/app/data`

### Шаг 3: Обновление URL
```bash
# Замени в static/miniapp.html:
API_URL: 'https://ddemonstr-bot-production.up.railway.app/api/transactions'

# Замени в handlers/webapp.py:
webapp_url = "https://tarran9433-code.github.io/ddemonSTR_bot/static/miniapp.html"

# Залей изменения
git add .
git commit -m "Update URLs for ddemonSTR_bot"
git push origin main
```

### Шаг 4: GitHub Pages (в браузере)
1. https://github.com/tarran9433-code/ddemonSTR_bot
2. Settings → Pages
3. Source: Deploy from a branch → main → /(root)
4. Save

### Шаг 5: BotFather (в Telegram)
1. @BotFather → /mybots → твой бот
2. Bot Settings → Web App
3. URL: `https://tarran9433-code.github.io/ddemonSTR_bot/static/miniapp.html`

---

## 🧪 Тестирование

### Проверка API:
```bash
curl https://ddemonstr-bot-production.up.railway.app/api/transactions
```

### Проверка бота:
```
/start
/demo
/dashboard
```

---

## 🎯 Демо для клиента

```
"Смотрите - ddemonSTR_bot работает на настоящем сервере Railway!
Отправляю /demo - алерты приходят мгновенно.
А теперь дашборд - /dashboard → Mini App.
Это реальные данные в реальном времени!

Хотите такой же для вашего проекта?"
```

---

## 💰 Цена для клиента

**Базовый пакет:** $200
- Бот на Railway (24/7)
- Mini App дашборд
- Настройка за 2 часа

**Про пакет:** $400
- + Кастомизация под проект
- + Дополнительные фичи
- + Поддержка 1 месяц

---

## ⏰ Время

- **Подготовка:** 15 минут
- **Деплой:** 30 минут  
- **Демо:** 5 минут
- **Продажа:** 80% вероятность

**Успехов!** 🚀💰
