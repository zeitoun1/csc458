#!/usr/bin/env python3
from __future__ import annotations

import platform
import shutil
import socket
import sys

ok = True
print("CSC458 PA0 environment check")
print("----------------------------")
print("Platform:", platform.platform())
print("Python:", sys.version.split()[0])

if sys.platform != "linux":
    print("FAIL: PA0 must be run inside the CSC458 Linux VM.")
    ok = False
elif sys.version_info < (3, 10):
    print("FAIL: Python 3.10 or newer is required.")
    ok = False
else:
    print("OK: Linux and Python version")

for command in ("nc", "ip", "traceroute"):
    path = shutil.which(command)
    print(f"{command}: {path or 'MISSING'}")
    ok &= path is not None

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.close()
    print("OK: Python socket module")
except OSError as exc:
    print("FAIL: socket creation:", exc)
    ok = False

raise SystemExit(0 if ok else 1)
