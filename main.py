from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse

from Src.Core.Exceptions import application_error
from Src.Dtos.report_result_dto import report_result_dto
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
    description="Формирование отчётов по доменным сущностям",
    lifespan=lifespan,
)


@app.exception_handler(application_error)
async def handle_application_error(_, error: application_error):
    """Преобразует ошибку приложения в ответ с кодом 400."""
    return JSONResponse(status_code=400, content={"detail": str(error)})


def find_entity(value_type: entity_type, code: str):
    """Возвращает сущность указанного типа или сообщает об отсутствии."""
    entity = storage_manager().find(value_type, code)

    if entity is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Сущность типа «{value_type.value}» "
                f"с кодом «{code}» не найдена"
            ),
        )

    return entity


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
        return Response(
            content=result.binary,
            media_type=result.media_type,
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{file_name}"'
                )
            },
        )

    return Response(content=result.text, media_type=result.media_type)


@app.get(
    "/api/reports/{response_format}/{value_type}/{code}",
    response_class=Response,
    summary="Сформировать отчёт указанного формата",
)
def get_report(
    response_format: report_format,
    value_type: entity_type,
    code: str,
) -> Response:
    """Формирует отчёт выбранного формата по типу и коду сущности."""
    entity = find_entity(value_type, code)
    factory = report_factory(settings_manager().settings)
    result = factory.create(response_format).build(entity)
    return create_response(result, value_type, code)


@app.get(
    "/api/reports/{value_type}/{code}",
    response_class=Response,
    summary="Сформировать отчёт в формате из настроек",
)
def get_default_report(
    value_type: entity_type,
    code: str,
) -> Response:
    """Формирует отчёт с использованием create_default()."""
    entity = find_entity(value_type, code)
    factory = report_factory(settings_manager().settings)
    result = factory.create_default().build(entity)
    return create_response(result, value_type, code)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
