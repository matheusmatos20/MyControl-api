#!/usr/bin/env bash
set -euo pipefail

# Render build hook: install SQL Server ODBC driver and Python deps
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends curl apt-transport-https ca-certificates gnupg

# Add Microsoft package repo (needed for msodbcsql18)
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# Render currently bases images on Debian 12 (bookworm)
DISTRO="debian/12"
curl "https://packages.microsoft.com/config/${DISTRO}/prod.list" -o /etc/apt/sources.list.d/microsoft-prod.list
apt-get update
ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 unixodbc unixodbc-dev

# Clean up apt cache to keep image small
apt-get clean
rm -rf /var/lib/apt/lists/*

# Python dependencies
python -m pip install --upgrade pip
pip install --no-cache-dir -r app/requirements.txt
pip install --no-cache-dir -e .
