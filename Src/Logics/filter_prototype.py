from collections.abc import Iterable
from copy import copy
from enum import Enum
from typing import Self

from Src.Core.Validator import validator
from Src.Core.abstract_prototype import T, abstract_prototype
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.comparison_factory import comparison_factory
from Src.Logics.property_path import property_path


class filter_prototype(abstract_prototype[T]):
    """Клонирует выборку произвольной модели по условиям DTO."""

    def __init__(self, source: Iterable[T], model: type[T]):
        """Принимает записи и класс для проверки путей даже в пустой выборке."""
        super().__init__(source)
        validator.validate_type(model, type, "Класс модели")
        for item in self.data:
            validator.validate_type(item, model, "Запись выборки")
        self.__model = model
        self.__comparisons = comparison_factory()

    def clone(self, filters: filter_dto) -> Self:
        """Возвращает новый прототип своего типа с исходными объектами моделей."""
        validator.validate_type(filters, filter_dto, "Фильтр")
        selected = self.data
        for condition in filters.conditions:
            field_types = property_path.field_types(self.__model, condition.field)
            strategy = self.__comparisons.create(condition.comparison)
            expected = strategy.prepare(condition.value, field_types)
            selected = tuple(
                item
                for item in selected
                if any(
                    strategy.matches(
                        value.value if isinstance(value, Enum) else value, expected
                    )
                    for value in property_path.values(item, condition.field)
                )
            )
        result = copy(self)
        result._data = selected
        return result
