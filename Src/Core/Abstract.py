from abc import ABC
from uuid import uuid4


class base_entity(ABC):
    """Базовый класс для доменных сущностей."""

    def __init__(self):
        """Инициализирует базовую сущность."""
        self.__id = str(uuid4())
        self.__name = ""

    @property
    def id(self) -> str:
        """Возвращает уникальный идентификатор сущности."""
        return self.__id

    @property
    def name(self) -> str:
        """Возвращает наименование сущности."""

        return self.__name

    @name.setter
    def name(self, value: str):
        """Изменяет наименование сущности."""
        if not value or not value.strip():
            raise ValueError("Имя не может быть пустым")

        self.__name = value.strip()
