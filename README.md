# Hexylon MCP

## 1. Descripción

Este repositorio contiene la implementación de un servidor MCP (Model Context Protocol) mínimo diseñado para ejecutarse dentro del dispositivo Hexylon de Gsertel.

El sistema actúa como una pasarela entre el equipo de medición RF y un modelo de lenguaje externo (LLM), permitiendo ejecutar comandos SCPI sobre el dispositivo y obtener respuestas directas sin procesamiento intermedio.

El MCP no contiene lógica de negocio ni interpretación de datos. Su función es exclusivamente exponer el acceso al dispositivo.

---

## 2. Arquitectura

El sistema sigue una arquitectura simple y estrictamente desacoplada:

- Hexylon  
  Dispositivo de medición que expone una interfaz SCPI sobre TCP (puerto 5025)

- MCP (este repositorio)  
  Servidor que actúa como pasarela y se ejecuta dentro del Hexylon

- LLM externo  
  Cliente que consume el MCP, interpreta resultados y realiza el procesamiento

Flujo de comunicación:

LLM → MCP → Hexylon

---

## 3. Requisitos

Para ejecutar este proyecto es necesario disponer de:

- Python 3.10 o superior
- Acceso de red al dispositivo Hexylon
- API remota del Hexylon habilitada
- Entorno Linux o compatible

---

## 4. Instalación

Clonar el repositorio:

```bash
git clone https://github.com/pabloseijo/Hexylon-MCP.git
cd hexylon-mcp
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

o, si se utiliza uv:

```bash
uv sync
```

---

## 5. Configuración

La configuración del sistema se encuentra en:

```bash
src/config.py
```

Parámetros principales:

- HEXYLON_HOST → dirección IP del dispositivo  
- HEXYLON_PORT → puerto SCPI (por defecto 5025)  
- SCPI_TIMEOUT → timeout de comunicación  
- MCP_TRANSPORT → tipo de transporte (streamable-http)

Es necesario ajustar la IP del Hexylon antes de ejecutar el sistema.

---

## 6. Ejecución del servidor

El servidor MCP se arranca mediante el script:

```bash
./scripts/run_server.sh
```

Durante el arranque:

- se muestra un banner identificativo
- se imprime la configuración del sistema
- se verifica la conectividad con el Hexylon
- se inicia el servidor MCP

El servidor queda expuesto en:

```bash
http://127.0.0.1:8000
```

---

## 7. Reinicio del servidor

Para reiniciar el servidor y liberar el puerto automáticamente:

```bash
./scripts/restart_server.sh
```

---

## 8. Pruebas

El repositorio incluye scripts de validación:

```bash
./scripts/run_tests.sh
```

Tipos de pruebas:

- test_scpi → comunicación directa con el Hexylon  
- test_mcp_local → ejecución de la tool MCP sin cliente externo  

Estas pruebas permiten validar cada capa del sistema de forma independiente.

---

## 9. Uso del MCP

El servidor expone una única tool:

```bash
send_scpi_command(command: str) -> str
```

Esta tool permite enviar comandos SCPI directamente al dispositivo.

Ejemplos de comandos válidos:

```bash
IDN?  
FREQ?  
MODE?
```

La respuesta devuelta es exactamente la proporcionada por el Hexylon, sin modificación.

---

## 10. Estructura del repositorio

```bash
hexylon-mcp/
├── src/
│   ├── server.py          # Servidor MCP
│   ├── scpi_client.py    # Cliente SCPI sobre TCP
│   └── config.py         # Configuración del sistema
│
├── test/
│   ├── test_scpi.py      # Pruebas del cliente SCPI
│   └── test_mcp_local.py # Pruebas de la tool MCP
│
├── scripts/
│   ├── run_server.sh     # Arranque del servidor
│   ├── run_tests.sh      # Ejecución de pruebas
│   └── restart_server.sh # Reinicio del servidor
│
├── pyproject.toml        # Definición de dependencias
├── requirements.txt      # Dependencias para pip
└── README.md             # Documentación del proyecto
```

---

## 11. Estado del proyecto

El sistema se encuentra en fase funcional inicial.

Actualmente:

- comunicación SCPI validada con el Hexylon
- cliente TCP implementado y probado
- servidor MCP operativo
- integración completa MCP → SCPI → dispositivo
- scripts de ejecución simplificados

El sistema es funcional para la ejecución de comandos básicos.

---

## 12. Limitaciones

El diseño actual es intencionadamente mínimo:

- no hay autenticación
- no se gestiona concurrencia
- no se implementa control avanzado de errores
- no se realiza validación de comandos
- no se mantiene estado

Estas decisiones son coherentes con el objetivo de mantener el MCP como pasarela pura.

---

## 13. Desarrollo

Para desarrollo local:

- ejecutar siempre desde la raíz del proyecto
- utilizar ejecución como módulo Python
- evitar dependencias de entorno como PYTHONPATH

Ejecución directa alternativa:

```bash
python3 -m src.server
```

---

## 14. Próximos pasos

Las siguientes fases del proyecto incluyen:

- integración con cliente MCP externo
- conexión con un LLM real
- validación de flujos completos de uso
- mejora de robustez ante errores de red
- pruebas en entorno real del Hexylon

---
