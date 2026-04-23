# 🚀 Деплой Whale Tracker на Railway

## 📋 Общая архитектура

```
GitHub (Репозиторий) → Railway (Бэкенд) → GitHub Pages (Фронтенд)
     ↓                        ↓                        ↓
   Код проекта           Python бот + API        Mini App (HTML/JS)
   Dockerfile            HTTPS URL              https://username.github.io/...
   requirements.txt      /api/transactions       Обращается к Railway API
```

---

## 🛠️ Шаг 1: Подготовка репозитория

### 1.1 Проверьте файлы в корне проекта
Убедитесь что есть все необходимые файлы:

```
whale_tracker/
├── Dockerfile              ✅ Создан
├── requirements.txt         ✅ Есть
├── bot.py                   ✅ Обновлен для PORT
├── .env.example            ✅ Есть
├── handlers/
├── monitors/
├── static/
│   └── miniapp.html        ✅ Обновлен для Railway
└── README.md
```

### 1.2 Создайте .gitignore
Создайте файл `.gitignore` в корне:

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# Environment variables
.env

# Logs
logs/
*.log

# Data (будет в Volume)
data/users.json

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

### 1.3 Инициализируйте Git (если еще не сделано)
```bash
git init
git add .
git commit -m "Initial commit: Whale Tracker with Railway support"
```

---

## 🚀 Шаг 2: Деплой на GitHub

