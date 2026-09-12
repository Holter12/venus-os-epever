# Implementation status

## Current

- Repository created and initial driver architecture committed.
- Modbus RTU framing, CRC16 and realtime register decoding are implemented.
- Venus OS solar-charger D-Bus abstraction is present.
- Service wrapper and configuration example are present.

## Not yet claimed as production-ready

The current commit is **not yet a complete hardware-validated Venus OS package**. In particular, the following must be completed and tested on an actual Cerbo GX running Venus OS:

1. Bind the D-Bus paths to the exact Venus OS `dbus.service` / `VeDbusService` API used by the target Venus OS release.
2. Validate the exact Tracer 2210AN register map and scaling against the controller firmware.
3. Validate device discovery, GUI presentation, device instance and VRM logging.
4. Add Venus OS service installation using the supported runit layout.
5. Add history/yield paths and state/error mapping where supported by the controller.
6. Test reconnect behaviour after USB/RS485 removal and controller power cycling.

The repository intentionally does not pretend these hardware-dependent checks have already passed.
