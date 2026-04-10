from src.scpi_client import send_scpi_command_to_hexylon
from src.config import HEXYLON_HOST, HEXYLON_PORT

print(send_scpi_command_to_hexylon(
    host=HEXYLON_HOST,
    port=HEXYLON_PORT,
    command="IDN?"
))