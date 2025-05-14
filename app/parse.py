"""Модуль парсеров для извлечения данных с сайта с письмами.

Этот модуль предоставляет функционал для асинхронного парсинга списка писем,
их идентификаторов и содержимого отдельных писем с использованием Playwright.

Classes:
    ParserBase: Базовый класс с общей логикой запуска браузера и получения HTML.
    LetterIdsParser: Извлекает ID писем с основной страницы.
    LetterParser: Парсит данные одного письма по его ID.
    Parser: Основной интерфейс для сбора заданного количества писем.

Features:
    - Асинхронная загрузка страниц через Playwright
    - Поддержка пагинации
    - Извлечение структурированных данных писем
"""

import logging
import re
from typing import List, Optional

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from app.models import LetterData

# Инициализация логгера
logger = logging.getLogger(__name__)


class ParserBase:
    """Базовый класс для парсеров. Содержит общую логику получения контента страниц."""

    def __init__(self):
        """Инициализация базового парсера."""
        self.browser = None # Браузер будет инициализирован при первом вызове

    async def start_browser(self):
        """Инициализирует браузер через Playwright, если он ещё не запущен.

        Returns:
            browser: Запущенный экземпляр браузера.
        """
        if self.browser is None:
            logger.info("Initializing browser via Playwright...")
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
        return self.browser

    async def get_html(self, url: str) -> Optional[str]:
        """Получает HTML-содержимое указанной страницы.

        Args:
            url (str): URL страницы для загрузки.

        Returns:
            Optional[str]: HTML-содержимое страницы или None при ошибке.
        """
        try:
            browser = await self.start_browser()
            page = await browser.new_page()
            logger.debug(f"Navigating to URL: {url}")
            await page.goto(url, timeout=60000)
            html = await page.content()
            await page.close()
            logger.debug(f"Successfully fetched HTML content from {url}")
            return html
        except Exception as e:
            logger.error(f"Failed to fetch page via Playwright: {e}", exc_info=True)
            return None

    async def parse(self, url: str) -> Optional[BeautifulSoup]:
        """Парсит HTML-содержимое страницы по указанному URL.

        Args:
            url (str): URL страницы для парсинга.

        Returns:
            Optional[BeautifulSoup]: Объект BeautifulSoup с разобранным содержимым или
                                     None при ошибке.
        """
        logger.debug(f"Parsing URL: {url}")
        html = await self.get_html(url)
        if not html:
            logger.warning(f"No HTML content received for parsing: {url}")
            return None
        soup = BeautifulSoup(html, "html.parser")
        logger.debug(f"Finished parsing HTML for URL: {url}")
        return soup


class LetterIdsParser(ParserBase):
    """Парсер для извлечения идентификаторов писем с основной страницы.

    Конструирует URL с учётом параметров страницы и количества элементов на странице.

    Attributes:
        page (int): Номер текущей страницы.
        chunk_size (int): Количество писем на одной странице.
        base_url (str): Базовый URL сайта.
        url (str): Текущий URL с параметрами пагинации.
    """

    def __init__(self, url: str, chunk_size: int = 24, page: int = 1):
        """Инициализация парсера Id писем.

        Args:
            url (str): Базовый URL сайта для извлечения писем.
            chunk_size (int, optional): Количество писем на одной странице. Default: 24.
            page (int, optional): Номер страницы для запроса. Default: 1.
        """
        self.page = page
        self.chunk_size = chunk_size
        self.base_url = url
        self.url = self._build_url()
        super().__init__()

    def _build_url(self) -> str:
        """Формирует URL для текущей страницы пагинации.

        Returns:
            str: Сформированный URL.
        """
        url = f"{self.base_url}?order_field=published_desc&page={self.page}\
&per={self.chunk_size}"
        logger.debug(f"Built URL for fetching letter IDs: {url}")
        return url

    def set_page(self, page: int) -> None:
        """Обновляет номер страницы и пересчитывает URL.

        Args:
            page (int): Новый номер страницы.
        """
        self.page = page
        self.url = self._build_url()
        logger.debug(f"Updated page number. New URL: {self.url}")

    async def get_letter_ids(self) -> List[str]:
        """Извлекает список идентификаторов писем с текущей страницы.

        Returns:
            List[str]: Список строк с ID писем.
        """
        logger.info(f"Fetching letter IDs from {self.url}")
        soup = await self.parse(self.url)
        if not soup:
            logger.warning(f"Failed to parse page for letter IDs: {self.url}")
            return []

        links = soup.find_all("a", class_="js-open_letter") # Находим ссылки с ID
        letter_ids = [id for link in links if (id := link.get("data-letter_id"))]
        logger.info(f"Found {len(letter_ids)} letter IDs on page {self.page}")
        return letter_ids


