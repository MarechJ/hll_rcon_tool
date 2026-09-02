import importlib
import os
import sys
from unittest import mock

os.environ.setdefault("HLL_MAINTENANCE_CONTAINER", "1")
os.environ.setdefault("SERVER_NUMBER", "1")

import textwrap
import time
from pathlib import Path
from xmlrpc.client import Fault, ServerProxy

import pytest

from rcon.process_supervisor.config import (
    ProgramConfig,
    SupervisorConfig,
    interpolate,
    load_config,
    parse_byte_size,
    parse_environment,
)
from rcon.process_supervisor.logging_setup import configure_logging
from rcon.process_supervisor.manager import ProcessSupervisor
from rcon.process_supervisor.rpc import start_rpc_server
from rcon.process_supervisor.states import ProcessState


def test_interpolate_env_variable():
    assert interpolate("foo_%(ENV_SERVER_NUMBER)s.log", {"SERVER_NUMBER": "3"}) == "foo_3.log"


def test_parse_environment():
    assert parse_environment("LOGGING_FILENAME=a.log,HLL_DB_DISABLE_CONNECTION_POOL=1") == {
        "LOGGING_FILENAME": "a.log",
        "HLL_DB_DISABLE_CONNECTION_POOL": "1",
    }


def test_load_config_parses_programs(tmp_path):
    config_text = textwrap.dedent(
        """
        [inet_http_server]
        port=127.0.0.1:9123

        [program:test_prog]
        command=/bin/sleep 30
        environment=LOGGING_FILENAME=test_%(ENV_SERVER_NUMBER)s.log
        autostart=false
        autorestart=unexpected
        startretries=2
        startsecs=0
        """
    )
    config_path = tmp_path / "supervisord.conf"
    config_path.write_text(config_text)

    config = load_config(config_path, {"SERVER_NUMBER": "7"})
    assert config.rpc_host == "127.0.0.1"
    assert config.rpc_port == 9123
    assert "test_prog" in config.programs
    prog = config.programs["test_prog"]
    assert prog.command == ["/bin/sleep", "30"]
    assert prog.environment["LOGGING_FILENAME"] == "test_7.log"
    assert prog.autostart is False
    assert prog.autorestart == "unexpected"
    assert prog.startretries == 2
    assert prog.startsecs == 0


def test_load_repo_supervisord_conf():
    config_path = Path(__file__).resolve().parents[1] / "config" / "supervisord.conf"
    env = {
        "SERVER_NUMBER": "1",
        "HLL_REDIS_URL": "redis://localhost:6379/0",
        "HLL_REDIS_HOST": "localhost",
        "HLL_REDIS_PORT": "6379",
        "HLL_REDIS_DB": "0",
    }
    config = load_config(config_path, env)
    expected = {
        "broadcasts",
        "expiring_vips",
        "seed_vip",
        "log_event_loop",
        "log_stream",
        "log_recorder",
        "auto_settings",
        "routines",
        "workers",
        "live_stats_refresh",
        "scoreboard",
        "automod",
        "blacklists",
        "watch_killrate",
        "cron",
        "scheduler",
    }
    assert expected.issubset(set(config.programs))
    assert config.logfile == "/logs/supervisord.log"
    assert config.logfile_maxbytes == 50 * 1024 * 1024
    assert config.logfile_backups == 10


def test_parse_byte_size():
    assert parse_byte_size("50MB") == 50 * 1024 * 1024
    assert parse_byte_size("1024") == 1024


def test_load_config_parses_supervisord_logfile(tmp_path):
    config_text = textwrap.dedent(
        """
        [supervisord]
        logfile=%(ENV_LOG_DIR)s/supervisord.log
        logfile_maxbytes=10MB
        logfile_backups=3

        [program:demo]
        command=/bin/true
        autostart=false
        """
    )
    config_path = tmp_path / "supervisord.conf"
    config_path.write_text(config_text)
    config = load_config(config_path, {"LOG_DIR": str(tmp_path / "logs")})
    assert config.logfile == str(tmp_path / "logs" / "supervisord.log")
    assert config.logfile_maxbytes == 10 * 1024 * 1024
    assert config.logfile_backups == 3


