FROM python:3.12-slim

# Установить системные зависимости для Playwright
RUN apt-get update && \
    apt-get install -y wget gnupg2 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 \
    libpango-1.0-0 libgtk-3-0 libxshmfence1 libxfixes3 libxext6 libx11-6 libxcb1 libx11-xcb1 \
    libxrender1 libxi6 libxtst6 libdbus-1-3 libatspi2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Установить Poetry
RUN pip install poetry

# Копировать pyproject.toml и poetry.lock
WORKDIR /app
COPY pyproject.toml poetry.lock* ./

# Установить зависимости проекта
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root

# Копировать исходный код
COPY . .

# Установить браузеры Playwright
RUN poetry run playwright install --with-deps

# Указать переменные окружения (можно переопределить при запуске)
ENV PYTHONUNBUFFERED=1
