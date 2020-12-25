import math
import time
from queue import PriorityQueue, Queue

from Destructor import Destructor
from Receiver import Receiver
from Sender import Sender
from utils import RDTlog


class Dispatcher(object):
    def __init__(self, socket, timeout=3, rate=102400):
        self.socket = socket
        self.to_ack = PriorityQueue()
        self.to_send = PriorityQueue()
        self.acked = Queue()
        self.flying = {}
        self.transmitted_pkt: int = 0
        self.timeout = [timeout]
        self.rate = [rate]

        # if close is invoked, if FIN received, if destructor running, if destructor end
        self.fin_status = [False, False, False, False]

        self.destructor = Destructor(self.flying, self.to_send, self.to_ack, self, self.fin_status, self.timeout)
        self.receiver = Receiver(socket, self.to_ack, self.to_send, self.acked, self.flying, self.rate, self.timeout,
                                 self.fin_status, self.destructor)
        self.receiver.start()
        self.sender = Sender(socket, self.to_ack, self.to_send, self.acked, self.flying, self.rate, self.timeout)
        self.sender.start()
        self.recv_footer = 1  # 指向尚未提供的最大 id （意味着小于 footer 的数据全部被上层捞走）

    def scoop(self, bufsize: int):
        start = time.time()
        ans = bytes(0)
        cart = [x + self.recv_footer for x in range(math.ceil(bufsize / 1400))]
        RDTlog(f"开始捞数据，准备捞{cart}", highlight=True)
        for pkg, goods in enumerate(cart):
            RDTlog(f"正在捞{goods} pkg_id={pkg}")
            data = None
            if pkg == 0:
                while data is None:
                    data = self.receiver.get_receive_packet(goods)
            else:
                data = self.receiver.get_receive_packet(goods)
            if data is None:
                RDTlog(f"{goods}没捞到，放弃")
                break
            else:
                ans += data
                self.recv_footer += 1
        RDTlog(f"捞完，耗时{time.time() - start}", highlight=True)
        return ans

    def fill(self, data: bytes):
        data_splits = [data[i:i + 1400] for i in range(0, len(data), 1400)]
        if data == b'FIN':
            RDTlog(f"发端想要发送FIN，此时拆得的包是{data_splits}", highlight=True)
        for pkg in data_splits:
            self.to_send.put(self.sender.pkg_header)
            self.sender.send_buffer[self.sender.pkg_header] = pkg
            self.sender.pkg_header += 1
        if data == b'FIN':
            RDTlog(f"此时待发送包有：{[(pkg_id, pkg_data) for pkg_id, pkg_data in self.sender.send_buffer.items() if pkg_id >= self.sender.pkg_header - 1]}")
        return self.sender.pkg_header - 1

    def shutdown(self):
        self.sender.stop()
        self.receiver.stop()
        # self.sender.join()
        # self.receiver.join()
