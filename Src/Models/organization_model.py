from Src.Core.Abstract import base_entity
from Src.Core.Validator import validator


class organization_model(base_entity):
    """Модель организации."""

    def __init__(
        self,
        name: str | None = None,
        inn: str | None = None,
        bik: str | None = None,
        account: str | None = None,
        corr_account: str | None = None,
        ownership_form: str | None = None,
    ):
        """Инициализирует организацию."""
        super().__init__()
        self.__inn = ""
        self.__bik = ""
        self.__account = ""
        self.__corr_account = ""
        self.__ownership_form = ""

        if name is not None:
            self.name = name
        if inn is not None:
            self.inn = inn
        if bik is not None:
            self.bik = bik
        if account is not None:
            self.account = account
        if corr_account is not None:
            self.corr_account = corr_account
        if ownership_form is not None:
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
