#!/bin/bash
set -e

PORT=8814

PID=$(netstat -tulnp 2>/dev/null | grep ":$PORT " | awk '{print $7}' | cut -d/ -f1 | head -1)

if [ -z "$PID" ]; then
  PID=$(ps aux | grep "src/server.py" | grep -v grep | awk '{print $2}' | head -1)
fi

if [ -z "$PID" ]; then
  echo "MCP no está ejecutándose."
  exit 0
fi

echo "Deteniendo MCP PID=$PID..."
kill "$PID" 2>/dev/null || true
sleep 1

if ps | awk '{print $1}' | grep -q "^$PID$"; then
  echo "Forzando parada..."
  kill -9 "$PID" 2>/dev/null || true
fi

echo "MCP detenido."