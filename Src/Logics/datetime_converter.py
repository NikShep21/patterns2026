from datetime import date, datetime

from Src.Core.Exceptions import validation_error
from Src.Core.Validator import validator
from Src.Core.abstract_converter import abstract_converter


class datetime_converter(abstract_converter):
    """Преобразует дату и время в строку формата ISO 8601."""

    def convert(self, field_name: str, value) -> dict:
        """Возвращает строковое представление даты и времени."""
        validator.validate_required_string(field_name, "Наименование поля")

        if not isinstance(value, (date, datetime)):
            raise validation_error("Значение не является датой")

        return {field_name.strip(): value.isoformat()}
