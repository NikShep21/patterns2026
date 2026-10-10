import pytest

from Src.Core.Exceptions import validation_error
from Src.Models.organization_model import organization_model


def test_success_init_without_arguments_returns_empty_organization():
    """Организацию можно создать до заполнения её реквизитов."""
    # Действие
    organization = organization_model()

    # Проверка
    assert organization.name == ""
    assert organization.inn == ""
    assert organization.bik == ""
    assert organization.account == ""
    assert organization.corr_account == ""
    assert organization.ownership_form == ""


@pytest.mark.parametrize(
    "inn",
    ("3801000000", "500100732259"),
    ids=("legal-entity", "individual-entrepreneur"),
)
def test_success_init_valid_inn_returns_created_organization(inn):
    """
    ИНН допустимой длины позволяет создать организацию.
    """
    # Действие
    organization = organization_model(
        "Ромашка",
        inn,
        "042520607",
        "40702810001",
        "30101810001",
        "ООО",
    )

    # Проверка
    assert organization.name == "Ромашка"
    assert organization.inn == inn
    assert organization.bik == "042520607"
    assert organization.account == "40702810001"
    assert organization.corr_account == "30101810001"
    assert organization.ownership_form == "ООО"


def test_success_ownership_form_outer_spaces_returns_trimmed_value():
    """
    Форма собственности сохраняется без внешних пробелов.
    """
    # Действие
    organization = organization_model(
        "Ромашка",
        "3801000000",
        "042520607",
        "40702810001",
        "30101810001",
        "  ООО  ",
    )

    # Проверка
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
    # Действие / Проверка
    with pytest.raises(validation_error):
        organization_model(
            "Ромашка",
            invalid_inn,
            "042520607",
            "40702810001",
            "30101810001",
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
    # Действие / Проверка
    with pytest.raises(validation_error):
        organization_model(
            "Ромашка",
            "3801000000",
            invalid_bik,
            "40702810001",
            "30101810001",
            "ООО",
        )


@pytest.mark.parametrize(
    "invalid_account",
    ("4070281000A", "4070281000"),
    ids=("non-digit", "wrong-length"),
)
def test_fail_account_invalid_value_raises_validation_error(invalid_account):
    """
    Некорректный номер счёта вызывает ошибку валидации.
    """
    # Действие / Проверка
    with pytest.raises(validation_error):
        organization_model(
            "Ромашка",
            "3801000000",
            "042520607",
            invalid_account,
            "30101810001",
            "ООО",
        )


@pytest.mark.parametrize(
    "invalid_corr_account",
    ("3010181000A", "3010181000"),
    ids=("non-digit", "wrong-length"),
)
def test_fail_corr_account_invalid_value_raises_validation_error(
    invalid_corr_account,
):
    """
    Некорректный корреспондентский счёт вызывает ошибку валидации.
    """
    # Действие / Проверка
    with pytest.raises(validation_error):
        organization_model(
            "Ромашка",
            "3801000000",
            "042520607",
            "40702810001",
            invalid_corr_account,
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
    # Подготовка
    organization = organization_model()

    # Действие / Проверка
    with pytest.raises(validation_error):
        organization.ownership_form = invalid_ownership_form
