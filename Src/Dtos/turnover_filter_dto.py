from collections.abc import Iterable
from datetime import datetime

from Src.Core.Exceptions import validation_error
from Src.Core.Validator import validator
from Src.Dtos.filter_condition_dto import filter_condition_dto
from Src.Dtos.filter_dto import filter_dto


class turnover_filter_dto(filter_dto):
    """Передаёт условия отбора движений и включённые границы периода ОСВ.

    Группы строк выбираются по подходящим движениям до end, включая историю.
    Начальные остатки берутся по полной истории групп до start, обороты —
    по отобранным движениям внутри периода.
    """

    def __init__(
        self,
        conditions: Iterable[filter_condition_dto] = (),
        start: str | datetime | None = None,
        end: str | datetime | None = None,
    ):
        """Проверяет период; время без часового пояса считается временем UTC."""
        super().__init__(conditions)
        self.__start = (
            validator.parse_datetime(start, "Начало периода")
            if start is not None
            else None
        )
        self.__end = (
            validator.parse_datetime(end, "Окончание периода")
            if end is not None
            else None
        )
        if self.start is not None and self.end is not None and self.start > self.end:
            raise validation_error("Начало периода не может быть позже окончания")

    @classmethod
    def from_dict(cls, data: dict) -> "turnover_filter_dto":
        """Создаёт фильтр ведомости из условий и границ периода."""
        validator.validate_fields(data, ("conditions", "start", "end"))
        return cls(cls._read_conditions(data), data.get("start"), data.get("end"))

    @property
    def start(self) -> datetime | None:
        """Возвращает включённую нижнюю границу периода."""
        return self.__start

    @property
    def end(self) -> datetime | None:
        """Возвращает включённую верхнюю границу периода."""
        return self.__end
