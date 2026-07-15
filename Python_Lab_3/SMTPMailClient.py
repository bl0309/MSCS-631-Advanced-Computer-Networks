import os
import socket
from email.utils import formatdate


CRLF = "\r\n"


def read_reply(client_socket):
    """Read an SMTP reply, including multiline replies."""
    chunks = []

    while True:
        data = client_socket.recv(1024).decode("utf-8", errors="replace")
        if not data:
            raise ConnectionError("SMTP server closed the connection.")

        chunks.append(data)
        lines = "".join(chunks).splitlines()

        if lines and len(lines[-1]) >= 4 and lines[-1][3] == " ":
            return int(lines[-1][:3]), "".join(chunks)


def send_command(
    client_socket,
    command,
    expected_code,
):
    print(f"C: {command}")
    client_socket.sendall((command + CRLF).encode("utf-8"))

    code, reply = read_reply(client_socket)
    print(f"S: {reply}", end="" if reply.endswith(CRLF) else "\n")

    expected_codes = (
        expected_code if isinstance(expected_code, tuple) else (expected_code,)
    )
    if code not in expected_codes:
        raise RuntimeError(
            f"Expected SMTP status {expected_codes}, but server returned {code}."
        )
    return code, reply


def build_message(sender, recipient, subject, body):
    headers = [
        f"From: {sender}",
        f"To: {recipient}",
        f"Subject: {subject}",
        f"Date: {formatdate(localtime=True)}",
        "Content-Type: text/plain; charset=utf-8",
    ]
    return CRLF.join(headers) + CRLF + CRLF + body


def main() -> None:
    mail_server = os.getenv("SMTP_SERVER", "localhost")
    mail_port = int(os.getenv("SMTP_PORT", "1025"))
    sender = os.getenv("SMTP_SENDER", "student@example.com")
    recipient = os.getenv("SMTP_RECIPIENT", "receiver@example.com")
    subject = os.getenv("SMTP_SUBJECT", "Python Lab 3 SMTP Test")
    body = os.getenv(
        "SMTP_BODY",
        "This message was sent by a Python SMTP socket client for Python Lab 3.",
    )
    # Fill in start
    client_socket = socket.create_connection((mail_server, mail_port), timeout=30)
    code, reply = read_reply(client_socket)
    print(f"S: {reply}", end="" if reply.endswith(CRLF) else "\n")
    if code != 220:
        raise RuntimeError(f"Expected SMTP status 220, but server returned {code}.")
    # Fill in end

    # Fill in start
    send_command(client_socket, "HELO localhost", 250)
    # Fill in end

    # Fill in start
    send_command(client_socket, f"MAIL FROM:<{sender}>", 250)
    # Fill in end

    # Fill in start
    send_command(client_socket, f"RCPT TO:<{recipient}>", (250, 251))
    # Fill in end

    # Fill in start
    send_command(client_socket, "DATA", 354)
    message = build_message(sender, recipient, subject, body)
    print("C: [message body]")
    client_socket.sendall((message + CRLF + "." + CRLF).encode("utf-8"))
    code, reply = read_reply(client_socket)
    print(f"S: {reply}", end="" if reply.endswith(CRLF) else "\n")
    if code != 250:
        raise RuntimeError(f"Expected SMTP status 250, but server returned {code}.")
    # Fill in end

    # Fill in start
    send_command(client_socket, "QUIT", 221)
    client_socket.close()
    # Fill in end


if __name__ == "__main__":
    main()
