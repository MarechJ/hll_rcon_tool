import array
import logging
import socket
import time
from threading import Lock, get_ident

MSGLEN = 8196
TIMEOUT_SEC = 20

logger = logging.getLogger(__name__)


class HLLAuthError(Exception):
    pass


class HLLConnection:
    """demonstration class only
    - coded for clarity, not efficiency
    """

    def __init__(self):
        self.xorkey = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(TIMEOUT_SEC)
        self._lock = Lock()

    def connect(self, host, port, password: str):
        self.sock.connect((host, port))
        self.xorkey = self.sock.recv(MSGLEN)
        self.send(f"login {password}".encode())
        result = self.receive()
        if result != b"SUCCESS":
            raise HLLAuthError("Invalid password")

    def close(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            logger.debug("Unable to send socket shutdown")
        self.sock.close()

    def send(self, msg, timed=False):
        self.lock()

        xored = self._xor(msg)
        before = time.time()
        sent = self.sock.send(xored)
        after = time.time()
        if sent != len(msg):
            raise RuntimeError("socket connection broken")
        if timed:
            return before, after, sent
        return sent

    def _xor(self, msg):
        n = []
        if not self.xorkey:
            raise RuntimeError("The game server did not return a key")
        for i in range(len(msg)):
            n.append(msg[i] ^ self.xorkey[i % len(self.xorkey)])

        return array.array("B", n).tobytes()

    def unlock(self):
        """
        With using the ServerCtl connection pool, locking an individual connection has low value, but is kept for
        backward compatibility and cowardliness :D Might be removed in future released.
        """
        self._lock.release()

    def lock(self):
        """
        With using the ServerCtl connection pool, locking an individual connection has low value, but is kept for
        backward compatibility and cowardliness :D Might be removed in future released.
        """
        if self._lock.locked():
            logger.warning("Mutex lock detected, this is unexpected in %s", get_ident())

        # logger.debug("Locking connection in %s", get_ident())
        if not self._lock.acquire(timeout=10):
            logger.error("Unable to acquirelock after 10sec in %s", get_ident())
            raise RuntimeError("Unable to acquirelock after 10sec in %s", get_ident())

    def receive(self, msglen=MSGLEN, timed=False, unlock=True):
        if not self._lock.locked() and unlock == True:
            logger.error(
                "Receiving on unlocked connection, this is unexpected in %s",
                get_ident(),
            )

        before = time.time()
        buff = self.sock.recv(msglen)

        msg = self._xor(buff)

        while len(buff) >= msglen:
            try:
                buff = self.sock.recv(msglen)
            except socket.timeout:
                break
            msg += self._xor(buff)
        after = time.time()

        if unlock:
            self.unlock()
        if timed:
            return before, after, msg
        return msg
