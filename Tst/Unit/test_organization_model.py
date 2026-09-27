import pytest

from Src.Core.Exceptions import validation_error
from Src.Models.organization_model import organization_model


@pytest.mark.parametrize(
    "inn",
    ("3801000000", "500100732259"),
    ids=("legal-entity", "individual-entrepreneur"),
)
def test_success_init_valid_inn_returns_created_organization(inn):
    """
    ИНН допустимой длины позволяет создать организацию.
    """
    # Act
    organization = organization_model(
        "Ромашка",
        inn,
        "042520607",
        "40702810000000000001",
        "ООО",
    )

    # Assert
    assert organization.name == "Ромашка"
    assert organization.inn == inn
    assert organization.bik == "042520607"
    assert organization.account == "40702810000000000001"
    assert organization.ownership_form == "ООО"


def test_success_ownership_form_outer_spaces_returns_trimmed_value():
    """
    Форма собственности сохраняется без внешних пробелов.
    """
    # Act
    organization = organization_model(
        "Ромашка",
        "3801000000",
        "042520607",
        "40702810000000000001",
        "  ООО  ",
    )

    # Assert
    assert organization.ownership_form == "ООО"


@pytest.mark.parametrize(
    "invalid_inn",
    (3801000000, "38010A0000", "380100000"),
    ids=("non-string", "non-digit", "wrong-length"),
)
def test_fail_inn_invalid_value_raises_validation_error(invalid_inn):
    """
    Некорректный ИНН вызывает ошибку валидации.
    """
    # Act / Assert
    with pytest.raises(validation_error):
        organization_model(
            "Ромашка",
            invalid_inn,
            "042520607",
            "40702810000000000001",
            "ООО",
        )


@pytest.mark.parametrize(
    "invalid_bik",
    ("04252A607", "04252060"),
    ids=("non-digit", "wrong-length"),
)
def test_fail_bik_invalid_value_raises_validation_error(invalid_bik):
    """
    Некорректный БИК вызывает ошибку валидации.
    """
    # Act / Assert
    with pytest.raises(validation_error):
        organization_model(
            "Ромашка",
            "3801000000",
            invalid_bik,
            "40702810000000000001",
            "ООО",
        )


@pytest.mark.parametrize(
    "invalid_account",
    ("4070281000000000000A", "4070281000000000000"),
    ids=("non-digit", "wrong-length"),
)
def test_fail_account_invalid_value_raises_validation_error(invalid_account):
    """
    Некорректный номер счёта вызывает ошибку валидации.
    """
    # Act / Assert
    with pytest.raises(validation_error):
        organization_model(
            "Ромашка",
            "3801000000",
            "042520607",
            invalid_account,
            "ООО",
        )


@pytest.mark.parametrize(
    "invalid_ownership_form",
    (None, "", "   "),
    ids=("non-string", "empty", "spaces-only"),
)
def test_fail_ownership_form_invalid_value_raises_validation_error(
    invalid_ownership_form,
):
    """
    Некорректная форма собственности вызывает ошибку валидации.
    """
    # Act / Assert
    with pytest.raises(validation_error):
        organization_model(
            "Ромашка",
            "3801000000",
            "042520607",
            "40702810000000000001",
            invalid_ownership_form,
        )
