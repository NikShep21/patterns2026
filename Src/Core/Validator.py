from Src.Core.Exceptions import validation_error


class validator:
    """Выполняет общие проверки значений моделей."""

    @staticmethod
    def validate_type(value, expected_type, field_name: str):
        """Проверяет соответствие значения ожидаемому типу."""
        if not isinstance(value, expected_type):
            raise validation_error(
                f"Поле «{field_name}» имеет некорректный тип"
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
