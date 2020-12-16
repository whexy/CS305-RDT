from queue import PriorityQueue
from time import time

from Receiver import Receiver
from Sender import Sender


class Dispatcher(object):
    def __init__(self, socket, timeout=10):
        to_ack = PriorityQueue()
        to_send = PriorityQueue()
        self.socket = socket
        self.to_ack = to_ack
        self.to_send = to_send
        self.transmitted_pkt: int = 0
        self.timeout: int = timeout
        self.receiver = Receiver(socket, to_ack, to_send)
        self.receiver.start()
        self.sender = Sender(socket, to_ack, to_send)
        self.sender.start()

        self.scoop_buffer = bytes
        self.recv_footer = 1  # 指向尚未提供的最大 id （意味着小于 footer 的数据全部被上层捞走）

    def scoop(self, bufsize: int):
        def scoop_pkg(pkg_id: int) -> bytes:
            # FIXME: DEBUG info
            print(f"{id(self.socket)}: 正在请求包裹{pkg_id}")
            # ---
            start_time = time()
            pkt: bytes = self.receiver.get_receive_packet(pkg_id)
            if pkt is None:
                self.to_ack.put(pkg_id)
            while pkt is None:
                # print(f"{id(self.socket)}: ACK列表长度为{self.to_ack.qsize()} ; SEND列表长度为{self.to_send.qsize()}")
                pkt = self.receiver.get_receive_packet(pkg_id)
                if time() - start_time > self.timeout:
                    print(f"{id(self.socket)}: 包裹{pkg_id}超时，重新请求")
                    start_time = time()
                    self.to_ack.put(pkg_id)
            return pkt

        start = time()
        ans = bytes(0)

        # 计算需要哪些包
        # FIXME: 现在只要求了下一个包, 改成按照 bufsize 算出来的值！
        cart = [self.recv_footer]
        self.recv_footer += 1

        # 阻塞拿包
        for goods in cart:
            ans += scoop_pkg(goods)

        print(f"{id(self.socket)}: 请求已经成功收到，内容是{ans}，耗时{time() - start}")
        return ans

    def fill(self, data: bytes):
        self.sender.send_buffer[self.sender.pkg_header] = data
        self.sender.pkg_header += 1

    def shutdown(self):
        self.sender.stop()
        self.receiver.stop()
