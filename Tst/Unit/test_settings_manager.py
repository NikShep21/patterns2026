import time

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
