from types import UnionType
from typing import Union, get_args, get_origin, get_type_hints

from Src.Core.Exceptions import validation_error
from Src.Logics.deserialize_factory import discover_models


class property_path:
    """Проверяет и раскрывает пути через публичные свойства и коллекции."""

    @classmethod
    def field_types(cls, model: type, path: str) -> tuple[type, ...]:
        """Определяет типы конечного поля независимо от наличия записей."""
        current = (model,)
        for part in path.split("."):
            following = []
            for source_type in current:
                attribute = getattr(source_type, part, None)
                if part.startswith("_") or not isinstance(attribute, property):
                    continue
                hints = get_type_hints(
                    attribute.fget,
                    globalns={**attribute.fget.__globals__, **discover_models()},
                )
                following.extend(cls.__element_types(hints.get("return")))
            if not following:
                raise validation_error(f"Неизвестное поле фильтра «{path}»")
            current = tuple(following)
        return current

    @classmethod
    def __element_types(cls, annotation) -> tuple[type, ...]:
        """Раскрывает объединения типов и типы элементов коллекций."""
        origin = get_origin(annotation)
        if origin in (Union, UnionType, list, tuple):
            return tuple(
                item_type
                for item in get_args(annotation)
                if item is not Ellipsis
                for item_type in cls.__element_types(item)
            )
        return (annotation,) if isinstance(annotation, type) else ()

    @classmethod
    def values(cls, source: object, path: str):
        """Возвращает значения пути, раскрывая вложенные списки и кортежи."""
        yield from cls.__walk(source, path.split("."))

    @classmethod
    def __walk(cls, source: object, parts: list[str]):
        """Читает значения по вложенному пути."""
        if isinstance(source, (list, tuple)):
            for item in source:
                yield from cls.__walk(item, parts)
        elif not parts:
            yield source
        elif source is not None:
            attribute = getattr(type(source), parts[0], None)
            if isinstance(attribute, property):
                yield from cls.__walk(getattr(source, parts[0]), parts[1:])
