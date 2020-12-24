import time

from rdt import RDTSocket


def start_socket2():
    listenSocket = RDTSocket(rate=None)
    listenSocket.bind(("127.0.0.1", 2345))
    socket2, addr = listenSocket.accept()
    # socket2.set_send_to(("127.0.0.1", 1234))
    # socket2.set_recv_from(("127.0.0.1", 1234))
    socket2.setblocking(True)

    start = time.time()
    while True:
        data = socket2.recv(1400)
        print(data[-10:])


start_socket2()
