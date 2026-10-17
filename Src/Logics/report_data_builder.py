from Src.Core.Abstract import base_entity
from Src.Core.Exceptions import validation_error
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model


class report_data_builder:
    """Подготавливает данные поддерживаемых сущностей для отчётов."""

    @staticmethod
    def build(source: base_entity) -> dict:
        """Возвращает данные сущности в виде вложенного словаря."""
        if isinstance(source, nomenclature_model):
            return {
                "nomenclature": report_data_builder.__nomenclature(source)
            }

        if isinstance(source, range_model):
            return {"range": report_data_builder.__range(source)}

        if isinstance(source, recipe_model):
            return {"recipe": report_data_builder.__recipe(source)}

        raise validation_error(
            f"Формирование отчёта для типа «{type(source).__name__}» не поддерживается"
        )

    @staticmethod
    def flatten(data: dict) -> list[tuple[str, str]]:
        """Преобразует вложенные данные в список путей и значений."""
        result = []
        report_data_builder.__flatten_value(data, "", result)
        return result

    @staticmethod
    def __reference(source: base_entity) -> dict:
        """Возвращает краткое представление связанной сущности."""
        return {
            "id": source.id,
            "name": source.name,
        }

    @staticmethod
    def __nomenclature(source: nomenclature_model) -> dict:
        """Возвращает данные номенклатуры."""
        return {
            "id": source.id,
            "name": source.name,
            "full_name": source.full_name,
            "type": source.type.value,
            "group": report_data_builder.__reference(source.group),
            "range": report_data_builder.__reference(source.range),
        }

    @staticmethod
    def __range(source: range_model) -> dict:
        """Возвращает данные единицы измерения."""
        return {
            "id": source.id,
            "name": source.name,
            "coefficient": source.coefficient,
            "base_range": report_data_builder.__reference(source.base_range),
        }

    @staticmethod
    def __recipe(source: recipe_model) -> dict:
        """Возвращает данные технологической карты."""
        ingredients = []

        for ingredient in source.ingredients:
            data = {
                "id": ingredient.id,
                "nomenclature": report_data_builder.__reference(
                    ingredient.nomenclature
                ),
                "quantity": ingredient.quantity,
                "range": report_data_builder.__reference(
                    ingredient.nomenclature.range
                ),
                "gross_weight": ingredient.gross_weight,
                "net_weight": ingredient.net_weight,
            }

            if ingredient.recipe is not None:
                data["recipe"] = report_data_builder.__reference(
                    ingredient.recipe
                )

            ingredients.append(data)

        return {
            "id": source.id,
            "name": source.name,
            "result": report_data_builder.__reference(source.result),
            "output_quantity": source.output_quantity,
            "output_range": report_data_builder.__reference(
                source.result.range
            ),
            "cooking_time": source.cooking_time,
            "gross_weight": source.gross_weight,
            "net_weight": source.net_weight,
            "ingredients": ingredients,
            "steps": list(source.steps),
        }

    @staticmethod
    def __flatten_value(
        value,
        path: str,
        result: list[tuple[str, str]],
    ) -> None:
        """Рекурсивно добавляет простые значения в плоский список."""
        if isinstance(value, dict):
            for key, item in value.items():
                item_path = f"{path}.{key}" if path else key
                report_data_builder.__flatten_value(item, item_path, result)
            return

        if isinstance(value, (list, tuple)):
            for index, item in enumerate(value, start=1):
                report_data_builder.__flatten_value(
                    item,
                    f"{path}.{index}",
                    result,
                )
            return

        result.append((path, str(value)))
