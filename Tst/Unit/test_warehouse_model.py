import pytest

from Src.Core.Exceptions import validation_error
from Src.Models.warehouse_model import warehouse_model


def test_success_init_valid_values_returns_created_warehouse():
    """
    Корректные данные позволяют создать склад.
    """
    # Act
    warehouse = warehouse_model(
        "Основной склад",
        "  г. Иркутск, ул. Ленина, д. 1  ",
    )

    # Assert
    assert warehouse.id
    assert warehouse.name == "Основной склад"
    assert warehouse.address == "г. Иркутск, ул. Ленина, д. 1"


@pytest.mark.parametrize(
    "invalid_address",
    (None, "", "   "),
    ids=("non-string", "empty", "spaces-only"),
)
def test_fail_address_invalid_value_raises_validation_error(invalid_address):
    """
    Некорректный адрес вызывает ошибку валидации.
    """
    # Act / Assert
    with pytest.raises(validation_error):
        warehouse_model("Основной склад", invalid_address)
