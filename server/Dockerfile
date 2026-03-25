FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей (с зеркалом и отключением проверки SSL для проблемных сетей)
RUN pip install --default-timeout=100 --trusted-host pypi.org --trusted-host pypi.io --no-cache-dir fastapi uvicorn

# Копирование приложения
COPY app/ /app/

# Запуск API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
