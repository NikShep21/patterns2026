from datetime import date
from enum import Enum

from Src.Core.Exceptions import operation_error
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_converter import abstract_converter
from Src.Logics.basic_converter import basic_converter
from Src.Logics.datetime_converter import datetime_converter
from Src.Logics.reference_converter import reference_converter


class convert_factory(abstract_convert_factory):
    """Рекурсивно преобразует объекты в словари по исходной структуре."""

    def __init__(self):
        """Инициализирует доступные конвертеры и путь преобразования."""
        self.__basic_converter = basic_converter()
        self.__datetime_converter = datetime_converter()
        self.__reference_converter = reference_converter(self)
        self.__path: list[object] = []

    def create(self, value) -> abstract_converter:
        """Возвращает конвертер, соответствующий типу значения."""
        if isinstance(value, date):
            return self.__datetime_converter

        if value is None or isinstance(
            value,
            (str, int, float, bool, Enum),
        ):
            return self.__basic_converter

        return self.__reference_converter

    def convert(self, source) -> dict:
        """Преобразует объект или простое значение в словарь."""
        if isinstance(source, dict):
            return self.__convert_field("value", source)["value"]

        if source is None or isinstance(
            source,
            (str, int, float, bool, Enum, date, list, tuple),
        ):
            return self.__convert_field("value", source)

        return self.__convert_object(source)

    def __convert_field(self, field_name: str, value) -> dict:
        """Преобразует именованное поле, раскрывая вложенные коллекции."""
        if isinstance(value, dict):
            data = {}
            for name, item in value.items():
                data.update(self.__convert_field(str(name), item))
            return {field_name: data}

        if isinstance(value, (list, tuple)):

            items = []
            for item in value:
                converted = self.__convert_field(field_name, item)
                items.append(converted[field_name])
            return {field_name: items}

        converter = self.create(value)
        return converter.convert(field_name, value)

    def __convert_object(self, source) -> dict:
        """Преобразует публичные свойства объекта во вложенный словарь."""
        if any(item is source for item in self.__path):
            raise operation_error(
                "Невозможно преобразовать объект с циклическими ссылками"
            )

        self.__path.append(source)

        try:
            result = {}
            for field_name in self.__get_field_names(source):
                value = getattr(source, field_name)
                result.update(self.__convert_field(field_name, value))
            return result
        finally:
            self.__path.pop()

    @staticmethod
    def __get_field_names(source) -> list[str]:
        """Возвращает публичные поля объекта в порядке наследования."""
        result = []

        for source_type in reversed(type(source).__mro__):
            for field_name, field in vars(source_type).items():
                if (
                    isinstance(field, property)
                    and not field_name.startswith("_")
                    and field_name not in result
                ):
                    result.append(field_name)

        for field_name in getattr(source, "__dict__", {}):
            if not field_name.startswith("_") and field_name not in result:
                result.append(field_name)

        return result
