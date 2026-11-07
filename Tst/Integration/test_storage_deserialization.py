import json
from pathlib import Path

from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.recipe_ingredient_model import recipe_ingredient_model


def test_success_load_restores_storage_models_and_shared_references(
    tmp_path, monkeypatch,
):
    """Сверяет поля и общие ссылки с хранилищем после загрузки."""
    # Подготовка
    monkeypatch.setattr(settings_manager, "_settings_manager__instance", None)
    monkeypatch.setattr(storage_manager, "_storage_manager__instance", None)
    storage = storage_manager()
    storage.load()

    serializer = convert_factory()
    original = serializer.convert(storage)
    reordered = dict(reversed(list(original.items())))
    reordered["ranges"].reverse()
    reordered["recipes"].reverse()
    path = tmp_path / "storage.json"
    path.write_text(json.dumps(reordered, ensure_ascii=False), encoding="utf-8")

    # Действие
    factory = deserialize_factory()
    loaded = factory.load(path)

    # Проверка
    assert serializer.convert(loaded) == reordered
    for name in ("ranges", "groups", "nomenclature", "warehouses", "recipes"):
        expected = {item.id: item for item in getattr(storage, name)}
        actual = loaded[name]
        assert len(actual) == len(expected)
        for item in actual:
            assert type(item) is type(expected[item.id])
            assert item.name == expected[item.id].name

    ranges = {item.name: item for item in loaded["ranges"]}
    groups = {item.name: item for item in loaded["groups"]}
    nomenclature = {item.name: item for item in loaded["nomenclature"]}
    recipes = {item.name: item for item in loaded["recipes"]}
    assert ranges["Килограмм"].base_range is ranges["Грамм"]
    assert nomenclature["Мука"].range is ranges["Килограмм"]
    assert nomenclature["Мука"].group is groups["Ингредиенты"]

    pancakes = recipes["Классические блины"]
    dough = recipes["Тесто для блинов"]
    assert isinstance(pancakes.ingredients[0], recipe_ingredient_model)
    assert pancakes.ingredients[0].recipe is dough
    assert pancakes.ingredients[0].nomenclature is dough.result
    assert dough.ingredients[0].nomenclature is nomenclature["Мука"]
    assert factory.load(path)["ranges"][0] is not loaded["ranges"][0]


def test_success_load_restores_packaged_json():
    """Проверяет, что приложенный JSON загружается и выгружается без потерь."""
    path = Path(__file__).resolve().parents[2] / "Docs" / "Json" / "initial_data.json"
    source = json.loads(path.read_text(encoding="utf-8"))

    restored = deserialize_factory().load(path)

    assert convert_factory().convert(restored) == source
