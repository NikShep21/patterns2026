from enum import Enum


class comparison_type(Enum):
    """Определяет способы сравнения значений при фильтрации."""

    EQUALS = "EQUALS"
    LIKE = "LIKE"
