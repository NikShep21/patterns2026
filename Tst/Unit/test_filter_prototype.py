import pytest

from Src.Core.Exceptions import validation_error
from Src.Dtos.filter_condition_dto import filter_condition_dto
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.comparison_factory import comparison_factory
from Src.Logics.filter_prototype import filter_prototype
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.comparison_type import comparison_type
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model


def condition(field, value, comparison=comparison_type.EQUALS):
    """Собирает одно условие для проверки прототипа."""
    return filter_dto((filter_condition_dto(field, comparison, value),))


@pytest.mark.parametrize("comparison", list(comparison_type))
def test_success_comparison_factory_supports_every_declared_operation(comparison):
    """У каждого значения перечисления есть выполняющая его стратегия."""
    assert comparison_factory().create(comparison).comparison is comparison


def test_success_filter_prototype_chains_clones_without_changing_original():
    """Два последовательных отбора сохраняют исходную выборку и общие модели."""
    kilogram = range_model.create_kilogram()
    gram = kilogram.base_range
    source = filter_prototype([gram, kilogram, range_model.create_piece()], range_model)

    first = source.clone(condition("name", "ГРАММ", comparison_type.LIKE))
    second = first.clone(condition("id", kilogram.id))

    assert len(source.data) == 3
    assert first.data == (gram, kilogram)
    assert second.data == (kilogram,)
    assert second.data[0] is kilogram
    assert source is not first and first is not second
    assert second.clone(filter_dto()) is not second


def test_success_filter_prototype_clone_preserves_subclass_and_custom_state():
    """Клон сохраняет фактический подкласс и дополнительные настройки."""
    derived = type("derived_prototype", (filter_prototype,), {})
    source = derived([range_model.create_gram()], range_model)
    source.label = "Настройка"
    result = source.clone(filter_dto())
    assert type(result) is derived
    assert result.label == "Настройка"


def test_success_filter_prototype_reads_nullable_nested_unit():
    """Поиск по базовой единице находит килограмм и пропускает пустую ссылку грамма."""
    kilogram = range_model.create_kilogram()
    source = filter_prototype([kilogram.base_range, kilogram], range_model)
    assert source.clone(condition("base_range.name", "Грамм")).data == (kilogram,)
    assert source.clone(condition("base_range.id", kilogram.base_range.id)).data == (
        kilogram,
    )


def test_success_filter_prototype_reads_nested_collections_and_forward_annotations(
    monkeypatch,
):
    """Поиск проходит через состав, вложенную карту и её ингредиенты."""
    monkeypatch.setattr(settings_manager, "_settings_manager__instance", None)
    monkeypatch.setattr(storage_manager, "_storage_manager__instance", None)
    storage = storage_manager()
    storage.load()
    source = filter_prototype(storage.recipes, recipe_model)

    result = source.clone(
        condition("ingredients.recipe.ingredients.nomenclature.name", "Мука")
    )

    assert tuple(item.name for item in result.data) == ("Классические блины",)


@pytest.mark.parametrize(
    "field",
    ("missing", "base_range.missing", "_data", "name.upper", "name..id", ".name"),
)
def test_fail_filter_prototype_rejects_unknown_or_private_paths_even_without_records(field):
    """Некорректный путь выдаёт ошибку независимо от содержимого выборки."""
    with pytest.raises(validation_error):
        filter_prototype([], range_model).clone(condition(field, "x"))


def test_fail_filter_prototype_validates_conditions_after_empty_intermediate_selection():
    """Неизвестный путь не скрывается за первым фильтром без совпадений."""
    filters = filter_dto(
        (
            filter_condition_dto("name", comparison_type.EQUALS, "Нет такого"),
            filter_condition_dto("missing", comparison_type.EQUALS, "x"),
        )
    )
    with pytest.raises(validation_error):
        filter_prototype([range_model.create_gram()], range_model).clone(filters)


@pytest.mark.parametrize(
    "field,value,comparison",
    (
        ("coefficient", "1", comparison_type.EQUALS),
        ("coefficient", True, comparison_type.EQUALS),
        ("coefficient", "1", comparison_type.LIKE),
        ("name", 1, comparison_type.LIKE),
        ("base_range", "Грамм", comparison_type.EQUALS),
        ("coefficient", None, comparison_type.EQUALS),
    ),
)
def test_fail_filter_prototype_rejects_incompatible_filter_values(field, value, comparison):
    """Операции проверяют совместимость поля и значения до перебора записей."""
    with pytest.raises(validation_error):
        filter_prototype([], range_model).clone(condition(field, value, comparison))


@pytest.mark.parametrize("value", (float("nan"), float("inf"), {}, []))
def test_fail_filter_condition_rejects_non_json_scalar_values(value):
    """DTO не принимает составные или неограниченные числовые значения."""
    with pytest.raises(validation_error):
        condition("name", value)


def test_success_filter_prototype_compares_numbers_and_null():
    """Полное совпадение числа и поиск пустой базовой единицы дают ожидаемые записи."""
    kilogram = range_model.create_kilogram()
    source = filter_prototype([kilogram.base_range, kilogram], range_model)
    assert source.clone(
        condition("coefficient", 1000)
    ).data == (kilogram,)
    assert source.clone(condition("base_range", None)).data == (kilogram.base_range,)
