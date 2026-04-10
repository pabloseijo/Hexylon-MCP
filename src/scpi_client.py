import socket
import time


class ScpiTimeoutError(Exception):
    pass


class ScpiConnectionError(Exception):
    pass


def send_scpi_command_to_hexylon(
    host: str,
    port: int,
    command: str,
    timeout: float = 5.0,
) -> str:
    # IMPORTANTE: el comando debe terminar con un salto de línea para que el Hexylon lo procese
    payload = (command + "\n").encode("ascii")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))

            sock.sendall(payload)

            # IMPORTANTE: cierre de escritura
            sock.shutdown(socket.SHUT_WR)

            # pequeño retardo para permitir respuesta
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
            f"Error de conexión con Hexylon en {host}:{port} para el comando: {command}"
        ) from exc

    response = b"".join(chunks).decode("utf-8", errors="replace").strip()

    if not response:
        raise ScpiTimeoutError(
            f"Respuesta vacía del Hexylon para el comando: {command}"
        )

    return response