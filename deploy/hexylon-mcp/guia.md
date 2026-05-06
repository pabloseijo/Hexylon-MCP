# Guía completa de despliegue del servidor MCP en Hexylon

## 1. Objetivo

El objetivo del despliegue es ejecutar un servidor MCP dentro del Hexylon para que un LLM local pueda enviar comandos SCPI al equipo de medida.

El MCP no interpreta los datos, no transforma respuestas y no aplica lógica de negocio. Su función es actuar como pasarela controlada entre el LLM y la API SCPI del Hexylon.

Flujo final:

```text
LLM local / PC
   |
   | HTTP MCP
   v
10.113.0.148:8814          ← IP externa de la placa principal (varía por unidad)
   |
   | DNAT / port forwarding (iptables en placa principal)
   v
169.254.1.2:8814           ← IP interna de la placa Linux (varía por unidad)
   |
   | Servidor MCP en Python
   v
169.254.1.1:5025           ← IP interna de la placa SCPI (varía por unidad)
   |
   | SCPI TCP
   v
Placa principal Hexylon
```

---

## 2. Problema inicial

El Hexylon dispone de un entorno Linux embebido con estas características:

```text
Arquitectura: aarch64
Kernel: Linux 4.14
glibc: 2.27
Python del sistema: 3.5.5
```

El SDK MCP requiere Python moderno, por lo que Python 3.5.5 no es suficiente.

El primer intento fue compilar Python 3.10 usando una imagen moderna, pero el binario generado dependía de versiones de glibc superiores:

```text
GLIBC_2.28
GLIBC_2.29
GLIBC_2.30
```

Ese binario no era compatible con el Hexylon porque el dispositivo solo dispone de:

```text
glibc 2.27
```

La solución fue compilar Python 3.10 usando una base compatible:

```text
Ubuntu 18.04 aarch64
```

Ubuntu 18.04 usa glibc 2.27, por lo que el Python generado queda alineado con el sistema del Hexylon.

---

## 3. Python portable generado

Se generó un paquete:

```text
python310-aarch64.tar.gz
```

que contiene:

```text
python310/
  bin/python3.10
  lib/
  include/
  ...
```

Este paquete se copia al Hexylon y se extrae en:

```text
/mnt/imx/root/python310
```

Validación:

```bash
/mnt/imx/root/python310/bin/python3.10 --version
```

Resultado esperado:

```text
Python 3.10.14
```

---

## 4. Problema con OpenSSL

Aunque Python 3.10 quedó operativo, apareció un error al importar módulos que requieren SSL:

```text
ImportError: libssl.so.1.1: cannot open shared object file
```

El Hexylon solo incluía OpenSSL 1.0.2:

```text
/usr/lib/libssl.so.1.0.2
/usr/lib/libcrypto.so.1.0.2
```

Pero Python 3.10 necesitaba OpenSSL 1.1:

```text
libssl.so.1.1
libcrypto.so.1.1
```

No se deben crear enlaces simbólicos desde OpenSSL 1.0.2 hacia 1.1, porque no son ABI-compatible.

La solución fue generar un segundo paquete:

```text
openssl-libs-aarch64.tar.gz
```

que contiene únicamente:

```text
lib/libssl.so.1.1
lib/libcrypto.so.1.1
```

Este paquete se extrae dentro de:

```text
/mnt/imx/root/python310
```

Validación:

```bash
LD_LIBRARY_PATH=/mnt/imx/root/python310/lib \
/mnt/imx/root/python310/bin/python3.10 -c "import ssl; print(ssl.OPENSSL_VERSION)"
```

Resultado esperado:

```text
OpenSSL 1.1.1...
```

---

## 5. Dependencias offline

El Hexylon no tiene acceso a Internet, por lo que las dependencias Python deben instalarse offline mediante wheels.

El error detectado fue que inicialmente se copiaron wheels de arquitectura incorrecta:

```text
x86_64
```

Ejemplos incorrectos:

