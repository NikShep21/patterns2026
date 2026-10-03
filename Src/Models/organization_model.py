from Src.Core.Abstract import base_entity
from Src.Core.Validator import validator


class organization_model(base_entity):
    """Модель организации."""

    def __init__(
        self,
        name: str,
        inn: str,
        bik: str,
        account: str,
        corr_account: str,
        ownership_form: str,
    ):
        """Инициализирует организацию."""
        super().__init__()
        self.name = name
        self.inn = inn
        self.bik = bik
        self.account = account
        self.corr_account = corr_account
        self.ownership_form = ownership_form

    @property
    def inn(self) -> str:
        """Возвращает ИНН организации."""
        return self.__inn

    @inn.setter
    def inn(self, value: str):
        """Изменяет ИНН организации."""
        validator.validate_numeric_string(value, "ИНН", (10, 12))
        self.__inn = value.strip()

    @property
    def bik(self) -> str:
        """Возвращает БИК организации."""
        return self.__bik

    @bik.setter
    def bik(self, value: str):
        """Изменяет БИК организации."""
        validator.validate_numeric_string(value, "БИК", (9,))
        self.__bik = value.strip()

    @property
    def account(self) -> str:
        """Возвращает номер счёта организации."""
        return self.__account

    @account.setter
    def account(self, value: str):
        """Изменяет номер счёта организации."""
        validator.validate_numeric_string(value, "Счёт", (11,))
        self.__account = value.strip()

    @property
    def corr_account(self) -> str:
        """Возвращает корреспондентский счёт банка."""
        return self.__corr_account

    @corr_account.setter
    def corr_account(self, value: str):
        """Изменяет корреспондентский счёт банка."""
        validator.validate_numeric_string(
            value,
            "Корреспондентский счёт",
            (11,),
        )
        self.__corr_account = value.strip()

    @property
    def ownership_form(self) -> str:
        """Возвращает форму собственности организации."""
        return self.__ownership_form

    @ownership_form.setter
    def ownership_form(self, value: str):
        """Изменяет форму собственности организации."""
        validator.validate_required_string(
            value,
            "Форма собственности",
        )
        self.__ownership_form = value.strip()
