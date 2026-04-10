import asyncio
import os

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


# Forzar bypass de proxy para localhost
os.environ["NO_PROXY"] = "127.0.0.1,localhost"
os.environ["no_proxy"] = "127.0.0.1,localhost"

# Opcional: eliminar proxies explícitamente
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
os.environ.pop("ALL_PROXY", None)
os.environ.pop("all_proxy", None)


MCP_URL = "http://127.0.0.1:8000/mcp"


async def main() -> None:
    async with streamable_http_client(MCP_URL) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("=== TOOLS DISPONIBLES ===")
            for tool in tools.tools:
                print(f"- {tool.name}")

            print("\n=== LLAMADA A send_scpi_command ===")
            result = await session.call_tool(
                "send_scpi_command",
                {"command": "IDN?"},
            )
            print(result)


if __name__ == "__main__":
    asyncio.run(main())