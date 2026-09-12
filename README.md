# venus-os-epever

Experimental Venus OS D-Bus driver for EPEVER Tracer AN MPPT solar charge controllers, initially targeting the Tracer 2210AN.

> **Status: experimental. Hardware validation required.** This is an independent community project, not an official Victron Energy or EPEVER product.

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
