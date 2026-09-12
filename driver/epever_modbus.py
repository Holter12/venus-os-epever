#!/usr/bin/env python3
"""Small dependency-light Modbus RTU client for EPEVER Tracer AN."""
import struct
import time


class ModbusError(Exception):
    pass


def crc16(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def build_read_holding(slave, address, count, function=3):
    frame = struct.pack('>BBHH', slave, function, address, count)
    return frame + struct.pack('<H', crc16(frame))


def parse_read_holding(response, slave, count, function=3):
    if len(response) < 5:
        raise ModbusError('short Modbus response')
    if response[0] != slave:
        raise ModbusError('unexpected slave address')
    if response[1] & 0x80:
        raise ModbusError('Modbus exception %d' % response[2])
    if response[1] != function or response[2] != count * 2:
        raise ModbusError('unexpected Modbus response')
    end = 3 + count * 2
    received = struct.unpack('<H', response[end:end + 2])[0]
    if crc16(response[:end]) != received:
        raise ModbusError('CRC mismatch')
    return list(struct.unpack('>%dH' % count, response[3:end]))


def u32(lo, hi):
    return lo | (hi << 16)


def s16(value):
    return value - 65536 if value & 0x8000 else value


class EpeverTracer:
    def __init__(self, serial_port, slave=1, baudrate=115200, timeout=1.0):
        self.serial_port = serial_port
        self.slave = slave
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial = None

    def open(self):
        import serial
        self._serial = serial.Serial(
            self.serial_port, baudrate=self.baudrate, bytesize=8,
            parity=serial.PARITY_NONE, stopbits=1, timeout=self.timeout,
        )

    def close(self):
        if self._serial:
            self._serial.close()
            self._serial = None

    def read_registers(self, address, count, function=3):
        if not self._serial:
            self.open()
        request = build_read_holding(self.slave, address, count, function)
        self._serial.reset_input_buffer()
        self._serial.write(request)
        expected = 5 + count * 2
        deadline = time.monotonic() + self.timeout
        response = bytearray()
        while len(response) < expected and time.monotonic() < deadline:
            chunk = self._serial.read(expected - len(response))
            if chunk:
                response.extend(chunk)
        return parse_read_holding(bytes(response), self.slave, count, function)

    def read_realtime(self):
        r = self.read_registers(0x3100, 28)
        return {
            'pv_voltage': r[0] * 0.01,
            'pv_current': r[1] * 0.01,
            'pv_power': u32(r[2], r[3]) * 0.01,
            'battery_voltage': r[4] * 0.01,
            'charge_current': r[5] * 0.01,
            'charge_power': u32(r[6], r[7]) * 0.01,
            'load_voltage': r[12] * 0.01,
            'load_current': r[13] * 0.01,
            'load_power': u32(r[14], r[15]) * 0.01,
            'battery_temperature': s16(r[16]) * 0.01,
            'controller_temperature': s16(r[17]) * 0.01,
            'power_components_temperature': s16(r[18]) * 0.01,
            'battery_soc': r[26],
            'battery_status': None,
            'charging_status': None,
        }

    def read_status(self):
        r = self.read_registers(0x3200, 2, function=4)
        return {'battery_status': r[0], 'charging_status': r[1]}

    def read_energy(self):
        r = self.read_registers(0x330C, 8, function=4)
        return {
            'generated_today': u32(r[0], r[1]) * 0.01,
            'generated_month': u32(r[2], r[3]) * 0.01,
            'generated_year': u32(r[4], r[5]) * 0.01,
            'generated_total': u32(r[6], r[7]) * 0.01,
        }

    @staticmethod
    def decode_charging_state(status):
        code = (status >> 2) & 0x03
        # Venus solar-charger state: 3 bulk, 4 absorption, 5 float, 7 equalize.
        return {0: 0, 1: 5, 2: 3, 3: 7}.get(code, 2)

    @staticmethod
    def decode_mpp_mode(values):
        return 2 if values.get('pv_power', 0) > 0 else 0