def test_arbiter_logs_spawn_and_stop_to_logfile(tmp_path):
    logfile = tmp_path / "supervisord.log"
    config = SupervisorConfig(
        programs={
            "demo": ProgramConfig(
                name="demo",
                command=["/bin/sleep", "30"],
                environment={"LOGGING_FILENAME": "demo.log"},
                autostart=False,
                startsecs=0,
            )
        },
        logfile=str(logfile),
    )
    configure_logging(config)
    supervisor = ProcessSupervisor(config, base_environ={"LOGGING_PATH": str(tmp_path)})
    supervisor.start_process("demo")
    supervisor.stop_process("demo")

    contents = logfile.read_text()
    assert "Spawned 'demo'" in contents
    assert "entered RUNNING state" in contents
    assert "Stopped process 'demo' via RPC" in contents


def _make_supervisor(tmp_path: Path, command: list[str], **overrides) -> ProcessSupervisor:
    program = {
        "name": "demo",
        "command": command,
        "environment": {"LOGGING_FILENAME": "demo.log"},
        "autostart": False,
        "autorestart": "unexpected",
        "startretries": 2,
        "startsecs": 0,
        "stopsignal": "TERM",
        "stopwaitsecs": 2,
        "directory": None,
    }
    program.update(overrides)
    from rcon.process_supervisor.config import ProgramConfig

    config = SupervisorConfig(
        programs={
            "demo": ProgramConfig(**program),
        }
    )
    env = {"LOGGING_PATH": str(tmp_path)}
    return ProcessSupervisor(config, base_environ=env)


def test_start_stop_lifecycle(tmp_path):
    supervisor = _make_supervisor(tmp_path, ["/bin/sleep", "30"], startsecs=0)
    supervisor.start_process("demo")
    info = supervisor.get_process_info("demo")
    assert info["state"] == ProcessState.RUNNING
    assert info["statename"] == "RUNNING"
    assert info["pid"] > 0
    assert "uptime" in info["description"]

    supervisor.stop_process("demo")
    info = supervisor.get_process_info("demo")
    assert info["state"] == ProcessState.STOPPED
    assert info["pid"] == 0


def test_start_failure_becomes_fatal(tmp_path):
    supervisor = _make_supervisor(
        tmp_path,
        ["/bin/sh", "-c", "exit 1"],
        startretries=1,
        startsecs=1,
    )
    supervisor.start_process("demo")
    deadline = time.time() + 5
    while time.time() < deadline:
        supervisor.tick()
        if supervisor.get_process_info("demo")["state"] == ProcessState.FATAL:
            break
        time.sleep(0.05)
    assert supervisor.get_process_info("demo")["state"] == ProcessState.FATAL


def test_autorestart_unexpected_only_on_nonzero_exit(tmp_path):
    supervisor = _make_supervisor(
        tmp_path,
        ["/bin/sh", "-c", "exit 0"],
        autorestart="unexpected",
        startsecs=0,
    )
    supervisor.start_process("demo")
    supervisor.tick()
    time.sleep(0.1)
    supervisor.tick()
    assert supervisor.get_process_info("demo")["state"] == ProcessState.EXITED

    supervisor = _make_supervisor(
        tmp_path,
        ["/bin/sh", "-c", "exit 2"],
        autorestart="unexpected",
        startsecs=0,
    )
    supervisor.start_process("demo")
    deadline = time.time() + 3
    while time.time() < deadline:
        supervisor.tick()
        state = supervisor.get_process_info("demo")["state"]
        if state in {ProcessState.BACKOFF, ProcessState.STARTING, ProcessState.RUNNING}:
            break
        time.sleep(0.05)
    assert supervisor.get_process_info("demo")["state"] in {
        ProcessState.BACKOFF,
        ProcessState.STARTING,
        ProcessState.RUNNING,
    }