```text
cffi-...-x86_64.whl
pydantic_core-...-x86_64.whl
rpds_py-...-x86_64.whl
cryptography-...-x86_64.whl
```

El Hexylon es `aarch64`, por tanto los wheels deben generarse para:

```text
manylinux2014_aarch64
```

Comando usado en el PC para generar wheels correctos:

```bash
python3 -m pip download \
  --dest wheels \
  --platform manylinux2014_aarch64 \
  --python-version 310 \
  --implementation cp \
  --abi cp310 \
  --only-binary=:all: \
  -r requirements.txt
```

La carpeta final debe contener wheels como:

```text
pydantic_core-...-aarch64.whl
rpds_py-...-aarch64.whl
cffi-...-aarch64.whl
```

---

## 6. Estructura final del paquete MCP

Dentro de `deploy/` se deja esta estructura:

```text
deploy/
  python310-aarch64.tar.gz
  openssl-libs-aarch64.tar.gz

  hexylon-mcp/
    src/
      __init__.py
      config.py
      scpi_client.py
      server.py

    wheels/
      *.whl

    requirements.txt
    pyproject.toml
    README.md
    uv.lock

    scripts/
      run.sh
      install.sh
      stop.sh
      status.sh
```

El MCP se empaqueta desde `deploy` con:

```bash
tar -czf hexylon-mcp.tar.gz hexylon-mcp
```

El paquete resultante es:

```text
deploy/hexylon-mcp.tar.gz
```

---

## 7. Configuración interna del MCP

Archivo:

```text
src/config.py
```

Configuración validada:

```python
HEXYLON_HOST = "169.254.1.1"   # IP interna de la placa SCPI — varía por unidad
HEXYLON_PORT = 5025

MCP_SERVER_NAME = "Hexylon-MCP"

MCP_TRANSPORT = "streamable-http"
MCP_HOST = "0.0.0.0"
MCP_PORT = 8814

SCPI_TIMEOUT = 5.0
```

Significado:

```text
169.254.1.1:5025
  Placa principal del Hexylon. Expone API SCPI.
  Esta IP es interna y solo accesible desde la placa Linux.

169.254.1.2
  Placa Linux donde se ejecuta Python y el MCP.

0.0.0.0:8814
  El MCP escucha en todas las interfaces de la placa Linux.
```

---

### 7.1 Cómo determinar HEXYLON_HOST en cada unidad

La IP `169.254.1.1` es la dirección interna de la placa SCPI en una unidad concreta.
**En otra unidad puede ser diferente.** Hay que determinarla antes de configurar el MCP.

Conéctate a la placa Linux del Hexylon y ejecuta:

```bash
arp -a
```

Resultado esperado:

```text
fpga (169.254.1.1) at 00:0e:7c:43:07:5f on eth0
```

La IP entre paréntesis es la que debes usar como `HEXYLON_HOST`.

Alternativamente:

```bash
ip route
```

Busca la ruta hacia la subred `169.254.x.x`. El gateway de esa ruta es `HEXYLON_HOST`.

Una vez identificada, actualiza `src/config.py`:

```python
HEXYLON_HOST = "169.254.X.X"  # sustituir por la IP real de cada unidad
```

---

## 8. Red real del Hexylon

El Hexylon tiene dos placas o dominios de red:

```text
Placa principal:
  IP externa: 10.113.0.148      ← accesible desde el PC (varía por unidad)
  IP interna: 169.254.1.1       ← accesible desde la placa Linux

Placa Linux/Python:
  IP interna: 169.254.1.2       ← donde corre el MCP
```

Resumen:

```text
169.254.1.1 = placa principal / FPGA / SCPI
169.254.1.2 = placa Linux / Python / MCP
```

El MCP **no debe usar** `10.113.0.148` como `HEXYLON_HOST`, porque esa IP pertenece
a la cara externa de la placa principal y no es accesible desde la placa Linux.

Debe usar la IP interna obtenida con `arp -a`:

```python
HEXYLON_HOST = "169.254.1.1"
```

