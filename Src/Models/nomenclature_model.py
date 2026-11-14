from Src.Core.Abstract import base_entity
from Src.Core.Exceptions import validation_error
from Src.Core.Validator import validator
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_type import nomenclature_type
from Src.Models.range_model import range_model


class nomenclature_model(base_entity):
    """Модель номенклатуры."""

    _max_full_name_length = 255

    def __init__(
        self,
        name: str,
        full_name: str,
        type: nomenclature_type,
        group: nomenclature_group_model,
        range: range_model,
    ):
        """Инициализирует номенклатуру."""
        super().__init__()
        self.name = name
        self.full_name = full_name
        self.type = type
        self.group = group
        self.range = range

    @classmethod
    def from_dict(cls, data: dict) -> "nomenclature_model":
        """Восстанавливает номенклатуру с уже загруженными связями."""
        try:
            item_type = nomenclature_type(data.get("type"))
        except ValueError as error:
            raise validation_error("Некорректный тип номенклатуры") from error

        item = cls(
            name=data.get("name"),
            full_name=data.get("full_name"),
            type=item_type,
            group=data.get("group"),
            range=data.get("range"),
        )
        item._restore_id(data.get("id"))
        return item

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
    def type(self) -> nomenclature_type:
        """Возвращает тип номенклатурной позиции."""
        return self.__type

    @type.setter
    def type(self, value: nomenclature_type):
        """Изменяет тип номенклатурной позиции."""
        validator.validate_type(value, nomenclature_type, "Тип номенклатуры")
        self.__type = value

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
