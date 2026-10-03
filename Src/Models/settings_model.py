from Src.Core.Abstract import base_entity
from Src.Core.Validator import validator
from Src.Models.organization_model import organization_model


class settings_model(base_entity):
    """Модель настроек приложения."""

    __organization: organization_model = None
    __boss_name: str = ""
    __accountant_name: str = ""

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
