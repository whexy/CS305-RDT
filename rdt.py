import time

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
        pkt = self.dispatcher.scoop(32)
        while pkt != b'SYN':
            pkt = self.dispatcher.scoop(32)
        addr = self.dispatcher.receiver.addr
        self.dispatcher.receiver.addr = None

        conn.dispatcher.socket.set_send_to(addr)
        conn.dispatcher.socket.set_recv_from(addr)
        conn.dispatcher.receiver.addr = addr

        conn.dispatcher.fill(b'SYNACK')
        pkt = conn.dispatcher.scoop(32)
        while pkt != b'SYNACKACK':
            pkt = conn.dispatcher.scoop(32)
        return conn, addr

    def connect(self, address: (str, int)):
        self.dispatcher.socket.set_send_to(address)
        self.dispatcher.socket.set_recv_from(address)

        self.dispatcher.fill(b'SYN')
        pkt = self.dispatcher.scoop(32)
        while pkt != b'SYNACK':
            pkt = self.dispatcher.scoop(32)
        self.dispatcher.fill(b'SYNACKACK')

    def recv(self, bufsize: int) -> bytes:
        assert self._recv_from, "Connection not established yet. Use recvfrom instead."
        return self.dispatcher.scoop(bufsize)

    def send(self, bytes: bytes):
        assert self._send_to, "Connection not established yet. Use sendto instead."
        self.dispatcher.fill(bytes)

    def close(self):
        self.send(b'FIN')
        pkt = self.recv(32)
        while pkt != b'FINACK':
            pkt = self.recv(32)
        while pkt != b'FIN':
            pkt = self.recv(32)
        wait_start_time = time.time()
        while time.time() - wait_start_time < self.dispatcher.timeout * 2:
            pass
        super().close()
        self.dispatcher.shutdown()

    def set_send_to(self, send_to):
        self._send_to = send_to

    def set_recv_from(self, recv_from):
        self._recv_from = recv_from
