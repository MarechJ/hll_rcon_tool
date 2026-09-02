"""Single managed subprocess with Supervisord-compatible state."""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from rcon.process_supervisor.config import ProgramConfig
from rcon.process_supervisor.preload import ensure_forkserver, fork_enabled
from rcon.process_supervisor.registry import (
    command_extra,
    ini_command_looks_like_python,
    worker_argv,
)
from rcon.process_supervisor.states import STATENAME, ProcessState
from rcon.process_supervisor.worker.fork_child import fork_main

logger = logging.getLogger(__name__)

_SIGNALS = {
    "TERM": signal.SIGTERM,
    "KILL": signal.SIGKILL,
    "HUP": signal.SIGHUP,
    "INT": signal.SIGINT,
    "QUIT": signal.SIGQUIT,
}


class ChildProcess(Protocol):
    pid: int
    returncode: int | None

    def poll(self) -> int | None: ...

    def wait(self, timeout: float | None = None) -> int: ...


class ForkedChild:
    """Popen-compatible wrapper for a multiprocessing forkserver child."""

    def __init__(self, process: Any) -> None:
        self._process = process

    @property
    def pid(self) -> int:
        return self._process.pid or 0

    @property
    def returncode(self) -> int | None:
        return self._process.exitcode

    def poll(self) -> int | None:
        self._process.join(timeout=0)
        return self._process.exitcode

    def wait(self, timeout: float | None = None) -> int:
        self._process.join(timeout=timeout)
        if self._process.is_alive():
            raise subprocess.TimeoutExpired(str(self.pid), timeout)
        return self._process.exitcode or 0


