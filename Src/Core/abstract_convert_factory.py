from abc import ABC, abstractmethod

from Src.Core.abstract_converter import abstract_converter


class abstract_convert_factory(ABC):
    """Определяет выбор конвертера и преобразование исходных данных."""

    @abstractmethod
    def create(self, value) -> abstract_converter:
        """Возвращает конвертер для переданного значения."""
        pass

    @abstractmethod
    def convert(self, source) -> dict:
        """Преобразует исходные данные в словарь."""
        pass
