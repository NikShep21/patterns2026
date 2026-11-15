from Src.Core.Abstract import base_entity
from Src.Core.Exceptions import (
    entity_conflict_error,
    entity_not_found_error,
    validation_error,
)
from Src.Core.Validator import validator
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.storage_manager import storage_manager
from Src.Models.recipe_model import recipe_model


class entity_service:
    """Координирует операции с доменными сущностями."""

    def __init__(self, storage: storage_manager):
        """Принимает хранилище доменных сущностей."""
        self.__storage = storage

    def list_entities(self, model: type[base_entity]) -> tuple[base_entity, ...]:
        """Возвращает все записи выбранной модели."""
        return self.__storage.entities(model)

    def get(self, model: type[base_entity], code: str) -> base_entity:
        """Возвращает запись или сообщает об её отсутствии."""
        entity = self.__storage.find(model, code)
        if entity is None:
            raise entity_not_found_error(f"Сущность с кодом «{code}» не найдена")
        return entity

    def create(self, model: type[base_entity], data: dict) -> base_entity:
        """Создаёт модель и сохраняет её после проверок."""
        entity = self.__build_entity(model, data)
        self.__validate_name(self.__storage.entities(model), entity)
        self.__storage.add(model, entity)
        return entity

    def update(
        self, model: type[base_entity], code: str, data: dict,
    ) -> base_entity:
        """Проверяет изменения и применяет их к существующей записи."""
        current = self.get(model, code)
        fields = {**convert_factory().convert(current), **data}
        if fields["id"] != current.id:
            self.__ensure_unreferenced(current)

        replacement = self.__build_entity(model, fields, current)
        self.__validate_name(self.__storage.entities(model), replacement, current)
        self.__validate_references_after_update(current, replacement)
        self.__storage.apply_update(current, replacement)
        return current

    def delete(self, model: type[base_entity], code: str) -> None:
        """Удаляет запись, когда на неё нет входящих ссылок."""
        entity = self.get(model, code)
        self.__ensure_unreferenced(entity)
        self.__storage.remove(model, entity)

    def __ensure_unreferenced(self, target: base_entity) -> None:
        """Запрещает удаление или смену кода при наличии входящих ссылок."""
        referrer = next(self.__storage.iter_referrers(target), None)
        if referrer is not None:
            raise entity_conflict_error(
                f"На сущность «{target.name}» ссылается «{referrer.name}»"
            )

    def __build_entity(
        self, model: type[base_entity], data: dict, current: base_entity | None = None,
    ) -> base_entity:
        """Собирает кандидата для записи и проверяет его связи с хранилищем."""
        known = {
            entity.id: entity
            for entity in self.__storage.all_entities()
            if entity is not current
        }
        model_type = model.__name__
        if data.get("model_type", model_type) != model_type:
            raise validation_error(f"Для этой коллекции ожидается «{model_type}»")
        if "id" in data:
            validator.validate_required_string(data["id"], "Код сущности")
            if data["id"] in known:
                raise entity_conflict_error(f"Код «{data['id']}» уже используется")

        candidate = deserialize_factory().deserialize(
            {**data, "model_type": model_type}, known=known,
        )
        pending = list(candidate.references())
        seen = set()
        while pending:
            reference = pending.pop()
            if reference is current:
                raise entity_conflict_error("Изменение создаёт циклическую ссылку")
            if known.get(reference.id) is not reference:
                raise validation_error(
                    f"Связанная сущность «{reference.name}» отсутствует в хранилище"
                )
            if reference.id not in seen:
                seen.add(reference.id)
                pending.extend(reference.references())
        return candidate

    def __validate_references_after_update(
        self, current: base_entity, replacement: base_entity,
    ) -> None:
        """Проверяет, сохраняются ли правила технологических карт после изменения."""
        for recipe in self.__storage.iter_referrers(current):
            if not isinstance(recipe, recipe_model):
                continue
            try:
                recipe.validate_entity_update(current, replacement)
            except validation_error as error:
                raise entity_conflict_error(str(error)) from error

    @staticmethod
    def __validate_name(
        collection: tuple[base_entity, ...], candidate: base_entity, current: base_entity | None = None,
    ) -> None:
        """Проверяет уникальность наименования в коллекции."""
        if any(
            entity is not current and entity.name.casefold() == candidate.name.casefold()
            for entity in collection
        ):
            raise entity_conflict_error(f"Наименование «{candidate.name}» уже используется")
