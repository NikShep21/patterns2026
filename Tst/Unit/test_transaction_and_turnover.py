import json
from datetime import datetime, timezone

import pytest

from Src.Core.Exceptions import validation_error
from Src.Dtos.filter_condition_dto import filter_condition_dto
from Src.Dtos.turnover_filter_dto import turnover_filter_dto
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.turnover_service import turnover_service
from Src.Models.comparison_type import comparison_type
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


def test_success_turnover_calculates_opening_period_boundaries_and_closing(
    movement_storage,
):
    """Ведомость учитывает историю до начала и включает обе границы периода."""
    storage, flour, warehouse, _ = movement_storage
    for quantity, day in ((10, 1), (-2, 3), (5, 5), (100, 6)):
        add(storage, flour, warehouse, quantity, day)

    (row,) = turnover_service(storage).build(
        turnover_filter_dto(start=moment(3), end=moment(5))
    )

    assert (row.opening_balance, row.income, row.expense, row.closing_balance) == (
        10,
        5,
        2,
        13,
    )
    assert row.nomenclature.id == flour.id


def test_success_turnover_keeps_rows_with_only_opening_balance(movement_storage):
    """Остаток сохраняется, когда в выбранном периоде движений не было."""
    storage, flour, warehouse, _ = movement_storage
    add(storage, flour, warehouse, 10, 1)
    (row,) = turnover_service(storage).build(
        turnover_filter_dto(start=moment(3), end=moment(5))
    )
    assert (row.opening_balance, row.income, row.expense, row.closing_balance) == (
        10,
        0,
        0,
        10,
    )


def test_success_turnover_excludes_groups_with_only_future_movements(movement_storage):
    """Склад с движениями только после конца периода не появляется в ведомости."""
    storage, flour, first, second = movement_storage
    add(storage, flour, first, 10, 1)
    add(storage, flour, second, 50, 6)

    (row,) = turnover_service(storage).build(turnover_filter_dto(end=moment(5)))

    assert row.warehouse.id == first.id
    assert row.closing_balance == 10


def test_success_turnover_separates_warehouses_units_and_allows_negative_balance(
    movement_storage,
):
    """Разные склады и единицы не складываются; расход без прихода даёт отрицательный остаток."""
    storage, flour, first, second = movement_storage
    add(storage, flour, first, 10, 1)
    add(storage, flour, second, -2, 1)
    add(storage, flour, first, 1000, 1, flour.range.base_range)
    rows = turnover_service(storage).build(turnover_filter_dto())
    totals = {(row.warehouse.id, row.range.id): row.closing_balance for row in rows}
    assert totals == {
        (first.id, flour.range.id): 10,
        (second.id, flour.range.id): -2,
        (first.id, flour.range.base_range.id): 1000,
    }


def test_success_turnover_movement_filter_preserves_complete_opening_balance(
    movement_storage,
):
    """Отбор по количеству движения не удаляет прежние расходы из начального остатка."""
    storage, flour, warehouse, _ = movement_storage
    for quantity, day in ((10, 1), (-3, 2), (-2, 3), (5, 5)):
        add(storage, flour, warehouse, quantity, day)
    filters = turnover_filter_dto(
        [filter_condition_dto("quantity", comparison_type.EQUALS, 5)],
        moment(3),
        moment(5),
    )
    (row,) = turnover_service(storage).build(filters)
    assert (row.opening_balance, row.income, row.expense, row.closing_balance) == (
        7,
        5,
        0,
        12,
    )


def test_success_turnover_filters_nested_group_and_retains_input_movements(
    movement_storage,
):
    """Отбор по группе товара использует общий путь и не меняет журнал движений."""
    storage, flour, warehouse, _ = movement_storage
    movement = add(storage, flour, warehouse, 10, 1)
    matching = filter_condition_dto(
        "nomenclature.group.name", comparison_type.EQUALS, flour.group.name
    )
    missing = filter_condition_dto(
        "nomenclature.group.name", comparison_type.EQUALS, "Нет такой"
    )
    assert len(turnover_service(storage).build(turnover_filter_dto([matching]))) == 1
    assert turnover_service(storage).build(turnover_filter_dto([missing])) == ()
    assert storage.transactions == (movement,)


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


def test_fail_turnover_rejects_reversed_period():
    """Период с окончанием раньше начала отклоняется до расчёта ведомости."""
    with pytest.raises(validation_error):
        turnover_filter_dto(start=moment(5), end=moment(1))


def test_success_turnover_normalizes_timezones():
    """Одинаковые моменты с разными часовыми поясами задают один период."""
    filters = turnover_filter_dto(start="2026-11-01T20:00:00+08:00", end=moment(1))
    assert filters.start == filters.end == moment(1)
