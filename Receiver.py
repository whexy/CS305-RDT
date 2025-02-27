import hashlib
import time
from threading import Thread
from typing import Dict, Tuple

from utils import RDTlog


class Receiver(Thread):
    def __init__(self, socket, to_ack, to_send, acked, flying, wnd_size, ssthresh, timeout, fin_status, destructor,
                 util):
        super().__init__()
        self.socket = socket
        self.to_ack = to_ack
        self.to_send = to_send
        self.acked = acked
        self.flying = flying
        self.wnd_size = wnd_size
        self.ssthresh = ssthresh
        self.timeout = timeout
        self.estimated_rtt = self.timeout[0]
        self.dev_rtt = self.timeout[0]
        self.fin_status = fin_status
        self.destructor = destructor
        self.addr: Tuple[str, int] or None = None

        self.util = util

        self.recv_buffer: Dict[int, bytes] = {}
        self.magic_set = set()

        self.is_running = True
        self.alpha = 0.125
        self.beta = 0.25

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

    def receive(self) -> bool:
        while True:
            if not self.is_running:
                return False
            try:
                packet, addr = self.socket.recvfrom(1440)
                break
            except:
                pass
        ack_id, send_id, data = self.parsing(packet)
        has_fin = False

        # 坏包
        if ack_id is None or send_id is None:
            return False

        if self.addr is None:
            if data in [b'SYN', b'SYNACK']:
                self.addr = addr
                self.socket.set_send_to(addr)
            else:
                return False
        elif self.addr != addr:
            return False

        if data == b'FIN':
            self.fin_status[1] = True
            if not self.fin_status[0]:
                has_fin = True

        if ack_id > 0:
            if ack_id in self.flying:
                sample_rtt = time.time() - self.flying[ack_id]
                self.dev_rtt = (1 - self.beta) * self.dev_rtt + self.beta * abs(sample_rtt - self.estimated_rtt)
                self.estimated_rtt = (1 - self.alpha) * self.estimated_rtt + self.alpha * sample_rtt
                self.timeout[0] = self.estimated_rtt + 4 * self.dev_rtt
                self.util.update("timeout", self.timeout[0])
                self.acked.put(ack_id)

                # Congestion Control
                if self.wnd_size[0] <= self.ssthresh[0]:
                    self.wnd_size[0] += 1
                else:
                    self.wnd_size[0] += 1 / self.wnd_size[0]
                self.util.update("wnd_size", int(self.wnd_size[0]))

        if send_id > 0:
            if data == b'FIN':
                self.recv_buffer[send_id] = bytes(0)

            else:
                self.recv_buffer[send_id] = data
            self.to_ack.put(send_id)

            RDTlog(
                f"Receiver 从 {addr} 收到包裹{send_id}，"
                f"包裹内容是{data[:10]}… {f'对方回复{ack_id}' if ack_id > 0 else '对方无回复'}。"
            )

        elif ack_id != 0:
            RDTlog(
                f"Receiver 从 {addr} 收到纯回复{ack_id}。"
            )

        # RDTlog(f"tosend size: {self.to_send.qsize()}")
        return has_fin

    def get_receive_packet(self, id):
        if id in self.recv_buffer:
            return self.recv_buffer[id]
        else:
            return None

    def run(self) -> None:
        RDTlog("收端线程启动")
        self.socket.setblocking(False)
        destructor_running = False
        while self.is_running:
            if self.receive():  # Got FIN
                RDTlog("发端收到FIN，准备启动关闭流程", highlight=True)
                if not destructor_running:
                    destructor_running = True
                    RDTlog("发端即将启动关闭流程", highlight=True)
                    self.destructor.start()
        RDTlog("收端线程关闭", highlight=True)

    def stop(self):
        self.is_running = False
        RDTlog("调用收端关闭接口", highlight=True)
