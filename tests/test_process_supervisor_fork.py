import os
import subprocess
from pathlib import Path
from unittest import mock

import pytest

os.environ.setdefault("HLL_MAINTENANCE_CONTAINER", "1")
os.environ.setdefault("SERVER_NUMBER", "1")

from rcon.process_supervisor.config import ProgramConfig
from rcon.process_supervisor.preload import (
    PRELOAD_MODULES,
    ensure_forkserver,
    fork_enabled,
)
from rcon.process_supervisor.process import ForkedChild, ManagedProcess
from rcon.process_supervisor.registry import command_extra, worker_argv


def test_preload_modules_frozen():
    assert PRELOAD_MODULES == ("hllrcon", "rcon.maps")


def test_preload_modules_exclude_forbidden():
    forbidden = {"rcon.cli", "rcon.settings", "rcon.rcon", "discord"}
    assert forbidden.isdisjoint(set(PRELOAD_MODULES))


def test_fork_enabled_respects_disable_flag(monkeypatch):
    monkeypatch.delenv("CRCON_SUPERVISOR_FORK", raising=False)
    assert fork_enabled() is True

    monkeypatch.setenv("CRCON_SUPERVISOR_FORK", "0")
    assert fork_enabled() is False

    monkeypatch.setenv("CRCON_SUPERVISOR_FORK", "false")
    assert fork_enabled() is False

    monkeypatch.setenv("CRCON_SUPERVISOR_FORK", "no")
    assert fork_enabled() is False

    monkeypatch.setenv("CRCON_SUPERVISOR_FORK", "off")
    assert fork_enabled() is False


def test_fork_enabled_false_on_windows(monkeypatch):
    monkeypatch.setattr("rcon.process_supervisor.preload.sys.platform", "win32")
    monkeypatch.setenv("CRCON_SUPERVISOR_FORK", "1")
    assert fork_enabled() is False


def test_ensure_forkserver_caches_context(monkeypatch):
    from rcon.process_supervisor import preload

    monkeypatch.setattr(preload, "_FORKSERVER_CONTEXT", None)
    ctx = mock.Mock(name="forkserver")
    set_preload = mock.Mock()
    get_context = mock.Mock(return_value=ctx)
    monkeypatch.setattr(preload.multiprocessing, "set_forkserver_preload", set_preload)
    monkeypatch.setattr(preload.multiprocessing, "get_context", get_context)

    first = ensure_forkserver()
    second = ensure_forkserver()
    assert first is ctx
    assert second is ctx
    set_preload.assert_called_once_with(list(PRELOAD_MODULES))
    get_context.assert_called_once_with("forkserver")


def test_cron_still_uses_popen_with_ini_command(tmp_path, monkeypatch):
    config = ProgramConfig(
        name="cron",
        command=["/bin/bash", "-c", "cron -f"],
        environment={"LOGGING_FILENAME": "cron.log"},
        startsecs=0,
    )
    process = ManagedProcess(config=config, base_environ={"LOGGING_PATH": str(tmp_path)})
    popen_mock = mock.Mock(pid=456)
    ctor = mock.Mock(return_value=popen_mock)
    warning = mock.Mock()
    monkeypatch.setattr("rcon.process_supervisor.process.subprocess.Popen", ctor)
    monkeypatch.setattr("rcon.process_supervisor.process.logger.warning", warning)
    process.spawn()
    assert command_extra(config) is None
    ctor.assert_called_once()
    assert ctor.call_args.args[0] == config.command
    warning.assert_not_called()


def test_python_ini_without_adapter_warns_and_execs_ini(tmp_path, monkeypatch):
    config = ProgramConfig(
        name="custom_loop",
        command=["/code/manage.py", "custom_loop"],
        environment={"LOGGING_FILENAME": "custom_loop.log"},
        startsecs=0,
    )
    process = ManagedProcess(config=config, base_environ={"LOGGING_PATH": str(tmp_path)})
    popen_mock = mock.Mock(pid=789)
    ctor = mock.Mock(return_value=popen_mock)
    warning = mock.Mock()
    monkeypatch.setattr("rcon.process_supervisor.process.subprocess.Popen", ctor)
    monkeypatch.setattr("rcon.process_supervisor.process.logger.warning", warning)
    process.spawn()
    assert command_extra(config) is None
    ctor.assert_called_once()
    assert ctor.call_args.args[0] == config.command
    warning.assert_called_once()
    assert warning.call_args.args[1] == "custom_loop"
    assert warning.call_args.args[3] == config.command


