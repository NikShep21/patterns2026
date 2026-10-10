from Src.Core.Abstract import base_entity
from Src.Core.Exceptions import operation_error, validation_error
from Src.Core.Validator import validator
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_type import nomenclature_type
from Src.Models.recipe_ingredient_model import recipe_ingredient_model


class recipe_model(base_entity):
    """Модель технологической карты приготовления блюда."""

    _allowed_result_types = (
        nomenclature_type.SEMI_FINISHED,
        nomenclature_type.DISH,
    )

    def __init__(
        self,
        name: str,
        result: nomenclature_model,
        ingredients: list[recipe_ingredient_model],
        output_quantity: int | float,
        cooking_time: int | float,
        steps: list[str],
    ):
        """Инициализирует технологическую карту."""
        super().__init__()
        self.name = name
        self.result = result
        self.ingredients = ingredients
        self.output_quantity = output_quantity
        self.cooking_time = cooking_time
        self.steps = steps

    @property
    def result(self) -> nomenclature_model:
        """Возвращает номенклатуру готового блюда."""
        return self.__result

    @result.setter
    def result(self, value: nomenclature_model):
        """Изменяет номенклатуру готового блюда."""
        validator.validate_type(value, nomenclature_model, "Результат")

        if value.type not in self._allowed_result_types:
            raise validation_error(
                "Результатом технологической карты может быть "
                "только полуфабрикат или блюдо"
            )

        self.__result = value

    @property
    def ingredients(self) -> tuple[recipe_ingredient_model, ...]:
        """Возвращает ингредиенты технологической карты."""
        return tuple(self.__ingredients)

    @ingredients.setter
    def ingredients(self, value: list[recipe_ingredient_model]):
        """Изменяет ингредиенты технологической карты."""
        validator.validate_type(value, list, "Ингредиенты")
        prepared_ingredients = []

        for ingredient in value:
            self.__validate_ingredient(ingredient, prepared_ingredients)
            prepared_ingredients.append(ingredient)

        self.__ingredients = prepared_ingredients

    def add_ingredient(self, value: recipe_ingredient_model) -> None:
        """Добавляет ингредиент в технологическую карту."""
        self.__validate_ingredient(value, self.__ingredients)
        self.__ingredients.append(value)

    def remove_ingredient(self, value: recipe_ingredient_model) -> None:
        """Исключает ингредиент из технологической карты."""
        validator.validate_type(value, recipe_ingredient_model, "Ингредиент")

        for ingredient in self.__ingredients:
            if ingredient.nomenclature == value.nomenclature:
                self.__ingredients.remove(ingredient)
                return

        raise operation_error(
            f"Ингредиент «{value.name}» отсутствует в технологической карте"
        )

    @property
    def output_quantity(self) -> int | float:
        """Возвращает количество единиц готового блюда."""
        return self.__output_quantity

    @output_quantity.setter
    def output_quantity(self, value: int | float):
        """Изменяет количество единиц готового блюда."""
        validator.validate_positive_number(value, "Количество на выходе")
        self.__output_quantity = value

    @property
    def cooking_time(self) -> int | float:
        """Возвращает время приготовления в минутах."""
        return self.__cooking_time

    @cooking_time.setter
    def cooking_time(self, value: int | float):
        """Изменяет время приготовления в минутах."""
        validator.validate_positive_number(value, "Время приготовления")
        self.__cooking_time = value

    @property
    def steps(self) -> tuple[str, ...]:
        """Возвращает последовательность приготовления."""
        return self.__steps

    @steps.setter
    def steps(self, value: list[str]):
        """Изменяет последовательность приготовления."""
        validator.validate_type(value, list, "Шаги приготовления")

        if not value:
            raise validation_error(
                "Поле «Шаги приготовления» не может быть пустым"
            )

        prepared_steps = []

        for step in value:
            validator.validate_required_string(step, "Шаг приготовления")
            prepared_steps.append(step.strip())

        self.__steps = tuple(prepared_steps)

    @property
    def gross_weight(self) -> int | float:
        """Вычисляет общий вес брутто всех ингредиентов."""
        return sum(
            ingredient.gross_weight for ingredient in self.__ingredients
        )

    @property
    def net_weight(self) -> int | float:
        """Вычисляет общий вес нетто всех ингредиентов."""
        return sum(
            ingredient.net_weight for ingredient in self.__ingredients
        )

    def __validate_ingredient(
        self,
        value: recipe_ingredient_model,
        ingredients: list[recipe_ingredient_model],
    ) -> None:
        """Проверяет ингредиент перед добавлением в состав."""
        validator.validate_type(value, recipe_ingredient_model, "Ингредиент")

        if value.nomenclature == self.__result:
            raise validation_error(
                "Результат технологической карты не может быть её ингредиентом"
            )

        if any(
            ingredient.nomenclature == value.nomenclature
            for ingredient in ingredients
        ):
            raise validation_error(
                f"Ингредиент «{value.name}» уже добавлен в технологическую карту"
            )
