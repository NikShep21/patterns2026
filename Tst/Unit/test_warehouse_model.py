from Src.Models.warehouse_model import warehouse_model


def test_success_init_valid_name_returns_created_warehouse():
    """
    Корректное имя позволяет создать склад.
    """
    # Act
    warehouse = warehouse_model("Основной склад")

    # Assert
    assert warehouse.id
    assert warehouse.name == "Основной склад"
