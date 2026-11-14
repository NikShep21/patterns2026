from Src.Core.Abstract import base_entity
from Src.Core.Validator import validator


class warehouse_model(base_entity):
    """Модель склада."""

    def __init__(self, name: str, address: str):
        """Инициализирует склад."""
        super().__init__()
        self.name = name
        self.address = address

    @classmethod
    def from_dict(cls, data: dict) -> "warehouse_model":
        """Восстанавливает склад из словаря."""
        warehouse = cls(name=data.get("name"), address=data.get("address"))
        warehouse._restore_id(data.get("id"))
        return warehouse

    @property
    def address(self) -> str:
        """Возвращает адрес склада."""
        return self.__address

    @address.setter
    def address(self, value: str):
        """Изменяет адрес склада."""
        validator.validate_required_string(value, "Адрес")
        self.__address = value.strip()
