import threading
import time
from queue import Queue
from socket import socket, AF_INET, SOCK_DGRAM, inet_aton, inet_ntoa


def bytes_to_addr(bytes):
    return inet_ntoa(bytes[:4]), int.from_bytes(bytes[4:8], 'big')


def addr_to_bytes(addr):
    return inet_aton(addr[0]) + addr[1].to_bytes(4, 'big')


server_addr = ('127.0.0.1', 12345)


class Worker(threading.Thread):
    def __init__(self, rate=None):
        super(Worker, self).__init__()
        self.buffer = 0
        self.queue = Queue()
        self.rate = rate

    def run(self):
        while True:
            data, to = self.queue.get()
            if self.rate:
                time.sleep(len(seg) / self.rate)
            self.buffer -= len(data)
            server.sendto(data, to)


if __name__ == '__main__':
    server = socket(AF_INET, SOCK_DGRAM)
    server.bind(server_addr)
    worker = Worker(20480)
    worker.start()
    while True:
        try:
            seg, client_addr = server.recvfrom(4096)
        except ConnectionResetError:
            seg, client_addr = server.recvfrom(4096)
        if worker.buffer > 48000:
            print('discard')
            continue

        to = bytes_to_addr(seg[:8])
        print(client_addr, to, worker.buffer)  # observe tht traffic
        worker.buffer += len(seg)
        worker.queue.put((addr_to_bytes(client_addr) + seg[8:], to))
