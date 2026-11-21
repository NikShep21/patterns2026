from Src.Core.Abstract import base_entity
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.filter_prototype import filter_prototype
from Src.Logics.storage_manager import storage_manager


class filter_service:
    """Получает доменные записи и применяет общий прототип фильтрации."""

    def __init__(self, storage: storage_manager):
        """Принимает хранилище исходных моделей."""
        self.__storage = storage

    def select(self, model: type[base_entity], filters: filter_dto) -> filter_prototype:
        """Возвращает прототип с отобранными записями выбранного класса."""
        return filter_prototype(self.__storage.entities(model), model).clone(filters)
