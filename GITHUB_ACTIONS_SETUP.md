# 🚀 Автоматический деплой ddemonSTR_bot с GitHub Actions

## 📋 Что делает этот автоматический деплой:

✅ **Автоматически создает volume** `whale_data`  
✅ **Деплоит приложение** на Fly.io  
✅ **Настраивает secrets** (BOT_TOKEN и другие)  
✅ **Работает при каждом push в main**  

---

## 🔧 Шаг 1: Настройка FLY_API_TOKEN

### 1.1 Получите FLY_API_TOKEN:
1. Зайдите на https://fly.io/dashboard
2. Нажмите на ваш профиль → **"Settings"**
3. **"Tokens"** → **"Create Token"**
4. Назовите токен: `ddemonstr-bot-deploy`
5. Скопируйте токен

### 1.2 Добавьте FLY_API_TOKEN в GitHub Secrets:
1. Откройте https://github.com/tarran9433-code/ddemonSTR_bot
2. **"Settings"** → **"Secrets and variables"** → **"Actions"**
3. **"New repository secret"**
4. **Name**: `FLY_API_TOKEN`
5. **Value**: ваш токен от Fly.io
6. Нажмите **"Add secret"**

---

## 🤖 Шаг 2: Настройка BOT_TOKEN

### 2.1 Получите BOT_TOKEN:
1. @BotFather в Telegram
2. `/newbot`
3. Назовите: `ddemonSTR Bot`
4. Скопируйте токен

### 2.2 Добавьте BOT_TOKEN в GitHub Secrets:
1. В том же разделе **"Actions"**
2. **"New repository secret"**
3. **Name**: `BOT_TOKEN`
4. **Value**: ваш токен от BotFather
5. Нажмите **"Add secret"**

---

## 🚀 Шаг 3: Запуск автоматического деплоя

### 3.1 Загрузите все изменения:
```bash
git add .github/workflows/deploy.yml fly.toml
git commit -m "Add GitHub Actions for automatic deployment with volume"
git push origin main
```

### 3.2 Проверьте деплой:
1. Перейдите в **"Actions"** в вашем репозитории
2. Увидите запущенный workflow **"Deploy to Fly.io"**
3. Дождитесь окончания (2-3 минуты)

---

## 🎯 Что произойдет автоматически:

1. **Создастся volume** `whale_data` (если еще не существует)
2. **Задеплоится приложение** на Fly.io
3. **Настроятся secrets** для бота
4. **Запустится бот** с вашими настройками

---

## 🌐 Результат:

После успешного деплоя ваш бот будет доступен по адресу:
```
https://ddemonstr-bot.fly.dev
```

API endpoint:
```
https://ddemonstr-bot.fly.dev/api/transactions
```

---

## 🔄 Обновления в будущем:

Теперь при каждом push в main ветку:
- Автоматически обновится приложение
- Сохранятся все данные в volume
- Не нужно настраивать ничего вручную

---

## 🚨 Возможные проблемы:

### Проблема: "FLY_API_TOKEN invalid"
**Решение:** Убедитесь что токен правильный и не истек

### Проблема: "BOT_TOKEN invalid"
**Решение:** Проверьте токен через curl API Telegram

### Проблема: "Volume already exists"
**Решение:** Это нормально, скрипт обработает ошибку

---

## 📱 Следующие шаги после деплоя:

1. **Настроить Mini App** для работы с Fly.io URL
2. **Включить GitHub Pages** для хостинга Mini App
3. **Зарегистрировать WebApp** в BotFather
4. **Протестировать всю систему**

---

## 💰 Коммерческое преимущество:

```
"ddemonSTR_bot развернут с помощью GitHub Actions!
✅ Полностью автоматический деплой
✅ CI/CD пайплайн
✅ Надежное хранилище данных
✅ Профессиональная инфраструктура

Это уровень Enterprise-решения!"
```

**Начинайте настройку секретов в GitHub!** 🚀