def test_rpc_start_stop_and_faults(tmp_path):
    supervisor = _make_supervisor(tmp_path, ["/bin/sleep", "30"], startsecs=0)
    server = start_rpc_server(supervisor, "127.0.0.1", 0)
    host, port = server.server_address
    client = ServerProxy(f"http://{host}:{port}/RPC2", allow_none=True)

    processes = client.supervisor.getAllProcessInfo()
    assert len(processes) == 1
    assert set(processes[0]) >= {
        "name",
        "group",
        "description",
        "start",
        "stop",
        "now",
        "state",
        "statename",
        "spawnerr",
        "exitstatus",
        "pid",
        "stdout_logfile",
    }

    assert client.supervisor.startProcess("demo") is True
    info = client.supervisor.getProcessInfo("demo")
    assert info["state"] == ProcessState.RUNNING

    with pytest.raises(Fault) as already_started:
        client.supervisor.startProcess("demo")
    assert already_started.value.faultCode == 60

    assert client.supervisor.stopProcess("demo") is True
    with pytest.raises(Fault) as not_running:
        client.supervisor.stopProcess("demo")
    assert not_running.value.faultCode == 70

    with pytest.raises(Fault) as bad_name:
        client.supervisor.startProcess("missing")
    assert bad_name.value.faultCode == 10

    server.shutdown()


def test_rpc_start_does_not_wait_startsecs(tmp_path):
    supervisor = _make_supervisor(
        tmp_path, ["/bin/sleep", "30"], startsecs=2, autostart=False
    )
    server = start_rpc_server(supervisor, "127.0.0.1", 0)
    host, port = server.server_address
    client = ServerProxy(f"http://{host}:{port}/RPC2", allow_none=True)

    started = time.monotonic()
    assert client.supervisor.startProcess("demo") is True
    elapsed = time.monotonic() - started
    assert elapsed < 0.5

    info = client.supervisor.getProcessInfo("demo")
    assert info["state"] in {ProcessState.STARTING, ProcessState.RUNNING}

    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        supervisor.tick()
        if supervisor.get_process_info("demo")["state"] == ProcessState.RUNNING:
            break
        time.sleep(0.05)
    assert supervisor.get_process_info("demo")["state"] == ProcessState.RUNNING

    supervisor.stop_process("demo")
    server.shutdown()


def _make_dual_supervisor(tmp_path: Path) -> ProcessSupervisor:
    def _prog(name: str, **overrides) -> ProgramConfig:
        defaults = {
            "name": name,
            "command": ["/bin/sleep", "30"],
            "environment": {"LOGGING_FILENAME": f"{name}.log"},
            "autostart": False,
            "autorestart": "unexpected",
            "startretries": 2,
            "startsecs": 0,
            "stopsignal": "TERM",
            "stopwaitsecs": 2,
            "directory": None,
        }
        defaults.update(overrides)
        return ProgramConfig(**defaults)

    config = SupervisorConfig(
        programs={
            "slow": _prog("slow", stopwaitsecs=5),
            "quick": _prog("quick"),
        }
    )
    return ProcessSupervisor(config, base_environ={"LOGGING_PATH": str(tmp_path)})


def test_stop_does_not_hold_lock_during_wait(tmp_path):
    import threading

    supervisor = _make_dual_supervisor(tmp_path)
    supervisor.start_process("slow")
    supervisor.start_process("quick")
    assert supervisor.get_process_info("slow")["state"] == ProcessState.RUNNING
    assert supervisor.get_process_info("quick")["state"] == ProcessState.RUNNING

    stop_error: list[BaseException] = []

    def stop_slow() -> None:
        try:
            supervisor.stop_process("slow")
        except BaseException as exc:
            stop_error.append(exc)

    stop_thread = threading.Thread(target=stop_slow, daemon=True)
    stop_thread.start()

    while stop_thread.is_alive():
        for call in (supervisor.get_all_process_info, supervisor.tick):
            started = time.monotonic()
            call()
            assert time.monotonic() - started < 0.5
        time.sleep(0.05)

    stop_thread.join(timeout=6)
    assert not stop_thread.is_alive()
    assert not stop_error

    assert supervisor.get_process_info("slow")["state"] == ProcessState.STOPPED
    assert supervisor.get_process_info("quick")["state"] == ProcessState.RUNNING

    supervisor.stop_process("quick")


