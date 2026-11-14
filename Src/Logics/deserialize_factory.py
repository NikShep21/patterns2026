import json
from functools import cache
from importlib import import_module
from inspect import getmembers, isabstract, isclass
from pathlib import Path
from pkgutil import iter_modules
from uuid import uuid4

from Src import Models
from Src.Core.Abstract import base_entity
from Src.Core.Exceptions import operation_error, validation_error
from Src.Core.Validator import validator
from Src.Logics.convert_factory import convert_factory


_loaded_models = dict[str, tuple[dict | None, base_entity | None]]


@cache
def _discover_models() -> dict[str, type[base_entity]]:
    """Находит конкретные модели с методом from_dict в пакете Src.Models."""
    models = {}
    for module_info in iter_modules(Models.__path__, prefix=f"{Models.__name__}."):
        module = import_module(module_info.name)
        for _, model in getmembers(module, isclass):
            if (
                model.__module__ == module.__name__
                and issubclass(model, base_entity)
                and not isabstract(model)
                and callable(getattr(model, "from_dict", None))
            ):
                models[model.__name__] = model
    return models


class deserialize_factory:
    """Восстанавливает модели из словарей с меткой типа."""

    def deserialize(
        self,
        source: dict,
        *,
        known: dict[str, base_entity] | None = None,
        generate_ids: bool = False,
    ) -> base_entity:
        """Восстанавливает одну модель и её вложенные объекты."""
        validator.validate_type(source, dict, "Данные модели")
        loaded = {}
        allow_references = known is not None
        if known is not None:
            loaded = {code: (None, entity) for code, entity in known.items()}
        return self.__deserialize_model(
            source, loaded, allow_references, generate_ids or allow_references,
        )

    def load(self, file_name: str | Path) -> dict[str, object]:
        """Читает выгрузку хранилища и восстанавливает все её коллекции."""
        try:
            with Path(file_name).open(encoding="utf-8") as file:
                source = json.load(file)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise operation_error(f"Не удалось прочитать JSON: {file_name}") from error

        validator.validate_type(source, dict, "Данные хранилища")
        loaded: _loaded_models = {}
        return {
            name: self.__deserialize_value(value, loaded)
            for name, value in source.items()
        }

    def __deserialize_model(
        self,
        source: dict,
        loaded: _loaded_models,
        allow_references: bool = False,
        generate_ids: bool = False,
    ) -> base_entity:
        """Выбирает класс, восстанавливает поля и переиспользует общие объекты."""
        validator.validate_type(source, dict, "Данные модели")
        if allow_references and source.keys() == {"id"}:
            code = source["id"]
            validator.validate_required_string(code, "Идентификатор ссылки")
            _, entity = loaded.get(code, (None, None))
            if entity is None:
                raise validation_error(f"Ссылка на неизвестную модель «{code}»")
            return entity

        model_type = source.get("model_type")
        validator.validate_required_string(model_type, "model_type")

        model = _discover_models().get(model_type)
        if model is None:
            raise validation_error(f"Неизвестный тип модели «{model_type}»")

        if generate_ids and "id" not in source:
            source = {"id": str(uuid4()), **source}
        entity_id = source.get("id")
        validator.validate_required_string(entity_id, "Идентификатор")
        if entity_id in loaded:
            previous, entity = loaded[entity_id]
            if entity is None:
                raise validation_error(f"Циклическая ссылка на модель «{entity_id}»")
            if previous is None:
                previous = convert_factory().convert(entity)
            if previous != source:
                raise validation_error(f"Разные данные модели с ID «{entity_id}»")
            return entity

        loaded[entity_id] = (source, None)
        fields = {
            name: self.__deserialize_value(value, loaded, allow_references, generate_ids)
            for name, value in source.items()
            if name != "model_type"
        }
        entity = model.from_dict(fields)
        loaded[entity_id] = (source, entity)
        return entity

    def __deserialize_value(
        self,
        value: object,
        loaded: _loaded_models,
        allow_references: bool = False,
        generate_ids: bool = False,
    ) -> object:
        """Восстанавливает вложенную модель или элементы списка."""
        if isinstance(value, dict):
            return self.__deserialize_model(value, loaded, allow_references, generate_ids)
        if isinstance(value, list):
            return [
                self.__deserialize_value(item, loaded, allow_references, generate_ids)
                for item in value
            ]
        return value
