#!/usr/bin/env bash
set -euo pipefail
cat > fetcher.py <<'PY'
import ipaddress
import socket
from urllib.parse import urlparse

import requests


def fetch(url: str) -> bytes:
    host = urlparse(url).hostname
    ip = ipaddress.ip_address(socket.gethostbyname(host))
    if ip.is_private or ip.is_loopback:
        raise ValueError("private address")
    response = requests.get(url, allow_redirects=True)
    return response.content
PY
