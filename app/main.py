import logging
import os

from dotenv import load_dotenv

from app.logger import setup_logger
from app.parse import LetterIdsParser

load_dotenv()
logger = logging.getLogger(__name__)


def main() -> None:
    setup_logger()
    url = os.getenv("SITE_URL")
    if not url:
        logger.error("SITE_URL is not set in the environment variables.")
        return
    logger.info(f"Using URL: {url}")

    # Example usage
    parser = LetterIdsParser(url)
    for i in range(50):
        parser.set_page(i)
        letter_ids = parser.get_letter_ids()
        print(letter_ids)


if __name__ == "__main__":
    main()
