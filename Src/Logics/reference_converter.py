from Src.Core.Validator import validator
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_converter import abstract_converter


class reference_converter(abstract_converter):
    """Преобразует ссылку на объект во вложенный словарь."""

    def __init__(self, factory: abstract_convert_factory):
        """Инициализирует конвертер фабрикой преобразования объектов."""
        validator.validate_type(factory, abstract_convert_factory, "Фабрика конвертации")
        self.__factory = factory

    def convert(self, field_name: str, value) -> dict:
        """Возвращает преобразованные поля связанного объекта."""
        validator.validate_required_string(field_name, "Наименование поля")
        return {
            field_name.strip(): self.__factory.convert(value),
        }
