from Src.Dtos.report_data_dto import (
    recipe_ingredient_report_data_dto,
    recipe_report_data_dto,
)
from Src.Logics.report_data_builder import report_data_builder
from Src.Models.recipe_model import recipe_model


class recipe_report_data_builder(report_data_builder):
    """Подготавливает данные технологической карты для отчёта."""

    def build(self, source: recipe_model) -> recipe_report_data_dto:
        ingredients = tuple(
            recipe_ingredient_report_data_dto(
                id=ingredient.id,
                nomenclature=self._build_reference(ingredient.nomenclature),
                quantity=ingredient.quantity,
                range=self._build_reference(ingredient.nomenclature.range),
                gross_weight=ingredient.gross_weight,
                net_weight=ingredient.net_weight,
                recipe=self._build_reference(ingredient.recipe),
            )
            for ingredient in source.ingredients
        )

        return recipe_report_data_dto(
            id=source.id,
            name=source.name,
            result=self._build_reference(source.result),
            output_quantity=source.output_quantity,
            output_range=self._build_reference(source.result.range),
            cooking_time=source.cooking_time,
            gross_weight=source.gross_weight,
            net_weight=source.net_weight,
            ingredients=ingredients,
            steps=source.steps,
        )
