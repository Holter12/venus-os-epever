# venus-os-epever

Experimental Venus OS D-Bus driver for EPEVER Tracer AN MPPT solar charge controllers, initially targeting the Tracer 2210AN.

> **Status: experimental. Realtime Modbus communication is hardware-validated; D-Bus/GUI validation is still required.** This is an independent community project, not an official Victron Energy or EPEVER product.

## What it does

The project reads an EPEVER Tracer AN controller over Modbus RTU/RS485 and publishes it as a Venus OS `com.victronenergy.solarcharger.*` D-Bus service. The goal is to let the existing Cerbo GX user interface consume the controller as a Solar Charger rather than using Node-RED as the presentation layer.

## Hardware

Typical topology:

```text
EPEVER Tracer 2210AN RS485
        |
        | Modbus RTU
        v
USB-RS485 adapter
        |
        v
Cerbo GX USB
```

The physical Cerbo GX MK2 + Tracer 2210AN connection has been tested successfully at 115200 8N1, slave address 1, using Modbus FC04 for the validated realtime registers. The adapter appeared as `/dev/ttyUSB0`.

## Current hardware finding

The Tracer returned Modbus exception 2 (Illegal Data Address) when the realtime block at `0x3100` was requested with FC03. The same registers returned valid data with FC04. The driver therefore uses FC04 explicitly for realtime telemetry.

A validated snapshot included 73.55 V PV voltage, 0.58 W PV power, 14.51 V battery voltage, 18.95 °C battery temperature, 24.32 °C controller temperature and 100 % SOC. These are measurements from one test, not fixed expected values.

## Repository layout

- `driver/` - Modbus and D-Bus driver code
- `service/` - Venus OS/runit service wrapper
- `tools/` - configuration and diagnostics helpers
- `tests/` - offline protocol/register tests
- `docs/` - installation and architecture documentation

## Installation

The intended target is Venus OS on a GX device. Install under `/data/venus-os-epever` so the package does not modify the read-only Venus OS system image.

```sh
wget -O /tmp/epever-install.sh https://raw.githubusercontent.com/Holter12/venus-os-epever/main/install.sh
sh /tmp/epever-install.sh
```

After installation, configure the serial device and Modbus address with the included setup helper. See `docs/install.md`.

## Safety

RS485 is low voltage, but the charge controller is connected to an electrical power system. Follow the EPEVER and Victron documentation and applicable electrical requirements. This software must not be relied upon as a safety function.