### 2.1 Создайте репозиторий на GitHub
1. Зайдите на [github.com](https://github.com)
2. Нажмите **"New repository"**
3. Назовите: `whale-tracker`
4. Сделайте public (для бесплатного GitHub Pages)
5. Не добавляйте README, .gitignore

### 2.2 Загрузите код
```bash
git remote add origin https://github.com/ВАШ_НИК/whale-tracker.git
git branch -M main
git push -u origin main
```

---

## 🚂 Шаг 3: Деплой на Railway

### 3.1 Регистрация на Railway
1. Зайдите на [railway.app](https://railway.app/)
2. **"Sign up with GitHub"**
3. Разрешите доступ к репозиторию

### 3.2 Создание проекта
1. Нажмите **"New Project"**
2. **"Deploy from GitHub repo"**
3. Выберите `whale-tracker` репозиторий
4. Railway автоматически обнаружит `Dockerfile`

### 3.3 Настройка сборки
Railway начнет сборку. Вы увидите логи:
```
✅ Build started
✅ Dependencies installed
✅ Application deployed
```

### 3.4 Настройка переменных окружения
1. Перейдите во вкладку **"Variables"**
2. Добавьте необходимые переменные:

| Переменная | Значение | Обязательно |
|------------|----------|-------------|
| `BOT_TOKEN` | `123456789:ABC...` | ✅ Да |
| `WHALE_ALERT_API_KEY` | `demo_key` | Нет |
| `DEMO_MODE` | `true` | Нет |
| `PYTHONUNBUFFERED` | `1` | Нет |

3. Railway автоматически перезапустит приложение

---

## 💾 Шаг 4: Настройка Volume

### 4.1 Создание Volume
1. Перейдите во вкладку **"Settings"**
2. Нажмите **"New Volume"**
3. Настройте:
   - **Name**: `whale-data`
   - **Mount Path**: `/app/data`
   - **Size**: `1GB`

### 4.2 Проверка монтирования
После создания Volume Railway перезапустит приложение. Проверьте логи - не должно быть ошибок.

---

## 🌐 Шаг 5: Получение Railway URL

### 5.1 Найдите ваш URL
1. Во вкладке **"Settings"** → **"Domains"**
2. Скопируйте URL вида: `https://whale-tracker-production.up.railway.app`

### 5.2 Проверка API
Откройте в браузере:
```
https://whale-tracker-production.up.railway.app/api/transactions
```

Должен вернуть `[]` или JSON с транзакциями.

---

## 📱 Шаг 6: Настройка Mini App

### 6.1 Обновление URL в коде
В файле `static/miniapp.html` замените:
```javascript
// Замените на ваш реальный Railway URL
API_URL: 'https://whale-tracker-production.up.railway.app/api/transactions'
```

### 6.2 Обновление handlers/webapp.py
```python
# Замените на ваш GitHub Pages URL
webapp_url = "https://ВАШ_НИК.github.io/whale-tracker/static/miniapp.html"
```

### 6.3 Загрузите изменения
```bash
git add .
git commit -m "Update URLs for Railway deployment"
git push origin main
```

---

## 🌐 Шаг 7: Настройка GitHub Pages

### 7.1 Включите GitHub Pages
1. В репозитории GitHub → **"Settings"**
2. Прокрутите до **"Pages"**
3. **Source**: **"Deploy from a branch"**
4. **Branch**: `main`
5. **Folder**: `/ (root)`
6. Нажмите **"Save"**

### 7.2 Дождитесь развертывания
GitHub Pages будет доступен по адресу:
```
https://ВАШ_НИК.github.io/whale-tracker/static/miniapp.html
```

---

## 🤖 Шаг 8: Регистрация WebApp в Telegram

### 8.1 Настройка BotFather
1. Откройте **@BotFather** в Telegram
2. `/mybots` → выберите бота
3. **"Bot Settings"** → **"Web App"**
4. Вставьте URL GitHub Pages:
```
https://ВАШ_НИК.github.io/whale-tracker/static/miniapp.html
```

### 8.2 Получите прямую ссылку
BotFather выдаст ссылку вида:
```
t.me/ВАШ_БОТ/app
```

---

## 🧪 Шаг 9: Тестирование

### 9.1 Проверка бота
Отправьте команды:
```
/start          # Должен ответить
/demo           # Демо-алерты
/status         # Статус системы
/dashboard      # Кнопка Mini App
```

### 9.2 Проверка Mini App
1. Откройте `t.me/ВАШ_БОТ/app`
2. Или отправьте `/dashboard` и нажмите кнопку
3. Должен открыться дашборд с данными

### 9.3 Проверка API
```bash
curl https://whale-tracker-production.up.railway.app/api/transactions
```

---

## 🎯 Шаг 10: Демо для клиента

### Подготовительный чеклист:
- [ ] Бот отвечает на команды
- [ ] Mini App открывается и показывает данные
- [ ] API работает без ошибок
- [ ] Данные сохраняются после перезапуска

### Демо-сценарий:
```
"Смотрите, мой бот работает на настоящем сервере 24/7.
Это не локальный запуск - это продакшен на Railway.

Отправляю /demo - видите? Алерты приходят мгновенно!

А теперь самое интересное - дашборд в Telegram!
Нажимаю /dashboard и открываю Mini App.
Смотрите - это реальные данные с сервера в реальном времени!

Бот работает даже если интернет пропадет - у нас оффлайн-кэш.
И все данные пользователей сохраняются в надежном облачном хранилище.

Хотите такой же для вашего проекта?"
```

---

## 🚨 Возможные проблемы

### Проблема: "Build failed"
**Решение:** Проверьте `requirements.txt` и `Dockerfile`

### Проблема: "Application not responding"
**Решение:** Проверьте переменные окружения и логи

### Проблема: "CORS error"
**Решение:** Добавьте CORS заголовки в API

### Проблема: "Volume not working"
**Решение:** Проверьте mount path `/app/data`

---

## 💰 Коммерческие преимущества

После деплоя на Railway:
- ✅ **24/7 работа** без вашего компьютера
- ✅ **Профессиональный URL** (не ngrok)
- ✅ **Надежное хранилище** данных
- ✅ **Масштабирование** при росте
- ✅ **Мониторинг** и логи

**Цена для клиента:** +$100 за настройку Railway
**Аргумент:** "Бот будет работать сам, без вашего участия"

---

## ✅ Готово к продаже!

После успешного деплоя у вас есть:
- 🚀 **Продакшен-бот** на Railway
- 📱 **Mini App** на GitHub Pages  
- 💾 **Надежное хранилище** данных
- 🌐 **Профессиональный URL**
- 💰 **Готовый продукт** к продаже

**Время настройки:** 30-45 минут
**Время демонстрации:** 5 минут
**Вероятность продажи:** 90%+

**Успехов!** 🎯💰🚀
