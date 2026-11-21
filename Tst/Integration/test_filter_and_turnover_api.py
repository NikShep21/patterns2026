import pytest
from fastapi.testclient import TestClient

from main import app
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.comparison_type import comparison_type


@pytest.fixture
def filter_api(monkeypatch):
    """Запускает API с независимыми первичными данными и транзакциями."""
    monkeypatch.setattr(settings_manager, "_settings_manager__instance", None)
    monkeypatch.setattr(storage_manager, "_storage_manager__instance", None)
    with TestClient(app) as client:
        yield client, storage_manager()


@pytest.mark.parametrize(
    "kind,collection",
    (
        ("range", "ranges"),
        ("group", "groups"),
        ("nomenclature", "nomenclature"),
        ("recipe", "recipes"),
    ),
)
def test_success_filter_api_selects_every_required_model_by_code(
    filter_api, kind, collection
):
    """Один маршрут и прототип отбирают каждый требуемый тип по уникальному коду."""
    client, storage = filter_api
    item = getattr(storage, collection)[0]
    result = client.post(
        f"/api/entities/{kind}/filter",
        json={"conditions": [{"field": "id", "value": item.id}]},
    )
    assert result.status_code == 200
    assert [row["id"] for row in result.json()] == [item.id]


def test_success_filter_api_selects_nested_unit_with_like(filter_api):
    """JSON DTO с LIKE находит килограмм по имени вложенной базовой единицы."""
    client, _ = filter_api
    response = client.post(
        "/api/entities/range/filter",
        json={
            "conditions": [
                {"field": "base_range.name", "comparison": "LIKE", "value": "ГРАММ"}
            ]
        },
    )
    assert response.status_code == 200
    assert [row["name"] for row in response.json()] == ["Килограмм"]


@pytest.mark.parametrize(
    "body,status",
    (
        ({"conditions": [{"field": "missing", "value": "x"}]}, 400),
        (
            {"conditions": [{"field": "name", "comparison": "UNKNOWN", "value": "x"}]},
            400,
        ),
        ({"conditions": [{"field": "name", "value": {"id": "x"}}]}, 400),
        (
            {
                "conditions": [
                    {"field": "coefficient", "comparison": "LIKE", "value": "1"}
                ]
            },
            400,
        ),
        ({"conditions": None}, 400),
        ({"unknown": 1}, 400),
    ),
)
def test_fail_filter_api_returns_validation_errors(filter_api, body, status):
    """Некорректные поля и условия отклоняются проверками DTO с ответом 400."""
    client, _ = filter_api
    assert client.post("/api/entities/range/filter", json=body).status_code == status


def test_success_turnover_api_returns_filtered_balances(filter_api):
    """ОСВ по муке возвращает начальный остаток, обороты и конечный остаток за период."""
    client, _ = filter_api
    response = client.post(
        "/api/reports/turnover",
        json={
            "start": "2026-11-03T12:00:00Z",
            "end": "2026-11-05T12:00:00Z",
            "conditions": [{"field": "nomenclature.name", "value": "Мука"}],
        },
    )
    assert response.status_code == 200
    (row,) = response.json()
    assert row["nomenclature"]["name"] == "Мука"
    assert row["range"]["name"] == "Килограмм"
    assert (
        row["opening_balance"],
        row["income"],
        row["expense"],
        row["closing_balance"],
    ) == (10, 5, 2, 13)


def test_fail_turnover_api_validates_period_and_unknown_fields(filter_api):
    """Неверные даты, обратный период и неизвестные пути не превращаются в пустую ведомость."""
    client, storage = filter_api
    assert (
        client.post("/api/reports/turnover", json={"start": "yesterday"}).status_code
        == 400
    )
    assert (
        client.post(
            "/api/reports/turnover",
            json={"start": "2026-11-05T00:00:00Z", "end": "2026-11-01T00:00:00Z"},
        ).status_code
        == 400
    )
    storage.clear()
    assert (
        client.post(
            "/api/reports/turnover",
            json={"conditions": [{"field": "missing", "value": "x"}]},
        ).status_code
        == 400
    )


def test_fail_entity_api_cannot_delete_warehouse_used_in_movements(filter_api):
    """Новые движения участвуют в существующей защите от удаления связанных записей."""
    client, storage = filter_api
    assert (
        client.delete(f"/api/entities/warehouse/{storage.warehouses[0].id}").status_code
        == 409
    )


@pytest.mark.parametrize(
    "boundary",
    (
        "0001-01-01T00:00:00+08:00",
        "9999-12-31T23:59:59-08:00",
    ),
)
def test_fail_turnover_api_rejects_dates_outside_utc_range(filter_api, boundary):
    """Перевод крайних ISO-дат в UTC даёт ошибку валидации вместо HTTP 500."""
    client, _ = filter_api
    assert (
        client.post("/api/reports/turnover", json={"start": boundary}).status_code
        == 400
    )
    body = {"conditions": [{"field": "period", "value": boundary}]}
    assert client.post("/api/reports/turnover", json=body).status_code == 400


