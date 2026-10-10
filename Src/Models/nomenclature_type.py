from enum import Enum


class nomenclature_type(Enum):
    """Определяет назначение номенклатурной позиции."""

    RAW_MATERIAL = "Сырьё"
    PRODUCT = "Продукт"
    SEMI_FINISHED = "Полуфабрикат"
    DISH = "Блюдо"
