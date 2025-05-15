"""Модуль для работы с письмами в базе данных.

Содержит асинхронные функции для создания записей о письмах и получения общего
количества писем.
"""

import logging
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from app.config import config
from app.db.database import get_session
from app.db.models import LetterData

# Инициализация логгера
logger: logging.Logger = logging.getLogger(__name__)


async def create_letter(new_letter: LetterData) -> None:
    """Создать новую запись письма в базе данных, при отсутсвии.

    Args:
        new_letter (LetterData): Объект письма, который нужно добавить в БД.

    Raises:
        SQLAlchemyError: Если произошла ошибка при взаимодействии с БД.
    """
    try:
        async for session in get_session():
            # Проверяем, существует ли письмо с таким id
            result = await session.execute(
                select(LetterData).filter(LetterData.id == new_letter.id)
            )
            letter: Optional[LetterData] = result.scalars().first()

            if letter:
                logger.info(f"Letter with ID {new_letter.id} already exists. Skipping.")
                return

            # Добавляем новое письмо
            session.add(new_letter)
            await session.commit()
            await session.refresh(new_letter)

            logger.info(f"Letter with ID {new_letter.id} successfully created.")
    except SQLAlchemyError as e:
        logger.error(f"Database error while creating letter: {e}")
        raise


async def get_letters_count() -> int:
    """Получить общее количество писем в базе данных.

    Returns:
        int: Количество записей писем в таблице `letters`.

    Raises:
        SQLAlchemyError: Если произошла ошибка при выполнении запроса к БД.
    """
    try:
        async for session in get_session():
            result = await session.execute(select(func.count()).select_from(LetterData))
            count: int = result.scalar_one()
            logger.info(f"Total letters in DB: {count}")
            return count
        return config.LETTERS_COUNT
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching letters count: {e}")
        raise


async def get_letter_by_id(letter_id: str) -> Optional[LetterData]:
    """Получить письмо по его ID.

    Args:
        letter_id (str): ID письма, которое нужно получить.

    Returns:
        Optional[LetterData]: Объект письма, если найдено, иначе None.
    """
    try:
        async for session in get_session():
            result = await session.execute(
                select(LetterData).filter(LetterData.id == letter_id)
            )
            letter: Optional[LetterData] = result.scalars().first()
            return letter
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching letter by ID: {e}")
        raise
