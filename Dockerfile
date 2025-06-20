FROM python:3.11-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install --no-install-recommends -y \
  build-essential \
  libsqlite3-dev \
  curl \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости проекта
COPY requirements.txt .

# Установка зависимостей Python
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Открываем порт
EXPOSE 8000

# Команда запуска сервера
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]
