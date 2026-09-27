# EPEVER Tracer 2210AN wiring

## RJ45 to isolated USB-RS485

Use one twisted pair:

```text
2210AN RJ45           USB-RS485 adapter
-----------           ------------------
Pin 3 or 4  B  ----> B
Pin 5 or 6  A  ----> A
```

Leave pins 1/2 (+5 V) and 7/8 (GND) disconnected when using a properly isolated USB-RS485 adapter.

EPEVER pin definition:
- 1/2 = +5 V
- 3/4 = RS485-B
- 5/6 = RS485-A
- 7/8 = GND

For the planned Cerbo installation, the RS485 cable segment is only about 15–30 cm, so a spare Cat5e/Cat6 twisted pair is appropriate. Keep the A/B pair together and do not repurpose the other pairs for power.

## Adapter selection

Preferred characteristics:
- galvanic isolation between USB and RS485
- Linux-compatible USB serial chipset
- automatic RS485 direction control
- support for the required baud rate
- optional 120 ohm termination

The adapter does not need to power the EPEVER controller and should not be fed from the controller's RJ45 +5 V pins.

## First hardware test

1. Verify that the USB adapter enumerates on Venus OS.
2. Run `tools/diagnose.py`.
3. Confirm that the controller answers at the configured address and baud rate.
4. Only after successful Modbus reads, enable the D-Bus service.

See `docs/install.md` for the exact commands.
