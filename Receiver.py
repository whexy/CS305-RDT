import hashlib
from threading import Thread
from typing import Dict, Tuple

from utils import RDTlog


class Receiver(Thread):
    def __init__(self, socket, to_ack, to_send, flying, rate):
        super().__init__()
        self.socket = socket
        self.to_ack = to_ack
        self.to_send = to_send
        self.flying = flying
        self.rate = rate
        self.addr: Tuple[str, int] or None = None

        self.recv_buffer: Dict[int, bytes] = {}

        self.is_running = True

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

        if self.addr is None:
            if data in [b'SYN', b'SYNACK']:
                self.addr = addr
                self.socket.set_send_to(addr)
            else:
                return
        elif self.addr != addr:
            return

        if ack_id > 0:
            if ack_id in self.flying:
                self.flying.pop(ack_id)
                self.rate[0] += 5120

        if send_id > 0:
            self.recv_buffer[send_id] = data
            self.to_ack.put(send_id)

        RDTlog(
            f"Receiver 从 {addr} 收到包裹{send_id}，"
            f"包裹内容是{data[:10]}… {f'对方回复{ack_id}' if ack_id > 0 else '对方无回复'}。"
        )
        # RDTlog(f"tosend size: {self.to_send.qsize()}")

    def get_receive_packet(self, id):
        if id in self.recv_buffer:
            return self.recv_buffer[id]
        else:
            return None

    def run(self) -> None:
        RDTlog("收端线程启动")
        while self.is_running:
            self.receive()

    def stop(self):
        self.is_running = False
