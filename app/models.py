"""Модуль, содержащий модели данных для работы с архивом писем.

Этот модуль предоставляет типизированные классы для представления
информации, извлечённой с сайта архива писем. Основной класс — LetterData —
используется для хранения структурированных данных одного письма,
включая метаданные и содержание.

Available classes:
    - LetterData: Класс для представления данных письма.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class LetterData:
    """Класс для представления данных письма из архива.

    Attributes:
        id (str): Уникальный идентификатор письма (например, номер или дата).
        date (str): Дата написания письма в формате ДД.ММ.ГГГГ.
        author (str): Имя автора письма.
        text (str): Текст письма.
        url (str): Ссылка на источник или архив, где хранится письмо.
        sender (str): Отправитель письма.
        recipient (str): Получатель письма.
        destination (str): Место назначения (адрес), связанное с письмом.
    """

    id: str
    date: str
    author: str
    text: str
    url: str
    sender: str
    recipient: str
    destination: str

    def to_dict(self) -> Dict[str, str]:
        """Преобразует объект LetterData в словарь.

        Returns:
            Dict[str, str]: Словарь, содержащий все поля объекта LetterData,
                            включая 'id', 'date', 'author', 'text', 'url',
                            'sender', 'recipient', 'destination'.
        """
        return {
            "id": self.id,
            "date": self.date,
            "author": self.author,
            "text": self.text,
            "url": self.url,
            "sender": self.sender,
            "recipient": self.recipient,
            "destination": self.destination,
        }
