import pytest

from Src.Core.Exceptions import validation_error
from Src.Logics.csv_report import csv_report
from Src.Logics.html_report import html_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.report_factory import report_factory
from Src.Logics.text_report import text_report
from Src.Logics.xml_report import xml_report
from Src.Models.report_format import report_format
from Src.Models.settings_model import settings_model


@pytest.mark.parametrize(
    ("value", "expected_type"),
    (
        (report_format.CSV, csv_report),
        (report_format.MARKDOWN, markdown_report),
        (report_format.XML, xml_report),
        (report_format.TXT, text_report),
        (report_format.HTML, html_report),
    ),
)
def test_success_report_factory_creates_requested_report(
    value,
    expected_type,
):
    """Проверяет создание отчёта каждого поддерживаемого формата."""
    # Подготовка
    factory = report_factory(settings_model())

    # Действие
    report = factory.create(value)

    # Проверка
    assert isinstance(report, expected_type)


@pytest.mark.parametrize("value", tuple(report_format))
def test_success_report_factory_creates_default_report(value):
    """Проверяет выбор формата отчёта из настроек."""
    # Подготовка
    settings = settings_model()
    settings.response_format = value
    factory = report_factory(settings)

    # Действие
    default_report = factory.create_default()
    explicit_report = factory.create(value)

    # Проверка
    assert type(default_report) is type(explicit_report)


def test_success_report_factory_uses_current_settings():
    """Проверяет применение изменённого формата настроек."""
    # Подготовка
    settings = settings_model()
    factory = report_factory(settings)
    settings.response_format = report_format.XML

    # Действие
    report = factory.create_default()

    # Проверка
    assert isinstance(report, xml_report)


@pytest.mark.parametrize("value", (None, "TXT", 1))
def test_fail_report_factory_invalid_format_raises_validation_error(value):
    """Проверяет ошибку при некорректном формате отчёта."""
    # Подготовка
    factory = report_factory(settings_model())

    # Действие / Проверка
    with pytest.raises(validation_error):
        factory.create(value)


def test_fail_report_factory_invalid_settings_raises_validation_error():
    """Проверяет ошибку при создании фабрики без настроек."""
    # Действие / Проверка
    with pytest.raises(validation_error):
        report_factory(None)
