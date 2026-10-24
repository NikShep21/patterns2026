class report_data_flattener:
    """Преобразует вложенные данные отчёта в плоский список."""

    @classmethod
    def flatten(cls, data: dict) -> list[tuple[str, str]]:
        """Возвращает список путей и значений вложенного словаря."""
        result = []
        cls.__flatten_value(data, "", result)
        return result

    @classmethod
    def __flatten_value(
        cls,
        value,
        path: str,
        result: list[tuple[str, str]],
    ) -> None:
        """Рекурсивно добавляет простые значения в плоский список."""
        if isinstance(value, dict):
            for key, item in value.items():
                item_path = f"{path}.{key}" if path else key
                cls.__flatten_value(item, item_path, result)
            return

        if isinstance(value, (list, tuple)):
            for index, item in enumerate(value, start=1):
                cls.__flatten_value(item, f"{path}.{index}", result)
            return

        result.append((path, str(value)))
