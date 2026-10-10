import pytest

from Src.Core.Exceptions import validation_error
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_type import nomenclature_type
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model


@pytest.fixture
def loaded_managers():
    """Подготавливает менеджеры для изолированного теста."""
    settings = settings_manager()
    settings.load()
    storage = storage_manager()
    storage.clear()

    yield settings, storage

    storage.clear()
    settings.settings.is_first_start = True


def test_success_create_returns_same_storage_manager_instance():
    """Повторное создание возвращает тот же экземпляр хранилища."""
    # Действие
    first_instance = storage_manager()
    second_instance = storage_manager()

    # Проверка
    assert first_instance is second_instance


def test_success_load_on_first_start_creates_initial_data(loaded_managers):
    """Загрузка при первом запуске формирует необходимые коллекции."""
    # Подготовка
    settings, storage = loaded_managers
    settings.settings.is_first_start = True

    # Действие
    storage.load()

    # Проверка
    assert storage.is_loaded is True
    assert len(storage.ranges) == 4
    assert len(storage.groups) == 2
    assert len(storage.nomenclature) == 7
    assert len(storage.warehouses) == 1
    assert len(storage.recipes) == 1


def test_success_not_first_start_keeps_storage_empty(loaded_managers):
    """Обычный запуск не формирует первичные данные."""
    # Подготовка
    settings, storage = loaded_managers
    settings.settings.is_first_start = False

    # Действие
    storage.convert()

    # Проверка
    assert storage.is_loaded is True
    assert storage.ranges == ()
    assert storage.groups == ()
    assert storage.nomenclature == ()
    assert storage.warehouses == ()
    assert storage.recipes == ()


def test_success_repeated_convert_does_not_duplicate_initial_data(
    loaded_managers,
):
    """Повторная подготовка не создаёт дубликаты первичных данных."""
    # Подготовка
    settings, storage = loaded_managers
    settings.settings.is_first_start = True

    # Действие
    storage.convert()
    storage.convert()

    # Проверка
    assert len(storage.ranges) == 4
    assert len(storage.groups) == 2
    assert len(storage.nomenclature) == 7
    assert len(storage.warehouses) == 1
    assert len(storage.recipes) == 1


def test_success_initial_data_preserves_model_relations(loaded_managers):
    """Первичные модели ссылаются на объекты из коллекций хранилища."""
    # Подготовка
    settings, storage = loaded_managers
    settings.settings.is_first_start = True

    # Действие
    storage.load()
    gram = next(item for item in storage.ranges if item.name == "Грамм")
    kilogram = next(
        item for item in storage.ranges if item.name == "Килограмм"
    )
    ingredients = next(
        item for item in storage.groups if item.name == "Ингредиенты"
    )
    flour = next(
        item for item in storage.nomenclature if item.name == "Мука"
    )

    # Проверка
    assert kilogram.base_range is gram
    assert flour.group is ingredients
    assert flour.range is kilogram
    assert flour.type is nomenclature_type.RAW_MATERIAL


def test_success_initial_data_contains_pancake_recipe(loaded_managers):
    """Первичные данные содержат технологическую карту блинов."""
    # Подготовка
    settings, storage = loaded_managers
    settings.settings.is_first_start = True

    # Действие
    storage.load()
    recipe = storage.recipes[0]
    pancakes = next(
        item for item in storage.nomenclature if item.name == "Блины"
    )

    # Проверка
    assert recipe.name == "Классические блины"
    assert recipe.result is pancakes
    assert recipe.result.type is nomenclature_type.DISH
    assert recipe.output_quantity == 10
    assert recipe.result.range.name == "Штука"
    assert recipe.cooking_time == 30
    assert len(recipe.ingredients) == 6
    assert len(recipe.steps) == 6
    assert recipe.gross_weight == 882
    assert recipe.net_weight == 862


def test_success_storage_loads_settings_when_needed(loaded_managers):
    """Хранилище самостоятельно загружает неподготовленные настройки."""
    # Подготовка
    settings, storage = loaded_managers
    settings._is_loaded = False

    # Действие
    storage.load()

    # Проверка
    assert settings.is_loaded is True
    assert storage.is_loaded is True


def test_success_add_models_places_them_in_corresponding_collections(
    loaded_managers,
):
    """Методы добавления помещают модели в нужные коллекции."""
    # Подготовка
    _, storage = loaded_managers
    unit = range_model("Порция", 1)
    group = nomenclature_group_model("Напитки")
    product = nomenclature_model(
        "Чай",
        "Чай чёрный байховый",
        nomenclature_type.PRODUCT,
        group,
        unit,
    )
    warehouse = warehouse_model("Бар", "ул. Центральная, д. 2")

    # Действие
    storage.add_range(unit)
    storage.add_group(group)
    storage.add_nomenclature(product)
    storage.add_warehouse(warehouse)

    # Проверка
    assert storage.ranges == (unit,)
    assert storage.groups == (group,)
    assert storage.nomenclature == (product,)
    assert storage.warehouses == (warehouse,)


@pytest.mark.parametrize(
    ("add_method", "first_value", "duplicate_value"),
    (
        (
            "add_range",
            range_model("Грамм", 1),
            range_model("грамм", 1),
        ),
        (
            "add_group",
            nomenclature_group_model("Ингредиенты"),
            nomenclature_group_model("ингредиенты"),
        ),
        (
            "add_warehouse",
            warehouse_model("Основной", "Адрес 1"),
            warehouse_model("основной", "Адрес 2"),
        ),
    ),
    ids=("range", "group", "warehouse"),
)
def test_fail_duplicate_name_raises_validation_error(
    loaded_managers,
    add_method,
    first_value,
    duplicate_value,
):
    """Одинаковые наименования внутри коллекции запрещены."""
    # Подготовка
    _, storage = loaded_managers
    add = getattr(storage, add_method)
    add(first_value)

    # Действие / Проверка
    with pytest.raises(validation_error):
        add(duplicate_value)


def test_fail_duplicate_nomenclature_name_raises_validation_error(
    loaded_managers,
):
    """Дубликат наименования номенклатуры вызывает ошибку."""
    # Подготовка
    _, storage = loaded_managers
    unit = range_model("Штука", 1)
    group = nomenclature_group_model("Блюда")
    first_product = nomenclature_model(
        "Блины",
        "Блины классические",
        nomenclature_type.DISH,
        group,
        unit,
    )
    duplicate_product = nomenclature_model(
        "блины",
        "Блины с начинкой",
        nomenclature_type.DISH,
        group,
        unit,
    )
    storage.add_nomenclature(first_product)

    # Действие / Проверка
    with pytest.raises(validation_error):
        storage.add_nomenclature(duplicate_product)
