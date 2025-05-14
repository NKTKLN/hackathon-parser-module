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
    parser = Parser(url, letters_count=1)
    letters_data = await parser.parse_letters()
    with open("data.json", "w", encoding="utf-8") as final:
        data = [letter.to_dict() for letter in letters_data]
        json.dump(data, final, ensure_ascii=False, indent=4)
    await parser.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
