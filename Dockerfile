FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения
COPY . .

# Создаем необходимые директории
RUN mkdir -p data logs

# Указываем порт, который будет слушать наше приложение
ENV PORT=8080

# Команда для запуска бота
CMD ["python", "bot.py"]
