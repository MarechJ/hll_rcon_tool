"""Program name registry and lazy run() dispatch for worker children."""

from __future__ import annotations

import sys

from rcon.process_supervisor.config import ProgramConfig
from rcon.process_supervisor.programs import (
    LOG_LOOP_HOOK_MODULES,
    _parse_log_recorder_args,
    ensure_log_loop_hooks,
)


def has_adapter(name: str) -> bool:
    from rcon.process_supervisor import programs

    return callable(getattr(programs, f"run_{name}", None))


def adapter_names() -> frozenset[str]:
    from rcon.process_supervisor import programs

    return frozenset(
        attr[4:]
        for attr, obj in vars(programs).items()
        if attr.startswith("run_") and callable(obj)
    )


def ini_command_looks_like_python(command: list[str]) -> bool:
    if not command:
        return False
    if command[0].endswith("manage.py"):
        return True
    return len(command) >= 3 and command[1] == "-m"


def command_extra(program: ProgramConfig) -> list[str] | None:
    """Return extra argv for the worker, or None to spawn the INI command as-is."""

    if not has_adapter(program.name):
        return None

    cmd = program.command
    if not cmd:
        return []

    if cmd[0].endswith("manage.py"):
        return cmd[2:]

    if len(cmd) >= 3 and cmd[1] == "-m":
        return []

    return cmd[1:]


def worker_argv(program: ProgramConfig) -> list[str]:
    extra = command_extra(program)
    if extra is None:
        return program.command
    return [
        sys.executable,
        "-m",
        "rcon.process_supervisor.worker",
        program.name,
        "--",
        *extra,
    ]


def run_program(name: str, extra: list[str]) -> None:
    from rcon.process_supervisor import programs

    fn = getattr(programs, f"run_{name}")
    if name == "log_recorder":
        fn(extra)
    else:
        fn()
