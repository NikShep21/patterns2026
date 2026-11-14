import json
from pathlib import Path

from Src.Core.Abstract import base_entity
from Src.Core.Exceptions import operation_error, validation_error
from Src.Core.Validator import validator
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_ingredient_model import recipe_ingredient_model
from Src.Models.recipe_model import recipe_model
from Src.Models.warehouse_model import warehouse_model


_loaded_models = dict[str, tuple[dict, base_entity | None]]


class deserialize_factory:
    """Восстанавливает модели из словарей с меткой типа."""

    __models = {
        model.__name__: model
        for model in (
            range_model,
            nomenclature_group_model,
            nomenclature_model,
            warehouse_model,
            recipe_ingredient_model,
            recipe_model,
        )
    }

    def deserialize(self, source: dict) -> base_entity:
        """Восстанавливает одну модель и её вложенные объекты."""
        return self.__deserialize_model(source, {})

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

    def __deserialize_model(self, source: dict, loaded: _loaded_models) -> base_entity:
        validator.validate_type(source, dict, "Данные модели")
        model_type = source.get("model_type")
        validator.validate_required_string(model_type, "model_type")

        model = self.__models.get(model_type)
        if model is None:
            raise validation_error(f"Неизвестный тип модели «{model_type}»")

        entity_id = source.get("id")
        validator.validate_required_string(entity_id, "Идентификатор")
        if entity_id in loaded:
            previous, entity = loaded[entity_id]
            if entity is None:
                raise validation_error(f"Циклическая ссылка на модель «{entity_id}»")
            if previous != source:
                raise validation_error(f"Разные данные модели с ID «{entity_id}»")
            return entity

        loaded[entity_id] = (source, None)
        fields = {
            name: self.__deserialize_value(value, loaded)
            for name, value in source.items()
            if name != "model_type"
        }
        entity = model.from_dict(fields)
        loaded[entity_id] = (source, entity)
        return entity

    def __deserialize_value(self, value: object, loaded: _loaded_models) -> object:
        if isinstance(value, dict):
            return self.__deserialize_model(value, loaded)
        if isinstance(value, list):
            return [self.__deserialize_value(item, loaded) for item in value]
        return value
