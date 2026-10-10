import json

from Src.Core.Exceptions import operation_error
from Src.Core.Validator import validator
from Src.Core.abstract_manager import abstract_manager
from Src.Models.organization_model import organization_model
from Src.Models.settings_model import settings_model


class settings_manager(abstract_manager):
    """Менеджер для работы с настройками."""

    __default_file_name: str = "settings.json"
    __settings: settings_model = None
    __instance = None

    def __init__(self):
        """Инициализирует менеджер настроек."""
        if getattr(self, "_initialized", False):
            return

        super().__init__()
        self.__settings = settings_model()
        self._initialized = True

    def __new__(cls):
        """Возвращает единственный экземпляр менеджера."""
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def load(self, file_name: str = ""):
        """Загружает настройки из файла."""
        validator.validate_type(file_name, str, "Имя файла")
        self._file_name = file_name.strip() or self.__default_file_name
        self._is_loaded = False

        try:
            with open(self._file_name, "r", encoding="utf-8") as file:
                self._data = json.load(file)
                self._is_loaded = self.convert()
        except Exception as error:
            raise operation_error(
                "Ошибка при загрузке и обработке файла: "
                f"{self._file_name}. Детали: {error}"
            )

    def convert(self) -> bool:
        """Преобразует загруженные данные в модель настроек."""
        validator.validate_type(self._data, dict, "Настройки")
        organization_data = self._data.get("organization", {})
        validator.validate_type(
            organization_data,
            dict,
            "Организация",
        )

        organization = organization_model()
        organization_fields = (
            "name",
            "inn",
            "bik",
            "account",
            "corr_account",
            "ownership_form",
        )

        for field in organization_fields:
            if field in organization_data:
                setattr(organization, field, organization_data[field])

        settings = settings_model()
        settings.organization = organization

        settings_fields = (
            "boss_name",
            "accountant_name",
            "is_first_start",
        )

        for field in settings_fields:
            if field in self._data:
                setattr(settings, field, self._data[field])

        self.__settings = settings

        return True

    @property
    def settings(self) -> settings_model:
        """Возвращает модель настроек."""
        return self.__settings