---

## 9. Routing y exposición hacia el PC

El LLM local se ejecuta en el PC, pero el MCP corre en la placa Linux interna.
El PC no puede acceder directamente a `169.254.1.2:8814`.

Se usa la placa principal como punto de entrada mediante port forwarding con `iptables`:

```text
PC → 10.113.0.148:8814 → 169.254.1.2:8814
```

### 9.1 Obtener la IP externa de la placa principal

La IP externa (`10.113.0.148` en este ejemplo) es la que el PC usa para conectarse
al Hexylon por SSH. Varía por unidad y por red. Consúltala al equipo o verifícala con:

```bash
# Desde el PC, la IP que usas para hacer SSH es la IP externa
ssh root@<IP_EXTERNA>
```

### 9.2 Aplicar las reglas de iptables

Conéctate a la **placa principal** del Hexylon:

```bash
ssh root@<IP_EXTERNA>
```

Activa el forwarding IPv4:

```bash
echo 1 > /proc/sys/net/ipv4/ip_forward
```

Redirige el tráfico del puerto 8814 hacia la placa Linux:

```bash
iptables -t nat -A PREROUTING \
  -p tcp --dport 8814 \
  -j DNAT --to-destination 169.254.1.2:8814
```

Permite el tráfico de ida y vuelta:

```bash
iptables -A FORWARD -p tcp -d 169.254.1.2 --dport 8814 -j ACCEPT
iptables -A FORWARD -p tcp -s 169.254.1.2 --sport 8814 -j ACCEPT
```

Aplica MASQUERADE para que las respuestas vuelvan correctamente al PC:

```bash
iptables -t nat -A POSTROUTING \
  -p tcp -d 169.254.1.2 --dport 8814 \
  -j MASQUERADE
```

### 9.3 Verificar que el routing funciona

Desde el PC:

```bash
curl http://<IP_EXTERNA>:8814/mcp
```

Respuesta esperada:

```json
{"jsonrpc":"2.0","id":"server-error","error":{"code":-32600,"message":"Not Acceptable: Client must accept text/event-stream"}}
```

Ese error es correcto — significa que el MCP responde. El cliente MCP real
enviará la cabecera `Accept: text/event-stream` correctamente.

### 9.4 Nota sobre persistencia

Las reglas `iptables` y el valor de `ip_forward` **se pierden al reiniciar**
la placa principal. En cada arranque hay que volver a aplicarlas manualmente,
o añadirlas al script de inicio del sistema si el Hexylon lo permite.

---

## 10. Instalación manual en el Hexylon

Debido a las características de la eMMC del Hexylon (filesystem lento, bloqueos
de I/O bajo carga), la instalación se realiza manualmente paso a paso desde
una sesión SSH directa en la placa Linux.

### 10.1 Transferir los paquetes desde el PC

El script `deploy_hexylon.sh` se encuentra en `scripts/` en la raíz del proyecto.

```bash
./scripts/deploy_hexylon.sh
```

El script solicitará:

```text
IP del Hexylon:   → IP externa del dispositivo (ej: 10.113.0.148)
Contraseña SSH:   → contraseña del usuario root
```

Lo que hace internamente:

1. Verifica que existen todos los ficheros necesarios en `deploy/`:
   - `python310-aarch64.tar.gz`
   - `openssl-libs-aarch64.tar.gz`
   - carpeta `hexylon-mcp/` con `src/`, `wheels/`, `scripts/` y `requirements.txt`

2. Aplica permisos de ejecución a los scripts internos del MCP

3. Empaqueta `hexylon-mcp/` en `hexylon-mcp.tar.gz`

4. Valida que los tres tarballs no están corruptos y que el tar de Python
   tiene la estructura correcta (`python310/` en la raíz, sin prefijo `root/`)

5. Transfiere los tres paquetes al Hexylon via `scp`:
```text
   /mnt/imx/root/python310-aarch64.tar.gz
   /mnt/imx/root/openssl-libs-aarch64.tar.gz
   /mnt/imx/root/hexylon-mcp.tar.gz
```

