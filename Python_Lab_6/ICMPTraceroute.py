import os
import select
import socket
import struct
import sys
import time


ICMP_ECHO_REPLY = 0
ICMP_ECHO_REQUEST = 8
ICMP_TIME_EXCEEDED = 11
DEFAULT_MAX_HOPS = 30
DEFAULT_TIMEOUT = 2
DEFAULT_PROBES = 3


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


def build_packet(packet_id, sequence_number):
    # Fill in start
    header = struct.pack(
        "!BBHHH", ICMP_ECHO_REQUEST, 0, 0, packet_id, sequence_number
    )
    data = struct.pack("!d", time.time()) + b"Advanced Computer Networks Traceroute"
    packet_checksum = checksum(header + data)
    header = struct.pack(
        "!BBHHH", ICMP_ECHO_REQUEST, 0, packet_checksum, packet_id, sequence_number
    )
    # Fill in end

    return header + data


def parse_icmp_packet(packet):
    # Fill in start
    ip_header_length = (packet[0] & 0x0F) * 4
    icmp_header = packet[ip_header_length : ip_header_length + 8]
    icmp_type, code, packet_checksum, packet_id, sequence_number = struct.unpack(
        "!BBHHH", icmp_header
    )
    # Fill in end

    return icmp_type, code, packet_id, sequence_number, ip_header_length


def receive_reply(receiver_socket, timeout):
    time_left = timeout

    while time_left > 0:
        started_select = time.time()
        ready = select.select([receiver_socket], [], [], time_left)
        select_duration = time.time() - started_select

        if not ready[0]:
            return None

        # Fill in start
        time_received = time.time()
        packet, address = receiver_socket.recvfrom(1024)
        icmp_type, code, packet_id, sequence_number, ip_header_length = (
            parse_icmp_packet(packet)
        )
        # Fill in end

        reply = {
            "address": address[0],
            "time_received": time_received,
            "icmp_type": icmp_type,
            "code": code,
            "packet_id": packet_id,
            "sequence_number": sequence_number,
            "ip_header_length": ip_header_length,
        }

        if icmp_type in {ICMP_TIME_EXCEEDED, ICMP_ECHO_REPLY}:
            return reply

        time_left -= select_duration

    return None


def reverse_dns(ip_address):
    try:
        return socket.gethostbyaddr(ip_address)[0]
    except socket.herror:
        return ip_address


def trace_probe(destination_address, ttl, packet_id, sequence_number, timeout):
    icmp_protocol = socket.getprotobyname("icmp")

    # Fill in start
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_protocol)
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_protocol)
    sender_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
    # Fill in end

    try:
        packet = build_packet(packet_id, sequence_number)

        # Fill in start
        time_sent = time.time()
        sender_socket.sendto(packet, (destination_address, 0))
        reply = receive_reply(receiver_socket, timeout)
        # Fill in end

        if reply is None:
            return None

        reply["rtt_ms"] = (reply["time_received"] - time_sent) * 1000
        return reply
    finally:
        receiver_socket.close()
        sender_socket.close()


def trace_route(destination_host, max_hops=DEFAULT_MAX_HOPS, timeout=DEFAULT_TIMEOUT):
    try:
        destination_address = socket.gethostbyname(destination_host)
    except socket.gaierror as error:
        print(f"Could not resolve {destination_host}: {error}")
        return

    print(f"traceroute to {destination_host} ({destination_address}), {max_hops} hops max")

    packet_id = os.getpid() & 0xFFFF
    sequence_number = 0

    for ttl in range(1, max_hops + 1):
        replies = []
        reached_destination = False

        for _ in range(DEFAULT_PROBES):
            sequence_number += 1
            try:
                # Fill in start
                reply = trace_probe(
                    destination_address, ttl, packet_id, sequence_number, timeout
                )
                # Fill in end
            except PermissionError:
                print("Raw ICMP sockets require administrator privileges.")
                print("Run with: sudo python3 ICMPTraceroute.py")
                return

            if reply is None:
                replies.append("*")
                continue

            replies.append(reply)
            if reply["icmp_type"] == ICMP_ECHO_REPLY:
                reached_destination = True

        print_hop(ttl, replies)

        if reached_destination:
            break


def print_hop(ttl, replies):
    addresses = [reply["address"] for reply in replies if isinstance(reply, dict)]

    if not addresses:
        print(f"{ttl:2d}  *  *  *")
        return

    hop_address = addresses[0]
    hop_name = reverse_dns(hop_address)
    parts = [f"{ttl:2d}", f"{hop_name} ({hop_address})"]

    for reply in replies:
        if reply == "*":
            parts.append("*")
        else:
            parts.append(f"{reply['rtt_ms']:.3f} ms")

    print("  ".join(parts))


def main():
    targets = sys.argv[1:] or [
        "google.com",
        "bbc.co.uk",
        "www.yahoo.co.jp",
        "abc.net.au",
    ]

    for index, target in enumerate(targets):
        if index:
            print()
        trace_route(target)


if __name__ == "__main__":
    main()
