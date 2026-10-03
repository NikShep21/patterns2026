from abc import ABC
from uuid import uuid4

from Src.Core.Validator import validator


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
        validator.validate_required_string(
            value,
            "Наименование",
            self._max_name_length,
        )
        self.__name = value.strip()

    def __eq__(self, other) -> bool:
        """Сравнивает сущности по уникальному идентификатору."""
        if not isinstance(other, base_entity):
            return NotImplemented

        return self.id == other.id
