# Implementation status

## Current release target: hardware-test build

- Modbus RTU framing and CRC16 implemented.
- Tracer AN realtime telemetry implemented.
- Status registers 0x3200/0x3201 implemented.
- Generated-energy counters 0x330C-0x3313 implemented.
- Venus OS VeDbusService solar-charger publisher implemented.
- Standard solar-charger paths such as /Pv/V, /Pv/0/P, /Yield/Power, /Yield/User, /Dc/0/*, /State and /ErrorCode are exported.
- Persistent runit service and /data/rc.local bootstrap are included.
- Standalone hardware diagnostic is included.
- Offline Modbus protocol tests are included.

## Cerbo GX hardware validation

A direct read-only test has now been completed against a physical Cerbo GX MK2 + EPEVER Tracer 2210AN.

Validated serial path:

- USB-RS485 adapter: /dev/ttyUSB0
- Modbus slave: 1
- Serial: 115200 8N1
- Modbus function: FC04 (Read Input Registers) for the validated realtime registers.
- The controller replied successfully over the Cerbo USB serial path.
- During the direct test, the Venus serial-starter consumers of /dev/ttyUSB0 were stopped so the port was available to the test; fuser /dev/ttyUSB0 showed no remaining holder.

### Important protocol finding

The Tracer returned Modbus exception 2 (Illegal Data Address) when the realtime block at 0x3100 was requested with FC03.

The same hardware returned valid data with FC04. Therefore the realtime implementation now explicitly uses FC04.

The validated realtime block is:

- 0x3100..0x3111: 18 registers
- 0x311A: battery SOC, read separately with FC04
- 0x3112: power-components temperature is documented in the register map, but was not part of the validated read and is therefore not reported by the driver yet.

### Validated snapshot

These are measured values from one hardware test and are not expected constants:

| Value | Observed |
|---|---:|
| PV voltage | 73.55 V |
| PV current | 0.00 A |
| PV power | 0.58 W |
| Battery voltage | 14.51 V |
| Charge current | 0.04 A |
| Charge power | 0.58 W |
| Load voltage | 14.51 V |
| Load current | 0.00 A |
| Load power | 0.00 W |
| Battery temperature | 18.95 °C |
| Controller temperature | 24.32 °C |
| Battery SOC | 100 % |

The EPEVER response therefore confirms that the physical RS485 path, slave address, baud rate, CRC handling and realtime register scaling are working for this controller.

## Hardware items not yet fully validated

The following still require separate physical validation:

1. Status registers 0x3200/0x3201 through the complete diagnostic path.
2. Generated-energy registers 0x330C-0x3313.
3. D-Bus service discovery and GX GUI presentation.
4. VRM logging/history behaviour.
5. Reconnect after serial disconnect and controller power cycle.
6. Behaviour across a Venus OS firmware update.
7. The 0x3112 power-components temperature register.
8. Any Modbus write/control operation. None is implemented; this is deliberate.

## Wiring reference confirmed during the test

For the isolated point-to-point adapter:

- EPEVER RJ45 pin 3 or 4 = RS485-B -> adapter B.
- EPEVER RJ45 pin 5 or 6 = RS485-A -> adapter A.
- EPEVER RJ45 pins 1/2 = +5 V -> leave disconnected.
- EPEVER RJ45 pins 7/8 = GND -> not required for a genuinely isolated RS485 link.

The planned short 15–30 cm Cat5e/Cat6 twisted-pair run is appropriate for this point-to-point RS485 connection.

> Status: physical Modbus realtime communication is now validated, but the project remains experimental and the D-Bus/GUI layer still needs hardware validation.