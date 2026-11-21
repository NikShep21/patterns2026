from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

from Src.Core.Exceptions import validation_error
from Src.Core.Validator import validator
from Src.Models.comparison_type import comparison_type


class abstract_comparison(ABC):
    """Задаёт проверку значения и выполнение операции сравнения."""

    comparison: comparison_type

    def prepare(self, value: object, field_types: tuple[type, ...]) -> object:
        """Проверяет совместимость значения с объявленным типом поля."""
        if value is None and type(None) in field_types:
            return value
        for field_type in field_types:
            if field_type is datetime:
                return validator.parse_datetime(value, "Значение фильтра")
            if issubclass(field_type, Enum):
                try:
                    return field_type(value).value
                except ValueError:
                    continue
            if field_type is bool and type(value) is bool:
                return value
            if field_type in (int, float) and type(value) in (int, float):
                return value
            if field_type is str and type(value) is str:
                return value
        raise validation_error("Значение фильтра не соответствует типу поля")

    @abstractmethod
    def matches(self, actual: object, expected: object) -> bool:
        """Проверяет соответствие фактического значения условию."""
        pass
