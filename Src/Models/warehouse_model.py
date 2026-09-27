from Src.Core.Abstract import base_entity


class warehouse_model(base_entity):
    """Модель склада."""

    def __init__(self, name: str):
        """Инициализирует склад."""
        super().__init__()
        self.name = name
