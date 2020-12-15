from unittest import TestCase

from Receiver import Receiver
from Sender import Sender


class TestUtils(TestCase):
    def test_parse_number(self):
        encoded_num = Sender.packNumber(12345)
        self.assertEqual(12345, Receiver.parseNumber(encoded_num))

    def test_packing(self):
        # Case 1: 成功解包
        expected = (1, 2, bytes([3, 4]))
        packet = Sender.packing(*expected)
        self.assertEquals(expected, Receiver.parsing(packet))

        # Case 2: 错误包裹
        packet_corrupt = bytearray(packet)
        packet_corrupt[2] = 99
        packet_corrupt = bytes(packet_corrupt)
        self.assertEquals((None,) * 3, Receiver.parsing(packet_corrupt))

        # Case 3: 无法解包
        packet_corrupt = bytes([1, 2, 5, 4, 5, 65, 6, 7, 12, 51, 45, 143, 61, 134, 64, 6])
        self.assertEquals((None,) * 3, Receiver.parsing(packet_corrupt))
