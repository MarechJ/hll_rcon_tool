import array
import base64
import logging
import socket
import threading
import time
import uuid
from threading import get_ident
import itertools
import json
import struct
from typing import Any, ClassVar, Self, Final
from enum import IntEnum

from hllrcon.exceptions import (
    HLLAuthError,
    HLLConnectionError,
    HLLConnectionRefusedError,
    HLLMessageError,
    HLLCommandError
)
from rcon.settings import RconCredentials

MSGLEN = 32_768
TIMEOUT_SEC = 20

logger = logging.getLogger(__name__)

REQUEST_HEADER_FORMAT: Final[str] = ">II"
RESPONSE_HEADER_FORMAT: Final[str] = "<II"

class RconResponseStatus(IntEnum):
    """Enumeration of RCON response status codes."""

    OK = 200
    """The request was successful."""

    BAD_REQUEST = 400
    """The request was invalid."""

    UNAUTHORIZED = 401
    """Insufficient or invalid authorization."""

    INTERNAL_ERROR = 500
    """An internal server error occurred."""


class RconResponse:
    """Represents a RCON response."""

    def __init__(
        self,
        request_id: int,
        command: str,
        version: int,
        status_code: RconResponseStatus,
        status_message: str,
        content_body: str,
    ) -> None:
        """Initializes a new RCON response.

        Parameters
        ----------
        request_id : int
            The ID of the request this response corresponds to.
        command : str
            The command that was executed.
        version : int
            The version of the command.
        status_code : RconResponseStatus
            The status code of the response.
        status_message : str
            A message describing the status of the response.
        content_body : str
            The body of the response, potentially JSON-deserializable.

        """
        self.request_id = request_id
        self.name = command
        self.version = version
        self.status_code = status_code
        self.status_message = status_message
        self.content_body = content_body

    @property
    def content_dict(self) -> dict[str, Any]:
        """JSON-deserialize the content body of the response.

        Raises
        ------
        json.JSONDecodeError
            The content body could not be deserialized.
        TypeError
            The deserialized content is not a dictionary.

        Returns
        -------
        dict[str, Any]
            The deserialized content body as a dictionary.

        """
        parsed_content = json.loads(self.content_body)
        if not isinstance(parsed_content, dict):
            msg = f"Expected JSON content to be a dict, got {type(parsed_content)}"
            raise TypeError(msg)
        return parsed_content

    def __str__(self) -> str:
        content: str | dict[str, Any]
        try:
            content = self.content_dict
        except (json.JSONDecodeError, TypeError):
            content = self.content_body

        return f"{self.status_code} {self.name} {content}"

    @classmethod
    def unpack(cls, request_id: int, body_encoded: bytes) -> Self:
        """Unpacks a RCON response from its bytes representation.

        Parameters
        ----------
        request_id : int
            The ID of the request this response corresponds to.
        body_encoded : bytes
            The encoded body of the response, which is expected to be a JSON string.

        Returns
        -------
        RconResponse
            The unpacked RCON response object.

        """
        body = json.loads(body_encoded)
        return cls(
            request_id=request_id,
            command=str(body["name"]),
            version=int(body["version"]),
            status_code=RconResponseStatus(int(body["statusCode"])),
            status_message=str(body["statusMessage"]),
            content_body=body["contentBody"],
        )

    def raise_for_status(self) -> None:
        """Raises an exception if the response status is not OK.

        Raises
        ------
        HLLCommandError
            The response status code is not `RconResponseStatus.OK`.

        """
        if self.status_code != RconResponseStatus.OK:
            raise HLLCommandError(self.status_code, self.status_message)


