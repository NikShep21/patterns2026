from collections.abc import Iterator
from dataclasses import dataclass, field, fields
from typing import ClassVar


@dataclass(frozen=True)
class report_node_dto:
    """Предоставляет форматировщикам поля узла отчёта."""

    def iter_fields(self) -> Iterator[tuple[str, object]]:
        for definition in fields(self):
            value = getattr(self, definition.name)
            if value is None and definition.metadata.get("omit_none"):
                continue
            yield definition.name, value


class report_data_dto(report_node_dto):
    """Данные верхнего уровня с именем раздела отчёта."""

    root_name: ClassVar[str]


@dataclass(frozen=True)
class report_reference_dto(report_node_dto):
    id: str
    name: str


@dataclass(frozen=True)
class range_report_data_dto(report_data_dto):
    root_name: ClassVar[str] = "range"

    id: str
    name: str
    coefficient: int | float
    base_range: report_reference_dto | None


@dataclass(frozen=True)
class nomenclature_report_data_dto(report_data_dto):
    root_name: ClassVar[str] = "nomenclature"

    id: str
    name: str
    full_name: str
    type: str
    group: report_reference_dto
    range: report_reference_dto


@dataclass(frozen=True)
class recipe_ingredient_report_data_dto(report_node_dto):
    id: str
    nomenclature: report_reference_dto
    quantity: int | float
    range: report_reference_dto
    gross_weight: int | float
    net_weight: int | float
    recipe: report_reference_dto | None = field(
        default=None,
        metadata={"omit_none": True},
    )


@dataclass(frozen=True)
class recipe_report_data_dto(report_data_dto):
    root_name: ClassVar[str] = "recipe"

    id: str
    name: str
    result: report_reference_dto
    output_quantity: int | float
    output_range: report_reference_dto
    cooking_time: int | float
    gross_weight: int | float
    net_weight: int | float
    ingredients: tuple[recipe_ingredient_report_data_dto, ...]
    steps: tuple[str, ...]
