import socket
import time


class ScpiClientError(Exception):
    """Excepción base para errores del cliente SCPI."""


class ScpiTimeoutError(ScpiClientError):
    """Timeout esperando respuesta del Hexylon."""


class ScpiConnectionError(ScpiClientError):
    """Error de conexión TCP con el Hexylon."""


def send_scpi_command_to_hexylon(
    host: str,
    port: int,
    command: str,
    timeout: float = 5.0,
) -> str:
    if not command or not command.strip():
        raise ValueError("El comando SCPI no puede estar vacío.")

    payload = (command.strip() + "\n").encode("ascii")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))

            sock.sendall(payload)
            sock.shutdown(socket.SHUT_WR)

            time.sleep(0.2)

            chunks = []

            while True:
                try:
                    data = sock.recv(4096)
                except socket.timeout:
                    break

                if not data:
                    break

                chunks.append(data)

    except socket.timeout as exc:
        raise ScpiTimeoutError(
            f"Timeout esperando respuesta del Hexylon para el comando: {command}"
        ) from exc
    except OSError as exc:
        raise ScpiConnectionError(
            f"Error de conexión con Hexylon en {host}:{port}"
        ) from exc

    response = b"".join(chunks).decode("utf-8", errors="replace").strip()

    if not response:
        raise ScpiTimeoutError(
            f"Respuesta vacía del Hexylon para el comando: {command}"
        )

    return response