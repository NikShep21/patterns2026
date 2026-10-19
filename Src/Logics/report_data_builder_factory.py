from Src.Core.Abstract import base_entity
from Src.Core.Exceptions import validation_error
from Src.Logics.nomenclature_report_data_builder import (
    nomenclature_report_data_builder,
)
from Src.Logics.range_report_data_builder import range_report_data_builder
from Src.Logics.recipe_report_data_builder import recipe_report_data_builder
from Src.Logics.report_data_builder import report_data_builder
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model


class report_data_builder_factory:
    """Выбирает builder данных по типу сущности."""

    __builders: dict[type[base_entity], type[report_data_builder]] = {
        nomenclature_model: nomenclature_report_data_builder,
        range_model: range_report_data_builder,
        recipe_model: recipe_report_data_builder,
    }

    @classmethod
    def create(cls, source: base_entity) -> report_data_builder:
        """Создаёт builder для переданной сущности."""
        builder_class = cls.__builders.get(type(source))

        if builder_class is None:
            raise validation_error(
                f"Формирование отчёта для типа «{type(source).__name__}» "
                "не поддерживается"
            )

        return builder_class()
