from copy import copy

import pytest

from Src.Core.Abstract import base_entity
from Src.Core.Exceptions import validation_error


def test_success_init_entity_returns_non_empty_string_id():
    """
    Создание сущности возвращает непустой строковый идентификатор.
    """
    # Действие
    entity = base_entity()

    # Проверка
    assert isinstance(entity.id, str)
    assert entity.id


def test_success_init_two_entities_returns_unique_ids():
    """
    Создание двух сущностей возвращает разные идентификаторы.
    """
    # Действие
    first_entity = base_entity()
    second_entity = base_entity()

    # Проверка
    assert first_entity.id != second_entity.id


def test_success_equal_ids_returns_equal_entities():
    """
    Сущности с одинаковым идентификатором считаются равными.
    """
    # Подготовка
    entity = base_entity()
    entity_copy = copy(entity)

    # Действие / Проверка
    assert entity == entity_copy


def test_success_different_ids_returns_unequal_entities():
    """
    Сущности с разными идентификаторами считаются неравными.
    """
    # Подготовка
    first_entity = base_entity()
    second_entity = base_entity()

    # Действие / Проверка
    assert first_entity != second_entity


def test_success_name_outer_spaces_returns_trimmed_value():
    """
    Имя с внешними пробелами сохраняется в очищенном виде.
    """
    # Подготовка
    entity = base_entity()

    # Действие
    entity.name = "  Молоко  "

    # Проверка
    assert entity.name == "Молоко"


def test_success_name_max_length_returns_same_value():
    """
    Имя длиной 50 символов сохраняется без изменений.
    """
    # Подготовка
    entity = base_entity()
    name = "а" * 50

    # Действие
    entity.name = name

    # Проверка
    assert entity.name == name


@pytest.mark.parametrize(
    "invalid_name",
    (None, "", "   ", "а" * 51),
    ids=("non-string", "empty", "spaces-only", "too-long"),
)
def test_fail_name_invalid_value_raises_validation_error(invalid_name):
    """
    Некорректное имя вызывает ошибку валидации.
    """
    # Подготовка
    entity = base_entity()

    # Действие / Проверка
    with pytest.raises(validation_error):
        entity.name = invalid_name
