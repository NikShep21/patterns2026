import json


from datetime import datetime, timezone


import pytest


from Src.Core.Exceptions import validation_error


from Src.Logics.convert_factory import convert_factory


from Src.Logics.deserialize_factory import deserialize_factory


from Src.Logics.settings_manager import settings_manager


from Src.Logics.storage_manager import storage_manager


from Src.Models.nomenclature_group_model import nomenclature_group_model


from Src.Models.nomenclature_model import nomenclature_model


from Src.Models.nomenclature_type import nomenclature_type


from Src.Models.range_model import range_model


from Src.Models.transaction_model import transaction_model


from Src.Models.warehouse_model import warehouse_model


def moment(day):
    """Возвращает фиксированное время учебного движения."""
    return datetime(2026, 11, day, 12, tzinfo=timezone.utc)


@pytest.fixture
def movement_storage(monkeypatch):
    """Готовит муку, две единицы и два склада без первичных движений."""
    monkeypatch.setattr(storage_manager, "_storage_manager__instance", None)
    storage = storage_manager()
    unit = range_model.create_kilogram()
    group = nomenclature_group_model("Продукты")
    flour = nomenclature_model(
        "Мука", "Мука", nomenclature_type.RAW_MATERIAL, group, unit
    )
    first = warehouse_model("Первый склад", "Адрес 1")
    second = warehouse_model("Второй склад", "Адрес 2")
    for entity in (unit.base_range, unit, group, flour, first, second):
        storage.add(type(entity), entity)
    return storage, flour, first, second


def add(storage, item, warehouse, quantity, day, unit=None):
    """Добавляет движение через общий механизм учёта записей и ссылок."""
    movement = transaction_model(
        item, warehouse, unit or item.range, quantity, moment(day)
    )
    storage.add(transaction_model, movement)
    return movement


@pytest.mark.parametrize(
    "quantity", (0, True, "1", float("nan"), float("inf"), 10**1000)
)
def test_fail_transaction_rejects_invalid_quantity(movement_storage, quantity):
    """Движение отклоняет ноль, неверный тип и числа за пределами допустимого диапазона."""
    _, flour, warehouse, _ = movement_storage
    with pytest.raises(validation_error):
        transaction_model(flour, warehouse, flour.range, quantity, moment(1))


def test_success_transaction_roundtrip_preserves_id_time_and_shared_links(
    movement_storage, tmp_path
):
    """Общая фабрика восстанавливает движения из JSON с исходными ссылками."""
    storage, flour, warehouse, _ = movement_storage
    first = add(storage, flour, warehouse, 10, 1)
    second = add(storage, flour, warehouse, -2, 3)
    original = convert_factory().convert(storage)
    path = tmp_path / "movements.json"
    path.write_text(json.dumps(original, ensure_ascii=False), encoding="utf-8")

    restored = deserialize_factory().load(path)

    assert convert_factory().convert(restored) == original
    left, right = restored["transactions"]
    assert (left.id, right.id) == (first.id, second.id)
    assert left.nomenclature is right.nomenclature
    assert left.warehouse is right.warehouse
    assert left.period == moment(1)


def test_success_initial_transactions_use_registered_models_and_reset_on_reload(
    monkeypatch,
):
    """Первый старт создаёт воспроизводимые движения с учтёнными входящими ссылками."""
    monkeypatch.setattr(settings_manager, "_settings_manager__instance", None)
    monkeypatch.setattr(storage_manager, "_storage_manager__instance", None)
    storage = storage_manager()
    storage.load()
    before = len(storage.transactions)
    assert before > 0
    assert any(item.quantity > 0 for item in storage.transactions)
    assert any(item.quantity < 0 for item in storage.transactions)
    for item in storage.transactions:
        assert any(value is item.nomenclature for value in storage.nomenclature)
        assert any(value is item.warehouse for value in storage.warehouses)
        assert item in tuple(storage.iter_referrers(item.warehouse))
    storage.convert()
    assert len(storage.transactions) == before
