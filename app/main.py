"""Модуль запуска парсинга писем с сайта 'Письма Победы'.

Этот модуль предназначен для асинхронного парсинга заданного количества писем
с веб-сайта https://pismapobedy.ru/letters.  Результат парсинга сохраняется
в JSON-файл `data.json` в текущей директории.

Functionality:
- Загрузка переменных окружения (LETTERS_COUNT).
- Настройка логирования.
- Инициализация и запуск парсера.
- Сохранение спарсенных данных в формате JSON.

Environment Variables:
    LETTERS_COUNT (str): Количество писем для парсинга. По умолчанию — 50.
"""

import asyncio
import json
import logging
import os

from dotenv import load_dotenv

from app.logger import setup_logger
from app.parse import Parser

load_dotenv()
logger = logging.getLogger(__name__)


async def main() -> None:
    """Основная функция для запуска и настройки парсера."""
    setup_logger()

    url = "https://pismapobedy.ru/letters"
    letters_count = int(os.getenv("LETTERS_COUT", "50"))
    if not url:
        logger.error("LETTERS_COUT is not set in the environment variables.")
        return

    # Example usage
    parser = Parser(url, letters_count=letters_count)
    letters_data = await parser.parse_letters()
    with open("data.json", "w", encoding="utf-8") as final:
        data = [letter.to_dict() for letter in letters_data]
        json.dump(data, final, ensure_ascii=False, indent=4)
    await parser.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