def test_tick_reap_during_stop_sets_stopped(tmp_path):
    supervisor = _make_supervisor(tmp_path, ["/bin/sleep", "30"], startsecs=0)
    supervisor.start_process("demo")
    proc = supervisor.get_process("demo")
    proc.stop(wait=False)

    deadline = time.time() + 3
    while time.time() < deadline:
        supervisor.tick()
        info = supervisor.get_process_info("demo")
        if info["state"] == ProcessState.STOPPED:
            break
        time.sleep(0.05)

    info = supervisor.get_process_info("demo")
    assert info["state"] == ProcessState.STOPPED
    assert info["statename"] == "STOPPED"
    assert info["pid"] == 0


def test_stop_wait_true_after_tick_reap(tmp_path):
    supervisor = _make_supervisor(tmp_path, ["/bin/sleep", "30"], startsecs=0)
    supervisor.start_process("demo")
    proc = supervisor.get_process("demo")
    proc.stop(wait=False)

    deadline = time.time() + 3
    while time.time() < deadline:
        supervisor.tick()
        if proc.popen is None:
            break
        time.sleep(0.05)

    proc.stop(wait=True)
    info = supervisor.get_process_info("demo")
    assert info["state"] == ProcessState.STOPPED
    assert info["pid"] == 0


def test_stop_none_popen_while_stopping_sets_stopped(tmp_path):
    supervisor = _make_supervisor(tmp_path, ["/bin/sleep", "30"], startsecs=0)
    proc = supervisor.get_process("demo")
    proc.state = ProcessState.STOPPING
    proc.popen = None
    proc.stop(wait=True)
    assert proc.state == ProcessState.STOPPED


def test_stop_when_not_running_is_noop(tmp_path):
    supervisor = _make_supervisor(tmp_path, ["/bin/sleep", "30"], startsecs=0)
    proc = supervisor.get_process("demo")
    proc.state = ProcessState.STOPPED
    proc.popen = mock.Mock()
    proc.stop(wait=True)
    assert proc.state == ProcessState.STOPPED
    proc.popen.poll.assert_not_called()


def test_stop_process_lookup_error_sets_stopped(tmp_path, monkeypatch):
    supervisor = _make_supervisor(tmp_path, ["/bin/sleep", "30"], startsecs=0)
    supervisor.start_process("demo")
    monkeypatch.setattr(
        "rcon.process_supervisor.process.os.killpg",
        mock.Mock(side_effect=ProcessLookupError),
    )
    proc = supervisor.get_process("demo")
    proc.stop(wait=True)
    assert proc.state == ProcessState.STOPPED
    assert proc.popen is None


def test_stop_wait_when_popen_cleared_mid_loop(tmp_path):
    supervisor = _make_supervisor(tmp_path, ["/bin/sleep", "30"], startsecs=0)
    supervisor.start_process("demo")
    proc = supervisor.get_process("demo")
    inner = proc.popen
    assert inner is not None

    class ClearingChild:
        def __init__(self) -> None:
            self.pid = inner.pid
            self.polls = 0
            self.returncode = 0

        def poll(self):
            self.polls += 1
            if self.polls >= 2:
                proc.popen = None
            return None

        def wait(self, timeout=None):
            return 0

    proc.popen = ClearingChild()
    try:
        proc.stop(wait=True)
        assert proc.state == ProcessState.STOPPED
    finally:
        if inner.poll() is None:
            inner.wait(timeout=2)


