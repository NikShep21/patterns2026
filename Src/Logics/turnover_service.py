from collections import defaultdict
from math import fsum

from Src.Core.Exceptions import validation_error
from Src.Core.Validator import validator
from Src.Dtos.turnover_filter_dto import turnover_filter_dto
from Src.Dtos.turnover_row_dto import turnover_row_dto
from Src.Logics.filter_prototype import filter_prototype
from Src.Logics.storage_manager import storage_manager
from Src.Models.transaction_model import transaction_model


class turnover_service:
    """Рассчитывает ОСВ из истории движений с отбором общим прототипом."""

    def __init__(self, storage: storage_manager):
        """Принимает хранилище складских транзакций."""
        self.__storage = storage

    def build(self, filters: turnover_filter_dto) -> tuple[turnover_row_dto, ...]:
        """Считает начальные остатки по полной истории выбранных групп."""
        validator.validate_type(filters, turnover_filter_dto, "Фильтр ОСВ")
        history = tuple(
            item for item in self.__storage.transactions
            if filters.end is None or item.period <= filters.end
        )

        opening = defaultdict(list)
        for item in history:
            if filters.start is not None and item.period < filters.start:
                opening[self.__key(item)].append(item.quantity)

        selected = filter_prototype(history, transaction_model).clone(filters)
        groups = {}
        movements = defaultdict(list)
        for item in selected.data:
            key = self.__key(item)
            groups.setdefault(key, item)
            if filters.start is None or item.period >= filters.start:
                movements[key].append(item.quantity)

        result = []
        for key, item in groups.items():
            quantities = movements[key]
            result.append(
                turnover_row_dto(
                    item.warehouse,
                    item.nomenclature,
                    item.range,
                    self.__sum(opening[key]),
                    self.__sum(value for value in quantities if value > 0),
                    self.__sum(-value for value in quantities if value < 0),
                )
            )
        return tuple(result)

    @staticmethod
    def __key(item: transaction_model) -> tuple[str, str, str]:
        """Разделяет количества по складу, товару и единице измерения."""
        return item.warehouse.id, item.nomenclature.id, item.range.id

    @staticmethod
    def __sum(values) -> float:
        """Суммирует количества и преобразует переполнение во внутреннюю ошибку."""
        try:
            return fsum(values)
        except OverflowError as error:
            raise validation_error("Переполнение при расчёте оборотов") from error
