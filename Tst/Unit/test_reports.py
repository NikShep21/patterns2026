from xml.etree.ElementTree import fromstring

import pytest

from Src.Logics.csv_report import csv_report
from Src.Logics.html_report import html_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.text_report import text_report
from Src.Logics.xml_report import xml_report
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_type import nomenclature_type
from Src.Models.range_model import range_model
from Src.Models.recipe_ingredient_model import recipe_ingredient_model
from Src.Models.recipe_model import recipe_model


@pytest.fixture
def report_sources():
    """Создаёт все поддерживаемые источники отчётов."""
    gram = range_model.create_gram()
    ingredients = nomenclature_group_model("Ингредиенты")
    dishes = nomenclature_group_model("Готовые блюда")
    flour = nomenclature_model(
        "Мука",
        "Мука пшеничная",
        nomenclature_type.RAW_MATERIAL,
        ingredients,
        gram,
    )
    pancakes = nomenclature_model(
        "Блины",
        "Блины классические",
        nomenclature_type.DISH,
        dishes,
        range_model.create_piece(),
    )
    recipe = recipe_model(
        "Классические блины",
        pancakes,
        [recipe_ingredient_model(flour, 0.2, 220, 200)],
        10,
        30,
        ["Замесить тесто.", "Выпекать блины."],
    )
    return gram, flour, recipe


@pytest.mark.parametrize(
    ("report_class", "is_binary", "media_type", "extension"),
    (
        (text_report, False, "text/plain; charset=utf-8", "txt"),
        (markdown_report, True, "text/markdown; charset=utf-8", "md"),
        (csv_report, True, "text/csv; charset=utf-8", "csv"),
        (xml_report, False, "application/xml; charset=utf-8", "xml"),
        (html_report, False, "text/html; charset=utf-8", "html"),
    ),
)
def test_success_report_builds_all_supported_entities(
    report_sources,
    report_class,
    is_binary,
    media_type,
    extension,
):
    """Проверяет формирование отчёта по каждому поддерживаемому типу."""
    # Подготовка
    report = report_class()

    for source in report_sources:
        # Действие
        result = report.build(source)

        # Проверка
        assert source.id in result.text
        assert source.name in result.text
        assert result.is_binary is is_binary
        assert result.media_type == media_type
        assert result.file_extension == extension


def test_success_markdown_report_contains_table(report_sources):
    """Проверяет табличную структуру Markdown-отчёта."""
    # Подготовка
    _, flour, _ = report_sources

    # Действие
    result = markdown_report().build(flour)

    # Проверка
    assert "| Поле | Значение |" in result.text
    assert "nomenclature.full_name" in result.text


def test_success_csv_report_contains_header(report_sources):
    """Проверяет заголовок и разделитель CSV-отчёта."""
    # Подготовка
    _, flour, _ = report_sources

    # Действие
    result = csv_report().build(flour)

    # Проверка
    assert result.text.startswith("Поле;Значение\n")
    assert "nomenclature.name;Мука" in result.text


def test_success_xml_report_contains_structured_data(report_sources):
    """Проверяет структуру XML-отчёта."""
    # Подготовка
    _, flour, _ = report_sources

    # Действие
    result = xml_report().build(flour)

    # Проверка
    assert fromstring(result.text).tag == "nomenclature"
    assert "<name>Мука</name>" in result.text


def test_success_html_report_contains_table(report_sources):
    """Проверяет структуру HTML-отчёта."""
    # Подготовка
    _, flour, _ = report_sources

    # Действие
    result = html_report().build(flour)

    # Проверка
    assert result.text.startswith("<!DOCTYPE html>")
    assert "<table>" in result.text
    assert "<td>Мука</td>" in result.text
