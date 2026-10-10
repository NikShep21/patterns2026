from Src.Core.Abstract import base_entity
from Src.Core.Exceptions import validation_error
from Src.Core.Validator import validator
from Src.Models.nomenclature_model import nomenclature_model


class recipe_ingredient_model(base_entity):
    """Модель ингредиента технологической карты."""

    def __init__(
        self,
        nomenclature: nomenclature_model,
        quantity: int | float,
        gross_weight: int | float,
        net_weight: int | float,
    ):
        """Инициализирует ингредиент и его нормативные веса."""
        super().__init__()
        self.__gross_weight = 0
        self.__net_weight = 0
        self.nomenclature = nomenclature
        self.quantity = quantity
        self.gross_weight = gross_weight
        self.net_weight = net_weight

    @property
    def nomenclature(self) -> nomenclature_model:
        """Возвращает номенклатуру ингредиента."""
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, value: nomenclature_model):
        """Изменяет номенклатуру ингредиента."""
        validator.validate_type(value, nomenclature_model, "Номенклатура")
        self.__nomenclature = value
        self.name = value.name

    @property
    def quantity(self) -> int | float:
        """Возвращает количество ингредиента в его единице измерения."""
        return self.__quantity

    @quantity.setter
    def quantity(self, value: int | float):
        """Изменяет количество ингредиента."""
        validator.validate_positive_number(value, "Количество ингредиента")
        self.__quantity = value

    @property
    def gross_weight(self) -> int | float:
        """Возвращает вес ингредиента до первичной обработки."""
        return self.__gross_weight

    @gross_weight.setter
    def gross_weight(self, value: int | float):
        """Изменяет вес ингредиента до первичной обработки."""
        validator.validate_positive_number(value, "Вес брутто")

        if self.__net_weight > value:
            raise validation_error(
                "Вес брутто не может быть меньше веса нетто"
            )

        self.__gross_weight = value

    @property
    def net_weight(self) -> int | float:
        """Возвращает вес ингредиента после первичной обработки."""
        return self.__net_weight

    @net_weight.setter
    def net_weight(self, value: int | float):
        """Изменяет вес ингредиента после первичной обработки."""
        validator.validate_positive_number(value, "Вес нетто")

        if value > self.__gross_weight:
            raise validation_error(
                "Вес нетто не может быть больше веса брутто"
            )

        self.__net_weight = value
