from collections.abc import Iterable

from Src.Core.Validator import validator
from Src.Dtos.filter_condition_dto import filter_condition_dto


class filter_dto:
    """Объединяет условия фильтрации, которые должны выполняться одновременно."""

    def __init__(self, conditions: Iterable[filter_condition_dto] = ()):
        """Сохраняет неизменяемый набор проверенных условий."""
        validator.validate_type(conditions, Iterable, "Условия фильтра")
        self.__conditions = tuple(conditions)
        for condition in self.__conditions:
            validator.validate_type(condition, filter_condition_dto, "Условие фильтра")

    @classmethod
    def from_dict(cls, data: dict) -> "filter_dto":
        """Создаёт фильтр из входящего словаря."""
        validator.validate_fields(data, ("conditions",))
        return cls(cls._read_conditions(data))

    @staticmethod
    def _read_conditions(data: dict) -> tuple[filter_condition_dto, ...]:
        """Восстанавливает список условий из проверенного словаря."""
        conditions = data.get("conditions", [])
        validator.validate_type(conditions, list, "Условия фильтра")
        return tuple(filter_condition_dto.from_dict(item) for item in conditions)

    @property
    def conditions(self) -> tuple[filter_condition_dto, ...]:
        """Возвращает условия отбора."""
        return self.__conditions
