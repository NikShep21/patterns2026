from abc import ABC, abstractmethod


class abstract_converter(ABC):
    """Определяет общий интерфейс преобразования значения в словарь."""

    @abstractmethod
    def convert(self, field_name: str, value) -> dict:
        """Возвращает словарь с наименованием и данными поля."""
        pass
