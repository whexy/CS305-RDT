import hashlib
import math
import time
import traceback
from queue import Empty
from threading import Thread
from typing import Dict

from utils import RDTlog


class Sender(Thread):
    def __init__(self, socket, to_ack, to_send, acked, flying, rate, timeout):
        super().__init__()
        self.socket = socket
        self.to_ack = to_ack
        self.to_send = to_send
        self.acked = acked
        self.flying = flying
        self.rate = rate
        self.timeout = timeout

        self.send_buffer: Dict[int, bytes] = {}

        self.pkg_header = 1  # pkg_header 指向下一个可以填充数据的pkg_id。
        self.last_send_id = 0
        self.last_ack_id = 0
        self.last_updated_time = 0

        self.is_running = True

    @staticmethod
    def packNumber(id: int) -> bytes:
        bits = bin(id)[2:]
        bits = bits.zfill((6 + len(bits)) // 7 * 7)
        slices = [bits[i: i + 7] for i in range(0, len(bits), 7)]
        return bytes(map(lambda x: int('1' + x, 2), slices))

    @staticmethod
    def packing(ack_id: int, send_id: int, data: bytes) -> bytes:
        length = len(data)
        pieces = [Sender.packNumber(ack_id), Sender.packNumber(
            send_id), Sender.packNumber(length), data]
        product = b'\x00'.join(pieces)
        md5 = hashlib.md5()
        md5.update(product)
        checksum = int(md5.hexdigest(), 16)
        return Sender.packNumber(checksum) + b'\x00' + product

    def send(self):
        try:
            ack_id = self.to_ack.get_nowait()
            while self.to_ack.qsize() > 3:
                if ack_id == self.last_ack_id:
                    RDTlog(f"忽略重复ack：{ack_id}")
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
                    RDTlog(f"忽略重复发送pkg={send_id}")
                    send_id = self.to_send.get_nowait()
                else:
                    self.last_send_id = send_id
                    break
        except Empty:
            send_id = 0

        if ack_id == 0 and send_id == 0:
            return

        RDTlog(f"Sender准备 发送{send_id}， ack{ack_id}")

        if send_id > 0:
            data = self.send_buffer[send_id]
        else:
            data = bytes(0)

        packet = self.packing(ack_id, send_id, data)
        time.sleep(len(packet) / self.rate[0])  # Congestion Control
        self.socket.sendto(packet, self.socket._send_to)
        self.flying[send_id] = time.time()

        RDTlog(f"Sender已经 发送{send_id}，ack{ack_id}，当前速率{self.rate[0]} bytes per second")

    def run(self) -> None:
        RDTlog("发端线程启动")
        while self.is_running:
            try:
                self.send()
            except:
                RDTlog("ERR")
                traceback.print_exc()
                continue
            if time.time() - self.last_updated_time > self.timeout[0] // 2:
                updated = False
                while not self.acked.empty():
                    ack_id = self.acked.get_nowait()
                    if ack_id in self.flying:
                        self.flying.pop(ack_id)
                for pkg_id, pkg_sent_time in self.flying.items():
                    if pkg_id == 0:
                        continue
                    if time.time() - pkg_sent_time > self.timeout[0]:
                        RDTlog(f"{pkg_id} 已超时", highlight=True)
                        self.to_send.put(pkg_id)
                        if not updated:
                            RDTlog(f"Rate={self.rate[0]}时减半", highlight=True)
                            self.rate[0] = math.ceil(self.rate[0] / 2)
                            updated = True
                self.last_updated_time = time.time()

    def stop(self):
        self.is_running = False
