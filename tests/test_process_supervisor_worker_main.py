import os
from unittest import mock

import pytest

os.environ.setdefault("HLL_MAINTENANCE_CONTAINER", "1")
os.environ.setdefault("SERVER_NUMBER", "1")

from rcon.process_supervisor.worker.__main__ import _parse_argv, main


def test_parse_argv_requires_name():
    with pytest.raises(SystemExit, match="usage"):
        _parse_argv([])


def test_parse_argv_with_separator():
    assert _parse_argv(["log_recorder", "--", "-i", "10"]) == ("log_recorder", ["-i", "10"])


def test_parse_argv_without_separator():
    assert _parse_argv(["broadcasts", "extra"]) == ("broadcasts", ["extra"])


def test_worker_main_success(monkeypatch):
    monkeypatch.setattr("rcon.models.install_unaccent", lambda: None)
    run_program = mock.Mock()
    monkeypatch.setattr("rcon.process_supervisor.registry.run_program", run_program)
    assert main(["broadcasts"]) == 0
    run_program.assert_called_once_with("broadcasts", [])


def test_worker_main_system_exit_codes(monkeypatch):
    monkeypatch.setattr("rcon.models.install_unaccent", lambda: None)

    def raise_exit(code):
        raise SystemExit(code)

    monkeypatch.setattr(
        "rcon.process_supervisor.registry.run_program",
        mock.Mock(side_effect=lambda *_: raise_exit(None)),
    )
    assert main(["broadcasts"]) == 0

    monkeypatch.setattr(
        "rcon.process_supervisor.registry.run_program",
        mock.Mock(side_effect=lambda *_: raise_exit(42)),
    )
    assert main(["broadcasts"]) == 42

    monkeypatch.setattr(
        "rcon.process_supervisor.registry.run_program",
        mock.Mock(side_effect=lambda *_: raise_exit("error")),
    )
    assert main(["broadcasts"]) == 1


def test_worker_main_unhandled_exception(monkeypatch):
    monkeypatch.setattr("rcon.models.install_unaccent", lambda: None)
    monkeypatch.setattr(
        "rcon.process_supervisor.registry.run_program",
        mock.Mock(side_effect=RuntimeError("boom")),
    )
    assert main(["broadcasts"]) == 1