class RconRequest:
    """Represents a RCON request."""

    __request_id_counter: ClassVar["itertools.count[int]"] = itertools.count(start=0)

    def __init__(
        self,
        command: str,
        version: int,
        auth_token: str | None,
        content_body: dict[str, Any] | str = "",
    ) -> None:
        """Initializes a new RCON request.

        Parameters
        ----------
        command : str
            The command to be executed.
        version : int
            The version of the command.
        auth_token : str | None
            The authentication token for the RCON connection.
        content_body : dict[str, Any] | str, optional
            An additional payload to send along with the command. Must be
            JSON-serializable.

        """
        self.name = command
        self.version = version
        self.auth_token = auth_token
        self.content_body = content_body
        self.request_id: int = next(self.__request_id_counter)

    def pack(self) -> tuple[bytes, bytes]:
        """Packs the request into a bytes object.

        Returns
        -------
        tuple[bytes, bytes]
            A tuple containing the header and body of the request.

        """
        body = {
            "authToken": self.auth_token or "",
            "version": self.version,
            "name": self.name,
            "contentBody": (
                self.content_body
                if isinstance(self.content_body, str)
                else json.dumps(self.content_body, separators=(",", ":"))
            ),
        }
        body_encoded = json.dumps(body, separators=(",", ":")).encode()
        header = struct.pack(
            REQUEST_HEADER_FORMAT,
            self.request_id,
            len(body_encoded),
        )
        return header, body_encoded


class RconConnection:
    """demonstration class only
    - coded for clarity, not efficiency
    """

    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(TIMEOUT_SEC)
        self.id = f"{get_ident()}-{uuid.uuid4()}"
        self.xorkey: bytes | None = None
        self.auth_token: str | None = None
        self._counter = itertools.count(start=0)

    def connect(self, host: str, port: int, password: str, timeout: float | None = 10) -> None:
        self.sock.settimeout(timeout)
        try:
            self.sock.connect((host, port))
        except socket.gaierror:
            msg = f"Address {host} could not be resolved"
            raise HLLConnectionError(msg) from None
        except ConnectionRefusedError:
            msg = f"The server refused connection over port {port}"
            raise HLLConnectionRefusedError(msg) from None
        except socket.timeout:
            msg = f"Connection to {host}:{port} timed out"
            raise HLLConnectionError(msg) from None

        logger.info("Connected!")
        try:
            self.authenticate(password)
        except HLLAuthError:
            self.close()
            raise

    def close(self) -> None:
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            logger.debug("Unable to send socket shutdown")
        self.sock.close()

    def authenticate(self, password: str) -> None:
        """Authenticate with the Hell Let Loose server.

        Parameters
        ----------
        password : str
            The RCON password to authenticate with.

        Raises
        ------
        HLLAuthError
            The provided password is incorrect.

        """
        logger.debug("Waiting to login...")

        xorkey_resp = self.send("ServerConnect", 2, "")
        xorkey_resp.raise_for_status()
        logger.info("Received xorkey")

        if not isinstance(xorkey_resp.content_body, str):
            msg = "ServerConnect response content_body is not a string"
            raise HLLMessageError(msg)
        self.xorkey = base64.b64decode(xorkey_resp.content_body)

        auth_token_resp = self.send("Login", 2, password)
        auth_token_resp.raise_for_status()
        logger.info("Received auth token, successfully authenticated")

        self.auth_token = auth_token_resp.content_body

    def send(
        self,
        command: str,
        version: int,
        content_body: dict[str, Any] | str = "",
    ) -> RconResponse:
        """Send a RCON command.

        Sends a request to the server and waits for a response.

        Parameters
        ----------
        command : str
            The command to execute on the server.
        version : int
            The version of the command.
        content_body : dict[str, Any] | str, optional
            An additional payload to send along with the command. Must be
            JSON-serializable.

        Raises
        ------
        HLLConnectionError
            The connection was closed
        HLLCommandError
            The server failed to execute the command
        HLLMessageError
            The server returned an unexpected response

        """
        request = RconRequest(
            command=command,
            version=version,
            auth_token=self.auth_token,
            content_body=content_body,
        )
        request.request_id = next(self._counter)
        header, body = request.pack()
        message = header + self._xor(body)
        logger.debug("Writing: %s", header + body)
        self._send(message)
        response = self._receive()
        logger.debug("Response: (%s) %s", response.name, response.content_body)
        response.raise_for_status()
        return response

    def _xor(self, message: bytes, offset: int = 0) -> bytes:
        """Encrypt or decrypt a message using the XOR key provided by the server.

        Parameters
        ----------
        message : bytes
            The message to encrypt or decrypt.
        offset : int, optional
            The offset to apply to the XOR key. Defaults to 0.

        Returns
        -------
        bytes
            The encrypted or decrypted message.

        """
        if not self.xorkey:
            return message

        n = [
            c ^ self.xorkey[(i + offset) % len(self.xorkey)]
            for i, c in enumerate(message)
        ]

        res = array.array("B", n).tobytes()
        if len(res) != len(message):
            logger.warning(
                "XOR operation resulted in a different length: %s != %s",
                len(res),
                len(message),
            )
            msg = "XOR operation resulted in a different length"
            raise ValueError(msg)

        return res
    
    def _send(self, message: bytes) -> int:
        sent = self.sock.send(message)
        if sent != len(message):
            raise RuntimeError("socket connection broken")
        return sent

    def _receive(self, msglen=MSGLEN) -> RconResponse:
        header_len = struct.calcsize(RESPONSE_HEADER_FORMAT)
        buffer = b""
        while len(buffer) < header_len:
            chunk = self.sock.recv(msglen)
            if not chunk:
                raise RuntimeError("socket connection broken")
            buffer += chunk

        pkt_id, pkt_len = struct.unpack(RESPONSE_HEADER_FORMAT, buffer[:header_len])
        pkt_size = header_len + pkt_len
        while len(buffer) < pkt_size:
            chunk = self.sock.recv(msglen)
            if not chunk:
                raise RuntimeError("socket connection broken")
            buffer += chunk

        decoded_body = self._xor(buffer[header_len:pkt_size])
        logger.debug("Unpacking: %s", decoded_body)
        return RconResponse.unpack(pkt_id, decoded_body)


