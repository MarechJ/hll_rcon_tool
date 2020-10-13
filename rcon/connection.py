import socket
import array
import time

MSGLEN = 8196
TIMEOUT_SEC = 10


class HLLAuthError(Exception):
    pass


class HLLConnection:
    """demonstration class only
      - coded for clarity, not efficiency
    """

    def __init__(self):
        self.xorkey = None
        self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self.sock.settimeout(10)

    def connect(self, host, port, password: str):
        self.sock.connect((host, port))
        self.xorkey = self.sock.recv(MSGLEN)
        self.send(f"login {password}".encode())
        result = self.receive()
        if result != b'SUCCESS':
            raise HLLAuthError('Invalid password')

    def close(self):
        self.sock.close()

    def send(self, msg, timed=False):
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

        return array.array('B', n).tobytes()

    def receive(self, msglen=MSGLEN, timed=False):
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
        if timed:
            return before, after, msg
        return msg
