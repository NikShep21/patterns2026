from abc import ABC
from uuid import uuid4

from Src.Core.Exceptions import validation_error


class base_entity(ABC):
    """Базовый класс для доменных сущностей."""

    _max_name_length = 50

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
        if not isinstance(value, str):
            raise validation_error("Наименование должно иметь строковый тип")

        if not value.strip():
            raise validation_error("Наименование не может быть пустым")

        value = value.strip()

        if len(value) > self._max_name_length:
            raise validation_error(
                f"Наименование не может быть длиннее {self._max_name_length} символов"
            )

        self.__name = value
