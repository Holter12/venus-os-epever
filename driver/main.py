#!/usr/bin/env python3
import configparser
import logging
import os
import signal
import time

from epever_modbus import EpeverTracer

LOG = logging.getLogger("epever")
RUN = True


def stop(_sig, _frame):
    global RUN
    RUN = False


def load_config(path):
    c = configparser.ConfigParser()
    c.read(path)
    return c["epever"] if "epever" in c else {}


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    cfg = load_config(os.environ.get("EPEVER_CONFIG", "/data/venus-os-epever/epever.conf"))
    port = cfg.get("port", "/dev/ttyUSB0")
    slave = int(cfg.get("slave", "1"))
    interval = max(1, int(cfg.get("poll_interval", "2")))
    LOG.info("Starting EPEVER driver on %s slave=%d", port, slave)
    dev = EpeverTracer(port, slave=slave)
    while RUN:
        try:
            values = dev.read_realtime()
            LOG.info("PV %.2f V %.2f A; battery %.2f V; charge %.2f A", values["pv_voltage"], values["pv_current"], values["battery_voltage"], values["charge_current"])
            # D-Bus publication is intentionally isolated and will be wired to
            # the Venus OS dbus-python service in the hardware integration test.
        except Exception as exc:
            LOG.warning("EPEVER read failed: %s", exc)
            dev.close()
            time.sleep(2)
        time.sleep(interval)
    dev.close()


if __name__ == "__main__":
    main()
