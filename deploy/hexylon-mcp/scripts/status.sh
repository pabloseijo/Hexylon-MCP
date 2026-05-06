#!/bin/bash

PORT=8814

echo "=== Estado MCP ==="

if netstat -tuln | grep -q ":$PORT "; then
  echo "Puerto $PORT: LISTEN"
else
  echo "Puerto $PORT: NO LISTEN"
fi

PID=$(netstat -tulnp 2>/dev/null | grep ":$PORT " | awk '{print $7}' | cut -d/ -f1 | head -1)

if [ -z "$PID" ]; then
  PID=$(ps aux | grep "src/server.py" | grep -v grep | awk '{print $2}' | head -1)
fi

if [ -n "$PID" ]; then
  echo "Proceso MCP: activo PID=$PID"
else
  echo "Proceso MCP: no encontrado"
fi

echo
echo "=== Conectividad local MCP ==="
curl -s --max-time 3 http://127.0.0.1:$PORT >/dev/null && echo "HTTP local: OK" || echo "HTTP local: ERROR"

echo
echo "=== Conectividad SCPI interna ==="
nc -z -w 3 169.254.1.1 5025 >/dev/null 2>&1 && echo "SCPI 169.254.1.1:5025: OK" || echo "SCPI 169.254.1.1:5025: ERROR"