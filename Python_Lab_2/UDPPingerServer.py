"""UDP ping server supplied for Python Lab 2 testing."""
from __future__ import annotations

import random
import socket


HOST = "127.0.0.1"
PORT = 12000


def run_server(host: str = HOST, port: int = PORT) -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))

    print(f"UDP ping server listening on {host}:{port}")

    try:
        while True:
            rand = random.randint(0, 10)
            message, address = server_socket.recvfrom(1024)
            decoded_message = message.decode("utf-8")
            print(f"Received from {address[0]}:{address[1]}: {decoded_message}")

            if rand < 4:
                print("Simulated packet loss")
                continue

            server_socket.sendto(decoded_message.upper().encode("utf-8"), address)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    run_server()
