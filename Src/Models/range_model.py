from Src.Core.Abstract import base_entity
from Src.Core.Exceptions import validation_error
from Src.Core.Validator import validator


class range_model(base_entity):
    """Модель единицы измерения."""

    def __init__(
        self,
        name: str,
        coefficient: int | float,
        base_range: "range_model | None" = None,
    ):
        """Инициализирует единицу измерения."""
        super().__init__()
        self.name = name
        self.coefficient = coefficient
        self.base_range = self if base_range is None else base_range

    @classmethod
    def create_gram(cls) -> "range_model":
        """Создаёт базовую единицу измерения «Грамм»."""
        return cls("Грамм", 1)

    @classmethod
    def create_kilogram(cls) -> "range_model":
        """Создаёт килограмм с граммом в качестве базовой единицы."""
        gram = cls.create_gram()
        return cls("Килограмм", 1000, gram)

    @classmethod
    def create_milliliter(cls) -> "range_model":
        """Создаёт базовую единицу измерения «Миллилитр»."""
        return cls("Миллилитр", 1)

    @classmethod
    def create_piece(cls) -> "range_model":
        """Создаёт базовую единицу измерения «Штука»."""
        return cls("Штука", 1)

    @property
    def coefficient(self) -> int | float:
        """Возвращает коэффициент пересчёта в базовую единицу."""
        return self.__coefficient

    @coefficient.setter
    def coefficient(self, value: int | float):
        """Изменяет коэффициент пересчёта в базовую единицу."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise validation_error("Коэффициент должен быть числом")

        if value <= 0:
            raise validation_error("Коэффициент должен быть больше нуля")

        self.__coefficient = value

    @property
    def base_range(self) -> "range_model":
        """Возвращает базовую единицу измерения."""
        return self.__base_range

    @base_range.setter
    def base_range(self, value: "range_model"):
        """Изменяет базовую единицу измерения."""
        validator.validate_type(value, range_model, "Базовая единица")
        self.__base_range = value
