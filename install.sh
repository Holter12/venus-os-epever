#!/bin/sh
set -eu

ROOT=/data/venus-os-epever
SERVICE=/opt/victronenergy/service/dbus-epever-tracer
ARCHIVE_URL=https://github.com/Holter12/venus-os-epever/archive/refs/heads/main.tar.gz
TMP_ARCHIVE=/tmp/venus-os-epever-main.tar.gz
TMP_DIR=/tmp/venus-os-epever-install

if [ "$(id -u)" != 0 ]; then
    echo 'Run as root' >&2
    exit 1
fi

# Venus OS normally does not ship with git. Install from the GitHub source
# archive instead of requiring a git clone.
rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

echo "Downloading venus-os-epever..."
wget -O "$TMP_ARCHIVE" "$ARCHIVE_URL"

echo "Extracting..."
tar -xzf "$TMP_ARCHIVE" -C "$TMP_DIR"

# GitHub archives contain a top-level directory named venus-os-epever-main.
SRC="$TMP_DIR/venus-os-epever-main"
if [ ! -d "$SRC" ]; then
    echo "Could not find extracted repository" >&2
    exit 1
fi

# Preserve a user-created configuration across upgrades.
OLD_CONFIG=
if [ -f "$ROOT/epever.conf" ]; then
    OLD_CONFIG=/tmp/epever.conf.preserve
    cp "$ROOT/epever.conf" "$OLD_CONFIG"
fi

rm -rf "$ROOT"
mkdir -p "$ROOT"
cp -R "$SRC"/. "$ROOT"/

if [ -n "$OLD_CONFIG" ] && [ -f "$OLD_CONFIG" ]; then
    cp "$OLD_CONFIG" "$ROOT/epever.conf"
else
    cp "$ROOT/epever.conf.example" "$ROOT/epever.conf"
fi

chmod +x "$ROOT/install.sh" "$ROOT/uninstall.sh"     "$ROOT/service/run" "$ROOT/service/log/run" "$ROOT/tools/"*.py

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

rm -rf "$TMP_DIR" "$TMP_ARCHIVE" "$OLD_CONFIG"

if [ -x /usr/bin/sv ]; then
    /usr/bin/sv up dbus-epever-tracer 2>/dev/null || true
fi

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
