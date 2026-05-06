#!/bin/bash

set -e

BASE_DIR="/mnt/imx/root/hexylon-mcp"
VENV="/mnt/imx/root/mcp-venv"
PYTHON="$VENV/bin/python"
PORT=8814

export LD_LIBRARY_PATH="/mnt/imx/root/python310/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="$BASE_DIR"

cd "$BASE_DIR"

# Liberar puerto si está ocupado
if netstat -tuln | grep -q ":$PORT "; then
  echo "Puerto $PORT ocupado, liberando..."
  PID=$(netstat -tulnp 2>/dev/null | grep ":$PORT" | awk '{print $7}' | cut -d/ -f1)
  if [ -n "$PID" ]; then
    kill -9 "$PID"
  fi
fi

exec "$PYTHON" src/server.py