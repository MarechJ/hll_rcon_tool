import array
import base64
from contextlib import contextmanager
import itertools
import json
import logging
import socket
import struct
import threading
import uuid
from enum import IntEnum
from threading import get_ident
from typing import Any, Self, ClassVar

from cachetools import TTLCache

TIMEOUT_SEC = 20
HEADER_FORMAT = "<III"
MAGIC_HEADER_VALUE = 0xDE450508

logger = logging.getLogger(__name__)

class HLLServerError(Exception):
    """Raised when the server failed to execute a command or responded unexpectedly"""

class HLLBrokenConnectionError(HLLServerError):
    """Raised when the connection has broken and needs to be re-established"""

class HLLCommandFailedError(HLLServerError):
    """Raised when a command failed"""

class HLLCommandError(HLLServerError):
    def __init__(self, status_code: int, *args: object) -> None:
        self.status_code = status_code
        super().__init__(*args)

    def __str__(self) -> str:
        """Return a string representation of the error."""
        exc_str = super().__str__()
        header = f"({self.status_code})"
        return f"{header} {exc_str}".rstrip()


class Request:
    __request_id_counter: ClassVar["itertools.count[int]"] = itertools.count(start=1)

    def __init__(self, command: str, version: int, auth_token: str | None, content: dict[str, Any] | str = "") -> None:
        self.name = command
        self.version = version
        self.auth_token = auth_token
        self.content = content
        self.request_id = next(self.__request_id_counter)
    
    def __str__(self) -> str:
        return f"Request #{self.request_id} ({self.name}, {self.version}, {self.content})"
    
    def __repr__(self) -> str:
        return "<" + self.__str__() + ">"

    def to_bytes(self) -> tuple[bytes, bytes]:
        body = {
            "authToken": self.auth_token or "",
            "version": self.version,
            "name": self.name,
            "contentBody": (self.content if isinstance(self.content, str) else json.dumps(self.content, separators=(",", ":"))),
        }
        body = json.dumps(body, separators=(",", ":")).encode()
        header = struct.pack(HEADER_FORMAT, MAGIC_HEADER_VALUE, self.request_id, len(body))
        return header, body


class ResponseStatus(IntEnum):
    OK = 200
    """The request was successful."""

    BAD_REQUEST = 400
    """The request was invalid."""

    UNAUTHORIZED = 401
    """Insufficient or invalid authorization."""

    INTERNAL_ERROR = 500
    """An internal server error occurred."""


class Handle:
    def __init__(self, conn: 'HLLConnection', request: 'Request') -> None:
        self.conn = conn
        self.request = request
        self._response: Response | None = None
    
    def receive(self) -> 'Response':
        if self._response is None:
            self._response = self.conn.receive(self.request.request_id)
        return self._response

class Response:
    def __init__(
            self,
            request_id: int,
            command: str,
            version: int,
            status_code: ResponseStatus,
            status_message: str,
            content: str,
    ) -> None:
        self.request_id = request_id
        self.name = command
        self.version = version
        self.status_code = status_code
        self.status_message = status_message
        self.content = content

    def is_ok(self) -> bool:
        return self.status_code == ResponseStatus.OK

    def is_successful(self) -> bool:
        if self.status_code >= ResponseStatus.INTERNAL_ERROR:
            raise HLLCommandError(self.status_code, self.status_message)
        elif self.status_code >= ResponseStatus.BAD_REQUEST:
            return False
        return True

    @property
    def content_dict(self) -> dict[str, Any]:
        parsed_content = json.loads(self.content)
        if not isinstance(parsed_content, dict):
            msg = f"Expected JSON content to be a dict, got {type(parsed_content)}"
            raise TypeError(msg)
        return parsed_content

    def __str__(self) -> str:
        content: str | dict[str, Any]
        try:
            content = self.content_dict
        except (json.JSONDecodeError, TypeError):
            content = self.content

        return f"{self.status_code} {self.name} {content}"

    @classmethod
    def from_bytes(cls, request_id: int, body_encoded: bytes) -> Self:
        body = json.loads(body_encoded)
        return cls(
            request_id=request_id,
            command=str(body["name"]),
            version=int(body["version"]),
            status_code=ResponseStatus(int(body["statusCode"])),
            status_message=str(body["statusMessage"]),
            content=body["contentBody"],
        )

    def raise_for_status(self) -> None:
        """Raises an exception if the response status is not OK.

        Raises
        ------
        HLLCommandError
            The response status code is not `RconResponseStatus.OK`.

        """
        if self.status_code != ResponseStatus.OK:
            raise HLLCommandError(self.status_code, self.status_message)


@contextmanager
def set_timeout(sock: socket.socket, timeout: float):
    original_timeout = sock.gettimeout()
    sock.settimeout(timeout)
    try:
        yield sock
    finally:
        sock.settimeout(original_timeout)


class HLLConnection:
    def __init__(self) -> None:
        self.xorkey = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(TIMEOUT_SEC)
        self.id = f"{get_ident()}-{uuid.uuid4()}"
        self.auth_token = None
        self.mu = threading.Lock()
        self._response_cache: TTLCache[int, Response] = TTLCache(maxsize=1024, ttl=60)

    def connect(self, host, port, password: str):
        self.sock.connect((host, port))

        server_hello = self.exchange("ServerConnect", 2, "")
        server_hello.raise_for_status()

        if not isinstance(server_hello.content, str):
            raise HLLBrokenConnectionError("ServerConnect response content is not a string")
        self.xorkey = base64.b64decode(server_hello.content)

        auth_token_resp = self.exchange("Login", 2, password)
        auth_token_resp.raise_for_status()

        self.auth_token = auth_token_resp.content

    def close(self) -> None:
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            logger.debug("Unable to send socket shutdown")
        self.sock.close()

    def send(self, command: str, version: int, body: dict[str, Any] | str = "") -> Handle:
        request = Request(
            command=command,
            version=version,
            auth_token=self.auth_token,
            content=body,
        )

        req_header, req_body = request.to_bytes()
        message = req_header + self._xor(req_body)
        self.sock.send(message)

        return Handle(self, request)

    def receive(self, request_id: int) -> Response:
        # Not sure if this lock is still necessary, but better safe than sorry
        self.mu.acquire()
        try:
            while request_id not in self._response_cache:
                header_len = struct.calcsize(HEADER_FORMAT)
                header_bytes = self.sock.recv(header_len)
                try:
                    magic, req_id, body_len = struct.unpack(HEADER_FORMAT, header_bytes)
                except struct.error:
                    raise HLLBrokenConnectionError(f"Failed to unpack response header: {header_bytes}")
                
                if magic != MAGIC_HEADER_VALUE:
                    raise HLLBrokenConnectionError(f"Invalid magic value: {magic:#x} (expected {MAGIC_HEADER_VALUE:#x})")

                with set_timeout(self.sock, 3):
                    raw = bytearray()
                    while len(raw) < body_len:
                        raw += self.sock.recv(body_len - len(raw))

                msg = self._xor(raw)
                response = Response.from_bytes(req_id, msg)

                self._response_cache[response.request_id] = response
        finally:
            self.mu.release()

        response = self._response_cache.pop(request_id)
        return response

    def exchange(self, command: str, version: int, body: dict[str, Any] | str = ""):
        handle = self.send(command, version, body)
        return handle.receive()

    def _xor(self, msg) -> bytes:
        if not self.xorkey:
            return msg
        n = []
        for i in range(len(msg)):
            n.append(msg[i] ^ self.xorkey[i % len(self.xorkey)])

        return array.array("B", n).tobytes()
