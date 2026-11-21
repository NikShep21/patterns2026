from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Generic, Self, TypeVar

from Src.Dtos.filter_dto import filter_dto

T = TypeVar("T")


class abstract_prototype(ABC, Generic[T]):
    """Хранит состав выборки и задаёт контракт клонирования с фильтром."""

    def __init__(self, source: Iterable[T]):
        """Сохраняет состав выборки с исходными ссылками на модели."""
        self._data = tuple(source)

    @property
    def data(self) -> tuple[T, ...]:
        """Возвращает записи текущей выборки."""
        return self._data

    @abstractmethod
    def clone(self, filters: filter_dto) -> Self:
        """Создаёт прототип своего типа с отфильтрованным составом."""
        pass
