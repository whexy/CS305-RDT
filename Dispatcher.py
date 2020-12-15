from time import time

from Controller import to_ack
from Receiver import Receiver


class Dispatcher(object):
    def __init__(self, timeout: int, receiver: Receiver):
        self.transmitted_pkt: int = 0
        self.timeout: int = timeout
        self.receiver: Receiver = receiver

    def scoop(self, id):
        start_time = time()
        pkt: bytes = self.receiver.get_receive_packet(id)
        while pkt is None:
            pkt = self.receiver.get_receive_packet(id)
            if time() - start_time > self.timeout:
                start_time = time()
                to_ack.put(id)
        return pkt
