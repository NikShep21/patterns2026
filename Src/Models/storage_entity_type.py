from enum import Enum


class storage_entity_type(Enum):
    """Определяет коллекции, доступные для CRUD."""

    RANGE = "range"
    GROUP = "group"
    NOMENCLATURE = "nomenclature"
    WAREHOUSE = "warehouse"
    RECIPE = "recipe"
