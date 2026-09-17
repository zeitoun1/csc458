#!/usr/bin/env python3
"""CSC458 PA0: a tiny HTTP/1.1 client built directly on a TCP socket."""

from __future__ import annotations

import argparse
import socket
import sys
import socket

DEFAULT_PORT = 80
RECV_CHUNK_SIZE = 4096
DEFAULT_TIMEOUT = 5.0


def get_url(host: str, path: str, port: int = DEFAULT_PORT, timeout: float = DEFAULT_TIMEOUT) -> bytes:
    """Fetch *path* from *host* using a direct TCP connection and HTTP/1.1.

    Return the complete HTTP response (status line, headers, blank line, and body)
    as bytes.
    
    The Host header must include the port when *port* is not the default HTTP
    port (80). For example:

        Host: example.com
        Host: 127.0.0.1:8080

    You must implement this function using Python's ``socket`` module. Do not use
    higher-level HTTP clients such as urllib, http.client, requests, aiohttp, etc.
    """

    if len(path) == 0 or path[0] != '/':
        raise ValueError("path must start with '/'")

    port_header = f":{port}" if port != DEFAULT_PORT else ""
    request = f"GET {path} HTTP/1.1\r\nHost: {host}{port_header}\r\nConnection: close\r\n\r\n"
    request_bytes = request.encode()
    response = bytearray(b'')

    with socket.create_connection((host, port), timeout) as server_socket:
        server_socket.sendall(request_bytes)
        while True:
            chunk = server_socket.recv(RECV_CHUNK_SIZE);
            if chunk == b'':
                return bytes(response)
            response.extend(chunk)

def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch an HTTP URL using a TCP socket (CSC458 PA0)."
    )
    parser.add_argument("host", help="server hostname or IP address")
    parser.add_argument("path", help="HTTP path beginning with '/', e.g. /")
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT, help="TCP port (default: 80)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="socket timeout in seconds (default: 5)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    try:
        response = get_url(args.host, args.path, args.port, args.timeout)
    except (OSError, ValueError) as exc:
        print(f"webget: {exc}", file=sys.stderr)
        return 1

    # Write bytes unchanged. HTTP bodies are not guaranteed to be UTF-8 text.
    sys.stdout.buffer.write(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

