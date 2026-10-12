from typing import TYPE_CHECKING

from Src.Core.Abstract import base_entity
from Src.Core.Exceptions import validation_error
from Src.Core.Validator import validator
from Src.Models.nomenclature_model import nomenclature_model

if TYPE_CHECKING:
    from Src.Models.recipe_model import recipe_model


class recipe_ingredient_model(base_entity):
    """Модель ингредиента технологической карты."""

    def __init__(
        self,
        nomenclature: nomenclature_model,
        quantity: int | float | None = None,
        gross_weight: int | float | None = None,
        net_weight: int | float | None = None,
        recipe: "recipe_model | None" = None,
    ):
        """Инициализирует ингредиент или вложенный полуфабрикат."""
        super().__init__()
        self.__gross_weight = 0
        self.__net_weight = 0
        self.__quantity = 0
        self.__recipe = None
        self.nomenclature = nomenclature
        self.__recipe = self.__validate_recipe(recipe)

        if self.__recipe is not None:
            if quantity is not None:
                raise validation_error(
                    "Количество ингредиента со связанной картой определяется её выходом"
                )

            if gross_weight is not None or net_weight is not None:
                raise validation_error(
                    "Для ингредиента с технологической картой веса "
                    "рассчитываются автоматически"
                )
            return

        if quantity is None:
            raise validation_error(
                "Для обычного ингредиента необходимо указать количество"
            )

        if gross_weight is None or net_weight is None:
            raise validation_error(
                "Для обычного ингредиента необходимо указать веса "
                "брутто и нетто"
            )

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
        if self.__recipe is not None:
            return self.__recipe.output_quantity

        return self.__quantity

    @quantity.setter
    def quantity(self, value: int | float):
        """Изменяет количество ингредиента."""
        if self.__recipe is not None:
            raise validation_error(
                "Количество ингредиента со связанной картой определяется её выходом"
            )

        validator.validate_positive_number(value, "Количество ингредиента")
        self.__quantity = value

    @property
    def recipe(self) -> "recipe_model | None":
        """Возвращает технологическую карту полуфабриката."""
        return self.__recipe

    @property
    def gross_weight(self) -> int | float:
        """Возвращает вес ингредиента до первичной обработки."""
        if self.__recipe is not None:
            return self.__recipe.gross_weight

        return self.__gross_weight

    @gross_weight.setter
    def gross_weight(self, value: int | float):
        """Изменяет вес ингредиента до первичной обработки."""
        if self.__recipe is not None:
            raise validation_error(
                "Вес ингредиента с технологической картой "
                "рассчитывается автоматически"
            )

        validator.validate_positive_number(value, "Вес брутто")

        if self.__net_weight > value:
            raise validation_error(
                "Вес брутто не может быть меньше веса нетто"
            )

        self.__gross_weight = value

    @property
    def net_weight(self) -> int | float:
        """Возвращает вес ингредиента после первичной обработки."""
        if self.__recipe is not None:
            return self.__recipe.net_weight

        return self.__net_weight

    @net_weight.setter
    def net_weight(self, value: int | float):
        """Изменяет вес ингредиента после первичной обработки."""
        if self.__recipe is not None:
            raise validation_error(
                "Вес ингредиента с технологической картой "
                "рассчитывается автоматически"
            )

        validator.validate_positive_number(value, "Вес нетто")

        if value > self.__gross_weight:
            raise validation_error(
                "Вес нетто не может быть больше веса брутто"
            )

        self.__net_weight = value

    def __validate_recipe(
        self,
        value: "recipe_model | None",
    ) -> "recipe_model | None":
        """Проверяет связанную технологическую карту."""
        if value is None:
            return None

        from Src.Models.recipe_model import recipe_model

        validator.validate_type(value, recipe_model, "Технологическая карта")

        if value.result != self.__nomenclature:
            raise validation_error(
                "Результат карты не соответствует номенклатуре ингредиента"
            )

        return value
