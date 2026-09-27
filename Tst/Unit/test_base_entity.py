import pytest

from Src.Core.Abstract import base_entity
from Src.Core.Exceptions import validation_error


def test_success_init_entity_returns_non_empty_string_id():
    """
    Создание сущности возвращает непустой строковый идентификатор.
    """
    # Act
    entity = base_entity()

    # Assert
    assert isinstance(entity.id, str)
    assert entity.id


def test_success_init_two_entities_returns_unique_ids():
    """
    Создание двух сущностей возвращает разные идентификаторы.
    """
    # Act
    first_entity = base_entity()
    second_entity = base_entity()

    # Assert
    assert first_entity.id != second_entity.id


def test_success_name_outer_spaces_returns_trimmed_value():
    """
    Имя с внешними пробелами сохраняется в очищенном виде.
    """
    # Arrange
    entity = base_entity()

    # Act
    entity.name = "  Молоко  "

    # Assert
    assert entity.name == "Молоко"


def test_success_name_max_length_returns_same_value():
    """
    Имя длиной 50 символов сохраняется без изменений.
    """
    # Arrange
    entity = base_entity()
    name = "а" * 50

    # Act
    entity.name = name

    # Assert
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
    # Arrange
    entity = base_entity()

    # Act / Assert
    with pytest.raises(validation_error):
        entity.name = invalid_name
