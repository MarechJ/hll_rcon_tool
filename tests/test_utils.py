import pytest

from rcon.commands import convert_tabs_to_spaces
from rcon.utils import (
    exception_in_chain,
    is_invalid_name_pineapple,
    is_invalid_name_whitespace,
)


class TestException(Exception):
    pass


class ChainedException(Exception):
    pass


class DeepChainedException(Exception):
    pass


def test_direct_exception():
    assert exception_in_chain(TestException(), TestException)


def test_no_match():
    assert exception_in_chain(ValueError(), TestException) is False


def test_explicit_chained():
    e = ValueError()
    e.__cause__ = TestException()

    assert exception_in_chain(e, TestException)


def test_implicit_chained():
    e = ValueError()
    e.__context__ = TestException()

    assert exception_in_chain(e, TestException)


def test_deeply_chained_explicit():
    e = ValueError()
    e.__cause__ = TestException()
    e.__cause__.__context__ = ChainedException()
    e.__cause__.__context__.__cause__ = DeepChainedException()

    assert exception_in_chain(e, DeepChainedException)


def test_deeply_chained_implicit():
    e = ValueError()
    e.__context__ = TestException()
    e.__context__.__cause__ = ChainedException()
    e.__context__.__cause__.__context__ = DeepChainedException()

    assert exception_in_chain(e, DeepChainedException)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("some\tcontaining\twords", "some containing words"),
        ("", ""),
        ("\t", " "),
        ("no tabs", "no tabs"),
    ],
)
def test_convert_tabs_to_spaces(value, expected):
    assert convert_tabs_to_spaces(value) == expected


@pytest.mark.parametrize(
    "name, expected",
    [("1234567890", False), ("1234567890 ", True), ("1234567890123456789 ", True)],
)
def test_is_invalid_name_whitespace(name, expected):
    assert is_invalid_name_whitespace(name) == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        ("12345678901234567890", False),
        ("123456789012345?", False),
        ("1234567890123456789?", True),
    ],
)
def test_is_invalid_name_pineapple(name, expected):
    assert is_invalid_name_pineapple(name) == expected
