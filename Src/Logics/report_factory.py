from Src.Core.Exceptions import validation_error
from Src.Core.Validator import validator
from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_report_factory import abstract_report_factory
from Src.Logics.csv_report import csv_report
from Src.Logics.html_report import html_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.text_report import text_report
from Src.Logics.xml_report import xml_report
from Src.Models.report_format import report_format
from Src.Models.settings_model import settings_model


class report_factory(abstract_report_factory):
    """Создаёт отчёты явно заданного или настроенного формата."""

    __reports: dict[report_format, type[abstract_report]] = {
        report_format.CSV: csv_report,
        report_format.MARKDOWN: markdown_report,
        report_format.XML: xml_report,
        report_format.TXT: text_report,
        report_format.HTML: html_report,
    }

    def __init__(self, settings: settings_model):
        """Инициализирует фабрику настройками приложения."""
        validator.validate_type(settings, settings_model, "Настройки")
        self.__settings = settings

    @property
    def settings(self) -> settings_model:
        """Возвращает настройки фабрики."""
        return self.__settings

    def create(self, value: report_format) -> abstract_report:
        """Создаёт отчёт указанного формата."""
        validator.validate_type(value, report_format, "Формат отчёта")
        report_class = self.__reports.get(value)

        if report_class is None:
            raise validation_error(
                f"Формат отчёта «{value.value}» не поддерживается"
            )

        return report_class()

    def create_default(self) -> abstract_report:
        """Создаёт отчёт в формате из настроек приложения."""
        return self.create(self.__settings.response_format)