def test_registered_spawn_uses_fork_when_enabled(tmp_path, monkeypatch):
    config = ProgramConfig(
        name="broadcasts",
        command=["/code/manage.py", "broadcast_loop"],
        environment={"LOGGING_FILENAME": "broadcasts.log"},
        startsecs=0,
    )
    process = ManagedProcess(config=config, base_environ={"LOGGING_PATH": str(tmp_path)})
    monkeypatch.setattr("rcon.process_supervisor.process.fork_enabled", lambda: True)

    proc_instance = mock.Mock()
    proc_instance.pid = 999
    proc_instance.exitcode = None
    process_class = mock.Mock(return_value=proc_instance)
    ctx = mock.Mock(Process=process_class)
    monkeypatch.setattr("rcon.process_supervisor.process.ensure_forkserver", lambda: ctx)

    popen_ctor = mock.Mock()
    monkeypatch.setattr("rcon.process_supervisor.process.subprocess.Popen", popen_ctor)

    process.spawn()
    popen_ctor.assert_not_called()
    process_class.assert_called_once()
    kwargs = process_class.call_args.kwargs
    assert kwargs["target"].__name__ == "fork_main"
    assert kwargs["daemon"] is False
    assert kwargs["args"][0] == "broadcasts"
    proc_instance.start.assert_called_once()


def test_registered_spawn_uses_popen_when_fork_disabled(tmp_path, monkeypatch):
    config = ProgramConfig(
        name="log_recorder",
        command=["/code/manage.py", "log_recorder", "-i", "10"],
        environment={"LOGGING_FILENAME": "log_recorder.log"},
        startsecs=0,
    )
    process = ManagedProcess(config=config, base_environ={"LOGGING_PATH": str(tmp_path)})
    monkeypatch.setattr("rcon.process_supervisor.process.fork_enabled", lambda: False)

    popen_mock = mock.Mock(pid=321)
    popen_ctor = mock.Mock(return_value=popen_mock)
    monkeypatch.setattr("rcon.process_supervisor.process.subprocess.Popen", popen_ctor)

    process.spawn()
    popen_ctor.assert_called_once()
    assert popen_ctor.call_args.args[0] == worker_argv(config)


def test_fork_main_sets_env_and_runs_program(monkeypatch):
    from rcon.process_supervisor.worker import fork_child

    env = {"LOGGING_FILENAME": "demo.log", "SERVER_NUMBER": "1"}
    monkeypatch.setattr(fork_child.os, "environ", dict(env))
    monkeypatch.setattr(fork_child.os, "setsid", lambda: None)
    monkeypatch.setattr(fork_child.os, "open", lambda *_a, **_k: 99)
    monkeypatch.setattr(fork_child.os, "dup2", lambda *_a, **_k: None)
    monkeypatch.setattr(fork_child.os, "close", lambda *_a, **_k: None)
    monkeypatch.setattr(fork_child.os, "_exit", lambda code: (_ for _ in ()).throw(SystemExit(code)))

    install = mock.Mock()
    monkeypatch.setattr("rcon.models.install_unaccent", install)
    reset = mock.Mock()
    monkeypatch.setattr(fork_child, "reset_inherited_resources", reset)
    run_program = mock.Mock()
    monkeypatch.setattr("rcon.process_supervisor.registry.run_program", run_program)

    with pytest.raises(SystemExit) as exc:
        fork_child.fork_main("broadcasts", [], env, "/tmp/demo.log", None)

    assert exc.value.code == 0
    assert fork_child.os.environ["LOGGING_FILENAME"] == "demo.log"
    install.assert_called_once_with()
    reset.assert_called_once_with()
    run_program.assert_called_once_with("broadcasts", [])


def test_fork_main_chdirs_and_maps_systemexit_codes(monkeypatch):
    from rcon.process_supervisor.worker import fork_child

    env = {"LOGGING_FILENAME": "demo.log"}
    monkeypatch.setattr(fork_child.os, "environ", dict(env))
    monkeypatch.setattr(fork_child.os, "setsid", lambda: None)
    monkeypatch.setattr(fork_child.os, "open", lambda *_a, **_k: 1)
    monkeypatch.setattr(fork_child.os, "dup2", lambda *_a, **_k: None)
    chdir = mock.Mock()
    monkeypatch.setattr(fork_child.os, "chdir", chdir)
    close = mock.Mock()
    monkeypatch.setattr(fork_child.os, "close", close)
    monkeypatch.setattr("rcon.models.install_unaccent", lambda: None)
    monkeypatch.setattr(fork_child, "reset_inherited_resources", lambda: None)

    def raise_exit(code):
        raise SystemExit(code)

    monkeypatch.setattr(
        "rcon.process_supervisor.registry.run_program",
        mock.Mock(side_effect=lambda *_: raise_exit(None)),
    )
    monkeypatch.setattr(fork_child.os, "_exit", lambda code: (_ for _ in ()).throw(SystemExit(code)))
    with pytest.raises(SystemExit) as none_code:
        fork_child.fork_main("broadcasts", [], env, "/tmp/demo.log", "/tmp")
    assert none_code.value.code == 0
    chdir.assert_called_once_with("/tmp")
    close.assert_not_called()

    monkeypatch.setattr(
        "rcon.process_supervisor.registry.run_program",
        mock.Mock(side_effect=lambda *_: raise_exit(7)),
    )
    with pytest.raises(SystemExit) as int_code:
        fork_child.fork_main("broadcasts", [], env, "/tmp/demo.log", None)
    assert int_code.value.code == 7

    monkeypatch.setattr(
        "rcon.process_supervisor.registry.run_program",
        mock.Mock(side_effect=lambda *_: raise_exit("fail")),
    )
    with pytest.raises(SystemExit) as str_code:
        fork_child.fork_main("broadcasts", [], env, "/tmp/demo.log", None)
    assert str_code.value.code == 1


