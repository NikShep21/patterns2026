"""Описания запросов и ответов для OpenAPI."""

from typing import Annotated, Any

from fastapi import Body

from Src.Models.comparison_type import comparison_type

report_responses: dict[int | str, dict[str, Any]] = {
    200: {
        "description": "Отчёт в выбранном формате",
        "content": {
            "text/csv": {"schema": {"type": "string", "format": "binary"}},
            "text/markdown": {"schema": {"type": "string", "format": "binary"}},
            "application/xml": {"schema": {"type": "string"}},
            "text/plain": {"schema": {"type": "string"}},
            "text/html": {"schema": {"type": "string"}},
        },
    },
    400: {"description": "Ошибка формирования отчёта"},
    404: {"description": "Сущность не найдена"},
}

entity_body = Annotated[
    dict[str, object],
    Body(
        description="Поля модели.",
        examples=[{"name": "Новый склад", "address": "ул. Ленина, 10"}],
    ),
]

entity_errors: dict[int | str, dict[str, Any]] = {
    400: {"description": "Некорректные данные или ссылка"},
    404: {"description": "Сущность не найдена"},
    409: {"description": "Конфликт кода, имени или связи"},
}


filter_condition_schema = {
    "type": "object",
    "additionalProperties": False,
    "required": ["field", "value"],
    "properties": {
        "field": {
            "type": "string",
            "description": "Публичное поле или вложенный путь.",
        },
        "comparison": {
            "type": "string",
            "enum": [item.value for item in comparison_type],
            "default": comparison_type.EQUALS.value,
        },
        "value": {"type": ["string", "number", "boolean", "null"]},
    },
}

filter_schema = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "conditions": {
            "type": "array",
            "items": filter_condition_schema,
            "default": [],
        },
    },
}

turnover_schema = {
    **filter_schema,
    "properties": {
        **filter_schema["properties"],
        "start": {
            "anyOf": [{"type": "string", "format": "date-time"}, {"type": "null"}],
            "description": "Включённое начало периода. Время без пояса считается UTC.",
        },
        "end": {
            "anyOf": [{"type": "string", "format": "date-time"}, {"type": "null"}],
            "description": "Включённое окончание периода. Время без пояса считается UTC.",
        },
    },
}

filter_body = Annotated[dict[str, object], Body(json_schema_extra=filter_schema)]
turnover_body = Annotated[dict[str, object], Body(json_schema_extra=turnover_schema)]
