import pytest

from rcon.user_config.end_of_round_rewards import validate_formula


@pytest.mark.parametrize(
    "value",
    [
        ("1+2"),
        ("x=1+2"),
    ],
)
def test_validate_formula(value: str):
    assert validate_formula(value) == value


@pytest.mark.parametrize(
    "value",
    [
        ("asdf"),
        ("x=1+2"),
    ],
)
def test_validate_formula_failures(value: str):
    with pytest.raises(ValueError):
        assert validate_formula(value) == value
