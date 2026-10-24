from Src.Core.Abstract import base_entity
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_data_builder_factory import report_data_builder_factory
from Src.Logics.report_data_flattener import report_data_flattener


class markdown_report(abstract_report):
    """Формирует отчёт в формате Markdown."""

    def build(self, source: base_entity) -> report_result_dto:
        """Формирует Markdown-отчёт по сущности."""
        lines = [
            "| Поле | Значение |",
            "| --- | --- |",
        ]

        builder = report_data_builder_factory.create(source)

        for field, value in report_data_flattener.flatten(
            builder.build(source)
        ):
            prepared_value = value.replace("|", "\\|").replace("\n", "<br>")
            lines.append(f"| {field} | {prepared_value} |")

        content = "\n".join(lines).encode("utf-8")
        return report_result_dto(
            content,
            "text/markdown; charset=utf-8",
            "md",
        )
