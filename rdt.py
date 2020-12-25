import time

from Dispatcher import Dispatcher
from USocket import UnreliableSocket
from utils import RDTlog


class RDTSocket(UnreliableSocket):

    def __init__(self, rate=None):
        super().__init__(rate=rate)
        self._rate = rate
        self._send_to = None
        self._recv_from = None

        self.next_address = None
        self.dispatcher = Dispatcher(self)

    def accept(self) -> ('RDTSocket', (str, int)):
        conn, addr = RDTSocket(self._rate), None
        pkt = self.dispatcher.scoop(32)
        while pkt != b'SYN':
            pkt = self.dispatcher.scoop(32)
        addr = self.dispatcher.receiver.addr
        self.dispatcher.receiver.addr = None
        RDTlog(f'接受到SYN包，创建新socket，地址为{self.next_address}', highlight=True)

        conn.dispatcher.socket.bind(self.next_address)
        self.next_address = (self.next_address[0], self.next_address[1] + 1)
        conn.dispatcher.recv_footer = self.dispatcher.recv_footer
        self.dispatcher.recv_footer = 1
        conn.dispatcher.socket.set_send_to(addr)
        conn.dispatcher.socket.set_recv_from(addr)
        conn.dispatcher.receiver.addr = addr

        RDTlog(f'新socket创建完毕，发送SYNACK', highlight=True)

        conn.dispatcher.fill(b'SYNACK')
        pkt = conn.dispatcher.scoop(32)
        while pkt != b'SYNACKACK':
            pkt = conn.dispatcher.scoop(32)

        RDTlog(f'收到SYNACKACK，通信建立', highlight=True)

        return conn, addr

    def connect(self, address: (str, int)):
        self.dispatcher.socket.set_send_to(address)
        self.dispatcher.socket.set_recv_from(address)

        self.dispatcher.fill(b'SYN')
        pkt = self.dispatcher.scoop(32)
        while pkt != b'SYNACK':
            pkt = self.dispatcher.scoop(32)
        self.dispatcher.fill(b'SYNACKACK')
        RDTlog(f'发送SYNACKACK，通信建立完毕', highlight=True)


    def recv(self, bufsize: int) -> bytes:
        assert self._recv_from, "Connection not established yet. Use recvfrom instead."
        return self.dispatcher.scoop(bufsize)

    def send(self, bytes: bytes):
        assert self._send_to, "Connection not established yet. Use sendto instead."
        self.dispatcher.fill(bytes)

    def close(self):
        pass
        # time.sleep(1000)
        # super().close()
        # self.dispatcher.shutdown()

    def set_send_to(self, send_to):
        self._send_to = send_to

    def set_recv_from(self, recv_from):
        self._recv_from = recv_from

    def bind(self, address: (str, int)):
        super().bind(address)
        self.next_address = address
        self.next_address = (self.next_address[0], self.next_address[1] + 1)
