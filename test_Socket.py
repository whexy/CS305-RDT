from rdt import RDTSocket


def start_socket1():
    socket1 = RDTSocket(rate=None)
    socket1.bind(("127.0.0.1", 1234))
    socket1.connect(("127.0.0.1", 2345))
    # socket1.set_send_to(("127.0.0.1", 2345))
    # socket1.set_recv_from(("127.0.0.1", 2345))

    socket1.setblocking(True)

    with open("Alice.txt", "rb") as f:
        data = f.read()
    socket1.send(data * 10)


start_socket1()
