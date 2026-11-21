from math import fsum, isfinite

from Src.Core.Exceptions import validation_error
from Src.Dtos.report_data_dto import report_reference_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model


class turnover_row_dto:
    """Передаёт остатки и обороты товара на одном складе в одной единице."""

    def __init__(
        self,
        warehouse: warehouse_model,
        nomenclature: nomenclature_model,
        range: range_model,
        opening_balance: float,
        income: float,
        expense: float,
    ):
        """Сохраняет данные строки и проверяет результат расчёта."""
        self.__warehouse = report_reference_dto(warehouse.id, warehouse.name)
        self.__nomenclature = report_reference_dto(nomenclature.id, nomenclature.name)
        self.__range = report_reference_dto(range.id, range.name)
        self.__opening_balance = opening_balance
        self.__income = income
        self.__expense = expense
        try:
            closing = fsum((opening_balance, income, -expense))
        except OverflowError as error:
            raise validation_error("Переполнение при расчёте остатка") from error
        if not all(
            isfinite(value) for value in (opening_balance, income, expense, closing)
        ):
            raise validation_error("Остатки и обороты должны быть конечными числами")
        self.__closing_balance = closing

    @property
    def warehouse(self) -> report_reference_dto:
        """Возвращает код и наименование склада."""
        return self.__warehouse

    @property
    def nomenclature(self) -> report_reference_dto:
        """Возвращает код и наименование товара."""
        return self.__nomenclature

    @property
    def range(self) -> report_reference_dto:
        """Возвращает код и наименование единицы количества."""
        return self.__range

    @property
    def opening_balance(self) -> float:
        """Возвращает остаток до начала периода."""
        return self.__opening_balance

    @property
    def income(self) -> float:
        """Возвращает сумму поступлений периода."""
        return self.__income

    @property
    def expense(self) -> float:
        """Возвращает сумму расходов периода положительным числом."""
        return self.__expense

    @property
    def closing_balance(self) -> float:
        """Возвращает начальный остаток плюс приход минус расход."""
        return self.__closing_balance
