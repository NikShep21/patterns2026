from Src.Core.Exceptions import validation_error
from Src.Core.Validator import validator
from Src.Core.abstract_comparison import abstract_comparison
from Src.Logics.equals_comparison import equals_comparison
from Src.Logics.like_comparison import like_comparison
from Src.Models.comparison_type import comparison_type


class comparison_factory:
    """Выбирает реализацию сравнения по её зарегистрированной операции."""

    def __init__(self):
        """Регистрирует поддерживаемые стратегии сравнения."""
        self.__strategies = {
            strategy.comparison: strategy()
            for strategy in (
                equals_comparison,
                like_comparison,
            )
        }

    def create(self, comparison: comparison_type) -> abstract_comparison:
        """Возвращает стратегию или сообщает о неизвестной операции."""
        validator.validate_type(comparison, comparison_type, "Операция сравнения")
        strategy = self.__strategies.get(comparison)
        if strategy is None:
            raise validation_error("Неизвестная операция сравнения")
        return strategy
