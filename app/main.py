"""Модуль запуска парсинга писем с сайта 'Письма Победы'.

Этот модуль предназначен для асинхронного парсинга заданного количества писем
с веб-сайта https://pismapobedy.ru/letters.

Functionality:
- Настройка логирования.
- Инициализация базы данных.
- Запуск парсера по расписанию.
"""

import logging

from rocketry import Rocketry  # type: ignore
from rocketry.conds import every  # type: ignore

from app.config import config
from app.db.database import init_db
from app.logger import setup_logger
from app.parse import Parser

app = Rocketry(execution="async")

# Инициализация логгера
logger = logging.getLogger(__name__)


@app.task(every("12 hours"))
async def scheduled_parsing() -> None:  # noqa: F401
    """Задача парсинга писем каждые 12 часов."""
    logger.info("Starting an letters parsing task...")
    await init_db()

    parser = Parser(config.URL, letters_count=config.LETTERS_COUNT)
    await parser.parse_letters()
    await parser.shutdown()
    logger.info("Parsing task completed.")


if __name__ == "__main__":
    setup_logger()
    app.run()
