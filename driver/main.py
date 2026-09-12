#!/usr/bin/env python3
import configparser
import logging
import os
import signal
import time

from epever_modbus import EpeverTracer, ModbusError
from dbus_service import EpeverDbusService

LOG = logging.getLogger("epever")
RUN = True


def stop(_sig, _frame):
    global RUN
    RUN = False


def load_config(path):
    c = configparser.ConfigParser()
    c.read(path)
    return c['epever'] if 'epever' in c else {}


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    cfg = load_config(os.environ.get('EPEVER_CONFIG', '/data/venus-os-epever/epever.conf'))
    port = cfg.get('port', '/dev/ttyUSB0')
    slave = int(cfg.get('slave', '1'))
    interval = max(1, int(cfg.get('poll_interval', '2')))
    instance = int(cfg.get('device_instance', '30'))
    baudrate = int(cfg.get('baudrate', '115200'))

    LOG.info('Starting EPEVER Tracer AN on %s slave=%d', port, slave)
    dbus_service = EpeverDbusService(instance=instance)
    dev = EpeverTracer(port, slave=slave, baudrate=baudrate)
    failures = 0

    while RUN:
        try:
            values = dev.read_realtime()
            values['state'] = values.get('state', 3)
            values['mpp_mode'] = 2 if values.get('pv_power', 0) > 0 else 0
            dbus_service.update(values, connected=True)
            failures = 0
            LOG.info('PV %.2f V %.2f A %.0f W; battery %.2f V %.2f A',
                     values['pv_voltage'], values['pv_current'], values['pv_power'],
                     values['battery_voltage'], values['charge_current'])
        except Exception as exc:
            failures += 1
            LOG.warning('EPEVER read failed (%d): %s', failures, exc)
            dbus_service.disconnect()
            dev.close()
            time.sleep(min(10, 1 + failures))
        time.sleep(interval)

    dev.close()
    dbus_service.disconnect()


if __name__ == '__main__':
    main()
