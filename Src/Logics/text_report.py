from Src.Core.Abstract import base_entity
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_data_builder_factory import report_data_builder_factory
from Src.Logics.report_data_flattener import report_data_flattener


class text_report(abstract_report):
    """Формирует отчёт в виде простого текста."""

    def build(self, source: base_entity) -> report_result_dto:
        """Формирует текстовый отчёт по сущности."""
        builder = report_data_builder_factory.create(source)
        lines = [
            f"{field}: {value}"
            for field, value in report_data_flattener.flatten(
                builder.build(source)
            )
        ]
        return report_result_dto(
            "\n".join(lines),
            "text/plain; charset=utf-8",
            "txt",
        )
