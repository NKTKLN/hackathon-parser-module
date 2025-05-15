"""Модуль конфигурации приложения.

Содержит класс Config для загрузки настроек из переменных окружения.
Позволяет управлять параметрами базы данных, пагинацией и внешними ресурсами.
"""

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Класс конфигурации приложения.

    Загружает настройки из .env файла и предоставляет:
        - Параметры подключения к PostgreSQL
        - URL внешнего ресурса с письмами
        - Количество писем для обработки

    Attributes:
        LETTERS_COUNT (int): Количество писем для загрузки/обработки.

        POSTGRES_HOST (str): Хост PostgreSQL сервера.
        POSTGRES_PORT (int): Порт PostgreSQL сервера.
        POSTGRES_DB (str): Имя базы данных PostgreSQL.
        POSTGRES_USER (str): Имя пользователя для подключения к БД.
        POSTGRES_PASSWORD (str): Пароль пользователя БД.
        POSTGRES_URL (str): Строка подключения к PostgreSQL (автогенерация).

        URL (str): Адрес сайта с архивом писем.
    """

    # Основные параметры
    LETTERS_COUNT: int

    # Настройки PostgreSQL
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # Внешний источник данных
    URL: str = "https://pismapobedy.ru/letters"

    @property
    def POSTGRES_URL(self) -> str:
        """Генерирует строку подключения к БД на основе параметров.

        Returns:
            str: Строка подключения к БД.
        """
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Конфигурация загрузки переменных окружения
    class Config:
        """Настройки загрузки переменных окружения из файла .env."""

        env_file = ".env"  # noqa: F841


# Единственный экземпляр конфигурации, используемый в приложении
config: Config = Config()  # type: ignore[call-arg]
