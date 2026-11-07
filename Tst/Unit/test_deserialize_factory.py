import json
from pathlib import Path

import pytest

from Src.Core.Exceptions import validation_error
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.warehouse_model import warehouse_model


@pytest.fixture
def initial_data():
    path = Path(__file__).resolve().parents[2] / "Docs" / "Json" / "initial_data.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_success_deserialize_factory_restores_kilogram_with_gram():
    """Проверяет восстановление килограмма, его базовой единицы и их ID."""
    # Подготовка
    kilogram = range_model.create_kilogram()
    source = json.loads(json.dumps(convert_factory().convert(kilogram)))

    # Действие
    restored = deserialize_factory().deserialize(source)

    # Проверка
    assert isinstance(restored, range_model)
    assert restored.id == kilogram.id
    assert restored.name == "Килограмм"
    assert restored.coefficient == 1000
    assert isinstance(restored.base_range, range_model)
    assert restored.base_range.id == kilogram.base_range.id
    assert restored.base_range.name == "Грамм"
    assert restored.base_range.coefficient == 1
    assert restored.base_range.base_range is None


@pytest.mark.parametrize(
    ("collection", "model"),
    (
        ("groups", nomenclature_group_model),
        ("nomenclature", nomenclature_model),
        ("warehouses", warehouse_model),
        ("recipes", recipe_model),
    ),
)
def test_success_deserialize_factory_restores_models_from_export(
    initial_data, collection, model,
):
    """Проверяет, что модели из выгрузки восстанавливаются со всеми полями."""
    deserializer = deserialize_factory()
    serializer = convert_factory()

    for source in initial_data[collection]:
        restored = deserializer.deserialize(source)

        assert isinstance(restored, model)
        assert serializer.convert(restored) == source


@pytest.mark.parametrize(
    "source",
    ({}, {"model_type": "unknown"}),
    ids=("missing-model-type", "unknown-model-type"),
)
def test_fail_deserialize_factory_rejects_invalid_model_type(source):
    """Проверяет ошибку при отсутствующей или неизвестной метке типа."""
    with pytest.raises(validation_error, match="model_type|Неизвестный тип"):
        deserialize_factory().deserialize(source)


def test_fail_load_rejects_conflicting_models_with_same_id(tmp_path):
    """Проверяет ошибку для двух записей с одним ID и разными данными."""
    gram = convert_factory().convert(range_model.create_gram())
    path = tmp_path / "storage.json"
    path.write_text(
        json.dumps({"ranges": [gram, {**gram, "coefficient": 2}]}),
        encoding="utf-8",
    )

    with pytest.raises(validation_error, match="Разные данные модели"):
        deserialize_factory().load(path)
