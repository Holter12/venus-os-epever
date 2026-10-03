# Hardware reference: EPEVER Tracer 2210AN

## Controller

- Model: EPEVER Tracer 2210AN
- Rated charge current: 20 A
- Rated PV charge power: 260 W @ 12 V / 520 W @ 24 V
- Communication: RS485 via RJ45

## RS485 RJ45 pinout

| RJ45 pin | Function |
|---:|---|
| 1 | +5 V |
| 2 | +5 V |
| 3 | RS485-B |
| 4 | RS485-B |
| 5 | RS485-A |
| 6 | RS485-A |
| 7 | GND |
| 8 | GND |

Pins 3/4 are RS485-B and pins 5/6 are RS485-A. For the point-to-point Cerbo connection, use only A and B at the isolated USB-RS485 adapter.

Do not connect the controller's +5 V pins to the USB-RS485 adapter. The adapter is powered from the Cerbo USB port.

### Wiring

```text
EPEVER Tracer 2210AN RJ45       Isolated USB-RS485 adapter
-------------------------       --------------------------
pin 3 or 4  RS485-B   --------  B
pin 5 or 6  RS485-A   --------  A
pin 1/2     +5 V      --------  not connected
pin 7/8     GND       --------  not required for isolated RS485
```

Use one twisted pair for A/B. The planned cable run is only about 15–30 cm alongside 12 V and 230 V wiring, so Cat5e/Cat6 is suitable for this short RS485 run.

## Modbus RTU

Hardware validation on a physical Cerbo GX MK2 + Tracer 2210AN confirmed:

- Device path: /dev/ttyUSB0
- Slave address: 1
- Baud rate: 115200
- Format: 8N1
- Realtime register block 0x3100..0x3111 responds to FC04 (Read Input Registers).
- Battery SOC at 0x311A responds to FC04.

An FC03 request to the realtime block returned Modbus exception 2 (Illegal Data Address), while the same block returned valid data with FC04. The driver therefore uses FC04 explicitly for realtime telemetry.

## Validated realtime register values

The following mapping was confirmed on the physical controller:

- 0x3100 = PV voltage, 0.01 V
- 0x3101 = PV current, 0.01 A
- 0x3102-0x3103 = PV power, 32-bit low/high, 0.01 W
- 0x3104 = battery voltage, 0.01 V
- 0x3105 = charge current, 0.01 A
- 0x3106-0x3107 = charge power, 32-bit low/high, 0.01 W
- 0x310C = load voltage, 0.01 V
- 0x310D = load current, 0.01 A
- 0x310E-0x310F = load power, 32-bit low/high, 0.01 W
- 0x3110 = battery temperature, signed, 0.01 °C
- 0x3111 = controller temperature, signed, 0.01 °C
- 0x311A = battery SOC, 1 %

Register 0x3112 (power-components temperature) is known from the register map but has not yet been hardware-validated in this project.

## Electrical notes

- RS485 is not Ethernet.
- Do not short the RJ45 +5 V and GND pins.
- Use a galvanically isolated USB-RS485 adapter between Cerbo and EPEVER.
- Do not enable an adapter's 120 ohm termination by default; this short point-to-point link should be evaluated before adding termination.
- Initial project scope is read-only telemetry. No Modbus write/control operations are implemented.

## Topology

```text
Cerbo GX MK2
    |
    | USB
    v
Isolated USB-RS485
    |
    | twisted pair A/B
    v
EPEVER Tracer 2210AN
```

## References

- EPEVER Tracer AN manual: https://www.epever.com/upload/file/2107/Tracer-AN-Manual-EN-V2.3_Software%20SV200.pdf
- EPEVER documentation portal: https://pilot.epever.com/support/documents

> Hardware-validation note: the physical RS485/realtime path is validated, but D-Bus/GUI behaviour and status/energy reads still require separate hardware validation.