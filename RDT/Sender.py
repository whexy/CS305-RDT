import hashlib
from typing import Dict

from Controller import to_ack, to_send


class Sender(object):
    def __init__(self, socket):
        self.send_buffer: Dict[int, bytes] = {}
        self.socket = socket
        # FIXME: This is a debug feature
        self.addr = ("1.2.3.4", 53)

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
        ack_id = to_ack.get()
        send_id = to_send.get()
        data = self.send_buffer[send_id]
        # TODO: 这里有一个问题，如果 send_id 不在 buffer 里？ 发空包？
        packet = self.packing(ack_id, send_id, data)
        self.socket.sendto(packet, self.addr)
