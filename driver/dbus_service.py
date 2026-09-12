#!/usr/bin/env python3
"""Venus OS D-Bus publisher for an EPEVER Tracer AN."""
import os
import platform
import sys

# Venus OS ships velib_python with the system image.
for p in ("/opt/victronenergy/velib_python", "/opt/victronenergy/velib_python/vedbus"):
    if p not in sys.path:
        sys.path.insert(0, p)

from vedbus import VeDbusService

SERVICE = "com.victronenergy.solarcharger.epever_2210an"
DEVICE_INSTANCE = 30
PRODUCT_ID = 0xE221

STATE_OFF = 0
STATE_FAULT = 2
STATE_BULK = 3
STATE_ABSORPTION = 4
STATE_FLOAT = 5
STATE_STORAGE = 6
STATE_EQUALIZE = 7


class EpeverDbusService:
    def __init__(self, service_name=SERVICE, instance=DEVICE_INSTANCE):
        self.service_name = service_name
        self.instance = instance
        self.service = VeDbusService(service_name, register=False)
        self._add_paths()
        self.service.register()

    def _add_paths(self):
        s = self.service
        s.add_path('/Mgmt/ProcessName', os.path.abspath(__file__))
        s.add_path('/Mgmt/ProcessVersion', '1.0.0')
        s.add_path('/Mgmt/Connection', 'EPEVER Modbus RTU')
        s.add_path('/DeviceInstance', self.instance)
        s.add_path('/ProductId', PRODUCT_ID)
        s.add_path('/ProductName', 'EPEVER Tracer 2210AN')
        s.add_path('/FirmwareVersion', 'unknown')
        s.add_path('/HardwareVersion', 'unknown')
        s.add_path('/Connected', 0)
        s.add_path('/Serial', 'unknown')
        s.add_path('/CustomName', 'EPEVER Tracer 2210AN', writeable=True)
        s.add_path('/NrOfTrackers', 1)
        s.add_path('/Pv/V', None)
        s.add_path('/Pv/I', None)
        s.add_path('/Pv/0/V', None)
        s.add_path('/Pv/0/I', None)
        s.add_path('/Pv/0/P', None)
        s.add_path('/Pv/0/MppOperationMode', None)
        s.add_path('/Yield/Power', None)
        s.add_path('/Yield/User', None)
        s.add_path('/Yield/System', None)
        s.add_path('/MppOperationMode', None)
        s.add_path('/Dc/0/Voltage', None)
        s.add_path('/Dc/0/Current', None)
        s.add_path('/Dc/0/Power', None)
        s.add_path('/Dc/0/Temperature', None)
        s.add_path('/Load/State', None)
        s.add_path('/Load/I', None)
        s.add_path('/State', STATE_OFF)
        s.add_path('/ErrorCode', 0)
        s.add_path('/Status', 'Disconnected')

    def update(self, data, connected=True):
        s = self.service
        s['/Connected'] = 1 if connected else 0
        if not connected:
            s['/Status'] = 'Disconnected'
            return
        pv_v = data.get('pv_voltage')
        pv_i = data.get('pv_current')
        pv_p = data.get('pv_power')
        batt_v = data.get('battery_voltage')
        charge_i = data.get('charge_current')
        charge_p = data.get('charge_power')
        state = data.get('state', STATE_BULK)
        error = data.get('error_code', 0)
        for path, value in (
            ('/Pv/V', pv_v), ('/Pv/I', pv_i), ('/Pv/0/V', pv_v),
            ('/Pv/0/I', pv_i), ('/Pv/0/P', pv_p), ('/Yield/Power', pv_p),
            ('/Dc/0/Voltage', batt_v), ('/Dc/0/Current', charge_i),
            ('/Dc/0/Power', charge_p), ('/Dc/0/Temperature', data.get('controller_temperature')),
            ('/Load/I', data.get('load_current')), ('/Load/State', data.get('load_state')),
            ('/State', state), ('/ErrorCode', error),
        ):
            if value is not None:
                s[path] = value
        # Venus defines 2 as current/voltage limited and 1 as MPPT active in
        # the aggregate MppOperationMode path. We expose the best available
        # information until controller status decoding is validated on hardware.
        mpp = data.get('mpp_mode')
        if mpp is not None:
            s['/MppOperationMode'] = mpp
            s['/Pv/0/MppOperationMode'] = mpp
        s['/Status'] = 'Connected'

    def disconnect(self):
        self.service['/Connected'] = 0
        self.service['/Status'] = 'Disconnected'
