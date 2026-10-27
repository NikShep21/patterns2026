from abc import ABC, abstractmethod

from Src.Core.Abstract import base_entity


class report_data_builder(ABC):
    """Определяет общий интерфейс подготовки данных сущности."""

    @abstractmethod
    def build(self, source: base_entity) -> dict:
        """Возвращает данные сущности в виде вложенного словаря."""
        pass

    @staticmethod
    def _build_reference(source: base_entity | None) -> dict | None:
        """Возвращает краткое представление сущности или None, если ссылки нет."""
        if source is None:
            return None

        return {
            "id": source.id,
            "name": source.name,
        }
