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

    def test_realtime_uses_fc04_and_reads_soc_separately(self):
        dev = EpeverTracer('/dev/null')
        calls = []

        realtime_block = [
            7355, 0, 58, 0, 1451, 4, 58, 0,
            0, 0, 0, 0, 1451, 0, 0, 0, 1895, 2432,
        ]

        def fake_read_registers(address, count, function=3):
            calls.append((address, count, function))
            if address == 0x3100:
                return realtime_block
            if address == 0x311A:
                return [100]
            raise AssertionError('unexpected register read')

        dev.read_registers = fake_read_registers
        values = dev.read_realtime()

        self.assertEqual(calls, [
            (0x3100, 18, 4),
            (0x311A, 1, 4),
        ])
        self.assertAlmostEqual(values['pv_voltage'], 73.55)
        self.assertAlmostEqual(values['pv_power'], 0.58)
        self.assertAlmostEqual(values['battery_voltage'], 14.51)
        self.assertAlmostEqual(values['battery_temperature'], 18.95)
        self.assertAlmostEqual(values['controller_temperature'], 24.32)
        self.assertEqual(values['battery_soc'], 100)
        self.assertIsNone(values['power_components_temperature'])


if __name__ == '__main__':
    unittest.main()
