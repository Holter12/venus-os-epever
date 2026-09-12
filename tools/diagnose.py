#!/usr/bin/env python3
"""Run this on the Cerbo to validate RS485/Modbus before enabling D-Bus."""
import argparse
import json
import sys

sys.path.insert(0, '/data/venus-os-epever/driver')
from epever_modbus import EpeverTracer


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--port', default='/dev/ttyUSB0')
    p.add_argument('--slave', type=int, default=1)
    p.add_argument('--baudrate', type=int, default=115200)
    args = p.parse_args()
    dev = EpeverTracer(args.port, args.slave, args.baudrate, timeout=2.0)
    try:
        realtime = dev.read_realtime()
        status = dev.read_status()
        energy = dev.read_energy()
        realtime.update(status)
        realtime.update(energy)
        realtime['charging_state'] = dev.decode_charging_state(status['charging_status'])
        print(json.dumps(realtime, indent=2, sort_keys=True))
        print('\nMODBUS OK')
    except Exception as exc:
        print('MODBUS FAILED:', repr(exc), file=sys.stderr)
        sys.exit(2)
    finally:
        dev.close()


if __name__ == '__main__':
    main()
