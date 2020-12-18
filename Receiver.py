import hashlib
import time
from threading import Thread
from typing import Dict

from utils import RDTlog


class Receiver(Thread):
    def __init__(self, socket, to_ack, to_send, flying):
        super().__init__()
        self.socket = socket
        self.to_ack = to_ack
        self.to_send = to_send
        self.flying = flying

        self.recv_buffer: Dict[int, bytes] = {}

    @staticmethod
    def parseNumber(id: bytes) -> int:
        return int(''.join(list(map(lambda x: bin(x & 0x7F)[2:9].zfill(7), id))), 2)

    @staticmethod
    def parsing(packet: bytes):
        try:
            checksum, product = packet.split(b"\x00", 1)
            checksum = Receiver.parseNumber(checksum)
            md5 = hashlib.md5()
            md5.update(product)
            parsing_check = int(md5.hexdigest(), 16)
            if checksum != parsing_check:
                RDTlog(f"Receiver 解包异常：Package checksum error: expected {checksum}, got {parsing_check}",
                       highlight=True)
                return None, None, None
            packet_raw = packet.split(b"\x00", 4)
            checksum, ack_id, send_id, length = map(Receiver.parseNumber, packet_raw[:4])
            data = packet_raw[4][:length]
            return ack_id, send_id, data
        except:
            # Package Error
            RDTlog(f"Receiver 解包异常：Package checksum error: cannot decode", highlight=True)
            return None, None, None

    def receive(self):
        packet, addr = self.socket.recvfrom(1440)
        ack_id, send_id, data = self.parsing(packet)

        # 坏包
        if ack_id is None or send_id is None:
            return

        if ack_id > 0:
            self.flying.pop(ack_id)

        if send_id > 0:
            self.recv_buffer[send_id] = data
            self.to_ack.put(send_id)

        RDTlog(
            f"Receiver 从 {addr} 收到包裹{send_id}，"
            f"包裹内容是{data[:10]}… {f'对方回复{ack_id}' if ack_id > 0 else '对方无回复'}。"
        )

    def get_receive_packet(self, id):
        if id in self.recv_buffer:
            return self.recv_buffer[id]
        else:
            return None

    def run(self) -> None:
        while True:
            self.receive()