@pytest.mark.parametrize("number", ("1e999", "NaN", "Infinity", "-Infinity"))
@pytest.mark.parametrize("nested", (False, True))
def test_fail_filter_api_handles_nonfinite_json_without_server_error(
    filter_api, number, nested
):
    """Ошибки числовых значений, включая вложенные, сериализуются в ответ 400."""
    client, _ = filter_api
    value = f"[{number}]" if nested else number
    body = '{"conditions":[{"field":"coefficient","value":' + value + "}]}"
    response = client.post(
        "/api/entities/range/filter",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert isinstance(response.json()["detail"], str)


def test_success_openapi_describes_typed_filters_and_both_post_routes(filter_api):
    """Swagger содержит схемы условий, перечисление операций и оба новых POST-запроса."""
    client, _ = filter_api
    schema = client.get("/openapi.json").json()
    assert "post" in schema["paths"]["/api/entities/{value_type}/filter"]
    assert "post" in schema["paths"]["/api/reports/turnover"]
    search = schema["paths"]["/api/entities/{value_type}/filter"]["post"][
        "requestBody"
    ]["content"]["application/json"]["schema"]
    turnover = schema["paths"]["/api/reports/turnover"]["post"]["requestBody"][
        "content"
    ]["application/json"]["schema"]
    assert search["additionalProperties"] is False
    assert set(search["properties"]) == {"conditions"}
    conditions = search["properties"]["conditions"]
    assert conditions["type"] == "array"
    item = conditions["items"]
    assert item["additionalProperties"] is False
    assert set(item["required"]) == {"field", "value"}
    assert set(item["properties"]) == {"field", "comparison", "value"}
    assert item["properties"]["comparison"]["enum"] == [
        value.value for value in comparison_type
    ]
    assert item["properties"]["comparison"]["default"] == "EQUALS"
    assert set(item["properties"]["value"]["type"]) == {
        "string",
        "number",
        "boolean",
        "null",
    }
    assert turnover["additionalProperties"] is False
    assert set(turnover["properties"]) == {"conditions", "start", "end"}
    assert turnover["properties"]["conditions"] == conditions
    for boundary in ("start", "end"):
        assert turnover["properties"][boundary]["anyOf"] == [
            {"type": "string", "format": "date-time"},
            {"type": "null"},
        ]


@pytest.mark.parametrize("body", (None, [], [1], 42, "filter"))
def test_fail_filter_api_rejects_non_object_json(filter_api, body):
    """Корень запроса должен быть JSON-объектом для обоих новых маршрутов."""
    client, _ = filter_api
    for route in ("/api/entities/range/filter", "/api/reports/turnover"):
        assert client.post(route, json=body).status_code == 422


def test_fail_filter_api_rejects_malformed_json_and_safely_serializes_bad_root(
    filter_api,
):
    """Неверный JSON и неконечное число в корне дают 422 без ошибки сервера."""
    client, _ = filter_api
    for route in ("/api/entities/range/filter", "/api/reports/turnover"):
        for body in ('{"conditions":', "NaN", "[Infinity]"):
            response = client.post(
                route, content=body, headers={"Content-Type": "application/json"}
            )
            assert response.status_code == 422
            assert isinstance(response.json()["detail"], list)


@pytest.mark.parametrize(
    "body",
    (
        {"conditions": [{"field": "name"}]},
        {"conditions": [{"value": "Грамм"}]},
        {"conditions": [{"field": "name", "value": "Грамм", "typo": 1}]},
        {"conditions": [None]},
        {"conditions": ["name"]},
        {"conditions": {}},
        {"conditions": "name"},
        {"conditions": 1},
    ),
)
def test_fail_filter_api_validates_dictionary_before_calling_service(filter_api, body):
    """DTO отклоняет пропущенные поля и неверные контейнеры вместо HTTP 500."""
    client, _ = filter_api
    for route in ("/api/entities/range/filter", "/api/reports/turnover"):
        assert client.post(route, json=body).status_code == 400


@pytest.mark.parametrize("comparison", (None, [], {}, 1, True, "UNKNOWN"))
def test_fail_filter_api_rejects_invalid_comparison_values(filter_api, comparison):
    """Неизвестный тип операции даёт штатную ошибку DTO."""
    client, _ = filter_api
    body = {
        "conditions": [{"field": "name", "comparison": comparison, "value": "Грамм"}]
    }
    assert client.post("/api/entities/range/filter", json=body).status_code == 400


def test_success_filter_api_supports_empty_conditions_null_and_default_comparison(
    filter_api,
):
    """Пустой фильтр возвращает все записи, null и пропущенная операция сохраняют смысл."""
    client, storage = filter_api
    for body in ({}, {"conditions": []}):
        response = client.post("/api/entities/range/filter", json=body)
        assert response.status_code == 200
        assert len(response.json()) == len(storage.ranges)
    response = client.post(
        "/api/entities/range/filter",
        json={"conditions": [{"field": "base_range", "value": None}]},
    )
    assert response.status_code == 200
    assert {row["id"] for row in response.json()} == {
        unit.id for unit in storage.ranges if unit.base_range is None
    }
    assert (
        client.post(
            "/api/reports/turnover", json={"start": None, "end": None}
        ).status_code
        == 200
    )


@pytest.mark.parametrize("boundary", ("start", "end"))
@pytest.mark.parametrize("value", (True, 1, [], {}, "yesterday"))
def test_fail_turnover_api_rejects_invalid_period_field_types(
    filter_api, boundary, value
):
    """Даты периода проходят проверку без преобразования чисел и контейнеров в даты."""
    client, _ = filter_api
    assert (
        client.post("/api/reports/turnover", json={boundary: value}).status_code == 400
    )
