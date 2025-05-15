"""Тесты для парсеров писем из приложения.

Содержит асинхронные тесты для проверки работы следующих компонентов:
- LetterIdsParser: извлечение списка идентификаторов писем из HTML.
- LetterParser: получение данных конкретного письма по идентификатору.
- Parser: общий парсер, который объединяет работу с идентификаторами и данными писем,
  а также создание объектов писем и проверку их количества.
"""

from typing import Callable, List, Set
from unittest.mock import patch

import pytest

from app.db.models import LetterData
from app.parsers import LetterIdsParser, LetterParser, Parser


@pytest.mark.asyncio
async def test_get_letter_ids(letter_ids_parser_mock: LetterIdsParser) -> None:
    """Тестирует метод `get_letter_ids` класса `LetterIdsParser`.

    Проверяется, что метод корректно извлекает список идентификаторов писем
    из мокированного HTML-ответа.

    Args:
        letter_ids_parser_mock (LetterIdsParser): Замоканный экземпляр LetterIdsParser.

    Asserts:
        Список идентификаторов писем равен ["id1", "id2", "id3"].
    """
    ids = await letter_ids_parser_mock.get_letter_ids()
    assert ids == ["id1", "id2", "id3"]  # noqa: S101


@pytest.mark.asyncio
async def test_get_letter_data(letter_parser_mock: LetterParser) -> None:
    """Тестирует метод `get_letter_data` класса `LetterParser`.

    Проверяется, что метод создаёт объект `LetterData` с правильными значениями полей,
    основываясь на мокированных данных.

    Args:
        letter_parser_mock (LetterParser): Замоканный экземпляр LetterParser.

    Asserts:
        - Возвращаемое значение является экземпляром LetterData.
        - Все поля объекта LetterData заполнены корректно.
    """
    letter_id = "id1"
    letter = await letter_parser_mock.get_letter_data(letter_id)

    assert isinstance(letter, LetterData)  # noqa: S101
    assert letter.id == "id1"  # noqa: S101
    assert letter.author == f"Author {letter_id}"  # noqa: S101
    assert letter.sender == f"Sender {letter_id}"  # noqa: S101
    assert letter.recipient == f"Recipient {letter_id}"  # noqa: S101
    assert letter.destination == f"Destination {letter_id}"  # noqa: S101
    assert letter.text == f"Text of letter {letter_id}"  # noqa: S101


@pytest.mark.asyncio
async def test_parser_parse_letters(
    created_letters: List[LetterData],
    create_letter_mock: Callable,
    letter_ids_parser_mock: LetterIdsParser,
    letter_parser_mock: LetterParser,
) -> None:
    """Тестирует метод `parse_letters` класса `Parser`.

    Проверяются следующие этапы:
        1. Получение списка идентификаторов писем.
        2. Парсинг данных каждого письма.
        3. Сохранение писем через create_letter.

    Используются моки для имитации внешних зависимостей.

    Args:
        created_letters (list): Список созданных писем (фикстура).
        create_letter_mock (Callable): Мок функции создания письма.
        letter_ids_parser_mock (LetterIdsParser): Мок парсера ID писем.
        letter_parser_mock (LetterParser): Мок парсера данных письма.

    Asserts:
        - Было создано ровно 3 письма.
        - Все ID уникальны и совпадают с ожидаемыми.
        - Первое письмо содержит корректные данные во всех полях.
    """
    letters_count_sequence: List[int] = [0, 0, 3]

    async def mocked_get_letters_count() -> int:
        """Мок-реализация асинхронной функции get_letters_count.

        Возвращает значения по порядку из `letters_count_sequence`.
        Если последовательность исчерпана, возвращает значение по умолчанию — 3.

        Returns:
            int: Количество писем, сохранённых в БД на момент вызова.
        """
        return letters_count_sequence.pop(0) if letters_count_sequence else 3

    with (
        patch(
            "app.parsers.LetterIdsParser.get_html", new=letter_ids_parser_mock.get_html
        ),
        patch("app.parsers.LetterParser.get_html", new=letter_parser_mock.get_html),
        patch("app.parsers.create_letter", new=create_letter_mock),
        patch("app.parsers.get_letters_count", new=mocked_get_letters_count),
    ):
        parser = Parser(url="http://example.com", letters_count=3)
        await parser.parse_letters()

    assert len(created_letters) == 3  # noqa: S101
    ids: Set[str] = {str(letter.id) for letter in created_letters}
    assert ids == {"id1", "id2", "id3"}  # noqa: S101

    first_letter = created_letters[0]
    assert first_letter.author == "Author id1"  # noqa: S101
    assert first_letter.sender == "Sender id1"  # noqa: S101
    assert first_letter.recipient == "Recipient id1"  # noqa: S101
    assert first_letter.destination == "Destination id1"  # noqa: S101
    assert first_letter.text == "Text of letter id1"  # noqa: S101
