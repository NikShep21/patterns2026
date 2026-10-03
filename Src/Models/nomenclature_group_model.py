from Src.Core.Abstract import base_entity


class nomenclature_group_model(base_entity):
    """Модель группы номенклатуры."""

    def __init__(self, name: str):
        """Инициализирует группу номенклатуры."""
        super().__init__()
        self.name = name
