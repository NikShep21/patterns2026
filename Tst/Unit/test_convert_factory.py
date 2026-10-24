from datetime import datetime

import pytest

from Src.Core.abstract_converter import abstract_converter
from Src.Core.Exceptions import operation_error
from Src.Logics.basic_converter import basic_converter
from Src.Logics.convert_factory import convert_factory
from Src.Logics.datetime_converter import datetime_converter
from Src.Logics.reference_converter import reference_converter
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_type import nomenclature_type
from Src.Models.range_model import range_model


class dated_value:
    """Тестовый объект с датой."""

    def __init__(self, created_at: datetime):
        self.__created_at = created_at

    @property
    def created_at(self) -> datetime:
        """Возвращает дату создания."""
        return self.__created_at


class plain_value:
    """Тестовый объект с публичными полями."""

    def __init__(self):
        self.name = "Значение"
        self.count = 2


@pytest.mark.parametrize(
    ("value", "expected_type"),
    (
        ("Мука", basic_converter),
        (100, basic_converter),
        (datetime(2026, 10, 24), datetime_converter),
        (object(), reference_converter),
    ),
    ids=("string", "number", "datetime", "reference"),
)
def test_success_convert_factory_selects_converter(value, expected_type):
    """Проверяет выбор конвертера по типу значения."""
    # Подготовка
    factory = convert_factory()

    # Действие
    result = factory.create(value)

    # Проверка
    assert isinstance(result, abstract_converter)
    assert isinstance(result, expected_type)


def test_success_convert_factory_converts_simple_value():
    """Проверяет преобразование простого значения фабрикой."""
    # Действие
    result = convert_factory().convert(100)

    # Проверка
    assert result == {"value": 100}


def test_success_convert_factory_converts_datetime_property():
    """Проверяет выбор конвертера даты для свойства объекта."""
    # Подготовка
    source = dated_value(datetime(2026, 10, 24, 15, 30))

    # Действие
    result = convert_factory().convert(source)

    # Проверка
    assert result == {"created_at": "2026-10-24T15:30:00"}


def test_success_convert_factory_converts_public_fields():
    """Проверяет преобразование объекта без свойств-дескрипторов."""
    # Действие
    result = convert_factory().convert(plain_value())

    # Проверка
    assert result == {"name": "Значение", "count": 2}


def test_success_convert_factory_converts_nested_model():
    """Проверяет рекурсивное преобразование составной модели."""
    # Подготовка
    gram = range_model.create_gram()
    group = nomenclature_group_model("Ингредиенты")
    flour = nomenclature_model(
        "Мука",
        "Мука пшеничная",
        nomenclature_type.RAW_MATERIAL,
        group,
        gram,
    )

    # Действие
    result = convert_factory().convert(flour)

    # Проверка
    assert result["id"] == flour.id
    assert result["name"] == "Мука"
    assert result["full_name"] == "Мука пшеничная"
    assert result["type"] == "Сырьё"
    assert result["group"]["name"] == "Ингредиенты"
    assert result["range"]["name"] == "Грамм"


def test_success_convert_factory_stops_cyclic_reference():
    """Проверяет завершение рекурсии для базовой единицы."""
    # Подготовка
    gram = range_model.create_gram()

    # Действие
    result = convert_factory().convert(gram)

    # Проверка
    assert result["base_range"] == {
        "id": gram.id,
        "name": "Грамм",
    }


def test_success_convert_factory_preserves_collection_structure():
    """Проверяет преобразование значений коллекции."""
    # Подготовка
    source = {
        "numbers": (1, 2),
        "items": ["first", "second"],
    }

    # Действие
    result = convert_factory().convert(source)

    # Проверка
    assert result == {
        "numbers": [1, 2],
        "items": ["first", "second"],
    }


@pytest.mark.parametrize("source", ([1, "Мука"], (1, "Мука")), ids=("list", "tuple"))
def test_success_convert_factory_converts_root_collection(source):
    """Проверяет обёртку для коллекции без имени поля."""
    # Действие
    result = convert_factory().convert(source)

    # Проверка
    assert result == {"value": [1, "Мука"]}


def test_success_convert_factory_converts_deeply_nested_values():
    """Проверяет модели и даты внутри вложенных словарей и коллекций."""
    # Подготовка
    source = {
        "outer": {
            "items": (
                {"model": plain_value()},
                [dated_value(datetime(2026, 10, 24, 15, 30)), None],
            ),
        },
    }

    # Действие
    result = convert_factory().convert(source)

    # Проверка
    assert result == {
        "outer": {
            "items": [
                {"model": {"name": "Значение", "count": 2}},
                [{"created_at": "2026-10-24T15:30:00"}, None],
            ],
        },
    }


def test_success_convert_factory_expands_shared_object_in_each_field():
    """Проверяет, что общая ссылка не считается циклом."""
    # Подготовка
    shared = plain_value()
    factory = convert_factory()

    # Действие
    result = factory.convert({"first": shared, "second": shared})

    # Проверка
    assert result == {
        "first": {"name": "Значение", "count": 2},
        "second": {"name": "Значение", "count": 2},
    }


def test_fail_convert_factory_cycle_does_not_affect_next_conversion():
    """Проверяет ошибку при цикле и повторное использование фабрики."""
    # Подготовка
    source = plain_value()
    source.link = source
    factory = convert_factory()

    # Действие / Проверка
    with pytest.raises(operation_error):
        factory.convert(source)

    source.link = None
    assert factory.convert(source) == {
        "name": "Значение",
        "count": 2,
        "link": None,
    }
