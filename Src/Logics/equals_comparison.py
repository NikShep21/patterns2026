from Src.Core.abstract_comparison import abstract_comparison
from Src.Models.comparison_type import comparison_type


class equals_comparison(abstract_comparison):
    """Проверяет полное совпадение значений."""

    comparison = comparison_type.EQUALS

    def matches(self, actual: object, expected: object) -> bool:
        """Возвращает результат сравнения на равенство."""
        return actual == expected
