#!/usr/bin/env python3
import configparser
import logging
import os
import signal
import time

from epever_modbus import EpeverTracer
from dbus_service import EpeverDbusService

LOG = logging.getLogger('epever')
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
    stats_interval = max(10, int(cfg.get('stats_interval', '60')))
    instance = int(cfg.get('device_instance', '30'))
    baudrate = int(cfg.get('baudrate', '115200'))

    LOG.info('Starting EPEVER Tracer AN on %s slave=%d baud=%d', port, slave, baudrate)
    dbus_service = EpeverDbusService(instance=instance)
    dev = EpeverTracer(port, slave=slave, baudrate=baudrate)
    failures = 0
    last_stats = 0

    while RUN:
        try:
            values = dev.read_realtime()
            status = dev.read_status()
            values.update(status)
            values['state'] = dev.decode_charging_state(status['charging_status'])
            values['mpp_mode'] = dev.decode_mpp_mode(values)
            if time.monotonic() - last_stats >= stats_interval:
                values.update(dev.read_energy())
                last_stats = time.monotonic()
            dbus_service.update(values, connected=True)
            failures = 0
            LOG.info('PV %.2f V %.2f A %.2f W; battery %.2f V %.2f A; SOC %d%%',
                     values['pv_voltage'], values['pv_current'], values['pv_power'],
                     values['battery_voltage'], values['charge_current'], values['battery_soc'])
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
