import pytest

from Src.Core.Exceptions import validation_error
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_type import nomenclature_type
from Src.Models.range_model import range_model
from Src.Models.recipe_ingredient_model import recipe_ingredient_model


@pytest.fixture
def flour():
    """Создаёт номенклатуру ингредиента."""
    group = nomenclature_group_model("Ингредиенты")
    unit = range_model.create_gram()
    return nomenclature_model(
        "Мука",
        "Мука пшеничная высшего сорта",
        nomenclature_type.RAW_MATERIAL,
        group,
        unit,
    )


def test_success_init_valid_values_returns_created_ingredient(flour):
    """Корректные данные позволяют создать ингредиент рецепта."""
    # Действие
    ingredient = recipe_ingredient_model(flour, 0.2, 200, 190)

    # Проверка
    assert ingredient.name == "Мука"
    assert ingredient.nomenclature is flour
    assert ingredient.quantity == 0.2
    assert ingredient.gross_weight == 200
    assert ingredient.net_weight == 190


@pytest.mark.parametrize(
    ("gross_weight", "net_weight"),
    (
        ("200", 190),
        (True, 1),
        (float("nan"), 1),
        (float("inf"), 1),
        (0, 0),
        (-1, 1),
        (200, "190"),
        (200, True),
        (200, 0),
        (200, -1),
    ),
    ids=(
        "gross-string",
        "gross-bool",
        "gross-nan",
        "gross-infinity",
        "gross-zero",
        "gross-negative",
        "net-string",
        "net-bool",
        "net-zero",
        "net-negative",
    ),
)
def test_fail_invalid_weight_raises_validation_error(
    flour,
    gross_weight,
    net_weight,
):
    """Некорректный вес вызывает ошибку валидации."""
    # Действие / Проверка
    with pytest.raises(validation_error):
        recipe_ingredient_model(flour, 0.2, gross_weight, net_weight)


def test_fail_net_greater_than_gross_raises_validation_error(flour):
    """Вес нетто не может превышать вес брутто."""
    # Действие / Проверка
    with pytest.raises(validation_error):
        recipe_ingredient_model(flour, 0.2, 100, 101)


def test_fail_nomenclature_wrong_type_raises_validation_error():
    """Номенклатура неверного типа вызывает ошибку валидации."""
    # Действие / Проверка
    with pytest.raises(validation_error):
        recipe_ingredient_model("Мука", 0.2, 200, 200)


@pytest.mark.parametrize(
    "quantity",
    ("0.2", True, 0, -1),
    ids=("string", "bool", "zero", "negative"),
)
def test_fail_invalid_quantity_raises_validation_error(flour, quantity):
    """Некорректное количество вызывает ошибку валидации."""
    # Действие / Проверка
    with pytest.raises(validation_error):
        recipe_ingredient_model(flour, quantity, 200, 200)
