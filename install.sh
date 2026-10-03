#!/bin/sh
set -eu

ROOT=/data/venus-os-epever
SERVICE=/service/dbus-epever-tracer
ARCHIVE_URL=https://github.com/Holter12/venus-os-epever/archive/refs/heads/main.tar.gz
TMP_ARCHIVE=/tmp/venus-os-epever-main.tar.gz
TMP_DIR=/tmp/venus-os-epever-install

if [ "$(id -u)" != 0 ]; then
    echo 'Run as root' >&2
    exit 1
fi

rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

echo "Downloading venus-os-epever..."
wget -O "$TMP_ARCHIVE" "$ARCHIVE_URL"

echo "Extracting..."
tar -xzf "$TMP_ARCHIVE" -C "$TMP_DIR"

SRC="$TMP_DIR/venus-os-epever-main"
if [ ! -d "$SRC" ]; then
    echo "Could not find extracted repository" >&2
    exit 1
fi

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

chmod +x "$ROOT/install.sh" "$ROOT/uninstall.sh" "$ROOT/service/run" "$ROOT/service/log/run" "$ROOT/tools/"*.py

# runit scans /service, not /opt/victronenergy/service.
# Keep the driver in /data and expose its service directory through /service.
rm -f "$SERVICE"
ln -s "$ROOT/service" "$SERVICE"

if [ ! -f /data/rc.local ]; then
    printf '#!/bin/sh\nexit 0\n' > /data/rc.local
    chmod +x /data/rc.local
fi

MARK='# venus-os-epever'
if ! grep -q "$MARK" /data/rc.local; then
    # Avoid sed here: BusyBox sed treats the || characters in the
    # replacement text as substitution delimiters.
    TMP_RC=/tmp/rc.local.epever
    awk -v service="$SERVICE" -v root="$ROOT" '
        /^exit 0$/ {
            print "# venus-os-epever"
            print "[ -L \"" service "\" ] || ln -s \"" root "/service\" \"" service "\""
        }
        { print }
    ' /data/rc.local > "$TMP_RC"
    mv "$TMP_RC" /data/rc.local
    chmod +x /data/rc.local
fi

rm -rf "$TMP_DIR" "$TMP_ARCHIVE" "$OLD_CONFIG"

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
