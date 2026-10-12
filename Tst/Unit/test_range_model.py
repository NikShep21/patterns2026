import pytest

from Src.Core.Exceptions import validation_error
from Src.Models.range_model import range_model


def test_success_create_gram_returns_base_gram():
    """Фабричный метод создаёт грамм как базовую единицу."""
    # Действие
    gram = range_model.create_gram()

    # Проверка
    assert gram.name == "Грамм"
    assert gram.coefficient == 1
    assert gram.base_range is gram


def test_success_create_kilogram_returns_unit_based_on_gram():
    """Фабричный метод создаёт килограмм с базой в граммах."""
    # Действие
    kilogram = range_model.create_kilogram()

    # Проверка
    assert kilogram.name == "Килограмм"
    assert kilogram.coefficient == 1000
    assert kilogram.base_range.name == "Грамм"
    assert kilogram.base_range.coefficient == 1
    assert kilogram.base_range.base_range is kilogram.base_range


@pytest.mark.parametrize(
    ("factory", "expected_name"),
    (
        (range_model.create_milliliter, "Миллилитр"),
        (range_model.create_piece, "Штука"),
    ),
    ids=("milliliter", "piece"),
)
def test_success_create_base_range_returns_expected_unit(
    factory,
    expected_name,
):
    """Фабричные методы создают ожидаемые базовые единицы."""
    # Действие
    unit = factory()

    # Проверка
    assert unit.name == expected_name
    assert unit.coefficient == 1
    assert unit.base_range is unit


def test_success_init_without_base_range_returns_self_as_base_range():
    """
    Базовая единица устанавливается базой для самой себя.
    """
    # Действие
    gram = range_model("грамм", 1)

    # Проверка
    assert gram.name == "грамм"
    assert gram.coefficient == 1
    assert gram.base_range is gram


def test_success_init_with_base_range_returns_passed_base_range():
    """
    Производная единица сохраняет переданную базовую единицу.
    """
    # Подготовка
    gram = range_model("грамм", 1)

    # Действие
    kilogram = range_model("килограмм", 1000, gram)

    # Проверка
    assert kilogram.base_range is gram


def test_success_init_float_coefficient_returns_same_coefficient():
    """
    Дробный коэффициент сохраняется без изменений.
    """
    # Действие
    unit = range_model("упаковка", 2.5)

    # Проверка
    assert unit.coefficient == 2.5


@pytest.mark.parametrize(
    "invalid_coefficient",
    ("1000", True, 0, -1000),
    ids=("non-numeric", "boolean", "zero", "negative"),
)
def test_fail_coefficient_invalid_value_raises_validation_error(
    invalid_coefficient,
):
    """
    Некорректный коэффициент вызывает ошибку валидации.
    """
    # Действие / Проверка
    with pytest.raises(validation_error):
        range_model("килограмм", invalid_coefficient)


def test_fail_base_range_wrong_type_raises_validation_error():
    """
    Базовая единица неверного типа вызывает ошибку валидации.
    """
    # Действие / Проверка
    with pytest.raises(validation_error):
        range_model("килограмм", 1000, "грамм")


def test_success_coefficient_kilogram_converts_amount_to_grams():
    """
    Коэффициент килограмма пересчитывает количество в граммы.
    """
    # Подготовка
    gram = range_model("грамм", 1)
    kilogram = range_model("килограмм", 1000, gram)
    amount_in_kilograms = 2

    # Действие
    amount_in_grams = amount_in_kilograms * kilogram.coefficient

    # Проверка
    assert amount_in_grams == 2000
