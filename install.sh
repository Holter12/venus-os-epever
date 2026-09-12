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

mkdir -p "$ROOT"
[ -f "$ROOT/epever.conf" ] || cp "$ROOT/epever.conf.example" "$ROOT/epever.conf"
chmod +x "$ROOT/service/run" "$ROOT/tools/"*.sh 2>/dev/null || true

# Venus OS documentation recommends persistent services under /opt/victronenergy/service.
# The symlink is recreated from /data/rc.local after firmware updates when necessary.
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

if [ -x /usr/bin/sv ]; then
  /usr/bin/sv up dbus-epever-tracer 2>/dev/null || true
fi

echo 'EPEVER Venus OS driver installed.'
echo "Config: $ROOT/epever.conf"
echo 'Check:  svstat /service/dbus-epever-tracer'
echo 'Check:  dbus -y | grep solarcharger'
echo 'Logs:   tail -F /data/log/dbus-epever-tracer/current | tai64nlocal'
