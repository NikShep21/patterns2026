import pytest
from fastapi.testclient import TestClient

from main import app
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager


@pytest.fixture
def entity_api(monkeypatch):
    """Запускает API с отдельным хранилищем для каждого теста."""
    monkeypatch.setattr(settings_manager, "_settings_manager__instance", None)
    monkeypatch.setattr(storage_manager, "_storage_manager__instance", None)
    with TestClient(app) as client:
        yield client, storage_manager()


@pytest.mark.parametrize("kind", ("warehouse", "group", "range", "nomenclature", "recipe"))
def test_success_entity_api_creates_reads_updates_and_deletes(entity_api, kind):
    """Проверяет полный цикл CRUD для каждого типа записей."""
    client, storage = entity_api
    bodies = {
        "warehouse": {"address": "ул. Ленина, 10"},
        "group": {},
        "range": {"coefficient": 1},
        "nomenclature": {
            "full_name": "Новая позиция",
            "type": "Сырьё",
            "group": {"id": storage.groups[0].id},
            "range": {"id": storage.ranges[0].id},
        },
        "recipe": {
            "result": {"id": storage.recipes[-1].result.id},
            "ingredients": [
                {
                    "model_type": "recipe_ingredient_model",
                    "name": storage.nomenclature[0].name,
                    "nomenclature": {"id": storage.nomenclature[0].id},
                    "quantity": 1,
                    "gross_weight": 100,
                    "net_weight": 95,
                },
            ],
            "output_quantity": 1,
            "cooking_time": 10,
            "steps": ["Приготовить блюдо"],
        },
    }
    collection = f"/api/entities/{kind}"
    response = client.post(collection, json={"name": "Новая запись", **bodies[kind]})
    assert response.status_code == 201
    created = response.json()
    code = created["id"]
    url = f"{collection}/{code}"
    assert created in client.get(collection).json()
    assert client.get(url).json() == created

    response = client.patch(url, json={"name": "Другое имя", "id": "new-code"})
    assert response.status_code == 200
    updated = response.json()
    assert updated == {**created, "name": "Другое имя", "id": "new-code"}
    assert client.get(url).status_code == 404

    url = f"{collection}/new-code"
    assert client.get(url).json() == updated
    assert client.delete(url).status_code == 204
    assert client.get(url).status_code == 404
    assert client.patch(url, json={"name": "Новое имя"}).status_code == 404
    assert client.delete(url).status_code == 404


def test_success_entity_api_preserves_links_when_editing_group(entity_api):
    """Разрешает обычную правку связанной группы, сохраняя её в номенклатуре."""
    client, storage = entity_api
    item = storage.nomenclature[0]
    group = item.group
    url = f"/api/entities/group/{group.id}"

    assert client.patch(url, json={"name": "Новое имя группы"}).status_code == 200
    assert item.group is group
    assert client.get(f"/api/entities/nomenclature/{item.id}").json()["group"]["name"] == "Новое имя группы"


@pytest.mark.parametrize("kind", ("range", "group", "nomenclature", "recipe"))
def test_fail_entity_api_blocks_deletion_and_id_change_with_references(entity_api, kind):
    """Отклоняет удаление и смену кода, пока на запись есть ссылки."""
    client, storage = entity_api
    entities = {
        "range": storage.ranges[0],
        "group": storage.nomenclature[0].group,
        "nomenclature": storage.recipes[0].ingredients[0].nomenclature,
        "recipe": storage.recipes[-1].ingredients[0].recipe,
    }
    url = f"/api/entities/{kind}/{entities[kind].id}"
    before = client.get(url).json()

    assert client.delete(url).status_code == 409
    assert client.patch(url, json={"id": "replacement-code"}).status_code == 409
    assert client.get(url).json() == before


def test_fail_entity_api_rejects_invalid_changes_without_modifying_storage(entity_api):
    """Сохраняет записи при неверной ссылке, цикле и недопустимом значении."""
    client, storage = entity_api
    gram, kilogram = storage.ranges[:2]
    range_url = f"/api/entities/range/{gram.id}"
    before = client.get(range_url).json()
    assert client.patch(range_url, json={"base_range": {"id": kilogram.id}}).status_code == 409
    assert client.patch(range_url, json={"coefficient": 0}).status_code == 400
    assert client.get(range_url).json() == before

    item = storage.nomenclature[0]
    item_url = f"/api/entities/nomenclature/{item.id}"
    before = client.get(item_url).json()
    assert client.patch(item_url, json={"group": {"id": "absent"}}).status_code == 400
    assert client.get(item_url).json() == before
