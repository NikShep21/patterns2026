import pytest

from Src.Core.Exceptions import operation_error, validation_error
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_type import nomenclature_type
from Src.Models.range_model import range_model
from Src.Models.recipe_ingredient_model import recipe_ingredient_model
from Src.Models.recipe_model import recipe_model


@pytest.fixture
def recipe_data():
    """Создаёт данные технологической карты."""
    gram = range_model.create_gram()
    piece = range_model.create_piece()
    ingredients_group = nomenclature_group_model("Ингредиенты")
    dishes_group = nomenclature_group_model("Готовые блюда")
    flour = nomenclature_model(
        "Мука",
        "Мука пшеничная",
        nomenclature_type.RAW_MATERIAL,
        ingredients_group,
        gram,
    )
    egg = nomenclature_model(
        "Яйцо",
        "Яйцо куриное",
        nomenclature_type.RAW_MATERIAL,
        ingredients_group,
        piece,
    )
    pancakes = nomenclature_model(
        "Блины",
        "Блины классические",
        nomenclature_type.DISH,
        dishes_group,
        piece,
    )
    ingredients = [
        recipe_ingredient_model(flour, 0.2, 200, 200),
        recipe_ingredient_model(egg, 2, 120, 100),
    ]
    return pancakes, ingredients


def test_success_init_valid_values_returns_created_recipe(recipe_data):
    """Корректные данные позволяют создать технологическую карту."""
    # Подготовка
    result, ingredients = recipe_data

    # Действие
    recipe = recipe_model(
        "Классические блины",
        result,
        ingredients,
        10,
        30,
        ["Замесить тесто.", "Выпекать блины."],
    )

    # Проверка
    assert recipe.name == "Классические блины"
    assert recipe.result is result
    assert recipe.ingredients == tuple(ingredients)
    assert recipe.output_quantity == 10
    assert recipe.result.range.name == "Штука"
    assert recipe.cooking_time == 30
    assert recipe.steps == ("Замесить тесто.", "Выпекать блины.")


def test_success_weights_return_sums_of_ingredient_weights(recipe_data):
    """Брутто и нетто рецепта вычисляются суммированием ингредиентов."""
    # Подготовка
    result, ingredients = recipe_data
    recipe = recipe_model(
        "Классические блины",
        result,
        ingredients,
        10,
        30,
        ["Приготовить блины."],
    )

    # Действие
    gross_weight = recipe.gross_weight
    net_weight = recipe.net_weight

    # Проверка
    assert gross_weight == 320
    assert net_weight == 300


def test_success_add_and_remove_ingredient_recalculates_weights(recipe_data):
    """Добавление и исключение ингредиента изменяет итоговые веса."""
    # Подготовка
    result, ingredients = recipe_data
    recipe = recipe_model(
        "Классические блины",
        result,
        [ingredients[0]],
        10,
        30,
        ["Приготовить блины."],
    )

    # Действие / Проверка
    assert recipe.gross_weight == 200
    assert recipe.net_weight == 200

    recipe.add_ingredient(ingredients[1])

    assert recipe.gross_weight == 320
    assert recipe.net_weight == 300

    recipe.remove_ingredient(ingredients[0])

    assert recipe.gross_weight == 120
    assert recipe.net_weight == 100


def test_fail_duplicate_ingredient_raises_validation_error(recipe_data):
    """Повторная номенклатура в составе рецепта запрещена."""
    # Подготовка
    result, ingredients = recipe_data
    recipe = recipe_model(
        "Классические блины",
        result,
        ingredients,
        10,
        30,
        ["Приготовить блины."],
    )
    duplicate = recipe_ingredient_model(
        ingredients[0].nomenclature,
        0.1,
        100,
        100,
    )

    # Действие / Проверка
    with pytest.raises(validation_error):
        recipe.add_ingredient(duplicate)


def test_fail_remove_missing_ingredient_raises_operation_error(recipe_data):
    """Исключение отсутствующего ингредиента вызывает ошибку операции."""
    # Подготовка
    result, ingredients = recipe_data
    recipe = recipe_model(
        "Классические блины",
        result,
        [ingredients[0]],
        10,
        30,
        ["Приготовить блины."],
    )

    # Действие / Проверка
    with pytest.raises(operation_error):
        recipe.remove_ingredient(ingredients[1])


def test_success_semi_finished_can_be_recipe_result(recipe_data):
    """Полуфабрикат может быть результатом технологической карты."""
    # Подготовка
    result, ingredients = recipe_data
    result.type = nomenclature_type.SEMI_FINISHED

    # Действие
    recipe = recipe_model(
        "Тесто для блинов",
        result,
        ingredients,
        1,
        15,
        ["Замесить тесто."],
    )

    # Проверка
    assert recipe.result.type is nomenclature_type.SEMI_FINISHED


def test_fail_raw_material_as_recipe_result_raises_validation_error(
    recipe_data,
):
    """Сырьё не может быть результатом технологической карты."""
    # Подготовка
    result, ingredients = recipe_data
    result.type = nomenclature_type.RAW_MATERIAL

    # Действие / Проверка
    with pytest.raises(validation_error):
        recipe_model(
            "Некорректная карта",
            result,
            ingredients,
            1,
            15,
            ["Приготовить."],
        )


@pytest.mark.parametrize(
    ("output_quantity", "cooking_time"),
    (
        (0, 30),
        (-1, 30),
        (True, 30),
        (10, 0),
        (10, -1),
        (10, "30"),
    ),
    ids=(
        "output-zero",
        "output-negative",
        "output-bool",
        "time-zero",
        "time-negative",
        "time-string",
    ),
)
def test_fail_invalid_positive_value_raises_validation_error(
    recipe_data,
    output_quantity,
    cooking_time,
):
    """Некорректный выход или время вызывает ошибку валидации."""
    # Подготовка
    result, ingredients = recipe_data

    # Действие / Проверка
    with pytest.raises(validation_error):
        recipe_model(
            "Классические блины",
            result,
            ingredients,
            output_quantity,
            cooking_time,
            ["Приготовить блины."],
        )


@pytest.mark.parametrize(
    "ingredients",
    (["Мука"], "Мука"),
    ids=("wrong-item-type", "wrong-collection-type"),
)
def test_fail_invalid_ingredients_raises_validation_error(
    recipe_data,
    ingredients,
):
    """Некорректная коллекция ингредиентов вызывает ошибку."""
    # Подготовка
    result, _ = recipe_data

    # Действие / Проверка
    with pytest.raises(validation_error):
        recipe_model(
            "Классические блины",
            result,
            ingredients,
            10,
            30,
            ["Приготовить блины."],
        )


@pytest.mark.parametrize(
    "steps",
    ([], [""], ["   "], [1], "Приготовить блины"),
    ids=("empty", "empty-step", "spaces", "wrong-item", "wrong-type"),
)
def test_fail_invalid_steps_raises_validation_error(recipe_data, steps):
    """Некорректные шаги приготовления вызывают ошибку."""
    # Подготовка
    result, ingredients = recipe_data

    # Действие / Проверка
    with pytest.raises(validation_error):
        recipe_model(
            "Классические блины",
            result,
            ingredients,
            10,
            30,
            steps,
        )