6. Muestra las instrucciones exactas para completar la instalación manualmente

Al terminar mostrará:

```text
ssh root@<IP_EXTERNA>
ssh imx
cd /root
```

Seguir con la sección 10.2.

### 10.2 Extracción e instalación

Una vez en la placa Linux (`/root`), ejecutar cada comando y esperar a que
el prompt vuelva antes de continuar. El tar de Python puede tardar 2-3 minutos.

```bash
tar -xzf python310-aarch64.tar.gz -C /mnt/imx/root
tar -xzf openssl-libs-aarch64.tar.gz -C /mnt/imx/root/python310
tar -xzf hexylon-mcp.tar.gz -C /mnt/imx/root
```

Crear el entorno virtual:

```bash
LD_LIBRARY_PATH=python310/lib python310/bin/python3.10 -m venv mcp-venv
```

Instalar dependencias offline:

```bash
LD_LIBRARY_PATH=python310/lib mcp-venv/bin/pip install \
  --no-index \
  --no-cache-dir \
  --find-links=hexylon-mcp/wheels \
  -r hexylon-mcp/requirements.txt
```

Validar la instalación:

```bash
LD_LIBRARY_PATH=python310/lib PYTHONPATH=hexylon-mcp \
mcp-venv/bin/python -c 'import ssl; import mcp; import src.scpi_client; print("OK")'
```

Resultado esperado:

```text
OK
```

---

## 11. Scripts locales en el Hexylon

Ubicación:

```text
/mnt/imx/root/hexylon-mcp/scripts
```

### run.sh

Arranca el servidor MCP con las variables de entorno correctas.

```bash
cd /mnt/imx/root/hexylon-mcp/scripts
sh run.sh
```

Ejecución en segundo plano:

```bash
nohup sh run.sh > ../mcp.log 2>&1 &
```

### stop.sh

Detiene el servidor MCP buscando el proceso por puerto o nombre.

```bash
sh stop.sh
```

### status.sh

Verifica el estado del sistema: puerto, proceso, HTTP local y SCPI interno.

```bash
sh status.sh
```

Ejemplo de salida:

```text
Puerto 8814: LISTEN
Proceso MCP: activo PID=1234
HTTP local: OK
SCPI 169.254.1.1:5025: OK
```

### install.sh

Reinstala el entorno virtual y las dependencias sin necesidad de usar
el script de despliegue completo.

```bash
sh install.sh
```

---

## 12. Flujo operativo recomendado

### Despliegue inicial desde el PC

```bash
./deploy_hexylon.sh
```

Seguir las instrucciones que muestra al finalizar.

### Configurar routing en la placa principal

```bash
ssh root@<IP_EXTERNA>
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A PREROUTING -p tcp --dport 8814 -j DNAT --to-destination 169.254.1.2:8814
iptables -A FORWARD -p tcp -d 169.254.1.2 --dport 8814 -j ACCEPT
iptables -A FORWARD -p tcp -s 169.254.1.2 --sport 8814 -j ACCEPT
iptables -t nat -A POSTROUTING -p tcp -d 169.254.1.2 --dport 8814 -j MASQUERADE
```

### Arrancar el MCP en la placa Linux

```bash
ssh root@<IP_EXTERNA>
ssh imx
cd /root/hexylon-mcp/scripts
sh run.sh
```

### Verificar desde el PC

```bash
curl http://<IP_EXTERNA>:8814/mcp
```

### Producción (background)

```bash
nohup sh run.sh > ../mcp.log 2>&1 &
```

### Reinicio del servicio

```bash
sh stop.sh
sh run.sh
```

---

## 13. Resultado final

Tras completar el despliegue:

```text
MCP activo en 0.0.0.0:8814 (placa Linux)
SCPI operativo en 169.254.1.1:5025 (placa principal)
Acceso externo vía <IP_EXTERNA>:8814
LLM puede ejecutar comandos SCPI a través del MCP
```
