import os
import select
import socket
import struct
import sys
import time


ICMP_ECHO_REQUEST = 8
DEFAULT_TIMEOUT = 1
DEFAULT_COUNT = 4


def checksum(source):
    total = 0
    count_to = (len(source) // 2) * 2
    count = 0

    while count < count_to:
        total += (source[count] << 8) + source[count + 1]
        total &= 0xFFFFFFFF
        count += 2

    if count_to < len(source):
        total += source[-1] << 8
        total &= 0xFFFFFFFF

    total = (total >> 16) + (total & 0xFFFF)
    total += total >> 16
    return ~total & 0xFFFF


def receive_one_ping(icmp_socket, packet_id, sequence_number, timeout):
    time_left = timeout

    while time_left > 0:
        started_select = time.time()
        ready = select.select([icmp_socket], [], [], time_left)
        select_duration = time.time() - started_select

        if not ready[0]:
            return None

        time_received = time.time()

        # Fill in start
        received_packet, address = icmp_socket.recvfrom(1024)
        ip_header = received_packet[:20]
        ip_header_length = (received_packet[0] & 0x0F) * 4
        ttl = ip_header[8]
        icmp_header = received_packet[ip_header_length : ip_header_length + 8]
        icmp_type, code, received_checksum, received_id, received_sequence = struct.unpack(
            "!BBHHH", icmp_header
        )
        # Fill in end

        if (
            icmp_type == 0
            and code == 0
            and received_id == packet_id
            and received_sequence == sequence_number
        ):
            # Fill in start
            time_sent = struct.unpack(
                "!d", received_packet[ip_header_length + 8 : ip_header_length + 16]
            )[0]
            return {
                "delay_ms": (time_received - time_sent) * 1000,
                "address": address[0],
                "ttl": ttl,
                "bytes": len(received_packet) - ip_header_length,
            }
            # Fill in end

        time_left -= select_duration

    return None


def send_one_ping(icmp_socket, destination_address, packet_id, sequence_number):
    # Fill in start
    checksum_value = 0
    header = struct.pack(
        "!BBHHH", ICMP_ECHO_REQUEST, 0, checksum_value, packet_id, sequence_number
    )
    data = struct.pack("!d", time.time()) + b"Advanced Computer Networks ICMP Ping"
    checksum_value = checksum(header + data)
    header = struct.pack(
        "!BBHHH", ICMP_ECHO_REQUEST, 0, checksum_value, packet_id, sequence_number
    )
    packet = header + data
    icmp_socket.sendto(packet, (destination_address, 1))
    # Fill in end


def do_one_ping(destination_host, timeout, sequence_number):
    icmp_protocol = socket.getprotobyname("icmp")

    # Fill in start
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_protocol)
    # Fill in end

    packet_id = os.getpid() & 0xFFFF
    destination_address = socket.gethostbyname(destination_host)

    try:
        # Fill in start
        send_one_ping(icmp_socket, destination_address, packet_id, sequence_number)
        result = receive_one_ping(
            icmp_socket, packet_id, sequence_number, timeout
        )
        # Fill in end
    finally:
        icmp_socket.close()

    return destination_address, result


def ping(destination_host, timeout=DEFAULT_TIMEOUT, count=DEFAULT_COUNT):
    print(f"PING {destination_host}: {count} ICMP echo requests")

    sent = 0
    received = 0
    delays = []

    for sequence_number in range(1, count + 1):
        try:
            destination_address, result = do_one_ping(
                destination_host, timeout, sequence_number
            )
        except PermissionError:
            print("Raw ICMP sockets require administrator privileges.")
            print("Run with: sudo python3 ICMPPingClient.py")
            return
        except socket.gaierror as error:
            print(f"Could not resolve {destination_host}: {error}")
            return

        sent += 1

        if result is None:
            print(f"Request timed out for icmp_seq={sequence_number}")
        else:
            received += 1
            delays.append(result["delay_ms"])
            print(
                f"{result['bytes']} bytes from {result['address']}: "
                f"icmp_seq={sequence_number} ttl={result['ttl']} "
                f"time={result['delay_ms']:.3f} ms"
            )

        time.sleep(1)

    loss = ((sent - received) / sent) * 100 if sent else 0
    print(f"\n--- {destination_host} ping statistics ---")
    print(f"{sent} packets transmitted, {received} received, {loss:.1f}% packet loss")

    if delays:
        print(
            "round-trip min/avg/max = "
            f"{min(delays):.3f}/{sum(delays) / len(delays):.3f}/{max(delays):.3f} ms"
        )


def main():
    targets = sys.argv[1:] or [
        "google.com",
        "bbc.co.uk",
        "u-tokyo.ac.jp",
        "abc.net.au",
    ]

    for index, target in enumerate(targets):
        if index:
            print()
        ping(target)


if __name__ == "__main__":
    main()
