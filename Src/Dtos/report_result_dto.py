from Src.Core.Validator import validator


class report_result_dto:
    """Хранит сформированное содержимое отчёта и его тип."""

    def __init__(
        self,
        content: str | bytes,
        media_type: str,
        file_extension: str,
    ):
        """Инициализирует результат формирования отчёта."""
        validator.validate_type(
            content,
            (str, bytes),
            "Содержимое отчёта",
        )
        validator.validate_required_string(media_type, "Тип содержимого")
        validator.validate_required_string(file_extension, "Расширение файла")

        self.__content = content
        self.__media_type = media_type.strip()
        self.__file_extension = file_extension.strip()

    @property
    def text(self) -> str:
        """Возвращает содержимое отчёта в виде текста."""
        if isinstance(self.__content, bytes):
            return self.__content.decode("utf-8")

        return self.__content

    @property
    def binary(self) -> bytes:
        """Возвращает содержимое отчёта в виде байтов."""
        if isinstance(self.__content, str):
            return self.__content.encode("utf-8")

        return self.__content

    @property
    def is_binary(self) -> bool:
        """Возвращает признак бинарного результата."""
        return isinstance(self.__content, bytes)

    @property
    def media_type(self) -> str:
        """Возвращает тип содержимого HTTP-ответа."""
        return self.__media_type

    @property
    def file_extension(self) -> str:
        """Возвращает расширение файла без точки."""
        return self.__file_extension
