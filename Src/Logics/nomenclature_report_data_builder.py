from Src.Dtos.report_data_dto import nomenclature_report_data_dto
from Src.Logics.report_data_builder import report_data_builder
from Src.Models.nomenclature_model import nomenclature_model


class nomenclature_report_data_builder(report_data_builder):
    """Подготавливает данные номенклатуры для отчёта."""

    def build(self, source: nomenclature_model) -> nomenclature_report_data_dto:
        return nomenclature_report_data_dto(
            id=source.id,
            name=source.name,
            full_name=source.full_name,
            type=source.type.value,
            group=self._build_reference(source.group),
            range=self._build_reference(source.range),
        )