class LetterParser(ParserBase):
    """Парсер для извлечения данных одного конкретного письма по его ID.

    Парсит содержимое отдельной страницы письма.

    Attributes:
        url (str): Базовый URL сайта, содержащего письма.
    """

    def __init__(self, url: str):
        """Инициализация парсера писем.

        Args:
            url (str): Базовый URL сайта, содержащего письма.
        """
        self.url = url
        super().__init__()

    async def get_letter_data(self, letter_id: str) -> Optional[LetterData]:
        """Парсит данные одного письма по его ID.

        Args:
            letter_id (str): Уникальный идентификатор письма.

        Returns:
            Optional[LetterData]: Экземпляр LetterData или None при ошибке.
        """
        url = f"{self.url}#letter-{letter_id}"
        logger.info(f"Parsing data for letter ID: {letter_id}, URL: {url}")
        soup = await self.parse(url)
        if not soup:
            logger.warning(f"Failed to parse letter page for ID: {letter_id}")
            return None

        # Ищем блок с содержимым письма
        letter_div = soup.find("div", class_="b-letter-text")
        if not letter_div:
            logger.warning(f"Letter content div not found for ID: {letter_id}")
            return None

        # Получаем сырые данные
        date_element = letter_div.find_all("p")[0]
        raw_date = date_element.text.strip() if date_element else "unknown"

        author_line = letter_div.find("p", string=lambda t: t and "От кого:" in t)
        raw_author = (
            author_line.text.replace("От кого:", "").strip() if author_line else "?"
        )

        text_block = letter_div.find("div", class_="text")
        raw_text = text_block.get_text(separator="\n").strip() if text_block else ""

        # Проверяем данные на корректность
        date_pattern = r"\d{2}\.\d{2}\.\d{2,4}"
        date = raw_date if re.fullmatch(date_pattern, raw_date) else "unknown"

        author_pattern = r"[А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+"
        author = raw_author if re.fullmatch(author_pattern, raw_author) else "unknown"

        text = raw_text if raw_text else "unknown"

        logger.info(f"Successfully parsed letter ID: {letter_id}")
        return LetterData(id=letter_id, date=date, author=author, text=text, url=url)


class Parser:
    """Основной парсер для сбора заданного количества писем с сайта.

    Использует LetterIdsParser для получения ID писем и LetterParser для их содержимого.

    Attributes:
        url (str): Базовый URL сайта для парсинга писем.
        letters_count (int): Необходимое количество писем для извлечения.
        letter_ids_parser (LetterIdsParser): Парсер для получения ID писем.
        letter_parser (LetterParser): Парсер для получения данных о письме.
    """

    def __init__(self, url: str, letters_count: int = 50, chunk_size: int = 24):
        """Инициализация основного парсера.

        Args:
            url (str): Базовый URL сайта для парсинга писем.
            letters_count (int, optional): Необходимое количество писем для извлечения.
                                           Default: 50.
            chunk_size (int, optional): Количество писем на одной странице. Default: 24.
        """
        self.url = url
        self.letters_count = letters_count
        self.letter_ids_parser = LetterIdsParser(url, chunk_size)
        self.letter_parser = LetterParser(url)

    async def parse_letters(self) -> List[LetterData]:
        """Выполняет полный процесс парсинга.

        Последовательно получает ID писем с каждой страницы, а затем извлекает данные
        по каждому ID до достижения нужного количества.

        Returns:
            List[LetterData]: Список объектов LetterData с данными писем.
        """
        logger.info("Starting to parse letters")
        letters_data = []
        total_parsed = 0

        page = 1
        while total_parsed < self.letters_count:
            logger.info(f"Processing page {page}")
            self.letter_ids_parser.set_page(page)
            letter_ids = await self.letter_ids_parser.get_letter_ids()

            if not letter_ids:
                logger.info(f"No letter IDs found on page {page}. Stopping.")
                break

            logger.debug(f"Found {len(letter_ids)} letter IDs on page {page}")

            if self.letters_count + len(letter_ids) > total_parsed:
                remaining_slots = self.letters_count - total_parsed
                letter_ids = letter_ids[:remaining_slots]

            for letter_id in letter_ids:
                letter_data = await self.letter_parser.get_letter_data(letter_id)
                if not letter_data:
                    continue

                letters_data.append(letter_data)
                total_parsed += 1

            page += 1

        logger.info(f"Finished parsing. Total letters parsed: {total_parsed}")
        return letters_data