def test_stop_sends_sigkill_after_stopwaitsecs(tmp_path):
    supervisor = _make_supervisor(
        tmp_path,
        ["/bin/sh", "-c", 'trap "" TERM; sleep 30'],
        startsecs=0,
        stopwaitsecs=0,
    )
    supervisor.start_process("demo")
    proc = supervisor.get_process("demo")
    proc.stop(wait=True)
    assert proc.state == ProcessState.STOPPED
    assert proc.popen is None


def test_autostart_on_run(tmp_path):
    supervisor = _make_supervisor(
        tmp_path,
        ["/bin/sleep", "1"],
        autostart=True,
        startsecs=0,
    )

    def shutdown_soon():
        time.sleep(0.2)
        supervisor.request_shutdown()

    import threading

    threading.Thread(target=shutdown_soon, daemon=True).start()
    exit_code = supervisor.run()
    assert exit_code == 0


def _repo_supervisord_config() -> SupervisorConfig:
    config_path = Path(__file__).resolve().parents[1] / "config" / "supervisord.conf"
    env = {
        "SERVER_NUMBER": "1",
        "HLL_REDIS_URL": "redis://localhost:6379/0",
        "HLL_REDIS_HOST": "localhost",
        "HLL_REDIS_PORT": "6379",
        "HLL_REDIS_DB": "0",
    }
    return load_config(config_path, env)


def test_adapters_match_supervisord_conf():
    from rcon.process_supervisor.registry import (
        adapter_names,
        has_adapter,
        ini_command_looks_like_python,
    )

    config = _repo_supervisord_config()
    assert adapter_names() <= set(config.programs)
    for name in ("workers", "cron", "scheduler"):
        assert not has_adapter(name)
    for name, program in config.programs.items():
        if ini_command_looks_like_python(program.command):
            assert has_adapter(name), f"{name} has Python INI command but no adapter"


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ([], False),
        (["/code/manage.py", "broadcast_loop"], True),
        (["python", "-m", "rcon.scoreboard"], True),
        (["rq", "worker", "--with-scheduler"], False),
        (["/bin/bash", "-c", "cron -f"], False),
        (["rqscheduler", "--interval", "10"], False),
    ],
)
def test_ini_command_looks_like_python(command, expected):
    from rcon.process_supervisor.registry import ini_command_looks_like_python

    assert ini_command_looks_like_python(command) is expected


def test_command_extra_log_recorder_scoreboard_cron():
    from rcon.process_supervisor.registry import command_extra, worker_argv

    config = _repo_supervisord_config()

    log_recorder = config.programs["log_recorder"]
    assert command_extra(log_recorder) == ["-i", "10"]
    assert worker_argv(log_recorder)[-3:] == ["--", "-i", "10"]

    scoreboard = config.programs["scoreboard"]
    assert command_extra(scoreboard) == []
    assert worker_argv(scoreboard) == [
        sys.executable,
        "-m",
        "rcon.process_supervisor.worker",
        "scoreboard",
        "--",
    ]

    cron = config.programs["cron"]
    assert command_extra(cron) is None
    assert worker_argv(cron) == cron.command


def test_worker_unknown_program_exits_nonzero(monkeypatch):
    from rcon.process_supervisor.worker.__main__ import main

    monkeypatch.setattr("rcon.models.install_unaccent", lambda: None)
    assert main(["unknown_program"]) != 0


def test_log_loop_hook_modules_frozen_list():
    from rcon.process_supervisor.registry import LOG_LOOP_HOOK_MODULES

    assert LOG_LOOP_HOOK_MODULES == (
        "rcon.hooks",
        "rcon.auto_kick",
        "rcon.automods.tk_autoban",
        "rcon.discord_chat",
        "rcon.recent_actions",
        "rcon.watchlist",
        "rcon.automods.automod",
    )


