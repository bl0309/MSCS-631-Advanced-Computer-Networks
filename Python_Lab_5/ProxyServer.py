import hashlib
import os
import socket
import sys
from pathlib import Path
from urllib.parse import urlsplit


BUFFER_SIZE = 4096
CACHE_DIR = Path("cache")
DEFAULT_PORT = 8888


def cache_file_for(host, port, path):
    cache_key = f"{host}:{port}{path}"
    return CACHE_DIR / hashlib.sha256(cache_key.encode("utf-8")).hexdigest()


def send_error(client_socket, status, message):
    body = f"{status} {message}\r\n".encode("utf-8")
    response = (
        f"HTTP/1.1 {status} {message}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Content-Type: text/plain\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("utf-8") + body
    client_socket.sendall(response)


def parse_request(request):
    request_line = request.split(b"\r\n", 1)[0].decode("iso-8859-1")
    parts = request_line.split()

    if len(parts) < 3:
        raise ValueError("Malformed HTTP request")

    method, target, version = parts
    if method.upper() != "GET":
        raise ValueError("Only GET requests are supported")

    parsed = urlsplit(target)

    if parsed.scheme and parsed.scheme.lower() != "http":
        raise ValueError("Only HTTP URLs are supported")

    if parsed.scheme:
        host = parsed.hostname
        port = parsed.port or 80
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
    else:
        host = None
        port = 80
        path = target

    headers = {}
    for line in request.split(b"\r\n")[1:]:
        if not line:
            break
        if b":" not in line:
            continue
        name, value = line.split(b":", 1)
        headers[name.decode("iso-8859-1").lower()] = value.strip().decode(
            "iso-8859-1"
        )

    if not host:
        host_header = headers.get("host")
        if not host_header:
            raise ValueError("Missing Host header")
        if ":" in host_header:
            host, port_text = host_header.rsplit(":", 1)
            port = int(port_text)
        else:
            host = host_header

    return method, host, port, path, version


def build_origin_request(host, path):
    return (
        f"GET {path} HTTP/1.0\r\n"
        f"Host: {host}\r\n"
        "Connection: close\r\n"
        "User-Agent: Python-Lab-5-Proxy/1.0\r\n"
        "\r\n"
    ).encode("iso-8859-1")


def fetch_from_origin(host, port, path):
    origin_request = build_origin_request(host, path)

    # Fill in start
    origin_socket = socket.create_connection((host, port), timeout=10)
    try:
        origin_socket.sendall(origin_request)
        response_chunks = []
        while True:
            chunk = origin_socket.recv(BUFFER_SIZE)
            if not chunk:
                break
            response_chunks.append(chunk)
    finally:
        origin_socket.close()
    # Fill in end

    return b"".join(response_chunks)


def handle_client(client_socket, client_address):
    try:
        # Fill in start
        request = client_socket.recv(BUFFER_SIZE)
        if not request:
            return
        method, host, port, path, version = parse_request(request)
        cache_file = cache_file_for(host, port, path)
        # Fill in end

        if cache_file.exists():
            # Fill in start
            print(f"Cache hit: http://{host}:{port}{path}")
            client_socket.sendall(cache_file.read_bytes())
            # Fill in end
            return

        # Fill in start
        print(f"Cache miss: http://{host}:{port}{path}")
        response = fetch_from_origin(host, port, path)
        CACHE_DIR.mkdir(exist_ok=True)
        cache_file.write_bytes(response)
        client_socket.sendall(response)
        # Fill in end

    except ValueError as error:
        print(f"Bad request from {client_address}: {error}")
        send_error(client_socket, "400", str(error))
    except OSError as error:
        print(f"Network error for {client_address}: {error}")
        send_error(client_socket, "502", "Bad Gateway")
    finally:
        client_socket.close()


def start_proxy(port):
    # Fill in start
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", port))
    server_socket.listen(5)
    # Fill in end

    print(f"Proxy server listening on port {port}")
    print("Configure your browser to use this machine as an HTTP proxy.")

    try:
        while True:
            # Fill in start
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")
            handle_client(client_socket, client_address)
            # Fill in end
    except KeyboardInterrupt:
        print("\nProxy server stopped.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    proxy_port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    start_proxy(proxy_port)
