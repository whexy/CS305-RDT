import heapq
import time
from threading import Thread

from USocket import UnreliableSocket


class RDTSocket(UnreliableSocket):
    """
    The functions with which you are to build your RDT.
    -   recvfrom(bufsize)->bytes, addr
    -   sendto(bytes, address)
    -   bind(address)

    You can set the mode of the socket.
    -   settimeout(timeout)
    -   setblocking(flag)
    By default, a socket is created in the blocking mode. 
    https://docs.python.org/3/library/socket.html#socket-timeouts

    """

    def __init__(self, rate=None, debug=True):
        super().__init__(rate=rate)
        self._rate = rate
        self._send_to = None
        self._recv_from = None
        self.debug = debug
        self.thread = RDTThread(self)

    def accept(self) -> ('RDTSocket', (str, int)):
        """
        Accept a connection. The socket must be bound to an address and listening for 
        connections. The return value is a pair (conn, address) where conn is a new 
        socket object usable to send and receive data on the connection, and address 
        is the address bound to the socket on the other end of the connection.

        This function should be blocking. 
        """
        conn, addr = RDTSocket(self._rate), None
        return conn, addr

    def connect(self, address: (str, int)):
        """
        Connect to a remote socket at address.
        Corresponds to the process of establishing a connection on the client side.
        """
        raise NotImplementedError()

    def recv(self, bufsize: int) -> bytes:
        """
        Receive data from the socket. 
        The return value is a bytes object representing the data received. 
        The maximum amount of data to be received at once is specified by bufsize. 
        
        Note that ONLY data send by the peer should be accepted.
        In other words, if someone else sends data to you from another address,
        it MUST NOT affect the data returned by this function.
        """
        assert self._recv_from, "Connection not established yet. Use recvfrom instead."
        data = self.thread.scoop_data()
        return data

    def send(self, bytes: bytes):
        """
        Send data to the socket. 
        The socket must be connected to a remote socket, i.e. self._send_to must not be none.
        """
        assert self._send_to, "Connection not established yet. Use sendto instead."
        self.thread.pend_data(bytes)

    def close(self):
        """
        Finish the connection and release resources. For simplicity, assume that
        after a socket is closed, neither futher sends nor receives are allowed.
        """
        super().close()

    def set_send_to(self, send_to):
        self._send_to = send_to

    def set_recv_from(self, recv_from):
        self._recv_from = recv_from


class RDTThread(Thread):
    def __init__(self, socket: UnreliableSocket):
        super().__init__()
        self.socket = socket
        self.time_thread = RDTTimeThread()

        self.ack_list = []
        self.pkg_list = []

        self.send_buffer = {}
        self.recv_buffer = {}

        self.max_ack = 0
        self.max_pkg = 0
        self.next_scooped_pkg = 0

    def run(self):
        pass

    @staticmethod
    def check(checksum, segment):
        # TODO: check sum
        return True

    @staticmethod
    def makeChecksum(segment):
        # TODO: make checksum
        return b'\x11' * 14 + b'\x00' + segment

    def RDT_recv(self):
        segment = self.socket.recvfrom(1400)

        checksum, ack_id, pkg_id, length, data = segment.split(b'\x00', 4)

        if self.check(checksum, segment):
            # TODO: self.time_thread.remove_pkg(pkg_id)

            # 1). pending to ack next package if the package is not re-transmitted
            if pkg_id > self.max_ack:
                self.max_ack += 1
                self.ack_list.append(self.max_ack)

            # 2). pending to send the ack-ed file
            self.pkg_list.append(ack_id)

        else:
            # Drop the packet! Do not trust the segment.
            pass

        self.recv_buffer[pkg_id] = data

    def RDT_send(self, addr):
        ack_id = self.ack_list.pop(0)
        pkg_id = self.pkg_list.pop(0)
        data = self.send_buffer[pkg_id]
        length = len(data)

        data = self.makeChecksum(b'\x00'.join([ack_id, pkg_id, length, data]))
        self.socket.sendto(data, addr)

    def pend_data(self, data: bytes):
        self.send_buffer[self.max_pkg] = data
        self.pkg_list.append(self.max_pkg)
        self.max_pkg += 1

    def scoop_data(self):
        # if recv_buffer has element in order
        if self.next_scooped_pkg in self.recv_buffer:
            data = self.recv_buffer[self.next_scooped_pkg]
        else:
            # TODO: Should block here or raise an error
            raise Exception("Pkt has not been recv-ed yet.")
        self.next_scooped_pkg += 1


class RDTTimeThread(Thread):
    def __init__(self, timeout=5):
        super().__init__()
        self.pkg_timeout = {}
        self.timeout = timeout

    def put_pkg(self, pkg_id):
        self.pkg_timeout[pkg_id] = time.time()

    def remove_pkg(self, pkg_id):
        if pkg_id in self.pkg_timeout:
            del self.pkg_timeout[pkg_id]
        else:
            raise Exception("What are you doing?")

    def run(self):
        # WRONG! while true doesn't work. While `while true`, we cannot delete anything from `pkg_timeout`.
        while True:
            for pkg_id, start_time in self.pkg_timeout.items():
                if time.time() - start_time > self.timeout:
                    # TODO: Queue require retransmit, set ack number
                    pass
            time.sleep(0.1)


class PriorityQueue(object):
    def __init__(self):
        self.pq = []

    def push(self, element):
        heapq.heappush(self.pq, element)

    def pop(self):
        return heapq.heappop(self.pq)