def test_worker_does_not_configure_arbiter_logging():
    worker_main = (
        Path(__file__).resolve().parents[1]
        / "rcon"
        / "process_supervisor"
        / "worker"
        / "__main__.py"
    )
    source = worker_main.read_text()
    assert "configure_logging" not in source
    assert "logging_setup" not in source


def test_run_program_unknown_raises_attribute_error():
    from rcon.process_supervisor.registry import run_program

    with pytest.raises(AttributeError):
        run_program("not_a_program", [])


def test_ensure_log_loop_hooks_imports_modules(monkeypatch):
    from rcon.process_supervisor.registry import LOG_LOOP_HOOK_MODULES, ensure_log_loop_hooks

    imported: list[str] = []

    def fake_import_module(name: str):
        imported.append(name)
        return object()

    monkeypatch.setattr(importlib, "import_module", fake_import_module)
    ensure_log_loop_hooks()
    assert imported == list(LOG_LOOP_HOOK_MODULES)


def test_supervisor_main_missing_config(tmp_path):
    from rcon.process_supervisor.__main__ import main

    missing = tmp_path / "missing.conf"
    assert main(["-c", str(missing)]) == 1


def test_supervisor_main_starts_and_shuts_down(tmp_path, monkeypatch):
    from rcon.process_supervisor import __main__ as supervisor_main

    config_text = textwrap.dedent(
        """
        [program:demo]
        command=/bin/sleep 30
        autostart=false
        startsecs=0
        environment=LOGGING_FILENAME=demo.log
        """
    )
    config_path = tmp_path / "supervisord.conf"
    config_path.write_text(config_text)

    supervisor = _make_supervisor(tmp_path, ["/bin/sleep", "30"], startsecs=0)
    supervisor.request_shutdown()

    monkeypatch.setattr(supervisor_main, "load_config", lambda _path: supervisor.config)
    monkeypatch.setattr(supervisor_main, "configure_logging", lambda _config: None)
    monkeypatch.setattr(supervisor_main, "ProcessSupervisor", lambda _config: supervisor)
    monkeypatch.setattr(
        supervisor_main,
        "start_rpc_server",
        lambda *_args, **_kwargs: mock.Mock(shutdown=lambda: None),
    )

    assert supervisor_main.main(["-c", str(config_path)]) == 0


def test_default_config_path_uses_numbered_file(monkeypatch):
    from rcon.process_supervisor.__main__ import _default_config_path

    monkeypatch.setenv("SERVER_NUMBER", "2")
    monkeypatch.setattr(
        "rcon.process_supervisor.__main__.os.path.exists",
        lambda path: path == "/config/supervisord_2.conf",
    )
    assert _default_config_path() == "/config/supervisord_2.conf"


def test_interpolate_missing_env_raises():
    with pytest.raises(KeyError, match="MISSING_VAR"):
        interpolate("value_%(ENV_MISSING_VAR)s", {})


def test_parse_environment_skips_blank_items():
    assert parse_environment("GOOD=1,,KEY=val") == {"GOOD": "1", "KEY": "val"}


def test_program_config_default_log_path():
    program = ProgramConfig(name="demo", command=["/bin/true"])
    path = program.log_path({"LOGGING_PATH": "/tmp/logs"})
    assert path == Path("/tmp/logs/demo.log")


def test_load_config_port_without_host(tmp_path):
    config_text = textwrap.dedent(
        """
        [inet_http_server]
        port=9123

        [program:demo]
        command=/bin/true
        autostart=false
        """
    )
    config_path = tmp_path / "supervisord.conf"
    config_path.write_text(config_text)
    config = load_config(config_path)
    assert config.rpc_host == "0.0.0.0"
    assert config.rpc_port == 9123


def test_load_config_skips_program_without_command(tmp_path):
    config_text = textwrap.dedent(
        """
        [program:empty]
        autostart=false
        """
    )
    config_path = tmp_path / "supervisord.conf"
    config_path.write_text(config_text)
    config = load_config(config_path)
    assert config.programs == {}


