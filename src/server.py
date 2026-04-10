from mcp.server.fastmcp import FastMCP

from config import (
    HEXYLON_HOST,
    HEXYLON_PORT,
    MCP_HOST,
    MCP_PORT,
    MCP_SERVER_NAME,
    MCP_TRANSPORT,
    SCPI_TIMEOUT,
)
from scpi_client import send_scpi_command_to_hexylon

mcp = FastMCP(MCP_SERVER_NAME)


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
    mcp.run(transport=MCP_TRANSPORT)
