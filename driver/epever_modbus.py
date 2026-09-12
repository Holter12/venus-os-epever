#!/usr/bin/env python3
"""Minimal dependency-free Modbus RTU client for EPEVER Tracer AN.

Designed to run on Venus OS without installing third-party Python packages.
The register addresses are kept in one place so they can be validated against
specific Tracer firmware during hardware testing.
"""
import struct
import time


class ModbusError(Exception):
    pass


def crc16(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def build_read_holding(slave, address, count):
    frame = struct.pack(">BBHH", slave, 3, address, count)
    c = crc16(frame)
    return frame + struct.pack("<H", c)


def parse_read_holding(response, slave, count):
    if len(response) < 5:
        raise ModbusError("short Modbus response")
    if response[0] != slave:
        raise ModbusError("unexpected slave address")
    if response[1] & 0x80:
        raise ModbusError("Modbus exception %d" % response[2])
    if response[1] != 3 or response[2] != count * 2:
        raise ModbusError("unexpected Modbus response")
    payload = response[3:3 + count * 2]
    received = struct.unpack("<H", response[3 + count * 2:5 + count * 2])[0]
    if crc16(response[:3 + count * 2]) != received:
        raise ModbusError("CRC mismatch")
    return list(struct.unpack(">%dH" % count, payload))


# Tracer AN realtime values. These are deliberately isolated for validation.
# EPEVER uses 16-bit registers with common 0.01 V / 0.01 A scaling.
REG = {
    "pv_voltage": (0x3100, 0.01),
    "pv_current": (0x3101, 0.01),
    "pv_power_l": (0x3102, 1.0),
    "pv_power_h": (0x3103, 1.0),
    "battery_voltage": (0x3104, 0.01),
    "charge_current": (0x3105, 0.01),
    "charge_power_l": (0x3106, 1.0),
    "charge_power_h": (0x3107, 1.0),
    "load_voltage": (0x310C, 0.01),
    "load_current": (0x310D, 0.01),
    "load_power_l": (0x310E, 1.0),
    "load_power_h": (0x310F, 1.0),
    "controller_temperature": (0x3110, 1.0),
    "battery_temperature": (0x3111, 1.0),
}


def u32(lo, hi):
    return lo | (hi << 16)


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
            parity=serial.PARITY_NONE, stopbits=1, timeout=self.timeout)

    def close(self):
        if self._serial:
            self._serial.close()
            self._serial = None

    def read_registers(self, address, count):
        if not self._serial:
            self.open()
        request = build_read_holding(self.slave, address, count)
        self._serial.reset_input_buffer()
        self._serial.write(request)
        expected = 5 + count * 2
        deadline = time.monotonic() + self.timeout
        response = bytearray()
        while len(response) < expected and time.monotonic() < deadline:
            chunk = self._serial.read(expected - len(response))
            if chunk:
                response.extend(chunk)
        return parse_read_holding(bytes(response), self.slave, count)

    def read_realtime(self):
        # 0x3100..0x3111 is contiguous on the Tracer AN realtime block.
        r = self.read_registers(0x3100, 18)
        return {
            "pv_voltage": r[0] * 0.01,
            "pv_current": r[1] * 0.01,
            "pv_power": u32(r[2], r[3]),
            "battery_voltage": r[4] * 0.01,
            "charge_current": r[5] * 0.01,
            "charge_power": u32(r[6], r[7]),
            "load_voltage": r[12] * 0.01,
            "load_current": r[13] * 0.01,
            "load_power": u32(r[14], r[15]),
            "controller_temperature": r[16],
            "battery_temperature": r[17],
        }
