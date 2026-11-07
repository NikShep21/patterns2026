from abc import ABC, abstractmethod
from typing import overload

from Src.Core.Abstract import base_entity
from Src.Dtos.report_data_dto import report_data_dto, report_reference_dto


class report_data_builder(ABC):
    """Определяет общий интерфейс подготовки данных сущности."""

    @abstractmethod
    def build(self, source: base_entity) -> report_data_dto:
        """Возвращает подготовленные данные сущности для отчёта."""
        pass

    @staticmethod
    @overload
    def _build_reference(source: base_entity) -> report_reference_dto: ...

    @staticmethod
    @overload
    def _build_reference(source: None) -> None: ...

    @staticmethod
    def _build_reference(
        source: base_entity | None,
    ) -> report_reference_dto | None:
        """Возвращает краткое представление сущности или None, если ссылки нет."""
        if source is None:
            return None

        return report_reference_dto(id=source.id, name=source.name)
