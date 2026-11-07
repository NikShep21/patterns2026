from xml.etree.ElementTree import Element, SubElement, indent, tostring

from Src.Core.Abstract import base_entity
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_data_dto import report_node_dto
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_data_builder_factory import report_data_builder_factory


class xml_report(abstract_report):
    """Формирует отчёт в формате XML."""

    def build(self, source: base_entity) -> report_result_dto:
        """Формирует XML-отчёт по сущности."""
        builder = report_data_builder_factory.create(source)
        data = builder.build(source)
        root = Element(data.root_name)
        self.__fill_element(root, data)
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

    def __fill_element(self, element: Element, value: object) -> None:
        """Рекурсивно добавляет данные в XML-элемент."""
        if isinstance(value, report_node_dto):
            for name, item in value.iter_fields():
                child = SubElement(element, name)
                self.__fill_element(child, item)
            return

        if isinstance(value, (list, tuple)):
            for item in value:
                child = SubElement(element, "item")
                self.__fill_element(child, item)
            return

        element.text = str(value)
