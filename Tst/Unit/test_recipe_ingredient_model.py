import pytest

from Src.Core.Exceptions import validation_error
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_type import nomenclature_type
from Src.Models.range_model import range_model
from Src.Models.recipe_ingredient_model import recipe_ingredient_model
from Src.Models.recipe_model import recipe_model


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
        (None, 190),
        (0, 0),
        (-1, 1),
        (200, "190"),
        (200, True),
        (200, None),
        (200, 0),
        (200, -1),
    ),
    ids=(
        "gross-string",
        "gross-bool",
        "gross-nan",
        "gross-infinity",
        "gross-missing",
        "gross-zero",
        "gross-negative",
        "net-string",
        "net-bool",
        "net-missing",
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
    (None, "0.2", True, 0, -1),
    ids=("missing", "string", "bool", "zero", "negative"),
)
def test_fail_invalid_quantity_raises_validation_error(flour, quantity):
    """Некорректное количество вызывает ошибку валидации."""
    # Действие / Проверка
    with pytest.raises(validation_error):
        recipe_ingredient_model(flour, quantity, 200, 200)


def test_success_nested_recipe_returns_its_full_weights(flour):
    """Вес полуфабриката рассчитывается по связанной технологической карте."""
    # Подготовка
    group = nomenclature_group_model("Полуфабрикаты")
    dough = nomenclature_model(
        "Тесто",
        "Тесто для блинов",
        nomenclature_type.SEMI_FINISHED,
        group,
        range_model.create_gram(),
    )
    dough_recipe = recipe_model(
        "Тесто для блинов",
        dough,
        [recipe_ingredient_model(flour, 1, 1100, 1000)],
        1000,
        15,
        ["Замесить тесто."],
    )

    # Действие
    ingredient = recipe_ingredient_model(
        dough,
        recipe=dough_recipe,
    )

    # Проверка
    assert ingredient.recipe is dough_recipe
    assert ingredient.quantity == dough_recipe.output_quantity
    assert ingredient.gross_weight == 1100
    assert ingredient.net_weight == 1000


def test_success_semi_finished_can_use_manual_weights(flour):
    """Полуфабрикат без связанной карты использует явно заданные веса."""
    # Подготовка
    dough = nomenclature_model(
        "Тесто",
        "Тесто для блинов",
        nomenclature_type.SEMI_FINISHED,
        nomenclature_group_model("Полуфабрикаты"),
        range_model.create_gram(),
    )

    # Действие
    ingredient = recipe_ingredient_model(dough, 300, 320, 300)

    # Проверка
    assert ingredient.recipe is None
    assert ingredient.gross_weight == 320
    assert ingredient.net_weight == 300


def test_fail_nested_recipe_result_mismatch_raises_validation_error(flour):
    """Связанная карта должна создавать номенклатуру строки состава."""
    # Подготовка
    group = nomenclature_group_model("Полуфабрикаты")
    unit = range_model.create_gram()
    dough = nomenclature_model(
        "Тесто",
        "Тесто для блинов",
        nomenclature_type.SEMI_FINISHED,
        group,
        unit,
    )
    filling = nomenclature_model(
        "Начинка",
        "Начинка для блинов",
        nomenclature_type.SEMI_FINISHED,
        group,
        unit,
    )
    filling_recipe = recipe_model(
        "Начинка для блинов",
        filling,
        [recipe_ingredient_model(flour, 1, 100, 100)],
        100,
        10,
        ["Приготовить начинку."],
    )

    # Действие / Проверка
    with pytest.raises(validation_error):
        recipe_ingredient_model(dough, recipe=filling_recipe)


def test_fail_nested_recipe_with_manual_weights_raises_validation_error(flour):
    """Для вложенной карты нельзя одновременно задавать готовые веса."""
    # Подготовка
    group = nomenclature_group_model("Полуфабрикаты")
    dough = nomenclature_model(
        "Тесто",
        "Тесто для блинов",
        nomenclature_type.SEMI_FINISHED,
        group,
        range_model.create_gram(),
    )
    dough_recipe = recipe_model(
        "Тесто для блинов",
        dough,
        [recipe_ingredient_model(flour, 1, 100, 100)],
        100,
        10,
        ["Замесить тесто."],
    )

    # Действие / Проверка
    with pytest.raises(validation_error):
        recipe_ingredient_model(
            dough,
            gross_weight=100,
            net_weight=100,
            recipe=dough_recipe,
        )


def test_fail_nested_recipe_with_explicit_quantity_raises(flour):
    """Количество строки со связанной картой нельзя задавать вручную."""
    # Подготовка
    group = nomenclature_group_model("Полуфабрикаты")
    dough = nomenclature_model(
        "Тесто",
        "Тесто для блинов",
        nomenclature_type.SEMI_FINISHED,
        group,
        range_model.create_gram(),
    )
    dough_recipe = recipe_model(
        "Тесто для блинов",
        dough,
        [recipe_ingredient_model(flour, 1, 100, 100)],
        100,
        10,
        ["Замесить тесто."],
    )

    # Действие / Проверка
    with pytest.raises(validation_error):
        recipe_ingredient_model(dough, 50, recipe=dough_recipe)
