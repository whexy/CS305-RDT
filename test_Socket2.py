from rdt import RDTSocket


def start_socket2():
    socket2 = RDTSocket(rate=10)
    socket2.bind(("127.0.0.1", 2345))
    socket2.set_send_to(("127.0.0.1", 1234))
    socket2.set_recv_from(("127.0.0.1", 1234))
    socket2.send("Across the great wall and we can reach every corner of the world.".encode("utf-8"))
    socket2.send(b"GoodBye")
    print(socket2.recv(3))
    msg = socket2.recv(1024)
    # if msg == b"GoodBye":
    #     socket2.close()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          

start_socket2()
