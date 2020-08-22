import socket
import array

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

    def send(self, msg):
        sent = self.sock.send(self._xor(msg))
        if sent != len(msg):
            raise RuntimeError("socket connection broken")
        return sent

    def _xor(self, msg):
        n = []
        if not self.xorkey:
            raise RuntimeError("The game server did not return a key")
        for i in range(len(msg)):
            n.append(msg[i] ^ self.xorkey[i % len(self.xorkey)])

        return array.array('B', n).tobytes()

    def receive(self, msglen=MSGLEN):
        buff = self.sock.recv(msglen)
        msg = self._xor(buff)

        while len(buff) >= msglen:
            buff = self.sock.recv(msglen)
            msg += self._xor(buff)

        return msg
