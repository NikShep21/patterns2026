from Src.Core.Abstract import base_entity
from Src.Core.Validator import validator
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.range_model import range_model


class nomenclature_model(base_entity):
    """Модель номенклатуры."""

    _max_full_name_length = 255

    def __init__(
        self,
        name: str,
        full_name: str,
        group: nomenclature_group_model,
        range: range_model,
    ):
        """Инициализирует номенклатуру."""
        super().__init__()
        self.name = name
        self.full_name = full_name
        self.group = group
        self.range = range

    @property
    def full_name(self) -> str:
        """Возвращает полное наименование номенклатуры."""
        return self.__full_name

    @full_name.setter
    def full_name(self, value: str):
        """Изменяет полное наименование номенклатуры."""
        validator.validate_required_string(
            value,
            "Полное наименование",
            self._max_full_name_length,
        )
        self.__full_name = value.strip()

    @property
    def group(self) -> nomenclature_group_model:
        """Возвращает группу номенклатуры."""
        return self.__group

    @group.setter
    def group(self, value: nomenclature_group_model):
        """Изменяет группу номенклатуры."""
        validator.validate_type(value, nomenclature_group_model, "Группа")
        self.__group = value

    @property
    def range(self) -> range_model:
        """Возвращает единицу измерения номенклатуры."""
        return self.__range

    @range.setter
    def range(self, value: range_model):
        """Изменяет единицу измерения номенклатуры."""
        validator.validate_type(value, range_model, "Единица измерения")
        self.__range = value
