import json
from io import StringIO
import time

import pytest

from Src.Core.Exceptions import operation_error
from Src.Logics.settings_manager import settings_manager


def test_not_raise_settings_manager_load():
    """Проверяет загрузку настроек без исключений."""
    # Подготовка
    manager = settings_manager()

    # Действие и проверка
    try:
        manager.load()
        assert True
    except operation_error:
        assert False
    except Exception:
        assert False


def test_not_empty_settings_manager_load():
    """Проверяет, что после загрузки настройки не пустые."""
    # Подготовка
    manager = settings_manager()

    # Действие
    try:
        manager.load()
    except Exception:
        assert False

    # Проверка
    assert manager.settings is not None


def test_equals_settings_manager_create():
    """Проверяет работу шаблона Singleton."""
    # Подготовка
    instance1 = settings_manager()
    time.sleep(1)
    instance2 = settings_manager()

    # Проверка
    assert instance1 == instance2


def test_equals_properties_settings_manager_create():
    """Проверяет общие настройки экземпляров Singleton."""
    # Подготовка
    instance1 = settings_manager()
    time.sleep(1)
    instance2 = settings_manager()

    # Проверка
    assert instance1.settings == instance2.settings


def test_is_loaded_settings_manager_true():
    """Проверяет признак загрузки и конвертации данных."""
    # Подготовка
    manager = settings_manager()

    # Действие
    try:
        manager.load()
    except Exception:
        assert False

    # Проверка
    assert manager.is_loaded


def test_success_settings_manager_loads_first_start_flag():
    """Проверяет загрузку признака первого запуска."""
    # Подготовка
    manager = settings_manager()

    # Действие
    manager.load()

    # Проверка
    assert manager.settings.is_first_start is True


def test_success_settings_manager_converts_all_fields():
    """Проверяет преобразование всех полей настроек в модели."""
    # Подготовка
    manager = settings_manager()

    # Действие
    manager.load()
    settings = manager.settings
    organization = settings.organization

    # Проверка
    assert organization.name == "ООО Ромашка"
    assert organization.inn == "7707083893"
    assert organization.bik == "044525225"
    assert organization.account == "40702810900"
    assert organization.corr_account == "30101810400"
    assert organization.ownership_form == "ООО"
    assert settings.boss_name == "Иванов И. И."
    assert settings.accountant_name == "Семёнов А. Г."


def test_success_settings_manager_loads_without_inn(monkeypatch):
    """Проверяет загрузку настроек без ИНН организации."""
    # Подготовка
    manager = settings_manager()
    data = {
        "organization": {
            "name": "ООО Ромашка",
            "bik": "044525225",
            "account": "40702810900",
            "corr_account": "30101810400",
            "ownership_form": "ООО",
        },
        "boss_name": "Иванов И. И.",
        "accountant_name": "Семёнов А. Г.",
        "is_first_start": True,
    }
    monkeypatch.setattr(
        "builtins.open",
        lambda *args, **kwargs: StringIO(
            json.dumps(data, ensure_ascii=False)
        ),
    )

    # Действие
    manager.load("settings-without-inn.json")

    # Проверка
    assert manager.is_loaded is True
    assert manager.settings.organization.inn == ""


def test_fail_settings_manager_missing_file_raises_operation_error(monkeypatch):
    """Проверяет ошибку при отсутствии файла настроек."""
    # Подготовка
    manager = settings_manager()

    def raise_file_not_found(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr("builtins.open", raise_file_not_found)

    # Действие / Проверка
    with pytest.raises(operation_error):
        manager.load("missing-settings.json")

    assert manager.is_loaded is False


def test_fail_settings_manager_invalid_first_start_raises_operation_error(
    monkeypatch,
):
    """Проверяет ошибку при некорректном признаке первого запуска."""
    # Подготовка
    manager = settings_manager()
    data = {
        "organization": {
            "name": "ООО Ромашка",
            "inn": "7707083893",
            "bik": "044525225",
            "account": "40702810900",
            "corr_account": "30101810400",
            "ownership_form": "ООО",
        },
        "boss_name": "Иванов И. И.",
        "accountant_name": "Семёнов А. Г.",
        "is_first_start": "true",
    }
    monkeypatch.setattr(
        "builtins.open",
        lambda *args, **kwargs: StringIO(
            json.dumps(data, ensure_ascii=False)
        ),
    )

    # Действие / Проверка
    with pytest.raises(operation_error):
        manager.load("invalid-settings.json")

    assert manager.is_loaded is False
