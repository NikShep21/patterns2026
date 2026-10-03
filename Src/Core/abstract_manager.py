from abc import ABC


class abstract_manager(ABC):
    """Абстрактный класс для загрузки и обработки данных."""

    def __init__(self):
        """Инициализирует общее состояние менеджера."""
        self._file_name: str = ""
        self._is_loaded: bool = False
        self._data = None

    def load(self, file_name: str = "") -> None:
        """Загружает данные из файла."""
        pass

    def convert(self) -> bool:
        """Обрабатывает загруженные данные."""
        return False

    @property
    def is_loaded(self) -> bool:
        """Возвращает признак успешной подготовки данных."""
        return self._is_loaded
