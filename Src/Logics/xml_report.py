from xml.etree.ElementTree import Element, SubElement, indent, tostring

from Src.Core.Abstract import base_entity
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_data_builder import report_data_builder


class xml_report(abstract_report):
    """Формирует отчёт в формате XML."""

    def build(self, source: base_entity) -> report_result_dto:
        """Формирует XML-отчёт по сущности."""
        data = report_data_builder.build(source)
        root_name, root_value = next(iter(data.items()))
        root = Element(root_name)
        self.__fill_element(root, root_value)
        indent(root)
        content = tostring(
            root,
            encoding="unicode",
            xml_declaration=False,
        )

        return report_result_dto(
            content,
            "application/xml; charset=utf-8",
            "xml",
        )

    def __fill_element(self, element: Element, value) -> None:
        """Рекурсивно добавляет данные в XML-элемент."""
        if isinstance(value, dict):
            for key, item in value.items():
                child = SubElement(element, key)
                self.__fill_element(child, item)
            return

        if isinstance(value, (list, tuple)):
            for item in value:
                child = SubElement(element, "item")
                self.__fill_element(child, item)
            return

        element.text = str(value)
