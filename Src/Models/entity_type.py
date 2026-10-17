from enum import Enum


class entity_type(Enum):
    """Определяет доступные в отчётах типы сущностей."""

    NOMENCLATURE = "nomenclature"
    RANGE = "range"
    RECIPE = "recipe"
