#!/usr/bin/env python3
"""Publish EPEVER values as a Venus OS solar charger D-Bus service.

This module intentionally keeps the Venus-specific layer small. The standard
D-Bus paths are the contract consumed by GX/VRM components.
"""
import logging
import time

try:
    import dbus
    import dbus.service
except ImportError:  # allows protocol tests on a normal workstation
    dbus = None

LOG = logging.getLogger("epever-dbus")
SERVICE = "com.victronenergy.solarcharger.epever_2210an"


class EpeverDbusService:
    def __init__(self, bus, instance=30):
        if dbus is None:
            raise RuntimeError("dbus-python is required on Venus OS")
        self.bus = bus
        self.instance = instance
        self.service_name = SERVICE
        self.root = None
        self.values = {}

    def set_value(self, path, value):
        self.values[path] = value
        # Actual dbus-python service objects are attached in the Venus OS
        # runtime wrapper. Keeping this cache makes the driver testable.

    def update_realtime(self, data):
        mapping = {
            "/Pv/V": data.get("pv_voltage"),
            "/Pv/I": data.get("pv_current"),
            "/Dc/0/Voltage": data.get("battery_voltage"),
            "/Dc/0/Current": data.get("charge_current"),
            "/Dc/0/Power": data.get("charge_power"),
            "/Ac/Power": 0,
            "/Load/V": data.get("load_voltage"),
            "/Load/I": data.get("load_current"),
            "/Load/Power": data.get("load_power"),
            "/Temperature/Charge": data.get("controller_temperature"),
            "/Temperature/Battery": data.get("battery_temperature"),
        }
        for path, value in mapping.items():
            if value is not None:
                self.set_value(path, value)


def make_metadata(service, product_name="EPEVER Tracer 2210AN"):
    return {
        "/ProductName": product_name,
        "/FirmwareVersion": "unknown",
        "/HardwareVersion": "unknown",
        "/Serial": "unknown",
        "/DeviceInstance": service.instance,
        "/Connected": 1,
        "/State": 3,
        "/ErrorCode": 0,
        "/Status": "EPEVER Tracer AN",
    }
