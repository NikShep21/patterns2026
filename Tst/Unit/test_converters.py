from datetime import datetime

import pytest

from Src.Core.Exceptions import validation_error
from Src.Logics.basic_converter import basic_converter
from Src.Logics.datetime_converter import datetime_converter
from Src.Logics.reference_converter import reference_converter
from Src.Models.nomenclature_type import nomenclature_type


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        ("Мука", "Мука"),
        (100, 100),
        (2.5, 2.5),
        (True, True),
        (None, None),
        (nomenclature_type.RAW_MATERIAL, "Сырьё"),
    ),
    ids=("string", "integer", "float", "boolean", "none", "enum"),
)
def test_success_basic_converter_returns_simple_value(value, expected):
    """Проверяет преобразование простых значений."""
    # Подготовка
    converter = basic_converter()

    # Действие
    result = converter.convert("field", value)

    # Проверка
    assert result == {"field": expected}


def test_success_datetime_converter_returns_iso_string():
    """Проверяет преобразование даты и времени в ISO 8601."""
    # Подготовка
    converter = datetime_converter()
    value = datetime(2026, 10, 24, 15, 30, 45)

    # Действие
    result = converter.convert("created_at", value)

    # Проверка
    assert result == {"created_at": "2026-10-24T15:30:45"}


def test_success_reference_converter_returns_nested_dictionary():
    """Проверяет преобразование ссылки на объект."""
    # Подготовка
    source = object()
    converter = reference_converter(lambda value: {"same": value is source})

    # Действие
    result = converter.convert("reference", source)

    # Проверка
    assert result == {"reference": {"same": True}}


@pytest.mark.parametrize(
    ("converter", "value"),
    (
        (basic_converter(), object()),
        (datetime_converter(), "2026-10-24"),
    ),
    ids=("basic", "datetime"),
)
def test_fail_converter_invalid_value_raises_validation_error(
    converter,
    value,
):
    """Проверяет отклонение неподдерживаемых значений."""
    # Действие / Проверка
    with pytest.raises(validation_error):
        converter.convert("field", value)


@pytest.mark.parametrize(
    "converter",
    (
        basic_converter(),
        datetime_converter(),
        reference_converter(lambda value: value),
    ),
    ids=("basic", "datetime", "reference"),
)
def test_fail_converter_empty_field_name_raises_validation_error(converter):
    """Проверяет обязательность наименования поля."""
    # Действие / Проверка
    with pytest.raises(validation_error):
        converter.convert(" ", "value")
