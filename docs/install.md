# Installation and first hardware test

## 1. Hardware

Use an RS485 adapter that exposes a normal Linux serial device on the Cerbo, preferably an isolated industrial USB-RS485 adapter. Wire the EPEVER RS485 A/B according to the EPEVER manual and the adapter manufacturer's labeling.

The Tracer AN Modbus interface is commonly 115200, 8N1, address 1. Some installations use another baud rate/address, so these are configurable.

## 2. SSH to the Cerbo

Enable SSH/root access using the normal Venus OS procedure. Then connect as root.

## 3. Install

```sh
wget -O /tmp/epever-install.sh https://raw.githubusercontent.com/Holter12/venus-os-epever/main/install.sh
sh /tmp/epever-install.sh
```

## 4. Find the USB serial device

```sh
ls -l /dev/ttyUSB* /dev/ttyACM* /dev/ttyXRUSB* 2>/dev/null
```

Set the result in `/data/venus-os-epever/epever.conf`.

## 5. Test Modbus before starting the D-Bus service

```sh
python3 /data/venus-os-epever/tools/diagnose.py --port /dev/ttyUSB0 --slave 1 --baudrate 115200
```

A successful test prints realtime values, status, energy counters and `MODBUS OK`.

**Do not continue to the GUI test if this fails.** Fix serial wiring, port, address or baud rate first.

## 6. Enable the service

```sh
sv up dbus-epever-tracer
svstat /service/dbus-epever-tracer
tail -F /data/log/dbus-epever-tracer/current | tai64nlocal
```

## 7. Verify D-Bus

```sh
dbus -y | grep -i solarcharger
dbus -y com.victronenergy.solarcharger.epever_2210an /Connected GetValue
dbus -y com.victronenergy.solarcharger.epever_2210an /Pv/V GetValue
dbus -y com.victronenergy.solarcharger.epever_2210an /Yield/Power GetValue
dbus -y com.victronenergy.solarcharger.epever_2210an /Dc/0/Voltage GetValue
```

The Venus D-Bus API defines the standard solar-charger paths including `/Pv/V`, `/Yield/Power`, `/Yield/User`, `/State`, `/ErrorCode` and `/Load/I`. The driver follows that API rather than inventing a parallel Node-RED data model.

## 8. GUI validation

After D-Bus is healthy, check the GX device list and Solar Chargers page. The device should appear as `EPEVER Tracer 2210AN`.

## 9. Collect diagnostics for development

If anything is wrong, collect:

```sh
cat /data/venus-os-epever/epever.conf
svstat /service/dbus-epever-tracer
ps | grep -i epever
dbus -y | grep -i epever
tail -n 200 /data/log/dbus-epever-tracer/current | tai64nlocal
```

Also run the standalone diagnostic and save its output.

## Important

The driver is experimental. Do not use it for protection, shutdown or safety-critical control. Reading Modbus telemetry is the first validation target; write/control operations are intentionally not implemented in this version.
