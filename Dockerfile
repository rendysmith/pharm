FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python-пакеты (с фиксом для старых CPU)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем код и нужные файлы
COPY main.py .
COPY utils/ ./utils/

# Создаём папку для volume (на всякий случай)
RUN mkdir -p /app/utils

# Запуск бота
CMD ["python", "main.py"]