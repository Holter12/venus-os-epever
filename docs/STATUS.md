# Implementation status

## Current release target: hardware-test build

- Modbus RTU framing and CRC16 implemented.
- Tracer AN realtime block implemented.
- Status registers 0x3200/0x3201 implemented.
- Generated-energy counters 0x330C-0x3313 implemented.
- Venus OS `VeDbusService` solar-charger publisher implemented.
- Standard solar-charger paths such as `/Pv/V`, `/Pv/0/P`, `/Yield/Power`, `/Yield/User`, `/Dc/0/*`, `/State` and `/ErrorCode` are exported.
- Persistent runit service and `/data/rc.local` bootstrap are included.
- Standalone hardware diagnostic is included.
- Offline Modbus protocol tests are included.

## Hardware validation still required

The code has not been executed against a physical Cerbo GX + Tracer 2210AN in this environment. The first hardware test should therefore be read-only diagnostics, followed by D-Bus/GUI validation.

Specifically validate:

1. USB-RS485 adapter enumeration and driver support on the target Venus OS release.
2. EPEVER baud rate/address and A/B polarity.
3. Exact 2210AN register response/scaling.
4. D-Bus service discovery and GX GUI presentation.
5. VRM logging/history behaviour.
6. Reconnect after serial disconnect and controller power cycle.
7. Behaviour across a Venus OS firmware update.

No Modbus write/control operations are implemented. This is deliberate for the first hardware-validation phase.
