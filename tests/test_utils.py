import pytest

from rcon.utils import exception_in_chain
from rcon.commands import convert_tabs_to_spaces


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
