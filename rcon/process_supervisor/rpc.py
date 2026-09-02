"""Supervisord-compatible XML-RPC interface."""

from __future__ import annotations

import logging
import threading
from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer

from rcon.process_supervisor.manager import ProcessSupervisor

logger = logging.getLogger(__name__)


class SupervisorRequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)


class SupervisorRPC:
    def __init__(self, supervisor: ProcessSupervisor):
        self._supervisor = supervisor

    def getAllProcessInfo(self) -> list[dict[str, object]]:
        return self._supervisor.get_all_process_info()

    def getProcessInfo(self, name: str) -> dict[str, object]:
        return self._supervisor.get_process_info(name)

    def startProcess(self, name: str) -> bool:
        return self._supervisor.start_process(name)

    def stopProcess(self, name: str) -> bool:
        return self._supervisor.stop_process(name)


def start_rpc_server(
    supervisor: ProcessSupervisor, host: str, port: int
) -> SimpleXMLRPCServer:
    server = SimpleXMLRPCServer(
        (host, port),
        requestHandler=SupervisorRequestHandler,
        allow_none=True,
        logRequests=False,
    )
    rpc = SupervisorRPC(supervisor)
    server.register_function(rpc.getAllProcessInfo, "supervisor.getAllProcessInfo")
    server.register_function(rpc.getProcessInfo, "supervisor.getProcessInfo")
    server.register_function(rpc.startProcess, "supervisor.startProcess")
    server.register_function(rpc.stopProcess, "supervisor.stopProcess")
    server.register_introspection_functions()

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info("XML-RPC listening on %s:%s/RPC2", host, port)
    return server
