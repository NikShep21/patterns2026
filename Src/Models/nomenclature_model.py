from Src.Core.Abstract import base_entity
from Src.Core.Exceptions import validation_error
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
        if not isinstance(value, str):
            raise validation_error(
                "Полное наименование должно иметь строковый тип"
            )

        value = value.strip()

        if not value:
            raise validation_error("Полное наименование не может быть пустым")

        if len(value) > self._max_full_name_length:
            raise validation_error(
                "Полное наименование не может быть длиннее "
                f"{self._max_full_name_length} символов"
            )

        self.__full_name = value

    @property
    def group(self) -> nomenclature_group_model:
        """Возвращает группу номенклатуры."""
        return self.__group

    @group.setter
    def group(self, value: nomenclature_group_model):
        """Изменяет группу номенклатуры."""
        if not isinstance(value, nomenclature_group_model):
            raise validation_error(
                "Группа должна иметь тип nomenclature_group_model"
            )

        self.__group = value

    @property
    def range(self) -> range_model:
        """Возвращает единицу измерения номенклатуры."""
        return self.__range

    @range.setter
    def range(self, value: range_model):
        """Изменяет единицу измерения номенклатуры."""
        if not isinstance(value, range_model):
            raise validation_error(
                "Единица измерения должна иметь тип range_model"
            )

        self.__range = value
