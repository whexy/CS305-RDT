from Dispatcher import Dispatcher
from USocket import UnreliableSocket


class RDTSocket(UnreliableSocket):

    def __init__(self, rate=None):
        super().__init__(rate=rate)
        self._rate = rate
        self._send_to = None
        self._recv_from = None

        self.dispatcher = Dispatcher(self)

    def accept(self) -> ('RDTSocket', (str, int)):
        conn, addr = RDTSocket(self._rate), None
        conn.set_send_to()
        conn.set_recv_from()
        return conn, addr

    def connect(self, address: (str, int)):
        raise NotImplementedError()

    def recv(self, bufsize: int) -> bytes:
        assert self._recv_from, "Connection not established yet. Use recvfrom instead."
        return self.dispatcher.scoop(bufsize)

    def send(self, bytes: bytes):
        assert self._send_to, "Connection not established yet. Use sendto instead."
        self.dispatcher.fill(bytes)

    def close(self):
        super().close()

    def set_send_to(self, send_to):
        self._send_to = send_to

    def set_recv_from(self, recv_from):
        self._recv_from = recv_from
