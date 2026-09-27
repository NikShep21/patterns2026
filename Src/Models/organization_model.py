from Src.Core.Abstract import base_entity
from Src.Core.Exceptions import validation_error


class organization_model(base_entity):
    """Модель организации."""

    def __init__(
        self,
        name: str,
        inn: str,
        bik: str,
        account: str,
        ownership_form: str,
    ):
        """Инициализирует организацию."""
        super().__init__()
        self.name = name
        self.inn = inn
        self.bik = bik
        self.account = account
        self.ownership_form = ownership_form

    @staticmethod
    def _normalize_required_string(value: str, field_name: str) -> str:
        """Проверяет и нормализует обязательное строковое поле."""
        if not isinstance(value, str):
            raise validation_error(
                f"Поле «{field_name}» должно иметь строковый тип"
            )

        value = value.strip()

        if not value:
            raise validation_error(f"Поле «{field_name}» не может быть пустым")

        return value

    @staticmethod
    def _normalize_numeric_string(
        value: str,
        field_name: str,
        allowed_lengths: tuple[int, ...],
    ) -> str:
        """Проверяет и нормализует обязательное цифровое поле."""
        value = organization_model._normalize_required_string(
            value,
            field_name,
        )

        if not value.isascii() or not value.isdigit():
            raise validation_error(
                f"Поле «{field_name}» должно содержать только цифры"
            )

        if len(value) not in allowed_lengths:
            expected_lengths = " или ".join(
                str(length) for length in allowed_lengths
            )
            raise validation_error(
                f"Поле «{field_name}» должно содержать {expected_lengths} цифр"
            )

        return value

    @property
    def inn(self) -> str:
        """Возвращает ИНН организации."""
        return self.__inn

    @inn.setter
    def inn(self, value: str):
        """Изменяет ИНН организации."""
        self.__inn = self._normalize_numeric_string(value, "ИНН", (10, 12))

    @property
    def bik(self) -> str:
        """Возвращает БИК организации."""
        return self.__bik

    @bik.setter
    def bik(self, value: str):
        """Изменяет БИК организации."""
        self.__bik = self._normalize_numeric_string(value, "БИК", (9,))

    @property
    def account(self) -> str:
        """Возвращает номер счёта организации."""
        return self.__account

    @account.setter
    def account(self, value: str):
        """Изменяет номер счёта организации."""
        self.__account = self._normalize_numeric_string(value, "Счёт", (20,))

    @property
    def ownership_form(self) -> str:
        """Возвращает форму собственности организации."""
        return self.__ownership_form

    @ownership_form.setter
    def ownership_form(self, value: str):
        """Изменяет форму собственности организации."""
        self.__ownership_form = self._normalize_required_string(
            value,
            "Форма собственности",
        )
