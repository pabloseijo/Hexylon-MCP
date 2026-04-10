import socket, asyncio

from mcp.server.fastmcp import FastMCP

from src.config import (
    HEXYLON_HOST,
    HEXYLON_PORT,
    MCP_SERVER_NAME,
    MCP_TRANSPORT,
    SCPI_TIMEOUT,
)
from src.scpi_client import send_scpi_command_to_hexylon

mcp = FastMCP(MCP_SERVER_NAME)

from src.config import (
    HEXYLON_HOST,
    HEXYLON_PORT,
    MCP_SERVER_NAME,
    MCP_TRANSPORT,
    SCPI_TIMEOUT,
)

def check_hexylon_reachable(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False

def print_banner() -> None:
    banner = r"""
██╗  ██╗███████╗██╗  ██╗██╗   ██╗██╗      ██████╗ ███╗   ██╗
██║  ██║██╔════╝╚██╗██╔╝╚██╗ ██╔╝██║     ██╔═══██╗████╗  ██║
███████║█████╗   ╚███╔╝  ╚████╔╝ ██║     ██║   ██║██╔██╗ ██║
██╔══██║██╔══╝   ██╔██╗   ╚██╔╝  ██║     ██║   ██║██║╚██╗██║
██║  ██║███████╗██╔╝ ██╗   ██║   ███████╗╚██████╔╝██║ ╚████║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝

                    HEXYLON MCP SERVER
    """

    print(banner)

    print("=== CONFIGURACIÓN DEL SISTEMA ===")
    print(f"Hexylon target : {HEXYLON_HOST}:{HEXYLON_PORT}")
    print(f"SCPI timeout   : {SCPI_TIMEOUT}s")
    
    status = "OK" if check_hexylon_reachable(HEXYLON_HOST, HEXYLON_PORT) else "NO ACCESIBLE"
    print(f"Estado conexión: {status}")
    
    print()
    print("=== MCP SERVER ===")
    print(f"Nombre         : {MCP_SERVER_NAME}")
    print(f"Transporte     : {MCP_TRANSPORT}")
    print("Endpoint       : http://127.0.0.1:8000")
    print()
    print("=== USO ===")
    print("Tool disponible:")
    print("  - send_scpi_command(command: str) -> str")
    print()
    print("Ejemplos de comandos SCPI:")
    print("  IDN?")
    print("  FREQ?")
    print("  MODE?")
    print()
    print("Nota:")
    print("  El MCP actúa como pasarela directa. No interpreta ni transforma respuestas.")
    print("-" * 60)
    
@mcp.tool()
def send_scpi_command(command: str) -> str:
    """
    Envía un comando SCPI al Hexylon y devuelve la respuesta sin procesar.
    """
    return send_scpi_command_to_hexylon(
        host=HEXYLON_HOST,
        port=HEXYLON_PORT,
        command=command,
        timeout=SCPI_TIMEOUT,
    )


if __name__ == "__main__":
    print_banner()
    
    try:
        mcp.run(transport=MCP_TRANSPORT)
    except KeyboardInterrupt:
        print("\nCierre solicitado por el usuario.")
    except asyncio.CancelledError:
        print("\nServidor detenido correctamente.")