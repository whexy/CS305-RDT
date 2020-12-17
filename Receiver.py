import hashlib
from threading import Thread
from typing import Dict


class Receiver(Thread):
    def __init__(self, socket, to_ack, to_send):
        super().__init__()
        self.recv_buffer: Dict[int, bytes] = {}
        self.socket = socket
        self.to_ack = to_ack
        self.to_send = to_send
        self.running = True

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
                print(f"Package checksum error: expected {checksum}, got {parsing_check}")
                return None, None, None
            packet_raw = packet.split(b"\x00", 4)
            checksum, ack_id, send_id, length = map(Receiver.parseNumber, packet_raw[:4])
            data = packet_raw[4][:length]
            return ack_id, send_id, data
        except:
            # Package Error
            print(f"Package checksum error: cannot decode")
            return None, None, None

    def receive(self):
        try:
            packet, addr = self.socket.recvfrom(1440)
        except:
            return
        ack_id, send_id, data = self.parsing(packet)

        if ack_id is None:
            # 坏包
            return

        print(
            f"{id(self.socket)}: Receiver 从 {addr} 收到包裹{send_id}，"
            f"包裹内容是{data}，{f'对方顺便请求我方发送{ack_id}' if ack_id > 0 else '对方无请求'}。"
        )

        if ack_id > 0:
            self.to_send.put(ack_id)

        self.recv_buffer[send_id] = data
        # TODO: 优化1: 对 send_id + 1 预请求

    def get_receive_packet(self, id):
        if id in self.recv_buffer:
            return self.recv_buffer[id]
        else:
            return None

    def run(self) -> None:
        while True:
            self.receive()