#!/usr/bin/env bash
set -euo pipefail
set -x

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "[render-build] Running app/render-build.sh from ${SCRIPT_DIR}"
bash "$SCRIPT_DIR/app/render-build.sh"