def test_fork_main_unhandled_exception_exits_one(monkeypatch):
    from rcon.process_supervisor.worker import fork_child

    env = {"LOGGING_FILENAME": "demo.log"}
    monkeypatch.setattr(fork_child.os, "environ", dict(env))
    monkeypatch.setattr(fork_child.os, "setsid", lambda: None)
    monkeypatch.setattr(fork_child.os, "open", lambda *_a, **_k: 99)
    monkeypatch.setattr(fork_child.os, "dup2", lambda *_a, **_k: None)
    monkeypatch.setattr(fork_child.os, "close", lambda *_a, **_k: None)
    monkeypatch.setattr("rcon.models.install_unaccent", lambda: None)
    monkeypatch.setattr(fork_child, "reset_inherited_resources", lambda: None)
    monkeypatch.setattr(
        "rcon.process_supervisor.registry.run_program",
        mock.Mock(side_effect=RuntimeError("boom")),
    )
    monkeypatch.setattr(fork_child.os, "_exit", lambda code: (_ for _ in ()).throw(SystemExit(code)))

    with pytest.raises(SystemExit) as exc:
        fork_child.fork_main("broadcasts", [], env, "/tmp/demo.log", None)
    assert exc.value.code == 1


def test_reset_inherited_resources_disposes_engine(monkeypatch):
    from rcon.process_supervisor.worker.fork_child import reset_inherited_resources

    engine = mock.Mock()
    monkeypatch.setattr("rcon.models._ENGINE", engine)
    monkeypatch.setattr("rcon.cache_utils._REDIS_POOL", object())
    monkeypatch.setattr("rcon.cache_utils._GLOBAL_REDIS_POOL", object())
    get_pool = mock.Mock()
    monkeypatch.setattr("rcon.cache_utils.get_redis_pool", get_pool)

    reset_inherited_resources()

    engine.dispose.assert_called_once_with(close=False)
    import rcon.cache_utils
    import rcon.models

    assert rcon.models._ENGINE is None
    assert rcon.cache_utils._REDIS_POOL is None
    assert rcon.cache_utils._GLOBAL_REDIS_POOL is None
    get_pool.assert_called_once_with(decode_responses=False)


def test_reset_inherited_resources_skips_missing_engine(monkeypatch):
    from rcon.process_supervisor.worker.fork_child import reset_inherited_resources

    monkeypatch.setattr("rcon.models._ENGINE", None)
    monkeypatch.setattr("rcon.cache_utils.get_redis_pool", mock.Mock())
    reset_inherited_resources()


def test_forked_child_poll_and_wait():
    process = mock.Mock()
    process.pid = 42
    process.exitcode = None
    process.is_alive.return_value = False
    child = ForkedChild(process)
    assert child.pid == 42
    assert child.poll() is None
    process.join.assert_called_with(timeout=0)

    process.exitcode = 3
    process.is_alive.return_value = False
    assert child.wait(timeout=1) == 3
    process.join.assert_called_with(timeout=1)


def test_forked_child_wait_timeout():
    process = mock.Mock()
    process.pid = 7
    process.exitcode = None
    process.is_alive.return_value = True
    child = ForkedChild(process)
    with pytest.raises(subprocess.TimeoutExpired):
        child.wait(timeout=0.01)


def test_forked_child_pid_zero_when_missing():
    process = mock.Mock()
    process.pid = None
    assert ForkedChild(process).pid == 0


def test_preload_and_fork_child_do_not_reference_cli():
    root = Path(__file__).resolve().parents[1] / "rcon" / "process_supervisor"
    preload = (root / "preload.py").read_text()
    fork_child = (root / "worker" / "fork_child.py").read_text()
    assert "rcon.cli" not in preload
    assert "rcon.cli" not in fork_child
