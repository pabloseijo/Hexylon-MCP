from scpi_client import send_scpi_command_to_hexylon

response = send_scpi_command_to_hexylon(
    host="10.113.0.148",
    port=5025,
    command="IDN?"
)

print(repr(response))
print(response)