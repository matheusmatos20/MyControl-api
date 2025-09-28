#!/usr/bin/env bash
set -euo pipefail
set -x

trap 'echo "[render-build] Failed at line ${LINENO}: ${BASH_COMMAND}" >&2' ERR

echo "[render-build] Starting build script inside $(pwd)"

# Base dirs for apt caches/lists to avoid read-only FS
APT_WORKDIR="${TMPDIR:-/tmp}/render-apt"
APT_LISTS_DIR="$APT_WORKDIR/lists"
APT_ARCHIVES_DIR="$APT_WORKDIR/archives"
mkdir -p "$APT_LISTS_DIR/partial" "$APT_ARCHIVES_DIR/partial"
APT_ARGS=("-o" "Dir::State::lists=$APT_LISTS_DIR" "-o" "Dir::Cache::archives=$APT_ARCHIVES_DIR")

# Render build hook: install SQL Server ODBC driver and Python deps
export DEBIAN_FRONTEND=noninteractive

echo "[render-build] Updating apt repositories"
apt-get "${APT_ARGS[@]}" update

echo "[render-build] Installing base packages"
apt-get "${APT_ARGS[@]}" install -y --no-install-recommends curl ca-certificates gnupg apt-transport-https

echo "[render-build] Configuring Microsoft package repository"
MICROSOFT_KEYRING=/usr/share/keyrings/microsoft-prod.gpg
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee "$MICROSOFT_KEYRING" > /dev/null

echo "deb [arch=amd64 signed-by=$MICROSOFT_KEYRING] https://packages.microsoft.com/config/debian/12/prod/ stable main"     | tee /etc/apt/sources.list.d/microsoft-prod.list

echo "[render-build] Refreshing apt after adding Microsoft repo"
apt-get "${APT_ARGS[@]}" update

echo "[render-build] Installing SQL Server ODBC driver"
ACCEPT_EULA=Y apt-get "${APT_ARGS[@]}" install -y --no-install-recommends msodbcsql18 unixodbc unixodbc-dev

echo "[render-build] Cleaning apt caches"
apt-get "${APT_ARGS[@]}" clean
rm -rf "$APT_WORKDIR"

echo "[render-build] Upgrading pip"
python3 -m pip install --upgrade pip

echo "[render-build] Installing project dependencies"
python3 -m pip install --no-cache-dir -r requirements.txt

echo "[render-build] Installing project in editable mode"
python3 -m pip install --no-cache-dir -e ..

echo "[render-build] Build script completed successfully"
