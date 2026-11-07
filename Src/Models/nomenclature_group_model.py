from Src.Core.Abstract import base_entity


class nomenclature_group_model(base_entity):
    """Модель группы номенклатуры."""

    def __init__(self, name: str):
        """Инициализирует группу номенклатуры."""
        super().__init__()
        self.name = name

    @classmethod
    def from_dict(cls, data: dict) -> "nomenclature_group_model":
        """Восстанавливает группу номенклатуры из словаря."""
        group = cls(name=data.get("name"))
        group._restore_id(data.get("id"))
        return group
