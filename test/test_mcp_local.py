from src.server import send_scpi_command

print(send_scpi_command("IDN?"))
print(send_scpi_command("FREQ?"))