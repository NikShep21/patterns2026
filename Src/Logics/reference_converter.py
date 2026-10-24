from collections.abc import Callable

from Src.Core.Validator import validator
from Src.Core.abstract_converter import abstract_converter


class reference_converter(abstract_converter):
    """Преобразует ссылку на объект во вложенный словарь."""

    def __init__(self, convert_reference: Callable):
        """Инициализирует конвертер функцией раскрытия объекта."""
        self.__convert_reference = convert_reference

    def convert(self, field_name: str, value) -> dict:
        """Возвращает преобразованные поля связанного объекта."""
        validator.validate_required_string(field_name, "Наименование поля")
        return {
            field_name.strip(): self.__convert_reference(value),
        }
