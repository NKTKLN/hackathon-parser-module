"""Модуль запуска парсинга писем с сайта 'Письма Победы'.

Этот модуль предназначен для асинхронного парсинга заданного количества писем
с веб-сайта https://pismapobedy.ru/letters.  Результат парсинга сохраняется
в JSON-файл `data.json` в текущей директории.

Functionality:
- Настройка логирования.
- Инициализация и запуск парсера.
"""

import asyncio
import logging

from app.config import config
from app.db.database import init_db
from app.logger import setup_logger
from app.parse import Parser

logger = logging.getLogger(__name__)


async def main() -> None:
    """Основная функция для запуска и настройки парсера."""
    setup_logger()

    await init_db()

    parser = Parser(config.URL, letters_count=config.LETTERS_COUNT)
    await parser.parse_letters()
    await parser.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
