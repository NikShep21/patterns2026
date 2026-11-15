from enum import Enum

from Src.Core.Abstract import base_entity
from Src.Logics.deserialize_factory import discover_models


def _collect_api_models() -> dict[str, type[base_entity]]:
    """Собирает модели, у которых явно задано имя для CRUD."""
    models = {}
    for model in discover_models().values():
        api_name = vars(model).get("api_name")
        if api_name is None:
            continue
        if api_name in models:
            raise ValueError(f"Имя сущности API «{api_name}» уже зарегистрировано")
        models[api_name] = model
    return models


_api_models = _collect_api_models()

storage_entity_type = Enum(
    "storage_entity_type",
    {name: name for name in sorted(_api_models)},
    module=__name__,
)
storage_entity_type.__doc__ = "Определяет коллекции, доступные для CRUD."


def api_entity_model(name: str) -> type[base_entity]:
    """Возвращает класс модели по её имени в API."""
    return _api_models[name]
