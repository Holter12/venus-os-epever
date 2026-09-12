#!/usr/bin/env python3
"""Venus OS D-Bus publisher for an EPEVER Tracer AN."""
import os
import sys

for p in ('/opt/victronenergy/velib_python', '/opt/victronenergy/velib_python/vedbus'):
    if p not in sys.path:
        sys.path.insert(0, p)

from vedbus import VeDbusService

SERVICE = 'com.victronenergy.solarcharger.epever_2210an'
DEVICE_INSTANCE = 30
PRODUCT_ID = 0xE221

STATE_OFF, STATE_FAULT, STATE_BULK, STATE_ABSORPTION = 0, 2, 3, 4
STATE_FLOAT, STATE_STORAGE, STATE_EQUALIZE = 5, 6, 7


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
        for path in ('/Pv/V', '/Pv/I', '/Pv/0/V', '/Pv/0/I', '/Pv/0/P', '/Pv/0/MppOperationMode',
                     '/Yield/Power', '/Yield/User', '/Yield/System', '/MppOperationMode',
                     '/Dc/0/Voltage', '/Dc/0/Current', '/Dc/0/Power', '/Dc/0/Temperature',
                     '/Load/State', '/Load/I', '/Load/Power', '/State'):
            s.add_path(path, None if path != '/State' else STATE_OFF)
        s.add_path('/History/Daily', None)
        s.add_path('/History/GeneratedToday', None)
        s.add_path('/History/GeneratedMonth', None)
        s.add_path('/History/GeneratedYear', None)
        s.add_path('/History/GeneratedTotal', None)
        s.add_path('/Battery/Soc', None)
        s.add_path('/ErrorCode', 0)
        s.add_path('/Status', 'Disconnected')

    def update(self, data, connected=True):
        s = self.service
        s['/Connected'] = 1 if connected else 0
        if not connected:
            s['/Status'] = 'Disconnected'
            return
        pairs = {
            '/Pv/V': data.get('pv_voltage'), '/Pv/I': data.get('pv_current'),
            '/Pv/0/V': data.get('pv_voltage'), '/Pv/0/I': data.get('pv_current'),
            '/Pv/0/P': data.get('pv_power'), '/Yield/Power': data.get('pv_power'),
            '/Dc/0/Voltage': data.get('battery_voltage'), '/Dc/0/Current': data.get('charge_current'),
            '/Dc/0/Power': data.get('charge_power'), '/Dc/0/Temperature': data.get('battery_temperature'),
            '/Load/I': data.get('load_current'), '/Load/Power': data.get('load_power'),
            '/Battery/Soc': data.get('battery_soc'), '/State': data.get('state'),
            '/ErrorCode': data.get('error_code', 0),
            '/Yield/User': data.get('generated_total'), '/Yield/System': data.get('generated_total'),
            '/History/GeneratedToday': data.get('generated_today'),
            '/History/GeneratedMonth': data.get('generated_month'),
            '/History/GeneratedYear': data.get('generated_year'),
            '/History/GeneratedTotal': data.get('generated_total'),
        }
        for path, value in pairs.items():
            if value is not None:
                s[path] = value
        if data.get('load_state') is not None:
            s['/Load/State'] = data['load_state']
        mpp = data.get('mpp_mode')
        if mpp is not None:
            s['/MppOperationMode'] = mpp
            s['/Pv/0/MppOperationMode'] = mpp
        s['/Status'] = 'Connected'

    def disconnect(self):
        self.service['/Connected'] = 0
        self.service['/Status'] = 'Disconnected'
