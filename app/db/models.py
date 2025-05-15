"""Модуль, содержащий модели данных для работы с архивом писем.

Этот модуль предоставляет типизированные классы для представления
информации, извлечённой с сайта архива писем. Основной класс — LetterData —
используется для хранения структурированных данных одного письма,
включая метаданные и содержание.

Classes:
    - LetterData: ORM-модель для хранения данных о письме в базе данных.
"""

from sqlalchemy import Column, DateTime, String

from app.db.database import Base


class LetterData(Base):
    """ORM-модель, представляющая данные письма из архива.

    Каждый экземпляр этого класса соответствует одной записи в таблице писем.
    Предоставляет доступ к основным полям письма: автор, дата, текст, адресат и т.д.

    Attributes:
        id (str): Уникальный идентификатор письма, служит первичным ключом.
        date (datetime): Дата написания письма (в формате datetime).
        author (str): Имя автора письма.
        text (str): Полный текст письма.
        url (str): URL-адрес источника, откуда было взято письмо.
        sender (str): Имя или данные отправителя письма.
        recipient (str): Имя или данные получателя письма.
        destination (str): Адрес или место назначения, связанное с письмом.
    """

    __tablename__ = "letters"

    id = Column(String, primary_key=True)
    date = Column(DateTime)
    author = Column(String)
    text = Column(String)
    url = Column(String)
    sender = Column(String)
    recipient = Column(String)
    destination = Column(String)
