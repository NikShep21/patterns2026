from collections.abc import Iterator
from datetime import datetime, timezone
from typing import TypeVar, cast

from Src.Core.Abstract import base_entity
from Src.Core.Exceptions import operation_error, validation_error
from Src.Core.Validator import validator
from Src.Core.abstract_manager import abstract_manager
from Src.Logics.settings_manager import settings_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_type import nomenclature_type
from Src.Models.range_model import range_model
from Src.Models.recipe_ingredient_model import recipe_ingredient_model
from Src.Models.recipe_model import recipe_model
from Src.Models.transaction_model import transaction_model
from Src.Models.warehouse_model import warehouse_model


_model = TypeVar("_model", bound=base_entity)


class storage_manager(abstract_manager):
    """Хранит модели и обновляет индекс ссылок при изменении записей."""

    __instance = None

    def __new__(cls):
        """Возвращает единственный экземпляр менеджера."""
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self):
        """Инициализирует коллекции хранилища."""
        if getattr(self, "_initialized", False):
            return

        super().__init__()
        self.__collections: dict[type[base_entity], list[base_entity]] = {}
        self.__incoming: dict[int, dict[int, base_entity]] = {}
        self._initialized = True

    def load(self, file_name: str = "") -> None:
        """Загружает настройки и подготавливает хранилище."""
        manager = settings_manager()

        if not manager.is_loaded:
            manager.load(file_name)

        self._is_loaded = self.convert()

    def convert(self) -> bool:
        """Формирует первичные данные при первом запуске."""
        manager = settings_manager()

        if not manager.is_loaded:
            raise operation_error("Настройки приложения не загружены")

        self.clear()

        if manager.settings.is_first_start:
            self.__create_initial_data()

        self._is_loaded = True
        return True

    def add_range(self, value: range_model) -> None:
        """Добавляет уникальную единицу измерения."""
        self.__add_unique(
            value,
            range_model,
            "Единица измерения",
        )

    def add_group(self, value: nomenclature_group_model) -> None:
        """Добавляет уникальную группу номенклатуры."""
        self.__add_unique(
            value,
            nomenclature_group_model,
            "Группа номенклатуры",
        )

    def add_nomenclature(self, value: nomenclature_model) -> None:
        """Добавляет уникальную номенклатуру."""
        self.__add_unique(
            value,
            nomenclature_model,
            "Номенклатура",
        )

    def add_warehouse(self, value: warehouse_model) -> None:
        """Добавляет уникальный склад."""
        self.__add_unique(value, warehouse_model, "Склад")

    def add_recipe(self, value: recipe_model) -> None:
        """Добавляет уникальную технологическую карту."""
        self.__add_unique(
            value,
            recipe_model,
            "Технологическая карта",
        )

    def clear(self) -> None:
        """Очищает все коллекции хранилища."""
        self.__collections.clear()
        self.__incoming.clear()
        self._is_loaded = False

    def find(self, model: type[_model], code: str) -> _model | None:
        """Возвращает сущность указанного класса по уникальному коду."""
        self.__validate_model(model)
        validator.validate_required_string(code, "Код сущности")
        collection = self.__collections.get(model, ())
        entity = next((item for item in collection if item.id == code), None)
        return cast(_model | None, entity)

    def entities(self, model: type[_model]) -> tuple[_model, ...]:
        """Возвращает записи указанного класса."""
        self.__validate_model(model)
        return cast(tuple[_model, ...], tuple(self.__collections.get(model, ())))

    def all_entities(self) -> tuple[base_entity, ...]:
        """Возвращает записи всех коллекций."""
        return tuple(
            entity for collection in self.__collections.values() for entity in collection
        )

    def add(self, model: type[base_entity], value: base_entity) -> None:
        """Добавляет модель в коллекцию её типа."""
        self.__validate_model(model)
        validator.validate_type(value, model, "Сущность")
        references = value.references()
        self.__collections.setdefault(model, []).append(value)
        self.__update_references(value, (), references)

    def apply_update(self, current: base_entity, replacement: base_entity) -> None:
        """Применяет проверенное обновление сохранённой записи и её связей."""
        previous = current.references()
        updated = replacement.references()
        current.replace_state(replacement)
        self.__update_references(current, previous, updated)

    def remove(self, model: type[base_entity], value: base_entity) -> None:
        """Удаляет модель из выбранной коллекции."""
        collection = self.__collections[model]
        for index, entity in enumerate(collection):
            if entity is value:
                references = entity.references()
                del collection[index]
                self.__update_references(entity, references, ())
                return
        raise ValueError("Сущность отсутствует в коллекции")

    def iter_referrers(self, target: base_entity) -> Iterator[base_entity]:
        """Перебирает сохранённые записи, которые ссылаются на цель."""
        incoming = self.__incoming.get(id(target))
        return iter(incoming.values()) if incoming is not None else iter(())

    def __update_references(
        self,
        source: base_entity,
        previous: tuple[base_entity, ...],
        updated: tuple[base_entity, ...],
    ) -> None:
        """Обновляет индекс по идентичности объектов. Коды записей могут меняться."""
        source_key = id(source)
        previous_keys = {id(target) for target in previous if target is not source}
        updated_keys = {id(target) for target in updated if target is not source}
        for target_key in previous_keys - updated_keys:
            incoming = self.__incoming.get(target_key)
            if incoming is not None:
                incoming.pop(source_key, None)
                if not incoming:
                    del self.__incoming[target_key]
        for target_key in updated_keys - previous_keys:
            self.__incoming.setdefault(target_key, {})[source_key] = source

    @staticmethod
    def __validate_model(model: type[base_entity]) -> None:
        """Проверяет, что ключ коллекции является классом модели."""
        validator.validate_type(model, type, "Класс модели")
        if not issubclass(model, base_entity):
            raise validation_error("Ожидается класс доменной модели")

    @property
    def ranges(self) -> tuple[range_model, ...]:
        """Возвращает единицы измерения."""
        return self.entities(range_model)

    @property
    def groups(self) -> tuple[nomenclature_group_model, ...]:
        """Возвращает группы номенклатуры."""
        return self.entities(nomenclature_group_model)

    @property
    def nomenclature(self) -> tuple[nomenclature_model, ...]:
        """Возвращает номенклатуру."""
        return self.entities(nomenclature_model)

    @property
    def warehouses(self) -> tuple[warehouse_model, ...]:
        """Возвращает склады."""
        return self.entities(warehouse_model)

    @property
    def recipes(self) -> tuple[recipe_model, ...]:
        """Возвращает технологические карты."""
        return self.entities(recipe_model)

    @property
    def transactions(self) -> tuple[transaction_model, ...]:
        """Возвращает складские движения для расчёта остатков и оборотов."""
        return self.entities(transaction_model)

    def __add_unique(
        self,
        value,
        expected_type,
        field_name: str,
    ) -> None:
        """Добавляет объект, если в коллекции ещё нет такого наименования."""
        validator.validate_type(value, expected_type, field_name)

        if any(item.name.casefold() == value.name.casefold() for item in self.entities(expected_type)):
            raise validation_error(
                f"Поле «{field_name}» с наименованием «{value.name}» уже существует"
            )

        self.add(expected_type, value)

    def __create_initial_data(self) -> None:
        """Создаёт минимальный набор данных для первого запуска."""
        kilogram = range_model.create_kilogram()
        gram = kilogram.base_range
        milliliter = range_model.create_milliliter()
        piece = range_model.create_piece()

        ingredients = nomenclature_group_model("Ингредиенты")
        semi_finished = nomenclature_group_model("Полуфабрикаты")
        finished_dishes = nomenclature_group_model("Готовые блюда")
        packaging = nomenclature_group_model("Упаковка")

        self.add_range(gram)
        self.add_range(kilogram)
        self.add_range(milliliter)
        self.add_range(piece)
        self.add_group(ingredients)
        self.add_group(semi_finished)
        self.add_group(finished_dishes)
        self.add_group(packaging)

        flour = nomenclature_model(
            "Мука",
            "Мука пшеничная высшего сорта",
            nomenclature_type.RAW_MATERIAL,
            ingredients,
            kilogram,
        )
        milk = nomenclature_model(
            "Молоко",
            "Молоко питьевое пастеризованное",
            nomenclature_type.RAW_MATERIAL,
            ingredients,
            milliliter,
        )
        egg = nomenclature_model(
            "Яйцо",
            "Яйцо куриное пищевое",
            nomenclature_type.RAW_MATERIAL,
            ingredients,
            piece,
        )
        sugar = nomenclature_model(
            "Сахар",
            "Сахар белый кристаллический",
            nomenclature_type.RAW_MATERIAL,
            ingredients,
            gram,
        )
        salt = nomenclature_model(
            "Соль",
            "Соль поваренная пищевая",
            nomenclature_type.RAW_MATERIAL,
            ingredients,
            gram,
        )
        vegetable_oil = nomenclature_model(
            "Масло растительное",
            "Масло подсолнечное рафинированное",
            nomenclature_type.RAW_MATERIAL,
            ingredients,
            milliliter,
        )
        dough = nomenclature_model(
            "Тесто для блинов",
            "Тесто для классических блинов",
            nomenclature_type.SEMI_FINISHED,
            semi_finished,
            gram,
        )
        pancakes = nomenclature_model(
            "Блины",
            "Блины классические готовые",
            nomenclature_type.DISH,
            finished_dishes,
            piece,
        )
        pancake_package = nomenclature_model(
            "Упаковка для блинов",
            "Контейнер для готовых блинов",
            nomenclature_type.PACKAGING,
            packaging,
            piece,
        )

        for item in (
            flour,
            milk,
            egg,
            sugar,
            salt,
            vegetable_oil,
            dough,
            pancakes,
            pancake_package,
        ):
            self.add_nomenclature(item)

        self.add_warehouse(
            warehouse_model("Основной склад", "ул. Центральная, д. 1")
        )
        for item, quantity, day in (
            (flour, 10, 1),
            (flour, -2, 3),
            (flour, 5, 5),
            (milk, 10000, 1),
            (milk, -1500, 4),
            (sugar, 3000, 1),
        ):
            self.add(
                transaction_model,
                transaction_model(
                    item,
                    self.warehouses[0],
                    item.range,
                    quantity,
                    datetime(2026, 11, day, 12, tzinfo=timezone.utc),
                ),
            )
        dough_recipe = recipe_model(
            "Тесто для блинов",
            dough,
            [
                recipe_ingredient_model(flour, 0.2, 200, 200),
                recipe_ingredient_model(milk, 500, 500, 500),
                recipe_ingredient_model(egg, 2, 120, 100),
                recipe_ingredient_model(sugar, 30, 30, 30),
                recipe_ingredient_model(salt, 2, 2, 2),
                recipe_ingredient_model(vegetable_oil, 30, 30, 30),
            ],
            862,
            10,
            [
                "Взбить яйца с сахаром и солью.",
                "Добавить половину молока и перемешать.",
                "Постепенно всыпать муку и размешать тесто.",
                "Добавить оставшееся молоко и растительное масло.",
                "Оставить тесто на 10 минут.",
            ],
        )
        self.add_recipe(dough_recipe)
        self.add_recipe(
            recipe_model(
                "Классические блины",
                pancakes,
                [
                    recipe_ingredient_model(
                        dough,
                        recipe=dough_recipe,
                    ),
                    recipe_ingredient_model(pancake_package, 1, 20, 20),
                ],
                10,
                30,
                [
                    "Взбить яйца с сахаром и солью.",
                    "Добавить половину молока и перемешать.",
                    "Постепенно всыпать муку и размешать тесто.",
                    "Добавить оставшееся молоко и растительное масло.",
                    "Оставить тесто на 10 минут.",
                    "Выпекать блины с двух сторон до золотистого цвета.",
                ],
            )
        )
