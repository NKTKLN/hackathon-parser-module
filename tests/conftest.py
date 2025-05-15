"""Модуль тестовых фикстур для парсеров писем.

Содержит набор фикстур, используемых при тестировании компонентов:
- LetterIdsParser — извлечение идентификаторов писем.
- LetterParser — парсинг данных конкретного письма.
- Логика создания объектов LetterData и проверка уникальности записей.

Фикстуры предоставляют:
- Моки HTTP-запросов и HTML-ответов.
- Временное хранилище писем в памяти вместо БД.
- Заглушки для функций сохранения данных.
"""

from typing import Any, Callable, List
from unittest.mock import AsyncMock

import pytest

from app.db.models import LetterData
from app.parsers import LetterIdsParser, LetterParser


@pytest.fixture
def letter_ids_parser_mock() -> LetterIdsParser:
    """Создаёт замоканный LetterIdsParser с фейковым HTML-ответом.

    Мокирует метод get_html, возвращая предопределённый HTML с тремя письмами.
    Используется для тестирования парсинга ID писем.

    Returns:
        LetterIdsParser: Настроенный мокированный экземпляр парсера ID писем.
    """
    parser = LetterIdsParser("http://example.com")
    parser.get_html = AsyncMock(  # type: ignore
        return_value="""
        <html>
          <body>
            <a class="js-open_letter" data-letter_id="id1"></a>
            <a class="js-open_letter" data-letter_id="id2"></a>
            <a class="js-open_letter" data-letter_id="id3"></a>
          </body>
        </html>
        """
    )
    return parser


@pytest.fixture
def letter_parser_mock() -> LetterParser:
    """Создаёт замоканный LetterParser с динамическим HTML для конкретного ID письма.

    При каждом вызове get_html возвращает уникальный HTML для заданного letter_id.
    Используется для тестирования парсинга данных одного письма.

    Returns:
        LetterParser: Настроенный мокированный экземпляр парсера письма.
    """
    parser = LetterParser("http://example.com")

    def letter_html(id: str) -> str:
        """Генерирует HTML-содержимое для тестового письма с заданным идентификатором.

        Используется в моках для тестирования парсинга данных письма.

        Args:
            id (str): Уникальный идентификатор письма, используемый для генерации
                      персонализированного HTML.

        Returns:
            str: Строка с HTML-разметкой, имитирующей страницу конкретного письма.
        """
        return f"""
        <div class="b-letter-text">
            <p>15.05.2025</p>
            <p><span>От кого:</span> Author {id}</p>
            <p><span>Откуда:</span> Sender {id}</p>
            <p><span>Кому:</span> Recipient {id}</p>
            <p><span>Куда:</span> Destination {id}</p>
            <div class="text">Text of letter {id}</div>
        </div>
        """

    parser.get_html = AsyncMock(  # type: ignore
        side_effect=lambda url: letter_html(url.split("#letter-")[-1])
    )
    return parser


@pytest.fixture
def created_letters() -> List[LetterData]:
    """Хранилище созданных писем в памяти.

    Используется для проверки логики добавления новых записей без обращения к БД.

    Returns:
        list: Список объектов LetterData, представляющих созданные письма.
    """
    return []  # будет хранить созданные письма


@pytest.fixture
def create_letter_mock(
    created_letters: List[LetterData],
) -> Callable[[LetterData], Any]:
    """Заглушка функции create_letter, которая сохраняет письма в памяти.

    Добавляет письмо в список только если оно ещё не существует.

    Args:
        created_letters (list): Список уже созданных писем.

    Returns:
        Callable: Мокированная асинхронная функция создания письма.
    """

    async def _create_letter(letter_data: LetterData) -> None:
        """Мок-реализация функции создания письма.

        Добавляет переданный объект LetterData в список `created_letters`, если письмо
        с таким ID ещё не было добавлено.

        Args:
            letter_data (LetterData): Объект письма, который необходимо добавить.
        """
        if letter_data.id not in {letter.id for letter in created_letters}:
            created_letters.append(letter_data)

    return _create_letter
