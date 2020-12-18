import hashlib
import time
from queue import Empty
from threading import Thread
from typing import Dict


class Sender(Thread):
    def __init__(self, socket, to_ack, to_send):
        super().__init__()
        self.send_buffer: Dict[int, bytes] = {}
        self.socket = socket
        self.to_ack = to_ack
        self.to_send = to_send
        self.pkg_header = 1  # pkg_header 指向下一个可以填充数据的pkg_id。
        self.running = True

        self.last_send_id = 0
        self.last_ack_id = 0

        self.last_urged = time.time()

    @staticmethod
    def packNumber(id: int) -> bytes:
        bits = bin(id)[2:]
        bits = bits.zfill((6 + len(bits)) // 7 * 7)
        slices = [bits[i: i + 7] for i in range(0, len(bits), 7)]
        return bytes(map(lambda x: int('1' + x, 2), slices))

    @staticmethod
    def packing(ack_id: int, send_id: int, data: bytes) -> bytes:
        length = len(data)
        pieces = [Sender.packNumber(ack_id), Sender.packNumber(send_id), Sender.packNumber(length), data]
        product = b'\x00'.join(pieces)
        md5 = hashlib.md5()
        md5.update(product)
        checksum = int(md5.hexdigest(), 16)
        return Sender.packNumber(checksum) + b'\x00' + product

    def send(self):

        # FIXME: 实验功能 发催促包
        if self.to_send.qsize() < 2:
            if time.time() - self.last_urged > 10:
                packet = self.packing(0, 0, b'gkd')
                self.socket.sendto(packet, self.socket._send_to)
                self.last_urged = time.time()

        try:
            ack_id = self.to_ack.get_nowait()
            while self.to_ack.qsize() > 3:
                if ack_id == self.last_ack_id:
                    print(f"忽略ack={ack_id}的重复请求")
                    ack_id = self.to_send.get_nowait()
                else:
                    self.last_ack_id = ack_id
                    break
        except Empty:
            ack_id = 0

        try:
            send_id = self.to_send.get_nowait()
            while self.to_send.qsize() > 3:
                if send_id == self.last_send_id:
                    print(f"忽略pkg={send_id}的重复请求")
                    send_id = self.to_send.get_nowait()
                else:
                    self.last_send_id = send_id
                    break
        except Empty:
            send_id = 0

        if ack_id == 0 and send_id == 0:
            return

        # FIXME: 调试
        print(
            f"{self.log_time()} Sender 正在打包 请求{ack_id}， 发送{send_id}")
        if send_id > 0:
            if send_id in self.send_buffer:
                data = self.send_buffer[send_id]
            else:
                data = bytes(0)
        else:
            data = bytes(0)

        packet = self.packing(ack_id, send_id, data)
        print(f"{self.log_time()} Sender 打包完成")
        self.socket.sendto(packet, self.socket._send_to)
        print(f"{self.log_time()} Sender 已经发出")

    def log_time(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def run(self) -> None:
        while True:
            time.sleep(0.05)
            self.send()
