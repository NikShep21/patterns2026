import pytest

from Src.Core.Exceptions import validation_error
from Src.Models.range_model import range_model


def test_success_init_without_base_range_returns_self_as_base_range():
    """
    Базовая единица устанавливается базой для самой себя.
    """
    # Act
    gram = range_model("грамм", 1)

    # Assert
    assert gram.name == "грамм"
    assert gram.coefficient == 1
    assert gram.base_range is gram


def test_success_init_with_base_range_returns_passed_base_range():
    """
    Производная единица сохраняет переданную базовую единицу.
    """
    # Arrange
    gram = range_model("грамм", 1)

    # Act
    kilogram = range_model("килограмм", 1000, gram)

    # Assert
    assert kilogram.base_range is gram


def test_success_init_float_coefficient_returns_same_coefficient():
    """
    Дробный коэффициент сохраняется без изменений.
    """
    # Act
    unit = range_model("упаковка", 2.5)

    # Assert
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
    # Act / Assert
    with pytest.raises(validation_error):
        range_model("килограмм", invalid_coefficient)


def test_fail_base_range_wrong_type_raises_validation_error():
    """
    Базовая единица неверного типа вызывает ошибку валидации.
    """
    # Act / Assert
    with pytest.raises(validation_error):
        range_model("килограмм", 1000, "грамм")


def test_success_coefficient_kilogram_converts_amount_to_grams():
    """
    Коэффициент килограмма пересчитывает количество в граммы.
    """
    # Arrange
    gram = range_model("грамм", 1)
    kilogram = range_model("килограмм", 1000, gram)
    amount_in_kilograms = 2

    # Act
    amount_in_grams = amount_in_kilograms * kilogram.coefficient

    # Assert
    assert amount_in_grams == 2000
