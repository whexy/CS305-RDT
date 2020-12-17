import hashlib
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
        try:
            ack_id = self.to_ack.get(timeout=0.5)
        except Empty:
            ack_id = 0

        try:
            send_id = self.to_send.get(timeout=0.5)
        except Empty:
            send_id = 0

        if ack_id == 0 and send_id == 0:
            return

        # FIXME: 调试
        print(f"{id(self.socket)}: Sender 正在打包 请求{ack_id}， 发送{send_id}")

        # print(f"{id(self.socket)}: 目前的send_buffer长这样：{self.send_buffer}")

        if send_id > 0:
            if send_id in self.send_buffer:
                data = self.send_buffer[send_id]
            else:
                # TODO: 这里有一个问题，如果 send_id 不在 buffer 里？ 发空包？
                print(f"{id(self.socket)}: 似乎上游没有数据可以发。这种情况还没有优化，所以我发个空包先。")
                data = bytes(0)
        else:
            data = bytes(0)

        packet = self.packing(ack_id, send_id, data)
        self.socket.sendto(packet, self.socket._send_to)

    def run(self) -> None:
        while True:
            self.send()