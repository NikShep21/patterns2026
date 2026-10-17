from enum import Enum

from Src.Core.Exceptions import validation_error
from Src.Core.Validator import validator


class report_format(Enum):
    """Определяет доступные форматы формирования отчётов."""

    CSV = "CSV"
    MARKDOWN = "Markdown"
    XML = "XML"
    TXT = "TXT"
    HTML = "HTML"

    @classmethod
    def from_string(cls, value: str) -> "report_format":
        """Возвращает формат отчёта по его строковому представлению."""
        validator.validate_required_string(value, "Формат ответа")
        prepared_value = value.strip().casefold()

        for item in cls:
            if item.value.casefold() == prepared_value:
                return item

        raise validation_error(
            f"Формат ответа «{value.strip()}» не поддерживается"
        )