def _format_uptime(seconds: float) -> str:
    total = int(max(0, seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}"


@dataclass
class ManagedProcess:
    config: ProgramConfig
    base_environ: dict[str, str]

    state: ProcessState = ProcessState.STOPPED
    pid: int = 0
    popen: ChildProcess | None = None
    log_file: Path | None = None
    spawnerr: str = ""
    exitstatus: int = 0
    start_time: int = 0
    stop_time: int = 0
    spawn_time: float = 0.0
    retries_remaining: int = field(init=False)
    manual_stop: bool = False
    _backoff_until: float = 0.0

    def __post_init__(self) -> None:
        self.retries_remaining = self.config.startretries

    @property
    def statename(self) -> str:
        return STATENAME[self.state]

    def is_running(self) -> bool:
        return self.state in {ProcessState.STARTING, ProcessState.RUNNING, ProcessState.STOPPING}

    def process_info(self, now: int | None = None) -> dict[str, object]:
        current = now if now is not None else int(time.time())
        if self.is_running() and self.pid:
            uptime = _format_uptime(time.time() - self.start_time)
            description = f"pid {self.pid}, uptime {uptime}"
        elif self.state == ProcessState.FATAL:
            description = "Exited too quickly (process log may have details)"
        elif self.state == ProcessState.EXITED:
            description = f"Exited with exit status {self.exitstatus}"
        elif self.state == ProcessState.STOPPED:
            description = "Not started"
        else:
            description = ""

        return {
            "name": self.config.name,
            "group": self.config.name,
            "description": description,
            "start": self.start_time,
            "stop": self.stop_time,
            "now": current,
            "state": int(self.state),
            "statename": self.statename,
            "spawnerr": self.spawnerr,
            "exitstatus": self.exitstatus,
            "pid": self.pid if self.is_running() else 0,
            "stdout_logfile": str(self.log_file or ""),
        }

    def spawn(self) -> None:
        if self.is_running():
            return

        child_env = self.config.child_environ(self.base_environ)
        self.log_file = self.config.log_path(child_env)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.spawnerr = ""

        try:
            extra = command_extra(self.config)
            if extra is None and ini_command_looks_like_python(self.config.command):
                logger.warning(
                    "Program %r has no programs.run_%s adapter; exec INI command as-is: %s",
                    self.config.name,
                    self.config.name,
                    self.config.command,
                )
            if extra is None or not fork_enabled():
                with self.log_file.open("ab", buffering=0) as log_handle:
                    self.popen = subprocess.Popen(
                        worker_argv(self.config),
                        cwd=self.config.directory,
                        env=child_env,
                        stdout=log_handle,
                        stderr=subprocess.STDOUT,
                        start_new_session=True,
                    )
            else:
                ctx = ensure_forkserver()
                proc = ctx.Process(
                    target=fork_main,
                    args=(
                        self.config.name,
                        extra,
                        child_env,
                        str(self.log_file),
                        self.config.directory,
                    ),
                    daemon=False,
                )
                proc.start()
                self.popen = ForkedChild(proc)
        except OSError as exc:
            self.spawnerr = str(exc)
            logger.error("Failed to spawn '%s': %s", self.config.name, exc)
            self.state = ProcessState.BACKOFF
            return

        self.pid = self.popen.pid
        self.spawn_time = time.time()
        self.start_time = int(self.spawn_time)
        self.stop_time = 0
        self.exitstatus = 0
        self.state = ProcessState.STARTING
        logger.info("Spawned '%s' with pid %s", self.config.name, self.pid)

        if self.config.startsecs == 0:
            self.state = ProcessState.RUNNING
            logger.info("Process '%s' entered RUNNING state", self.config.name)

    def stop(self, wait: bool = True) -> None:
        if self.popen is None:
            if self.state == ProcessState.STOPPING:
                self.state = ProcessState.STOPPED
            return
        if not self.is_running():
            return

        self.manual_stop = True
        self.state = ProcessState.STOPPING
        logger.info("Stopping '%s' (pid %s)", self.config.name, self.pid)
        sig = _SIGNALS.get(self.config.stopsignal, signal.SIGTERM)
        try:
            os.killpg(self.popen.pid, sig)
        except ProcessLookupError:
            self._finalize_exit(0)
            self.state = ProcessState.STOPPED
            return

        if not wait:
            return

        deadline = time.time() + self.config.stopwaitsecs
        while time.time() < deadline:
            child = self.popen
            if child is None:
                self.state = ProcessState.STOPPED
                return
            if child.poll() is not None:
                self._finalize_exit(child.returncode or 0)
                self.state = ProcessState.STOPPED
                return
            time.sleep(0.05)

        child = self.popen
        if child is None:
            self.state = ProcessState.STOPPED
            return
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

        try:
            child.wait(timeout=1)
        except subprocess.TimeoutExpired:
            pass

        self._finalize_exit(child.returncode or 0)
        self.state = ProcessState.STOPPED

    def start(self, wait: bool = True) -> None:
        if self.is_running():
            raise RuntimeError("already started")
        self.manual_stop = False
        self.retries_remaining = self.config.startretries
        self.spawn()
        if wait:
            self._wait_for_start()

    def _wait_for_start(self) -> None:
        if self.config.startsecs <= 0:
            return
        deadline = time.time() + self.config.startsecs
        while time.time() < deadline:
            if self.popen and self.popen.poll() is not None:
                self._handle_exit(self.popen.returncode or 0)
                return
            time.sleep(0.05)
        if self.popen and self.popen.poll() is None:
            self.state = ProcessState.RUNNING
            logger.info("Process '%s' entered RUNNING state", self.config.name)

    def tick(self) -> None:
        if self.popen is None:
            if self.state == ProcessState.BACKOFF:
                self._retry_from_backoff()
            return

        returncode = self.popen.poll()
        if returncode is None:
            if (
                self.state == ProcessState.STARTING
                and time.time() - self.spawn_time >= self.config.startsecs
            ):
                self.state = ProcessState.RUNNING
                logger.info("Process '%s' entered RUNNING state", self.config.name)
            return

        self._handle_exit(returncode)

    def _handle_exit(self, returncode: int) -> None:
        exited_pid = self.pid
        if self.state == ProcessState.STOPPING:
            self._finalize_exit(returncode)
            self.state = ProcessState.STOPPED
            logger.info(
                "Process '%s' (pid %s) stopped with status %s",
                self.config.name,
                exited_pid,
                returncode,
            )
            return

        if self.state == ProcessState.STARTING:
            self._finalize_exit(returncode)
            if self.manual_stop:
                self.state = ProcessState.STOPPED
                logger.info(
                    "Process '%s' (pid %s) exited during start with status %s; now STOPPED",
                    self.config.name,
                    exited_pid,
                    returncode,
                )
                return
            if self.retries_remaining > 0:
                self.retries_remaining -= 1
                self.state = ProcessState.BACKOFF
                self._backoff_until = time.time() + 1.0
                logger.info(
                    "Process '%s' (pid %s) exited during start with status %s; now BACKOFF (%s retries left)",
                    self.config.name,
                    exited_pid,
                    returncode,
                    self.retries_remaining,
                )
            else:
                self.state = ProcessState.FATAL
                logger.error(
                    "Process '%s' (pid %s) exited during start with status %s; now FATAL",
                    self.config.name,
                    exited_pid,
                    returncode,
                )
            return

        self._finalize_exit(returncode)
        if self.manual_stop:
            self.state = ProcessState.STOPPED
            logger.info(
                "Process '%s' (pid %s) exited with status %s; now STOPPED",
                self.config.name,
                exited_pid,
                returncode,
            )
            return

        if self._should_autorestart(returncode):
            self.state = ProcessState.BACKOFF
            self._backoff_until = time.time() + 1.0
            logger.info(
                "Process '%s' (pid %s) exited with status %s; now BACKOFF (autorestart)",
                self.config.name,
                exited_pid,
                returncode,
            )
        else:
            self.state = ProcessState.EXITED
            logger.info(
                "Process '%s' (pid %s) exited with status %s; now EXITED",
                self.config.name,
                exited_pid,
                returncode,
            )

    def _should_autorestart(self, returncode: int) -> bool:
        policy = self.config.autorestart
        if policy is True:
            return True
        if policy is False:
            return False
        return returncode != 0

    def _retry_from_backoff(self) -> None:
        if self.manual_stop:
            self.state = ProcessState.STOPPED
            return
        if time.time() < self._backoff_until:
            return
        self.spawn()

    def _finalize_exit(self, returncode: int) -> None:
        self.exitstatus = returncode
        self.stop_time = int(time.time())
        self.pid = 0
        self.popen = None
