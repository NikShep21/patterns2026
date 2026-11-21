from math import isfinite

from Src.Core.Exceptions import validation_error
from Src.Core.Validator import validator
from Src.Models.comparison_type import comparison_type


class filter_condition_dto:
    """Описывает одно сравнение публичного поля, в том числе вложенного."""

    def __init__(self, field: str, comparison: comparison_type, value: object):
        """Проверяет путь к полю, операцию и значение условия."""
        validator.validate_required_string(field, "Поле фильтра")
        parts = field.split(".")
        if any(not part.isidentifier() or part.startswith("_") for part in parts):
            raise validation_error("Некорректный путь к полю фильтра")
        validator.validate_type(comparison, comparison_type, "Операция сравнения")
        if value is not None and type(value) not in (str, int, float, bool):
            raise validation_error(
                "Значение фильтра должно быть простым значением JSON"
            )
        if isinstance(value, float) and not isfinite(value):
            raise validation_error("Значение фильтра должно быть конечным числом")
        self.__field = field
        self.__comparison = comparison
        self.__value = value

    @classmethod
    def from_dict(cls, data: dict) -> "filter_condition_dto":
        """Создаёт условие из полей JSON."""
        validator.validate_fields(
            data, ("field", "comparison", "value"), ("field", "value")
        )
        try:
            comparison = comparison_type(
                data.get("comparison", comparison_type.EQUALS.value)
            )
        except (ValueError, TypeError) as error:
            raise validation_error("Неизвестная операция сравнения") from error
        return cls(data["field"], comparison, data["value"])

    @property
    def field(self) -> str:
        """Возвращает путь к публичному полю модели."""
        return self.__field

    @property
    def comparison(self) -> comparison_type:
        """Возвращает способ сравнения."""
        return self.__comparison

    @property
    def value(self) -> object:
        """Возвращает искомое значение в представлении JSON."""
        return self.__value
