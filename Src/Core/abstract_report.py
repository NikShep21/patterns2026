from abc import ABC, abstractmethod

from Src.Core.Abstract import base_entity
from Src.Dtos.report_result_dto import report_result_dto


class abstract_report(ABC):
    """Определяет общий интерфейс формирования отчётов."""

    @abstractmethod
    def build(self, source: base_entity) -> report_result_dto:
        """Формирует отчёт по переданной сущности."""
        pass
