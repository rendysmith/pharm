FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем файлы
COPY main.py .
COPY utils ./utils

# Создаём __init__.py чтобы utils был пакетом
RUN touch utils/__init__.py

CMD ["python", "main.py"]