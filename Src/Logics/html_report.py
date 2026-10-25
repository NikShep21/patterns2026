from html import escape

from Src.Core.Abstract import base_entity
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_data_builder_factory import report_data_builder_factory
from Src.Logics.report_data_flattener import report_data_flattener


class html_report(abstract_report):
    """Формирует отчёт в формате HTML."""

    def build(self, source: base_entity) -> report_result_dto:
        """Формирует HTML-отчёт по сущности."""
        rows = []

        builder = report_data_builder_factory.create(source)

        for field, value in report_data_flattener.flatten(
            builder.build(source)
        ):
            rows.append(
                "<tr>"
                f"<th>{escape(field)}</th>"
                f"<td>{escape(value)}</td>"
                "</tr>"
            )

        content = (
            "<!DOCTYPE html>\n"
            '<html lang="ru">\n'
            '<head><meta charset="utf-8"><title>Отчёт</title></head>\n'
            "<body>\n"
            "<table>\n"
            f"{'\n'.join(rows)}\n"
            "</table>\n"
            "</body>\n"
            "</html>"
        )

        return report_result_dto(
            content,
            "text/html; charset=utf-8",
            "html",
        )
