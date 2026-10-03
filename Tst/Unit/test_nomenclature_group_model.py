from Src.Models.nomenclature_group_model import nomenclature_group_model


def test_success_init_valid_name_returns_created_group():
    """
    Корректное имя позволяет создать группу номенклатуры.
    """
    # Действие
    group = nomenclature_group_model("Молочные продукты")

    # Проверка
    assert group.id
    assert group.name == "Молочные продукты"
