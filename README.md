# Hexylon MCP

## Descripción

Este proyecto implementa un **servidor MCP (Model Context Protocol)** mínimo diseñado para ejecutarse dentro del dispositivo **Hexylon de Gsertel**.

El objetivo del sistema es actuar como una **pasarela entre el dispositivo y un modelo de inteligencia artificial externo (LLM)**, permitiendo que dicho modelo acceda a los datos del equipo y los procese.

---

## Arquitectura del sistema

El sistema se compone de tres elementos principales:

- **Hexylon**
  - Dispositivo de medición RF
  - Expone una API basada en SCPI sobre TCP (puerto 5025)
  - Ejecuta el servidor MCP

- **MCP (este proyecto)**
  - Se ejecuta dentro del Hexylon
  - Actúa como pasarela
  - Expone acceso a la API del dispositivo

- **LLM externo**
  - Consume el MCP
  - Interpreta los datos
  - Realiza el procesamiento y razonamiento

Flujo de comunicación:

LLM → MCP → Hexylon

---

## Objetivo del proyecto

Desarrollar un MCP mínimo que:

- permita ejecutar comandos SCPI sobre el Hexylon
- devuelva las respuestas sin procesar
- sirva como interfaz estándar para un LLM

---

## Principios de diseño

El MCP sigue un enfoque estrictamente minimalista:

- no contiene lógica de negocio
- no interpreta datos
- no genera diagnósticos
- no transforma información más allá de lo necesario

Su única responsabilidad es:

- recibir peticiones
- comunicarse con el dispositivo
- devolver la respuesta

---

## Tecnologías utilizadas

- Python 3.10+
- SDK oficial de MCP (`mcp`)
- Gestión de dependencias con `uv`
- Comunicación con el dispositivo mediante TCP (SCPI)

---

## Estructura del proyecto

hexylon-mcp/
- server.py → servidor MCP
- scpi_client.py → cliente TCP para comandos SCPI
- config.py → configuración del sistema
- pyproject.toml → dependencias
- README.md → documentación

---

## Estado actual

El proyecto se encuentra en fase inicial.

Actualmente:

- se ha definido la arquitectura
- se ha preparado el entorno de desarrollo
- se está implementando el MCP mínimo

---

## Próximos pasos

- implementación del cliente SCPI
- definición de la tool MCP principal
- integración con el Hexylon
- validación de comandos básicos (IDN?, MEAS?, etc.)

---