from typing import Dict

from .Controller import to_send


class Receiver(object):
    def __init__(self, socket):
        self.recv_buffer: Dict[int, bytes] = {}
        self.socket = socket
        # FIXME: This is a debug feature
        self.addr = ("1.2.3.4", 53)

    @staticmethod
    def parseNumber(id: bytes) -> int:
        return int(''.join(list(map(lambda x: bin(x & 0x7F)[2:9], id))), 2)

    @staticmethod
    def parsing(packet: bytes):
        packet_raw = packet.split(b"\x00", 4)
        checksum, ack_id, send_id, length = map(Receiver.parseNumber, packet_raw[:4])
        data = packet_raw[4][:length]
        return ack_id, send_id, data

    def receive(self):
        packet = self.socket.recvfrom(1440)
        ack_id, send_id, data = self.parsing(packet)

        to_send.put(ack_id)
        self.recv_buffer[send_id] = data

        # TODO: 优化1: 对 send_id + 1 预请求

    def get_receive_packet(self, id):
        if id in self.recv_buffer:
            return self.recv_buffer[id]
        else:
            return None
