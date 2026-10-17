import pytest

from Src.Core.Exceptions import validation_error
from Src.Dtos.report_result_dto import report_result_dto


def test_success_report_result_dto_stores_text_content():
    """Проверяет хранение текстового результата отчёта."""
    # Подготовка
    content = "Наименование: Мука"

    # Действие
    result = report_result_dto(content, "text/plain", "txt")

    # Проверка
    assert result.text == content
    assert result.binary == content.encode("utf-8")
    assert result.is_binary is False
    assert result.media_type == "text/plain"
    assert result.file_extension == "txt"


def test_success_report_result_dto_stores_binary_content():
    """Проверяет хранение бинарного результата отчёта."""
    # Подготовка
    content = "Наименование;Мука".encode("utf-8")

    # Действие
    result = report_result_dto(content, "text/csv", "csv")

    # Проверка
    assert result.text == "Наименование;Мука"
    assert result.binary == content
    assert result.is_binary is True
    assert result.media_type == "text/csv"
    assert result.file_extension == "csv"


@pytest.mark.parametrize(
    ("content", "media_type", "file_extension"),
    (
        (123, "text/plain", "txt"),
        ("Данные", "", "txt"),
        ("Данные", "text/plain", ""),
    ),
)
def test_fail_report_result_dto_invalid_value_raises_validation_error(
    content,
    media_type,
    file_extension,
):
    """Проверяет отклонение некорректных параметров результата."""
    # Действие / Проверка
    with pytest.raises(validation_error):
        report_result_dto(content, media_type, file_extension)
