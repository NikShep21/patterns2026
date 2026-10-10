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
from Src.Models.warehouse_model import warehouse_model


class storage_manager(abstract_manager):
    """Хранит доменные модели приложения."""

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
        self.__ranges: list[range_model] = []
        self.__groups: list[nomenclature_group_model] = []
        self.__nomenclature: list[nomenclature_model] = []
        self.__warehouses: list[warehouse_model] = []
        self.__recipes: list[recipe_model] = []
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
            self.__ranges,
            value,
            range_model,
            "Единица измерения",
        )

    def add_group(self, value: nomenclature_group_model) -> None:
        """Добавляет уникальную группу номенклатуры."""
        self.__add_unique(
            self.__groups,
            value,
            nomenclature_group_model,
            "Группа номенклатуры",
        )

    def add_nomenclature(self, value: nomenclature_model) -> None:
        """Добавляет уникальную номенклатуру."""
        self.__add_unique(
            self.__nomenclature,
            value,
            nomenclature_model,
            "Номенклатура",
        )

    def add_warehouse(self, value: warehouse_model) -> None:
        """Добавляет уникальный склад."""
        self.__add_unique(self.__warehouses, value, warehouse_model, "Склад")

    def add_recipe(self, value: recipe_model) -> None:
        """Добавляет уникальную технологическую карту."""
        self.__add_unique(
            self.__recipes,
            value,
            recipe_model,
            "Технологическая карта",
        )

    def clear(self) -> None:
        """Очищает все коллекции хранилища."""
        self.__ranges.clear()
        self.__groups.clear()
        self.__nomenclature.clear()
        self.__warehouses.clear()
        self.__recipes.clear()
        self._is_loaded = False

    @property
    def ranges(self) -> tuple[range_model, ...]:
        """Возвращает единицы измерения."""
        return tuple(self.__ranges)

    @property
    def groups(self) -> tuple[nomenclature_group_model, ...]:
        """Возвращает группы номенклатуры."""
        return tuple(self.__groups)

    @property
    def nomenclature(self) -> tuple[nomenclature_model, ...]:
        """Возвращает номенклатуру."""
        return tuple(self.__nomenclature)

    @property
    def warehouses(self) -> tuple[warehouse_model, ...]:
        """Возвращает склады."""
        return tuple(self.__warehouses)

    @property
    def recipes(self) -> tuple[recipe_model, ...]:
        """Возвращает технологические карты."""
        return tuple(self.__recipes)

    @staticmethod
    def __add_unique(
        collection: list,
        value,
        expected_type,
        field_name: str,
    ) -> None:
        """Добавляет объект, если в коллекции ещё нет такого наименования."""
        validator.validate_type(value, expected_type, field_name)

        if any(item.name.casefold() == value.name.casefold() for item in collection):
            raise validation_error(
                f"Поле «{field_name}» с наименованием «{value.name}» уже существует"
            )

        collection.append(value)

    def __create_initial_data(self) -> None:
        """Создаёт минимальный набор данных для первого запуска."""
        kilogram = range_model.create_kilogram()
        gram = kilogram.base_range
        milliliter = range_model.create_milliliter()
        piece = range_model.create_piece()

        ingredients = nomenclature_group_model("Ингредиенты")
        finished_dishes = nomenclature_group_model("Готовые блюда")

        self.add_range(gram)
        self.add_range(kilogram)
        self.add_range(milliliter)
        self.add_range(piece)
        self.add_group(ingredients)
        self.add_group(finished_dishes)

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
        pancakes = nomenclature_model(
            "Блины",
            "Блины классические готовые",
            nomenclature_type.DISH,
            finished_dishes,
            piece,
        )

        for item in (
            flour,
            milk,
            egg,
            sugar,
            salt,
            vegetable_oil,
            pancakes,
        ):
            self.add_nomenclature(item)

        self.add_warehouse(
            warehouse_model("Основной склад", "ул. Центральная, д. 1")
        )
        self.add_recipe(
            recipe_model(
                "Классические блины",
                pancakes,
                [
                    recipe_ingredient_model(flour, 0.2, 200, 200),
                    recipe_ingredient_model(milk, 500, 500, 500),
                    recipe_ingredient_model(egg, 2, 120, 100),
                    recipe_ingredient_model(sugar, 30, 30, 30),
                    recipe_ingredient_model(salt, 2, 2, 2),
                    recipe_ingredient_model(vegetable_oil, 30, 30, 30),
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
