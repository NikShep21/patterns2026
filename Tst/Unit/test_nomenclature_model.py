import pytest

from Src.Core.Exceptions import validation_error
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


def test_success_init_valid_values_returns_created_nomenclature():
    """
    Корректные данные позволяют создать номенклатуру со связями.
    """
    # Подготовка
    group = nomenclature_group_model("Молочные продукты")
    unit = range_model("литр", 1)

    # Действие
    nomenclature = nomenclature_model(
        "Молоко",
        "Молоко питьевое пастеризованное 3,2%",
        group,
        unit,
    )

    # Проверка
    assert nomenclature.name == "Молоко"
    assert nomenclature.full_name == "Молоко питьевое пастеризованное 3,2%"
    assert nomenclature.group is group
    assert nomenclature.range is unit


def test_success_full_name_outer_spaces_returns_trimmed_value():
    """
    Полное имя сохраняется без внешних пробелов.
    """
    # Подготовка
    group = nomenclature_group_model("Молочные продукты")
    unit = range_model("литр", 1)

    # Действие
    nomenclature = nomenclature_model(
        "Молоко",
        "  Молоко питьевое  ",
        group,
        unit,
    )

    # Проверка
    assert nomenclature.full_name == "Молоко питьевое"


def test_success_full_name_max_length_returns_same_value():
    """
    Полное имя длиной 255 символов сохраняется без изменений.
    """
    # Подготовка
    group = nomenclature_group_model("Группа")
    unit = range_model("штука", 1)
    full_name = "а" * 255

    # Действие
    nomenclature = nomenclature_model(
        "Номенклатура",
        full_name,
        group,
        unit,
    )

    # Проверка
    assert nomenclature.full_name == full_name


@pytest.mark.parametrize(
    "invalid_full_name",
    (None, "", "   ", "а" * 256),
    ids=("non-string", "empty", "spaces-only", "too-long"),
)
def test_fail_full_name_invalid_value_raises_validation_error(
    invalid_full_name,
):
    """
    Некорректное полное имя вызывает ошибку валидации.
    """
    # Подготовка
    group = nomenclature_group_model("Группа")
    unit = range_model("штука", 1)

    # Действие / Проверка
    with pytest.raises(validation_error):
        nomenclature_model("Товар", invalid_full_name, group, unit)


def test_fail_group_wrong_type_raises_validation_error():
    """
    Группа неверного типа вызывает ошибку валидации.
    """
    # Подготовка
    unit = range_model("штука", 1)

    # Действие / Проверка
    with pytest.raises(validation_error):
        nomenclature_model("Товар", "Полное имя товара", "Группа", unit)


def test_fail_range_wrong_type_raises_validation_error():
    """
    Единица измерения неверного типа вызывает ошибку валидации.
    """
    # Подготовка
    group = nomenclature_group_model("Группа")

    # Действие / Проверка
    with pytest.raises(validation_error):
        nomenclature_model("Товар", "Полное имя товара", group, "штука")
