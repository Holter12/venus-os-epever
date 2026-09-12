import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / 'driver'))
from epever_modbus import crc16, build_read_holding, parse_read_holding, EpeverTracer


def response(slave, values, function=3):
    body = struct.pack('>BBB', slave, function, len(values) * 2) + struct.pack('>%dH' % len(values), *values)
    return body + struct.pack('<H', crc16(body))


class TestModbus(unittest.TestCase):
    def test_crc_known_request(self):
        frame = build_read_holding(1, 0x3100, 2)
        self.assertEqual(frame.hex(), '010331000002caf7')

    def test_response_parse(self):
        values = parse_read_holding(response(1, [1234, 5678]), 1, 2)
        self.assertEqual(values, [1234, 5678])

    def test_status_decode(self):
        self.assertEqual(EpeverTracer.decode_charging_state(0x00), 0)
        self.assertEqual(EpeverTracer.decode_charging_state(0x04), 5)
        self.assertEqual(EpeverTracer.decode_charging_state(0x08), 3)
        self.assertEqual(EpeverTracer.decode_charging_state(0x0C), 7)


if __name__ == '__main__':
    unittest.main()
