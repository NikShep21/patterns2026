from enum import Enum

from Src.Core.Exceptions import validation_error
from Src.Core.Validator import validator
from Src.Core.abstract_converter import abstract_converter


class basic_converter(abstract_converter):
    """Преобразует простые значения в словарь."""

    def convert(self, field_name: str, value) -> dict:
        """Возвращает строку, число, логическое значение или None."""
        validator.validate_required_string(field_name, "Наименование поля")

        if isinstance(value, Enum):
            value = value.value
        elif value is not None and not isinstance(
            value,
            (str, int, float, bool),
        ):
            raise validation_error("Значение не является простым типом")

        return {field_name.strip(): value}
