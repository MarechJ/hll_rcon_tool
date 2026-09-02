"""Process supervisor manager: spawn, reap, and restart managed programs."""

from __future__ import annotations

import logging
import os
import signal
import threading
import time
from xmlrpc.server import Fault

from rcon.process_supervisor.config import SupervisorConfig
from rcon.process_supervisor.process import ManagedProcess
from rcon.process_supervisor.states import (
    FAULT_ALREADY_STARTED,
    FAULT_BAD_NAME,
    FAULT_NOT_RUNNING,
    ProcessState,
)

logger = logging.getLogger(__name__)


class ProcessSupervisor:
    def __init__(self, config: SupervisorConfig, base_environ: dict[str, str] | None = None):
        self.config = config
        self.base_environ = dict(base_environ if base_environ is not None else os.environ)
        self._lock = threading.RLock()
        self._processes: dict[str, ManagedProcess] = {
            name: ManagedProcess(program, self.base_environ)
            for name, program in config.programs.items()
        }
        self._shutdown = False

    def get_process(self, name: str) -> ManagedProcess:
        try:
            return self._processes[name]
        except KeyError as exc:
            raise Fault(FAULT_BAD_NAME, f"BAD_NAME: unknown process {name}") from exc

    def get_all_process_info(self) -> list[dict[str, object]]:
        with self._lock:
            now = int(time.time())
            return [proc.process_info(now) for proc in self._processes.values()]

    def get_process_info(self, name: str) -> dict[str, object]:
        with self._lock:
            return self.get_process(name).process_info()

    def start_process(self, name: str) -> bool:
        with self._lock:
            proc = self.get_process(name)
            if proc.is_running():
                raise Fault(
                    FAULT_ALREADY_STARTED,
                    f"ALREADY_STARTED: {name}",
                )
            proc.start(wait=False)
        logger.info("Started process '%s' via RPC", name)
        return True

    def stop_process(self, name: str) -> bool:
        with self._lock:
            proc = self.get_process(name)
            if not proc.is_running():
                raise Fault(
                    FAULT_NOT_RUNNING,
                    f"NOT_RUNNING: {name}",
                )
            proc.stop(wait=False)
        proc.stop(wait=True)
        with self._lock:
            if proc.state != ProcessState.STOPPED:
                proc.state = ProcessState.STOPPED
        logger.info("Stopped process '%s' via RPC", name)
        return True

    def autostart(self) -> None:
        with self._lock:
            for proc in self._processes.values():
                if proc.config.autostart:
                    proc.start(wait=False)

    def tick(self) -> None:
        with self._lock:
            for proc in self._processes.values():
                proc.tick()

    def stop_all(self) -> None:
        with self._lock:
            for proc in self._processes.values():
                if proc.is_running():
                    proc.stop(wait=True)
                    proc.state = ProcessState.STOPPED

    def run(self) -> int:
        self._install_signal_handlers()
        self.autostart()

        try:
            while not self._shutdown:
                self.tick()
                time.sleep(0.1)
        finally:
            self.stop_all()
        return 0

    def request_shutdown(self) -> None:
        self._shutdown = True

    def _install_signal_handlers(self) -> None:
        def handler(signum: int, _frame: object) -> None:
            logger.info("Received signal %s, shutting down", signum)
            self.request_shutdown()

        signal.signal(signal.SIGTERM, handler)
        signal.signal(signal.SIGINT, handler)
