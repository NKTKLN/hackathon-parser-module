import logging
from abc import ABC
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Parser(ABC):
    headers = {"User-Agent": "Mozilla/5.0"}

    def get_html(self, url: str) -> Optional[str]:
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None

    def parse(self, url: str) -> Optional[BeautifulSoup]:
        html = self.get_html(url)
        if not html:
            return None
        soup = BeautifulSoup(html, "html.parser")
        return soup


class LetterIdsParser(Parser):
    def __init__(self, url: str, chunk_size: int = 24, page: int = 1):
        self.page = page
        self.chunk_size = chunk_size
        self.base_url = url
        self.url = self._build_url()

    def _build_url(
        self,
    ) -> str:
        return f"{self.base_url}?order_field=published_desc&page={self.page}&per={self.chunk_size}"

    def set_page(self, page: int) -> None:
        self.page = page
        self.url = self._build_url()

    # ToDo: добавить итератор

    def get_letter_ids(self) -> List[Optional[str]]:
        soup = self.parse(self.url)
        if not soup:
            return []
        links = soup.find_all("a", class_="js-open_letter")
        return [href for link in links if (href := link.get("href"))]
