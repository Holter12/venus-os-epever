#!/bin/sh
set -eu

ROOT=/data/venus-os-epever
SERVICE=/opt/victronenergy/service/dbus-epever-tracer
REPO=https://github.com/Holter12/venus-os-epever.git

if [ "$(id -u)" != 0 ]; then echo 'Run as root' >&2; exit 1; fi

if [ -d "$ROOT/.git" ]; then
  git -C "$ROOT" pull --ff-only
else
  rm -rf "$ROOT"
  git clone "$REPO" "$ROOT"
fi

[ -f "$ROOT/epever.conf" ] || cp "$ROOT/epever.conf.example" "$ROOT/epever.conf"
chmod +x "$ROOT/install.sh" "$ROOT/uninstall.sh" "$ROOT/service/run" "$ROOT/service/log/run"

rm -f "$SERVICE"
ln -s "$ROOT/service" "$SERVICE"

if [ ! -f /data/rc.local ]; then
  printf '#!/bin/sh\nexit 0\n' > /data/rc.local
  chmod +x /data/rc.local
fi

MARK='# venus-os-epever'
if ! grep -q "$MARK" /data/rc.local; then
  sed -i "s|^exit 0$|# venus-os-epever\n[ -L '$SERVICE' ] || ln -s '$ROOT/service' '$SERVICE'\nexit 0|" /data/rc.local
fi

if [ -x /usr/bin/sv ]; then /usr/bin/sv up dbus-epever-tracer 2>/dev/null || true; fi

echo 'Installed venus-os-epever.'
echo "Config: $ROOT/epever.conf"
echo 'First hardware test:'
echo "  python3 $ROOT/tools/diagnose.py --port /dev/ttyUSB0 --slave 1 --baudrate 115200"
echo 'Service:'
echo '  svstat /service/dbus-epever-tracer'
echo 'D-Bus:'
echo '  dbus -y | grep solarcharger'
echo 'Logs:'
echo '  tail -F /data/log/dbus-epever-tracer/current | tai64nlocal'
