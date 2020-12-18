import time

from rdt import RDTSocket


def start_socket2():
    socket2 = RDTSocket(rate=None)
    socket2.bind(("127.0.0.1", 2345))
    socket2.set_send_to(("127.0.0.1", 1234))
    socket2.set_recv_from(("127.0.0.1", 1234))
    start = time.time()
    socket2.setblocking(True)

    while True:
        data = socket2.recv(1400)
        print(data[-10:])


start_socket2()
