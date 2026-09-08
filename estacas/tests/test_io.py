import pytest

from src.io import normalize_date_value


@pytest.mark.parametrize("raw, expected", [
    ("01-06-49", "01-06-2049"),
    ("01-06-50", "01-06-1950"),
])
def test_normalize_date_value_two_digit_year_rollover(raw, expected):
    assert normalize_date_value(raw) == expected
