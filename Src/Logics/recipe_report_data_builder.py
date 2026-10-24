from Src.Logics.report_data_builder import report_data_builder
from Src.Models.recipe_model import recipe_model


class recipe_report_data_builder(report_data_builder):
    """Подготавливает данные технологической карты для отчёта."""

    def build(self, source: recipe_model) -> dict:
        """Возвращает данные технологической карты в виде словаря."""
        ingredients = []

        for ingredient in source.ingredients:
            data = {
                "id": ingredient.id,
                "nomenclature": self._build_reference(
                    ingredient.nomenclature
                ),
                "quantity": ingredient.quantity,
                "range": self._build_reference(
                    ingredient.nomenclature.range
                ),
                "gross_weight": ingredient.gross_weight,
                "net_weight": ingredient.net_weight,
            }

            if ingredient.recipe is not None:
                data["recipe"] = self._build_reference(ingredient.recipe)

            ingredients.append(data)

        return {
            "recipe": {
                "id": source.id,
                "name": source.name,
                "result": self._build_reference(source.result),
                "output_quantity": source.output_quantity,
                "output_range": self._build_reference(
                    source.result.range
                ),
                "cooking_time": source.cooking_time,
                "gross_weight": source.gross_weight,
                "net_weight": source.net_weight,
                "ingredients": ingredients,
                "steps": list(source.steps),
            }
        }
