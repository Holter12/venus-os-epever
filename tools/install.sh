#!/bin/sh
set -eu
ROOT=/data/venus-os-epever
REPO=https://github.com/Holter12/venus-os-epever.git
mkdir -p "$ROOT"
if command -v git >/dev/null 2>&1; then
  if [ -d "$ROOT/.git" ]; then
    git -C "$ROOT" pull --ff-only
  else
    git clone "$REPO" "$ROOT"
  fi
else
  echo "git is required for this development installer" >&2
  exit 1
fi
mkdir -p "$ROOT"
[ -f "$ROOT/epever.conf" ] || cp "$ROOT/epever.conf.example" "$ROOT/epever.conf"
chmod +x "$ROOT/service/run"
echo "Installed files to $ROOT"
echo "IMPORTANT: service registration is intentionally not enabled by this development installer yet."
