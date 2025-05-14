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

    url = os.getenv("SITE_URL")
    if not url:
        logger.error("SITE_URL is not set in the environment variables.")
        return
    logger.info(f"Using URL: {url}")

    # Example usage
    parser = Parser(url)
    letters_data = await parser.parse_letters()
    with open("data.json", "w") as final:
        json.dump(letters_data, final)


if __name__ == "__main__":
    asyncio.run(main())
