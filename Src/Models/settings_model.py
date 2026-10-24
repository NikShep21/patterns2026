from Src.Core.Abstract import base_entity
from Src.Core.Validator import validator
from Src.Models.organization_model import organization_model
from Src.Models.report_format import report_format


class settings_model(base_entity):
    """Модель настроек приложения."""

    def __init__(self):
        """Инициализирует настройки значениями первого запуска."""
        super().__init__()
        self.__organization = organization_model()
        self.__boss_name = ""
        self.__accountant_name = ""
        self.__is_first_start = True
        self.__response_format = report_format.TXT

    @property
    def organization(self) -> organization_model:
        """Возвращает карточку организации."""
        return self.__organization

    @organization.setter
    def organization(self, value: organization_model) -> None:
        """Изменяет карточку организации."""
        validator.validate_type(value, organization_model, "Организация")
        self.__organization = value

    @property
    def boss_name(self) -> str:
        """Возвращает наименование директора."""
        return self.__boss_name

    @boss_name.setter
    def boss_name(self, value: str) -> None:
        """Изменяет наименование директора."""
        validator.validate_required_string(value, "Директор", 255)
        self.__boss_name = value.strip()

    @property
    def accountant_name(self) -> str:
        """Возвращает наименование главного бухгалтера."""
        return self.__accountant_name

    @accountant_name.setter
    def accountant_name(self, value: str) -> None:
        """Изменяет наименование главного бухгалтера."""
        validator.validate_required_string(value, "Главный бухгалтер", 255)
        self.__accountant_name = value.strip()

    @property
    def is_first_start(self) -> bool:
        """Возвращает признак первого запуска приложения."""
        return self.__is_first_start

    @is_first_start.setter
    def is_first_start(self, value: bool) -> None:
        """Изменяет признак первого запуска приложения."""
        validator.validate_type(value, bool, "Первый запуск")
        self.__is_first_start = value

    @property
    def response_format(self) -> report_format:
        """Возвращает формат ответа по умолчанию."""
        return self.__response_format

    @response_format.setter
    def response_format(self, value: report_format) -> None:
        """Изменяет формат ответа по умолчанию."""
        validator.validate_type(value, report_format, "Формат ответа")
        self.__response_format = value
