#!/usr/bin/env bash
set -euxo pipefail

# Render build hook: install SQL Server ODBC driver and Python deps
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends curl ca-certificates gnupg apt-transport-https

# Add Microsoft package repo (needed for msodbcsql18)
MICROSOFT_KEYRING=/usr/share/keyrings/microsoft-prod.gpg
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee "$MICROSOFT_KEYRING" > /dev/null

echo "deb [arch=amd64 signed-by=$MICROSOFT_KEYRING] https://packages.microsoft.com/config/debian/12/prod/ stable main" \
    | tee /etc/apt/sources.list.d/microsoft-prod.list

apt-get update
ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 unixodbc unixodbc-dev

# Clean up apt cache to keep image small
apt-get clean
rm -rf /var/lib/apt/lists/*

# Python dependencies
python3 -m pip install --upgrade pip
python3 -m pip install --no-cache-dir -r app/requirements.txt
python3 -m pip install --no-cache-dir -e .
