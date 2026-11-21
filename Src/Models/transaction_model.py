from datetime import datetime
from math import isfinite

from Src.Core.Abstract import base_entity
from Src.Core.Exceptions import validation_error
from Src.Core.Validator import validator
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model


class transaction_model(base_entity):
    """Хранит неизменяемое движение товара по складу в указанной единице."""

    def __init__(
        self,
        nomenclature: nomenclature_model,
        warehouse: warehouse_model,
        range: range_model,
        quantity: int | float,
        period: datetime,
    ):
        """Проверяет ссылки, ненулевое количество и время движения."""
        super().__init__()
        validator.validate_type(nomenclature, nomenclature_model, "Номенклатура")
        validator.validate_type(warehouse, warehouse_model, "Склад")
        validator.validate_type(range, range_model, "Единица измерения")
        if type(quantity) not in (int, float):
            raise validation_error("Количество движения должно быть числом")
        try:
            finite = isfinite(quantity)
        except OverflowError as error:
            raise validation_error("Количество движения слишком велико") from error
        if not finite or quantity == 0:
            raise validation_error(
                "Количество движения должно быть конечным и ненулевым"
            )
        validator.validate_type(period, datetime, "Период движения")
        self.__nomenclature = nomenclature
        self.__warehouse = warehouse
        self.__range = range
        self.__quantity = quantity
        self.__period = validator.parse_datetime(period, "Период движения")

    @classmethod
    def from_dict(cls, data: dict) -> "transaction_model":
        """Восстанавливает движение с исходным ID и загруженными ссылками."""
        transaction = cls(
            data.get("nomenclature"),
            data.get("warehouse"),
            data.get("range"),
            data.get("quantity"),
            validator.parse_datetime(data.get("period"), "Период движения"),
        )
        transaction._restore_id(data.get("id"))
        return transaction

    @property
    def name(self) -> str:
        """Возвращает текущее наименование товара для общего интерфейса сущностей."""
        return self.nomenclature.name

    @property
    def nomenclature(self) -> nomenclature_model:
        """Возвращает товар движения."""
        return self.__nomenclature

    @property
    def warehouse(self) -> warehouse_model:
        """Возвращает склад движения."""
        return self.__warehouse

    @property
    def range(self) -> range_model:
        """Возвращает единицу, в которой указано количество."""
        return self.__range

    @property
    def quantity(self) -> int | float:
        """Возвращает положительный приход или отрицательный расход."""
        return self.__quantity

    @property
    def period(self) -> datetime:
        """Возвращает время движения в UTC."""
        return self.__period

    def references(self) -> tuple[base_entity, ...]:
        """Возвращает используемые товар, склад и единицу измерения."""
        return self.nomenclature, self.warehouse, self.range
