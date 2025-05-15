"""Модуль запуска парсинга писем с сайта 'Письма Победы'.

Этот модуль предназначен для асинхронного парсинга заданного количества писем
с веб-сайта https://pismapobedy.ru/letters.

Functionality:
- Настройка логирования.
- Инициализация базы данных.
- Запуск парсера по расписанию.
"""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore

from app.config import config
from app.db.database import init_db
from app.logger import setup_logger
from app.parsers import Parser

# Инициализация логгера
logger = logging.getLogger(__name__)


async def scheduled_parsing() -> None:
    """Задача парсинга писем по расписанию."""
    logger.info("Starting letters parsing task...")
    parser = Parser(config.URL, letters_count=config.LETTERS_COUNT)
    await parser.parse_letters()
    await parser.shutdown()
    logger.info("Parsing task completed.")


async def main() -> None:
    """Основная функция для запуска парсинга."""
    setup_logger()
    await init_db()

    # Сначала запускаем задачу один раз сразу
    await scheduled_parsing()

    scheduler = AsyncIOScheduler()
    # Запуск задачи каждые 12 часов
    scheduler.add_job(
        lambda: asyncio.create_task(scheduled_parsing()), "interval", hours=12
    )
    scheduler.start()

    logger.info("Scheduler started. Running forever...")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
