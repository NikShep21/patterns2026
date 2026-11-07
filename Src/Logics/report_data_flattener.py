from Src.Dtos.report_data_dto import report_data_dto, report_node_dto


class report_data_flattener:
    """Преобразует вложенные данные отчёта в плоский список."""

    @classmethod
    def flatten(cls, data: report_data_dto) -> list[tuple[str, str]]:
        """Возвращает список путей и значений полей отчёта."""
        result = []
        cls.__flatten_value(data, data.root_name, result)
        return result

    @classmethod
    def __flatten_value(
        cls,
        value: object,
        path: str,
        result: list[tuple[str, str]],
    ) -> None:
        """Рекурсивно добавляет простые значения в плоский список."""
        if isinstance(value, report_node_dto):
            for name, item in value.iter_fields():
                cls.__flatten_value(item, f"{path}.{name}", result)
            return

        if isinstance(value, (list, tuple)):
            for index, item in enumerate(value, start=1):
                cls.__flatten_value(item, f"{path}.{index}", result)
            return

        result.append((path, str(value)))