def test_registered_program_spawns_worker_argv(tmp_path, monkeypatch):
    from rcon.process_supervisor.process import ManagedProcess
    from rcon.process_supervisor.registry import worker_argv

    monkeypatch.setenv("CRCON_SUPERVISOR_FORK", "0")

    config = ProgramConfig(
        name="broadcasts",
        command=["/code/manage.py", "broadcast_loop"],
        environment={"LOGGING_FILENAME": "broadcasts.log"},
        startsecs=0,
    )
    process = ManagedProcess(config=config, base_environ={"LOGGING_PATH": str(tmp_path)})
    process.spawn()
    assert process.popen is not None
    assert process.popen.args == worker_argv(config)
    process.stop()


def test_spawn_failure_sets_backoff(tmp_path, monkeypatch):
    from rcon.process_supervisor.process import ManagedProcess

    config = ProgramConfig(
        name="demo",
        command=["/bin/sleep", "1"],
        environment={"LOGGING_FILENAME": "demo.log"},
        startsecs=0,
    )
    process = ManagedProcess(config=config, base_environ={"LOGGING_PATH": str(tmp_path)})
    monkeypatch.setattr(
        "rcon.process_supervisor.process.subprocess.Popen",
        mock.Mock(side_effect=OSError("spawn failed")),
    )
    process.spawn()
    assert process.state == ProcessState.BACKOFF
    assert "spawn failed" in process.spawnerr


def test_start_already_running_raises(tmp_path):
    from rcon.process_supervisor.process import ManagedProcess

    config = ProgramConfig(
        name="demo",
        command=["/bin/sleep", "30"],
        environment={"LOGGING_FILENAME": "demo.log"},
        startsecs=0,
    )
    process = ManagedProcess(config=config, base_environ={"LOGGING_PATH": str(tmp_path)})
    process.spawn()
    with pytest.raises(RuntimeError, match="already started"):
        process.start()
    process.stop()


def test_process_info_descriptions(tmp_path):
    from rcon.process_supervisor.process import ManagedProcess

    config = ProgramConfig(
        name="demo",
        command=["/bin/sleep", "30"],
        environment={"LOGGING_FILENAME": "demo.log"},
        startsecs=0,
    )
    process = ManagedProcess(config=config, base_environ={"LOGGING_PATH": str(tmp_path)})
    assert process.process_info()["description"] == "Not started"

    process.state = ProcessState.FATAL
    assert "too quickly" in process.process_info()["description"]

    process.state = ProcessState.EXITED
    process.exitstatus = 3
    assert process.process_info()["description"] == "Exited with exit status 3"


def test_autorestart_always_and_never(tmp_path):
    from rcon.process_supervisor.process import ManagedProcess

    always = ProgramConfig(
        name="demo",
        command=["/bin/true"],
        environment={"LOGGING_FILENAME": "demo.log"},
        autorestart=True,
        startsecs=0,
    )
    process = ManagedProcess(config=always, base_environ={"LOGGING_PATH": str(tmp_path)})
    assert process._should_autorestart(0) is True

    never = ProgramConfig(
        name="demo",
        command=["/bin/true"],
        environment={"LOGGING_FILENAME": "demo.log"},
        autorestart=False,
        startsecs=0,
    )
    process = ManagedProcess(config=never, base_environ={"LOGGING_PATH": str(tmp_path)})
    assert process._should_autorestart(1) is False


def test_backoff_manual_stop_becomes_stopped(tmp_path):
    from rcon.process_supervisor.process import ManagedProcess

    config = ProgramConfig(
        name="demo",
        command=["/bin/sleep", "1"],
        environment={"LOGGING_FILENAME": "demo.log"},
        startsecs=0,
    )
    process = ManagedProcess(config=config, base_environ={"LOGGING_PATH": str(tmp_path)})
    process.state = ProcessState.BACKOFF
    process.manual_stop = True
    process._retry_from_backoff()
    assert process.state == ProcessState.STOPPED
