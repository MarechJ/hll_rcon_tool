from rcon.utils import exception_in_chain


class FakeException(Exception):
    pass


class ChainedException(Exception):
    pass


class DeepChainedException(Exception):
    pass


def test_direct_exception():
    assert exception_in_chain(FakeException(), FakeException)


def test_no_match():
    assert exception_in_chain(ValueError(), FakeException) is False


def test_explicit_chained():
    e = ValueError()
    e.__cause__ = FakeException()

    assert exception_in_chain(e, FakeException)


def test_implicit_chained():
    e = ValueError()
    e.__context__ = FakeException()

    assert exception_in_chain(e, FakeException)


def test_deeply_chained_explicit():
    e = ValueError()
    e.__cause__ = FakeException()
    e.__cause__.__context__ = ChainedException()
    e.__cause__.__context__.__cause__ = DeepChainedException()

    assert exception_in_chain(e, DeepChainedException)


def test_deeply_chained_implicit():
    e = ValueError()
    e.__context__ = FakeException()
    e.__context__.__cause__ = ChainedException()
    e.__context__.__cause__.__context__ = DeepChainedException()

    assert exception_in_chain(e, DeepChainedException)
