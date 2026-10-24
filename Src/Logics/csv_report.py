from csv import writer
from io import StringIO

from Src.Core.Abstract import base_entity
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.convert_factory import convert_factory
from Src.Logics.report_data_flattener import report_data_flattener


class csv_report(abstract_report):
    """Формирует отчёт в формате CSV."""

    def build(self, source: base_entity) -> report_result_dto:
        """Формирует CSV-отчёт по сущности."""
        output = StringIO(newline="")
        csv_writer = writer(output, delimiter=";", lineterminator="\n")
        csv_writer.writerow(("Поле", "Значение"))
        factory = convert_factory()
        root_name = type(source).__name__.removesuffix("_model")
        csv_writer.writerows(
            report_data_flattener.flatten(
                {root_name: factory.convert(source)}
            )
        )

        return report_result_dto(
            output.getvalue().encode("utf-8"),
            "text/csv; charset=utf-8",
            "csv",
        )
