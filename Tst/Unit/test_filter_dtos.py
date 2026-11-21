import pytest

from Src.Core.Exceptions import validation_error
from Src.Dtos.filter_condition_dto import filter_condition_dto
from Src.Dtos.filter_dto import filter_dto
from Src.Models.comparison_type import comparison_type


def test_success_filter_dto_from_dict_builds_plain_objects_without_changing_source():
    """Словарь преобразуется в обычные DTO с исходными типами значений."""
    source = {"conditions": [{"field": "base_range", "value": None}]}
    result = filter_dto.from_dict(source)
    (condition,) = result.conditions
    assert type(result) is filter_dto
    assert type(condition) is filter_condition_dto
    assert condition.comparison is comparison_type.EQUALS
    assert condition.value is None
    assert source == {"conditions": [{"field": "base_range", "value": None}]}


@pytest.mark.parametrize("source", (None, [], "filter", 1))
@pytest.mark.parametrize("dto", (filter_condition_dto, filter_dto))
def test_fail_filter_dtos_from_dict_reject_invalid_root(dto, source):
    """Каждый метод from_dict проверяет тип корня до обращения к ключам."""
    with pytest.raises(validation_error):
        dto.from_dict(source)
