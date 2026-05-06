# Hexylon MCP

> **Despliegue en dispositivo:** consulta la [Guía completa de despliegue](deploy/hexylon-mcp/guia.md) para instrucciones de instalación en el Hexylon.

---

## 1. Descripción

Este repositorio contiene la implementación de un servidor MCP (Model Context Protocol) mínimo diseñado para ejecutarse dentro del dispositivo Hexylon de Gsertel.

El sistema actúa como una pasarela entre el equipo de medición RF y un modelo de lenguaje externo (LLM), permitiendo ejecutar comandos SCPI sobre el dispositivo y obtener respuestas directas sin procesamiento intermedio.

El MCP no contiene lógica de negocio ni interpretación de datos. Su función es exclusivamente exponer el acceso al dispositivo.

---

## 2. Arquitectura

El sistema sigue una arquitectura simple y estrictamente desacoplada:

- **Hexylon** — dispositivo de medición que expone una interfaz SCPI sobre TCP (puerto 5025)
- **MCP (este repositorio)** — servidor que actúa como pasarela y se ejecuta dentro del Hexylon
- **LLM externo** — cliente que consume el MCP, interpreta resultados y realiza el procesamiento

Flujo de comunicación:

```text
LLM local / PC
   |
   | HTTP MCP (puerto 8814)
   v
10.113.0.148:8814          ← IP externa del Hexylon (varía por unidad)
   |
   | DNAT / port forwarding
   v
169.254.1.2:8814           ← Placa Linux interna
   |
   | Servidor MCP en Python
   v
169.254.1.1:5025           ← Placa SCPI interna
   |
   | SCPI TCP
   v
Placa principal Hexylon
```

---

## 3. Requisitos

### Desarrollo local

- Python 3.10 o superior
- Acceso de red al dispositivo Hexylon
- API remota del Hexylon habilitada
- Entorno Linux o compatible

### Despliegue en el Hexylon

- `python310-aarch64.tar.gz` — Python 3.10 portable compilado para glibc 2.27
- `openssl-libs-aarch64.tar.gz` — OpenSSL 1.1 para aarch64
- `sshpass` instalado en el PC de despliegue

Consulta la [guía de despliegue](deploy/hexylon-mcp/guia.md) para el proceso completo.

---

## 4. Instalación local

Clonar el repositorio:

```bash
git clone https://github.com/pabloseijo/Hexylon-MCP.git
cd hexylon-mcp
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

o con uv:

```bash
uv sync
```

---

## 5. Configuración

La configuración del sistema se encuentra en `src/config.py`:

```python
HEXYLON_HOST = "169.254.1.1"   # IP interna de la placa SCPI — varía por unidad
HEXYLON_PORT = 5025

MCP_SERVER_NAME = "Hexylon-MCP"
MCP_TRANSPORT   = "streamable-http"
MCP_HOST        = "0.0.0.0"
MCP_PORT        = 8814

SCPI_TIMEOUT = 5.0
```

> **Importante:** `HEXYLON_HOST` debe ser la IP interna de la placa SCPI, no la IP externa del dispositivo. Para determinarla en cada unidad ejecuta `arp -a` desde la placa Linux. Consulta la [guía de despliegue](deploy/hexylon-mcp/guia.md) para más detalles.

---

## 6. Ejecución local

```bash
./scripts/run.sh
```

o directamente:

```bash
python3 -m src.server
```

Durante el arranque se muestra la configuración activa, se verifica la conectividad con el Hexylon y se inicia el servidor MCP.

---

## 7. Despliegue en el Hexylon

El despliegue se realiza desde el PC con el script:

```bash
./deploy_hexylon.sh
```

El script transfiere los paquetes necesarios y muestra las instrucciones paso a paso para completar la instalación manualmente en el dispositivo.

Consulta la [guía de despliegue](deploy/hexylon-mcp/guia.md) para el proceso completo, incluyendo la configuración del routing con `iptables`.

---

## 8. Scripts locales en el Hexylon

Una vez instalado, los scripts de gestión se encuentran en `/mnt/imx/root/hexylon-mcp/scripts`:

| Script | Función |
|---|---|
| `run.sh` | Arranca el servidor MCP |
| `stop.sh` | Detiene el servidor MCP |
| `status.sh` | Verifica estado del sistema |

Ejecución en producción (background):

```bash
nohup sh run.sh > ../mcp.log 2>&1 &
```

---

## 9. Pruebas

```bash
./scripts/run_tests.sh
```

Tipos de pruebas disponibles:

- `test_scpi.py` — comunicación directa con el Hexylon via SCPI
- `test_mcp_local.py` — ejecución de la tool MCP sin cliente externo
- `test_mcp_remote.py` — pruebas remotas del MCP mediante cliente externo

---

## 10. Uso del MCP

El servidor expone una única tool:

```python
send_scpi_command(command: str) -> str
```

Ejemplos de comandos válidos:

```
IDN?
FREQ?
MODE?
```

La respuesta devuelta es exactamente la proporcionada por el Hexylon, sin modificación.

---

## 11. Estructura del repositorio

```text
hexylon-mcp/
├── deploy/
│   ├── hexylon-mcp/           # Paquete desplegable en el Hexylon
│   │   ├── src/
│   │   │   ├── server.py      # Servidor MCP
│   │   │   ├── scpi_client.py # Cliente SCPI sobre TCP
│   │   │   └── config.py      # Configuración del sistema
│   │   ├── scripts/
│   │   │   ├── run.sh         # Arranque del servidor
│   │   │   ├── stop.sh        # Detención del servidor
│   │   │   ├── status.sh      # Verificación del estado
│   │   │   └── install.sh     # Reinstalación del entorno
│   │   ├── wheels/            # Dependencias offline para aarch64
│   │   ├── requirements.txt
│   │   └── guia.md            # Guía completa de despliegue
│   ├── python310-aarch64.tar.gz
│   └── openssl-libs-aarch64.tar.gz
│
├── src/
│   ├── server.py
│   ├── scpi_client.py
│   └── config.py
│
├── test/
│   ├── test_scpi.py
│   ├── test_mcp_local.py
│   └── test_mcp_remote.py
│
├── scripts/
│   ├── run.sh
│   └── run_tests.sh
│
├── deploy_hexylon.sh          # Script de despliegue desde el PC
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 12. Estado del proyecto

El sistema se encuentra en fase funcional:

- comunicación SCPI validada con el Hexylon
- cliente TCP implementado y probado
- servidor MCP operativo en el dispositivo
- integración completa LLM → MCP → SCPI → dispositivo
- routing configurado mediante iptables
- scripts de despliegue y gestión operativos

---

## 13. Limitaciones

El diseño actual es intencionadamente mínimo:

- no hay autenticación
- no se gestiona concurrencia
- no se implementa control avanzado de errores
- no se realiza validación de comandos SCPI
- no se mantiene estado entre llamadas

Estas decisiones son coherentes con el objetivo de mantener el MCP como pasarela pura.

