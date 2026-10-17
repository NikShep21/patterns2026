import pytest

from Src.Core.Exceptions import validation_error
from Src.Logics.report_data_builder import report_data_builder
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_type import nomenclature_type
from Src.Models.range_model import range_model
from Src.Models.recipe_ingredient_model import recipe_ingredient_model
from Src.Models.recipe_model import recipe_model
from Src.Models.warehouse_model import warehouse_model


@pytest.fixture
def report_entities():
    """Создаёт сущности для проверки состава отчётов."""
    gram = range_model.create_gram()
    ingredients = nomenclature_group_model("Ингредиенты")
    dishes = nomenclature_group_model("Готовые блюда")
    flour = nomenclature_model(
        "Мука",
        "Мука пшеничная",
        nomenclature_type.RAW_MATERIAL,
        ingredients,
        gram,
    )
    pancakes = nomenclature_model(
        "Блины",
        "Блины классические",
        nomenclature_type.DISH,
        dishes,
        range_model.create_piece(),
    )
    recipe = recipe_model(
        "Классические блины",
        pancakes,
        [recipe_ingredient_model(flour, 0.2, 220, 200)],
        10,
        30,
        ["Замесить тесто.", "Выпекать блины."],
    )
    return gram, flour, recipe


def test_success_report_data_builder_builds_range(report_entities):
    """Проверяет состав данных единицы измерения."""
    # Подготовка
    gram, _, _ = report_entities

    # Действие
    data = report_data_builder.build(gram)["range"]

    # Проверка
    assert data["id"] == gram.id
    assert data["name"] == "Грамм"
    assert data["coefficient"] == 1
    assert data["base_range"] == {"id": gram.id, "name": "Грамм"}


def test_success_report_data_builder_builds_nomenclature(report_entities):
    """Проверяет состав данных номенклатуры."""
    # Подготовка
    _, flour, _ = report_entities

    # Действие
    data = report_data_builder.build(flour)["nomenclature"]

    # Проверка
    assert data["id"] == flour.id
    assert data["name"] == "Мука"
    assert data["full_name"] == "Мука пшеничная"
    assert data["type"] == "Сырьё"
    assert data["group"]["name"] == "Ингредиенты"
    assert data["range"]["name"] == "Грамм"


def test_success_report_data_builder_builds_recipe(report_entities):
    """Проверяет состав данных технологической карты."""
    # Подготовка
    _, _, recipe = report_entities

    # Действие
    data = report_data_builder.build(recipe)["recipe"]

    # Проверка
    assert data["id"] == recipe.id
    assert data["name"] == "Классические блины"
    assert data["result"]["name"] == "Блины"
    assert data["output_quantity"] == 10
    assert data["output_range"]["name"] == "Штука"
    assert data["cooking_time"] == 30
    assert data["gross_weight"] == 220
    assert data["net_weight"] == 200
    assert data["ingredients"][0]["nomenclature"]["name"] == "Мука"
    assert data["steps"] == ["Замесить тесто.", "Выпекать блины."]


def test_fail_report_data_builder_unsupported_entity_raises_validation_error():
    """Проверяет ошибку для неподдерживаемой сущности."""
    # Подготовка
    warehouse = warehouse_model("Основной склад", "ул. Центральная, д. 1")

    # Действие / Проверка
    with pytest.raises(validation_error):
        report_data_builder.build(warehouse)