class RconConnectionPool:
    def __init__(self, credentials: RconCredentials, max_open=20, max_idle=20):
        self.max_open = max_open
        self.max_idle = max_idle
        self.open_conn = 0
        self.idle_conn: list[RconConnection] = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.host = credentials.host
        self.port = credentials.port
        self.password = credentials.password

    def close_connection(self, conn: RconConnection):
        with self.condition:
            conn.close()
            self.open_conn -= 1
            self.condition.notify()

    def return_connection(self, conn: RconConnection):
        with self.condition:
            if len(self.idle_conn) <= self.max_idle:
                self.idle_conn.append(conn)
                self.open_conn -= 1
            else:
                conn.close()
                self.open_conn -= 1
            self.condition.notify()

    def get_connection(self, timeout=30) -> RconConnection:
        logger.debug("Waiting to acquire lock %s", threading.get_ident())
        with self.condition:
            # If any idle connections available
            if len(self.idle_conn) != 0:
                conn = self.idle_conn.pop()
                logger.debug("acquiring connection from idle pool: %s", conn.id)
                return conn

            # If can open another connection
            elif self.open_conn < self.max_open:
                conn = RconConnection()
                logger.debug("Opening a new connection with ID %s", conn.id)
                self._open_connection(conn)
                self.open_conn += 1
                return conn
                
            # Wait for active connection to become idle up to 30 seconds
            end_time = time.time() + timeout
            while not len(self.idle_conn):
                remaining = end_time - time.time()
                if remaining <= 0:
                    raise TimeoutError("Timeout while waiting for connection.")
                self.condition.wait(timeout=remaining)

            return self.idle_conn.pop()

    def _open_connection(self, conn: RconConnection) -> None:
        try:
            conn.connect(
                self.host, self.port, self.password
            )
        except (TypeError, ValueError) as e:
            logger.exception("Invalid connection information", e)
            raise
