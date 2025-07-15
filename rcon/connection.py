import array
import base64
import itertools
import json
import logging
import socket
import struct
import uuid
from enum import IntEnum
from threading import get_ident
from typing import Any, Self, ClassVar

TIMEOUT_SEC = 20
HEADER_FORMAT = "<II"

logger = logging.getLogger(__name__)


class HLLAuthError(Exception):
    pass


class HLLError(Exception):
    pass


class HLLCommandError(HLLError):
    def __init__(self, status_code: int, *args: object) -> None:
        self.status_code = status_code
        super().__init__(*args)

    def __str__(self) -> str:
        """Return a string representation of the error."""
        exc_str = super().__str__()
        header = f"({self.status_code})"
        return f"{header} {exc_str}".rstrip()


class HLLMessageError(HLLError):
    """Raised when the game server returns an unexpected value."""


class Request:
    __request_id_counter: ClassVar["itertools.count[int]"] = itertools.count(start=1)

    def __init__(self, command: str, version: int, auth_token: str | None, content: dict[str, Any] | str = "") -> None:
        self.name = command
        self.version = version
        self.auth_token = auth_token
        self.content = content

    def to_bytes(self) -> bytes:
        body = {
            "authToken": self.auth_token or "",
            "version": self.version,
            "name": self.name,
            "contentBody": (self.content if isinstance(self.content, str) else json.dumps(self.content, separators=(",", ":"))),
        }
        body = json.dumps(body, separators=(",", ":")).encode()
        return body


class ResponseStatus(IntEnum):
    OK = 200
    """The request was successful."""

    BAD_REQUEST = 400
    """The request was invalid."""

    UNAUTHORIZED = 401
    """Insufficient or invalid authorization."""

    INTERNAL_ERROR = 500
    """An internal server error occurred."""


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


class HLLConnection:
    def __init__(self) -> None:
        self.xorkey = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(TIMEOUT_SEC)
        self.id = f"{get_ident()}-{uuid.uuid4()}"
        self.auth_token = None

    def connect(self, host, port, password: str):
        self.sock.connect((host, port))
        # read first 4 bytes (RCONv1 XOR key, which is not used anymore)
        self.sock.recv(4)

        server_hello = self.exchange("ServerConnect", 2, "")
        server_hello.raise_for_status()

        if not isinstance(server_hello.content, str):
            msg = "ServerConnect response content is not a string"
            raise HLLMessageError(msg)
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

    def exchange(self, command: str, version: int, body: dict[str, Any] | str = ""):
        request = Request(
            command=command,
            version=version,
            auth_token=self.auth_token,
            content=body,
        )

        message = self._xor(request.to_bytes())
        self.sock.send(message)
        header_len = struct.calcsize(HEADER_FORMAT)
        header_bytes = self.sock.recv(header_len)
        req_id, body_len = struct.unpack(HEADER_FORMAT, header_bytes)
        self.sock.settimeout(1)

        raw: bytearray = bytearray()
        while len(raw) < body_len:
            raw += self.sock.recv(body_len - len(raw))
        msg = self._xor(raw)
        return Response.from_bytes(req_id, msg)

    def _xor(self, msg) -> bytes:
        if not self.xorkey:
            return msg
        n = []
        for i in range(len(msg)):
            n.append(msg[i] ^ self.xorkey[i % len(self.xorkey)])

        return array.array("B", n).tobytes()
