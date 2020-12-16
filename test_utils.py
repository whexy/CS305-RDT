from multiprocessing import Process
from unittest import TestCase

from Receiver import Receiver
from Sender import Sender
from rdt import RDTSocket


class TestUtils(TestCase):
    def test_parse_number(self):
        encoded_num = Sender.packNumber(12345)
        self.assertEqual(12345, Receiver.parseNumber(encoded_num))


class TestPacking(TestCase):
    def test_normal(self):
        # Case 1: 成功解包
        expected = (1, 2, bytes([3, 4]))
        packet = Sender.packing(*expected)
        self.assertEquals(expected, Receiver.parsing(packet))

    def test_error(self):
        # Case 2: 错误包裹
        expected = (1, 2, bytes([3, 4]))
        packet = Sender.packing(*expected)
        packet_corrupt = bytearray(packet)
        packet_corrupt[2] = 99
        packet_corrupt = bytes(packet_corrupt)
        self.assertEquals((None,) * 3, Receiver.parsing(packet_corrupt))

    def test_ignore(self):
        # Case 3: 无法解包
        packet_corrupt = bytes([1, 2, 5, 4, 5, 65, 6, 7, 12, 51, 45, 143, 61, 134, 64, 6])
        self.assertEquals((None,) * 3, Receiver.parsing(packet_corrupt))


class TestRDTSocket(TestCase):

    def test_settle_up(self):
        def start_socket1():
            socket1 = RDTSocket(rate=10)
            socket1.bind(("127.0.0.1", 1234))
            socket1.set_send_to(("127.0.0.1", 2345))
            socket1.set_recv_from(("127.0.0.1", 2345))
            socket1.send("Hello World".encode("utf-8"))
            socket1.send(b"GoodBye")
            print(socket1.recv(1024))
            msg = socket1.recv(1024)
            # if msg == b"GoodBye":
            #     socket1.close()

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

        p = Process(target=start_socket1)
        p.start()

        p = Process(target=start_socket2)
        p.start()