from dataclasses import dataclass


@dataclass
class LetterData:
    """
    Класс для представления данных письма из архива.

    Атрибуты:
        id (str): Уникальный идентификатор письма (например, дата).
        title (str): Заголовок или краткое описание письма.
        date (str): Дата написания письма в формате ДД.ММ.ГГГГ.
        author (str): Имя автора письма.
        text (str): Текст письма.
        url (str): Ссылка на источник или архив, где хранится письмо.
    """

    id: str
    title: str
    date: str
    author: str
    text: str
    url: str
