"""UDP ping client for Python Lab 2."""
from __future__ import annotations

import argparse
import socket
import time


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12000
PING_COUNT = 10
TIMEOUT_SECONDS = 1.0


def run_client(host: str, port: int, count: int, timeout: float) -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)

    rtts: list[float] = []
    lost_packets = 0

    try:
        for sequence_number in range(1, count + 1):
            send_time = time.time()
            message = f"Ping {sequence_number} {send_time}"

            try:
                client_socket.sendto(message.encode("utf-8"), (host, port))
                response, server_address = client_socket.recvfrom(1024)
                receive_time = time.time()
                rtt = receive_time - send_time
                rtts.append(rtt)

                print(f"Reply from {server_address[0]}:{server_address[1]}: {response.decode('utf-8')}")
                print(f"Sequence {sequence_number}: RTT = {rtt * 1000:.3f} ms")
            except socket.timeout:
                lost_packets += 1
                print(f"Sequence {sequence_number}: Request timed out")
    finally:
        client_socket.close()

    received_packets = count - lost_packets
    loss_rate = (lost_packets / count) * 100 if count else 0

    print("\n--- UDP ping statistics ---")
    print(f"{count} packets transmitted, {received_packets} received, {loss_rate:.1f}% packet loss")
    if rtts:
        print(
            "RTT min/avg/max = "
            f"{min(rtts) * 1000:.3f}/"
            f"{(sum(rtts) / len(rtts)) * 1000:.3f}/"
            f"{max(rtts) * 1000:.3f} ms"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the UDP pinger client.")
    parser.add_argument("--host", default=SERVER_HOST, help=f"Server host. Default: {SERVER_HOST}")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help=f"Server port. Default: {SERVER_PORT}")
    parser.add_argument("--count", type=int, default=PING_COUNT, help=f"Number of pings. Default: {PING_COUNT}")
    parser.add_argument(
        "--timeout",
        type=float,
        default=TIMEOUT_SECONDS,
        help=f"Socket timeout in seconds. Default: {TIMEOUT_SECONDS}",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_client(args.host, args.port, args.count, args.timeout)
