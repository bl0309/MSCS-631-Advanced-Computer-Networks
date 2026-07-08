"""Simple TCP web server for the socket programming lab."""
from __future__ import annotations

import argparse
import mimetypes
import socket
from pathlib import Path
from urllib.parse import unquote, urlparse


HOST = "127.0.0.1"
PORT = 6789
BUFFER_SIZE = 4096
WEB_ROOT = Path(__file__).resolve().parent


def build_response(status: str, body: bytes, content_type: str) -> bytes:
    """Build a minimal HTTP/1.1 response packet."""
    headers = [
        f"HTTP/1.1 {status}",
        f"Content-Length: {len(body)}",
        f"Content-Type: {content_type}",
        "Connection: close",
        "",
        "",
    ]
    return "\r\n".join(headers).encode("iso-8859-1") + body


def requested_file(path: str) -> Path:
    """Resolve the requested HTTP path inside the lab directory."""
    parsed_path = unquote(urlparse(path).path)
    if parsed_path == "/":
        parsed_path = "/HelloWorld.html"

    relative_path = parsed_path.lstrip("/")
    candidate = (WEB_ROOT / relative_path).resolve()
    if WEB_ROOT not in candidate.parents and candidate != WEB_ROOT:
        raise PermissionError("Requested path is outside the web root.")
    return candidate


def handle_request(message: str) -> bytes:
    request_line = message.splitlines()[0] if message.splitlines() else ""
    parts = request_line.split()

    if len(parts) < 3:
        body = b"<html><body><h1>400 Bad Request</h1></body></html>"
        return build_response("400 Bad Request", body, "text/html; charset=utf-8")

    method, path, _version = parts
    if method != "GET":
        body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        return build_response("405 Method Not Allowed", body, "text/html; charset=utf-8")

    try:
        filename = requested_file(path)
        body = filename.read_bytes()
        content_type = mimetypes.guess_type(filename.name)[0] or "application/octet-stream"
        return build_response("200 OK", body, content_type)
    except (FileNotFoundError, IsADirectoryError):
        body = (
            b"<html><head><title>404 Not Found</title></head>"
            b"<body><h1>404 Not Found</h1><p>The requested file was not found.</p></body></html>"
        )
        return build_response("404 Not Found", body, "text/html; charset=utf-8")
    except PermissionError:
        body = b"<html><body><h1>403 Forbidden</h1></body></html>"
        return build_response("403 Forbidden", body, "text/html; charset=utf-8")


def run_server(host: str, port: int) -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"Ready to serve on http://{host}:{port}/HelloWorld.html")

    try:
        while True:
            connection_socket, address = server_socket.accept()
            with connection_socket:
                print(f"Accepted connection from {address[0]}:{address[1]}")
                message = connection_socket.recv(BUFFER_SIZE).decode("iso-8859-1")
                response = handle_request(message)
                connection_socket.sendall(response)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server_socket.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Python socket web server lab.")
    parser.add_argument("--host", default=HOST, help=f"Host address to bind. Default: {HOST}")
    parser.add_argument("--port", type=int, default=PORT, help=f"Port to bind. Default: {PORT}")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_server(args.host, args.port)
