#!/usr/bin/env bash
set -euo pipefail
set -x

trap 'echo "[render-build] Failed at line ${LINENO}: ${BASH_COMMAND}" >&2' ERR

echo "[render-build] Starting build script inside $(pwd)"

echo "[render-build] Running as user: $(id -u -n) (uid=$(id -u))"

# Determine sudo availability (Render builds run as non-root)
SUDO=""
if [[ $(id -u) -ne 0 ]]; then
  if command -v sudo >/dev/null 2>&1; then
    echo "[render-build] sudo available at $(command -v sudo)"
    if sudo -n true 2>/dev/null; then
      SUDO="sudo"
      echo "[render-build] sudo usable without password"
    else
      echo "[render-build] sudo present but requires password; skipping"
    fi
  else
    echo "[render-build] sudo not available; running without it"
  fi
else
  echo "[render-build] Running as root user"
fi

# Base dirs for apt caches/lists to avoid read-only FS
APT_WORKDIR="${TMPDIR:-/tmp}/render-apt"
APT_LISTS_DIR="$APT_WORKDIR/lists"
APT_ARCHIVES_DIR="$APT_WORKDIR/archives"
mkdir -p "$APT_LISTS_DIR/partial" "$APT_ARCHIVES_DIR/partial"
APT_ARGS=("-o" "Dir::State::lists=$APT_LISTS_DIR" "-o" "Dir::Cache::archives=$APT_ARCHIVES_DIR")

APT_GET() {
  if [[ -n "$SUDO" ]]; then
    "${SUDO}" apt-get "${APT_ARGS[@]}" "$@"
  elif [[ $(id -u) -eq 0 ]]; then
    apt-get "${APT_ARGS[@]}" "$@"
  else
    echo "[render-build] ERROR: apt-get requires sudo or root privileges." >&2
    echo "[render-build]       Current user $(id -u -n) lacks permission to install packages." >&2
    echo "[render-build]       Consider switching the service to a Docker deployment or Render native root build." >&2
    exit 100
  fi
}

# Render build hook: install SQL Server ODBC driver and Python deps
export DEBIAN_FRONTEND=noninteractive

echo "[render-build] Updating apt repositories"
APT_GET update

echo "[render-build] Installing base packages"
APT_GET install -y --no-install-recommends curl ca-certificates gnupg apt-transport-https

echo "[render-build] Configuring Microsoft package repository"
MICROSOFT_KEYRING=/usr/share/keyrings/microsoft-prod.gpg
if [[ -n "$SUDO" ]]; then
  curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | ${SUDO} tee "$MICROSOFT_KEYRING" > /dev/null
  echo "deb [arch=amd64 signed-by=$MICROSOFT_KEYRING] https://packages.microsoft.com/config/debian/12/prod/ stable main"     | ${SUDO} tee /etc/apt/sources.list.d/microsoft-prod.list
else
  curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee "$MICROSOFT_KEYRING" > /dev/null
  echo "deb [arch=amd64 signed-by=$MICROSOFT_KEYRING] https://packages.microsoft.com/config/debian/12/prod/ stable main"     | tee /etc/apt/sources.list.d/microsoft-prod.list
fi

echo "[render-build] Refreshing apt after adding Microsoft repo"
APT_GET update

echo "[render-build] Installing SQL Server ODBC driver"
ACCEPT_EULA=Y APT_GET install -y --no-install-recommends msodbcsql18 unixodbc unixodbc-dev

echo "[render-build] Cleaning apt caches"
APT_GET clean
if [[ -n "$SUDO" ]]; then
  ${SUDO} rm -rf "$APT_WORKDIR"
else
  rm -rf "$APT_WORKDIR"
fi

echo "[render-build] Upgrading pip"
python3 -m pip install --upgrade pip

echo "[render-build] Installing project dependencies"
python3 -m pip install --no-cache-dir -r requirements.txt

echo "[render-build] Installing project in editable mode"
python3 -m pip install --no-cache-dir -e ..

echo "[render-build] Build script completed successfully"
