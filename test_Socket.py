from rdt import RDTSocket


def start_socket1():
    socket1 = RDTSocket(rate=5)
    socket1.bind(("127.0.0.1", 1234))
    socket1.set_send_to(("127.0.0.1", 2345))
    socket1.set_recv_from(("127.0.0.1", 2345))

    socket1.setblocking(False)
    socket1.settimeout(1)
    socket1.send("Hello World".encode("utf-8"))
    socket1.send(b"GoodBye")
    print(socket1.recv(1024))
    msg = socket1.recv(1024)
    # if msg == b"GoodBye":
    #     socket1.close()

start_socket1()