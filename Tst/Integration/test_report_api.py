import pytest
from fastapi.testclient import TestClient

from main import app
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.entity_type import entity_type
from Src.Models.report_format import report_format


@pytest.fixture
def api_data():
    """Подготавливает API и первичные данные приложения."""
    settings = settings_manager()
    settings.load()
    settings.settings.is_first_start = True
    storage = storage_manager()
    storage.clear()
    storage.load()

    with TestClient(app) as client:
        yield client, settings, storage

    storage.clear()
    settings.settings.is_first_start = True


@pytest.mark.parametrize(
    ("value", "content_type", "extension", "is_file"),
    (
        (report_format.CSV, "text/csv", "csv", True),
        (report_format.MARKDOWN, "text/markdown", "md", True),
        (report_format.XML, "application/xml", "xml", False),
        (report_format.TXT, "text/plain", "txt", False),
        (report_format.HTML, "text/html", "html", False),
    ),
)
def test_success_get_report_returns_requested_format(
    api_data,
    value,
    content_type,
    extension,
    is_file,
):
    """Проверяет HTTP-ответы всех поддерживаемых форматов."""
    # Подготовка
    client, _, storage = api_data
    recipe = storage.recipes[0]

    # Действие
    response = client.get(
        f"/api/reports/{value.value}/recipe/{recipe.id}"
    )

    # Проверка
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(content_type)
    assert recipe.id in response.text
    assert recipe.name in response.text

    if is_file:
        disposition = response.headers["content-disposition"]
        assert "attachment" in disposition
        assert disposition.endswith(f'.{extension}"')
    else:
        assert "content-disposition" not in response.headers


@pytest.mark.parametrize(
    ("value_type", "collection_name"),
    (
        (entity_type.NOMENCLATURE, "nomenclature"),
        (entity_type.RANGE, "ranges"),
        (entity_type.RECIPE, "recipes"),
    ),
)
def test_success_get_report_supports_required_entity_types(
    api_data,
    value_type,
    collection_name,
):
    """Проверяет отчёты для трёх требуемых типов сущностей."""
    # Подготовка
    client, _, storage = api_data
    entity = getattr(storage, collection_name)[0]

    # Действие
    response = client.get(
        f"/api/reports/TXT/{value_type.value}/{entity.id}"
    )

    # Проверка
    assert response.status_code == 200
    assert entity.id in response.text
    assert entity.name in response.text


def test_success_get_default_report_uses_settings_format(api_data):
    """Проверяет применение create_default() в API."""
    # Подготовка
    client, settings, storage = api_data
    settings.settings.response_format = report_format.MARKDOWN
    nomenclature = storage.nomenclature[0]

    # Действие
    response = client.get(
        f"/api/reports/nomenclature/{nomenclature.id}"
    )

    # Проверка
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert response.headers["content-disposition"].endswith('.md"')
    assert nomenclature.name in response.text


def test_fail_get_report_unknown_code_returns_not_found(api_data):
    """Проверяет ответ 404 для неизвестного кода сущности."""
    # Подготовка
    client, _, _ = api_data

    # Действие
    response = client.get("/api/reports/TXT/recipe/unknown-code")

    # Проверка
    assert response.status_code == 404


@pytest.mark.parametrize(
    "path",
    (
        "/api/reports/PDF/recipe/code",
        "/api/reports/TXT/warehouse/code",
    ),
)
def test_fail_get_report_invalid_path_value_returns_unprocessable_entity(
    api_data,
    path,
):
    """Проверяет ответ 422 для неизвестного формата или типа."""
    # Подготовка
    client, _, _ = api_data

    # Действие
    response = client.get(path)

    # Проверка
    assert response.status_code == 422
