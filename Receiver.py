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

        self.to_ack_max = 1

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
                print(f"Receiver 解包异常：Package checksum error: expected {checksum}, got {parsing_check}")
                return None, None, None
            packet_raw = packet.split(b"\x00", 4)
            checksum, ack_id, send_id, length = map(Receiver.parseNumber, packet_raw[:4])
            data = packet_raw[4][:length]
            return ack_id, send_id, data
        except:
            # Package Error
            print(f"Receiver 解包异常：Package checksum error: cannot decode")
            return None, None, None

    def receive(self):
        packet, addr = self.socket.recvfrom(1440)
        ack_id, send_id, data = self.parsing(packet)

        # 坏包
        if ack_id is None:
            return

        if send_id > self.to_ack_max:
            self.to_ack_max = send_id

        print(
            f"Receiver 从 {addr} 收到包裹{send_id}，"
            f"包裹内容是{data[:10]}… {f'对方请求发送{ack_id}' if ack_id > 0 else '对方无请求'}。"
        )

        if ack_id > 0:
            self.to_send.put(ack_id)
        else:
            # TODO SEND id 是0，看data
            # 这里放特殊功能
            if data == b'gkd':
                print(f"Receiver 收到催促包")
                pend_ack = []
                for pkg_id in range(send_id, self.to_ack_max):
                    if pkg_id not in self.recv_buffer:
                        self.to_ack.put(pkg_id)
                        pend_ack.append(pkg_id)
                print(f"Receiver 新增ack {pend_ack}")

        self.recv_buffer[send_id] = data

    def get_receive_packet(self, id):
        if id in self.recv_buffer:
            return self.recv_buffer[id]
        else:
            return None

    def run(self) -> None:
        while True:
            self.receive()
