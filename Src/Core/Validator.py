from datetime import datetime, timezone
from math import isfinite

from Src.Core.Exceptions import validation_error


class validator:
    """Выполняет общие проверки значений моделей."""

    @staticmethod
    def parse_datetime(value: str | datetime, field_name: str) -> datetime:
        """Приводит ISO-дату к UTC; время без пояса считается временем UTC."""
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError as error:
                raise validation_error(
                    f"Поле «{field_name}» должно содержать ISO-дату"
                ) from error
        validator.validate_type(value, datetime, field_name)
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        try:
            return value.astimezone(timezone.utc)
        except (OverflowError, ValueError) as error:
            raise validation_error(
                f"Поле «{field_name}» выходит за диапазон дат UTC"
            ) from error

    @staticmethod
    def validate_type(value, expected_type, field_name: str):
        """Проверяет соответствие значения ожидаемому типу."""
        if not isinstance(value, expected_type):
            raise validation_error(
                f"Поле «{field_name}» имеет некорректный тип"
            )

    @staticmethod
    def validate_fields(
        data: dict, allowed: tuple[str, ...], required: tuple[str, ...] = ()
    ):
        """Проверяет состав полей входящего словаря."""
        validator.validate_type(data, dict, "Данные")
        unknown = data.keys() - set(allowed)
        missing = set(required) - data.keys()
        if unknown:
            raise validation_error(
                f"Неизвестные поля: {', '.join(sorted(map(str, unknown)))}"
            )
        if missing:
            raise validation_error(
                f"Отсутствуют обязательные поля: {', '.join(sorted(missing))}"
            )

    @staticmethod
    def validate_required_string(
        value,
        field_name: str,
        max_length: int | None = None,
    ):
        """Проверяет обязательную строку."""
        validator.validate_type(value, str, field_name)
        stripped_value = value.strip()

        if not stripped_value:
            raise validation_error(f"Поле «{field_name}» не может быть пустым")

        if max_length is not None and len(stripped_value) > max_length:
            raise validation_error(
                f"Поле «{field_name}» не может быть длиннее "
                f"{max_length} символов"
            )

    @staticmethod
    def validate_numeric_string(
        value,
        field_name: str,
        allowed_lengths: tuple[int, ...] | None = None,
    ):
        """Проверяет строку из цифр допустимой длины."""
        validator.validate_required_string(value, field_name)
        stripped_value = value.strip()

        if not stripped_value.isascii() or not stripped_value.isdigit():
            raise validation_error(
                f"Поле «{field_name}» должно содержать только цифры"
            )

        if allowed_lengths is not None and len(stripped_value) not in allowed_lengths:
            expected_lengths = " или ".join(
                str(length) for length in allowed_lengths
            )
            raise validation_error(
                f"Поле «{field_name}» должно содержать "
                f"{expected_lengths} цифр"
            )

    @staticmethod
    def validate_positive_number(value, field_name: str):
        """Проверяет положительное числовое значение."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise validation_error(
                f"Поле «{field_name}» должно быть числом"
            )

        if not isfinite(value):
            raise validation_error(
                f"Поле «{field_name}» должно быть конечным числом"
            )

        if value <= 0:
            raise validation_error(
                f"Поле «{field_name}» должно быть больше нуля"
            )
