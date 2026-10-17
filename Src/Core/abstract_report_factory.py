from abc import ABC, abstractmethod

from Src.Core.abstract_report import abstract_report
from Src.Models.report_format import report_format


class abstract_report_factory(ABC):
    """Определяет общий интерфейс фабрики отчётов."""

    @abstractmethod
    def create(self, value: report_format) -> abstract_report:
        """Создаёт отчёт указанного формата."""
        pass

    @abstractmethod
    def create_default(self) -> abstract_report:
        """Создаёт отчёт в формате из настроек приложения."""
        pass
