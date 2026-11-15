from contextlib import asynccontextmanager
from urllib.parse import quote

import uvicorn
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse

from Src.api_docs import entity_body, entity_errors, report_responses
from Src.api_entity_types import api_entity_model, storage_entity_type
from Src.Core.Exceptions import (
    application_error,
    entity_conflict_error,
    entity_not_found_error,
)
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.convert_factory import convert_factory
from Src.Logics.entity_service import entity_service
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.entity_type import entity_type
from Src.Models.report_format import report_format


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Загружает настройки и хранилище при запуске приложения."""
    settings = settings_manager()

    if not settings.is_loaded:
        settings.load()

    storage = storage_manager()

    if not storage.is_loaded:
        storage.load()

    yield


app = FastAPI(
    title="Ромашка",
    description="Отчёты и управление доменными сущностями",
    lifespan=lifespan,
)

@app.exception_handler(application_error)
async def handle_application_error(_, error: application_error):
    """Преобразует ошибку приложения в HTTP-ответ."""
    status = 400
    if isinstance(error, entity_not_found_error):
        status = 404
    elif isinstance(error, entity_conflict_error):
        status = 409
    return JSONResponse(status_code=status, content={"detail": str(error)})


def find_entity(value_type: storage_entity_type, code: str):
    """Возвращает сущность указанного типа или сообщает об отсутствии."""
    entity = storage_manager().find(api_entity_model(value_type.value), code)

    if entity is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Сущность типа «{value_type.value}» "
                f"с кодом «{code}» не найдена"
            ),
        )

    return entity


def find_report_entity(value_type: entity_type, code: str):
    """Ищет запись по коду из отчёта с учётом прежней обработки пробелов."""
    storage_type = storage_entity_type(value_type.value)
    if code != code.strip():
        entity = storage_manager().find(api_entity_model(storage_type.value), code)
        if entity is not None:
            return entity
    return find_entity(storage_type, code.strip())


def create_response(
    result: report_result_dto,
    value_type: entity_type,
    code: str,
) -> Response:
    """Формирует текстовый ответ или скачиваемый файл отчёта."""
    if result.is_binary:
        file_name = (
            f"{value_type.value}-{code}.{result.file_extension}"
        )
        encoded_file_name = quote(file_name, safe="")
        if encoded_file_name == file_name:
            disposition = f'attachment; filename="{file_name}"'
        else:
            disposition = f"attachment; filename*=UTF-8''{encoded_file_name}"
        return Response(
            content=result.binary,
            media_type=result.media_type,
            headers={"Content-Disposition": disposition},
        )

    return Response(content=result.text, media_type=result.media_type)


@app.get(
    "/api/report-formats",
    summary="Получить список форматов отчётов",
    tags=["Отчёты"],
)
def get_report_formats() -> list[report_format]:
    """Возвращает доступные форматы отчётов."""
    return list(report_format)


@app.get(
    "/api/reports/{response_format}/{value_type}/{code}",
    response_class=Response,
    responses=report_responses,
    tags=["Отчёты"],
    summary="Сформировать отчёт указанного формата",
)
def get_report(
    response_format: report_format,
    value_type: entity_type,
    code: str,
) -> Response:
    """Формирует отчёт выбранного формата по типу и коду сущности."""
    entity = find_report_entity(value_type, code)
    factory = report_factory(settings_manager().settings)
    result = factory.create(response_format).build(entity)
    return create_response(result, value_type, code)


@app.get(
    "/api/reports/{value_type}/{code}",
    response_class=Response,
    responses=report_responses,
    tags=["Отчёты"],
    summary="Сформировать отчёт в формате из настроек",
)
def get_default_report(
    value_type: entity_type,
    code: str,
) -> Response:
    """Формирует отчёт с использованием create_default()."""
    entity = find_report_entity(value_type, code)
    factory = report_factory(settings_manager().settings)
    result = factory.create_default().build(entity)
    return create_response(result, value_type, code)


@app.get("/api/entities/{value_type}", tags=["Сущности"])
async def list_entities(value_type: storage_entity_type) -> list[dict]:
    """Возвращает все записи выбранной коллекции."""
    serializer = convert_factory()
    entities = entity_service(storage_manager()).list_entities(api_entity_model(value_type.value))
    return [serializer.convert(entity) for entity in entities]


@app.get(
    "/api/entities/{value_type}/{code}",
    tags=["Сущности"],
    responses={404: entity_errors[404]},
)
async def get_entity(value_type: storage_entity_type, code: str) -> dict:
    """Возвращает запись по коду."""
    entity = entity_service(storage_manager()).get(api_entity_model(value_type.value), code)
    return convert_factory().convert(entity)


@app.post(
    "/api/entities/{value_type}",
    status_code=201,
    tags=["Сущности"],
    responses={400: entity_errors[400], 409: entity_errors[409]},
)
async def create_entity(value_type: storage_entity_type, data: entity_body) -> dict:
    """Проверяет данные и создаёт запись."""
    entity = entity_service(storage_manager()).create(api_entity_model(value_type.value), data)
    return convert_factory().convert(entity)


@app.patch(
    "/api/entities/{value_type}/{code}",
    tags=["Сущности"],
    responses=entity_errors,
)
async def update_entity(value_type: storage_entity_type, code: str, data: entity_body) -> dict:
    """Обновляет переданные поля записи."""
    entity = entity_service(storage_manager()).update(api_entity_model(value_type.value), code, data)
    return convert_factory().convert(entity)


@app.delete(
    "/api/entities/{value_type}/{code}",
    status_code=204,
    tags=["Сущности"],
    responses={404: entity_errors[404], 409: entity_errors[409]},
)
async def delete_entity(value_type: storage_entity_type, code: str) -> None:
    """Удаляет запись, если на неё не ссылаются другие сущности."""
    entity_service(storage_manager()).delete(api_entity_model(value_type.value), code)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
