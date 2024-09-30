FROM python:3.10-slim

WORKDIR /app

# Копируем только файл с зависимостями на этапе установки пакетов
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем оставшуюся часть проекта
COPY . .

# Запускаем скрипт для инициализации базы данных
CMD ["python", "db_setup.py"]
