from abc import ABC, abstractmethod

from Src.Core.Abstract import base_entity


class report_data_builder(ABC):
    """Определяет общий интерфейс подготовки данных сущности."""

    @abstractmethod
    def build(self, source: base_entity) -> dict:
        """Возвращает данные сущности в виде вложенного словаря."""
        pass

    @staticmethod
    def _build_reference(source: base_entity) -> dict:
        """Возвращает краткое представление связанной сущности."""
        return {
            "id": source.id,
            "name": source.name,
        }
