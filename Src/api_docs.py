"""Описания запросов и ответов для OpenAPI."""

from typing import Annotated

from fastapi import Body


report_responses = {
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

entity_errors = {
    400: {"description": "Некорректные данные или ссылка"},
    404: {"description": "Сущность не найдена"},
    409: {"description": "Конфликт кода, имени или связи"},
}
