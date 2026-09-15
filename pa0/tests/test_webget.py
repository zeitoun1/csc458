from __future__ import annotations

import ast
import importlib.util
import socket
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEBGET_PATH = ROOT / "src" / "webget.py"

spec = importlib.util.spec_from_file_location("webget", WEBGET_PATH)
assert spec and spec.loader
webget = importlib.util.module_from_spec(spec)
spec.loader.exec_module(webget)


class OneShotServer:
    def __init__(self, body: bytes, chunks: tuple[int, ...] = ()) -> None:
        self.body = body
        self.chunks = chunks
        self.request = b""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("127.0.0.1", 0))
        self._sock.listen(1)
        self.port = self._sock.getsockname()[1]
        self._thread = threading.Thread(target=self._serve, daemon=True)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._thread.join(timeout=2)
        self._sock.close()

    def _serve(self):
        conn, _ = self._sock.accept()
        with conn:
            conn.settimeout(2)
            buf = bytearray()
            while b"\r\n\r\n" not in buf:
                piece = conn.recv(4096)
                if not piece:
                    break
                buf.extend(piece)
            self.request = bytes(buf)
            response = (
                b"HTTP/1.1 200 OK\r\n"
                + b"Content-Type: application/octet-stream\r\n"
                + f"Content-Length: {len(self.body)}\r\n".encode()
                + b"Connection: close\r\n\r\n"
                + self.body
            )
            if not self.chunks:
                conn.sendall(response)
                return
            i = 0
            for size in self.chunks:
                if i >= len(response):
                    break
                conn.sendall(response[i : i + size])
                i += size
            if i < len(response):
                conn.sendall(response[i:])


class PublicTests(unittest.TestCase):
    def test_01_source_imports(self):
        self.assertTrue(callable(webget.get_url))

    def test_02_no_high_level_http_library(self):
        tree = ast.parse(WEBGET_PATH.read_text(encoding="utf-8"))
        forbidden = {"urllib", "http.client", "requests", "aiohttp", "httpx"}
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
        bad = sorted(
            name for name in imports if any(name == f or name.startswith(f + ".") for f in forbidden)
        )
        self.assertEqual(bad, [], f"Do not use high-level HTTP libraries: {bad}")

    def test_03_basic_get_and_headers(self):
        with OneShotServer(b"hello-pa0") as server:
            response = webget.get_url("127.0.0.1", "/hello", server.port, 2.0)
        self.assertTrue(response.startswith(b"HTTP/1.1 200 OK\r\n"))
        self.assertTrue(response.endswith(b"hello-pa0"))
        self.assertIn(b"GET /hello HTTP/1.1\r\n", server.request)
        self.assertIn(f"Host: 127.0.0.1:{server.port}\r\n".encode(), server.request)
        self.assertIn(b"Connection: close\r\n", server.request)
        self.assertTrue(server.request.endswith(b"\r\n\r\n"))

    def test_04_reads_until_eof_not_single_recv(self):
        body = (b"0123456789abcdef" * 900) + b"END"
        with OneShotServer(body, chunks=(7, 13, 31, 101, 509, 1024)) as server:
            response = webget.get_url("127.0.0.1", "/large", server.port, 2.0)
        self.assertTrue(response.endswith(body))
        self.assertEqual(response.count(b"END"), 1)

    def test_05_query_string_is_preserved(self):
        with OneShotServer(b"query-ok") as server:
            webget.get_url("127.0.0.1", "/search?q=networks&n=2", server.port, 2.0)
        self.assertIn(b"GET /search?q=networks&n=2 HTTP/1.1\r\n", server.request)

    def test_06_path_must_begin_with_slash(self):
        with self.assertRaises(ValueError):
            webget.get_url("127.0.0.1", "missing-leading-slash", 9, 0.01)


if __name__ == "__main__":
    unittest.main(verbosity=2)

