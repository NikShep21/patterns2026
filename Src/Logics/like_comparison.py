from Src.Core.Exceptions import validation_error
from Src.Core.abstract_comparison import abstract_comparison
from Src.Models.comparison_type import comparison_type


class like_comparison(abstract_comparison):
    """Ищет подстроку без учёта регистра."""

    comparison = comparison_type.LIKE

    def prepare(self, value: object, field_types: tuple[type, ...]) -> str:
        """Разрешает поиск подстроки только в строковых полях."""
        if str not in field_types or not isinstance(value, str):
            raise validation_error("LIKE применяется только к строкам")
        return value

    def matches(self, actual: object, expected: str) -> bool:
        """Проверяет вхождение искомой строки."""
        return isinstance(actual, str) and expected.casefold() in actual.casefold()
