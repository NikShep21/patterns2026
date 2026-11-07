from Src.Dtos.report_data_dto import range_report_data_dto
from Src.Logics.report_data_builder import report_data_builder
from Src.Models.range_model import range_model


class range_report_data_builder(report_data_builder):
    """Подготавливает данные единицы измерения для отчёта."""

    def build(self, source: range_model) -> range_report_data_dto:
        return range_report_data_dto(
            id=source.id,
            name=source.name,
            coefficient=source.coefficient,
            base_range=self._build_reference(source.base_range),
        )
