# First Cerbo GX + Tracer 2210AN validation

## Before connecting

- [ ] Cerbo GX MK2 has SSH/root access.
- [ ] EPEVER is powered normally from the battery/PV system.
- [ ] USB-RS485 adapter is isolated/appropriate for the installation.
- [ ] A/B polarity is confirmed from the adapter documentation.
- [ ] No safety-critical function depends on this driver.

## Modbus-only test

Run:

```sh
python3 /data/venus-os-epever/tools/diagnose.py --port /dev/ttyUSB0 --slave 1 --baudrate 115200
```

Record the complete output. Expected fields include PV voltage/current/power, battery voltage/current, load values, SOC, temperatures, status and generated energy counters.

If it fails:

```sh
ls -l /dev/ttyUSB* /dev/ttyACM* /dev/ttyXRUSB* 2>/dev/null
```

Then try the known controller baud/address from the installation.

## D-Bus test

After Modbus succeeds:

```sh
sv up dbus-epever-tracer
svstat /service/dbus-epever-tracer

dbus -y | grep -i epever
```

Then:

```sh
dbus -y com.victronenergy.solarcharger.epever_2210an /Connected GetValue
dbus -y com.victronenergy.solarcharger.epever_2210an /Pv/V GetValue
dbus -y com.victronenergy.solarcharger.epever_2210an /Pv/0/P GetValue
dbus -y com.victronenergy.solarcharger.epever_2210an /Yield/Power GetValue
dbus -y com.victronenergy.solarcharger.epever_2210an /Dc/0/Voltage GetValue
dbus -y com.victronenergy.solarcharger.epever_2210an /State GetValue
```

## GX GUI

- [ ] EPEVER appears in device list.
- [ ] Product name is correct.
- [ ] PV voltage/current/power agree with EPEVER local display.
- [ ] Battery voltage/current agree with EPEVER.
- [ ] State changes between no-charge, bulk/boost, float and equalization as applicable.
- [ ] Daily/total yield values are sane.

## Failure capture

```sh
svstat /service/dbus-epever-tracer
tail -n 300 /data/log/dbus-epever-tracer/current | tai64nlocal
dbus -y | grep -i -E 'epever|solarcharger'
```

Save this together with the diagnostic output and the Venus OS version (`/opt/victronenergy/version`).
