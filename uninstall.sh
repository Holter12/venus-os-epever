#!/bin/sh
set -eu
ROOT=/data/venus-os-epever
SERVICE=/opt/victronenergy/service/dbus-epever-tracer
if [ "$(id -u)" != 0 ]; then echo 'Run as root' >&2; exit 1; fi
if [ -x /usr/bin/sv ]; then /usr/bin/sv down dbus-epever-tracer 2>/dev/null || true; fi
rm -f "$SERVICE"
if [ -f /data/rc.local ]; then
  sed -i "/# venus-os-epever/d;/dbus-epever-tracer/d;/venus-os-epever.*ln -s/d" /data/rc.local || true
fi
rm -rf "$ROOT"
echo 'EPEVER Venus OS driver removed.'
