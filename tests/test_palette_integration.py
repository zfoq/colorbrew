"""Opt-in integration tests for external palette sources.

These tests spin up a local HTTP server that serves palette JSON so the
network code path is exercised without relying on third-party uptime.
They are skipped unless ``COLORBREW_RUN_INTEGRATION_TESTS=1`` is set, so
normal local test runs stay offline.
"""

from __future__ import annotations

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

import pytest

from colorbrew.data import get_palette, refresh_palette
from colorbrew.data.material_colors import MATERIAL_COLORS
from colorbrew.data.tailwind_colors import TAILWIND_COLORS

pytestmark = pytest.mark.skipif(
    os.environ.get("COLORBREW_RUN_INTEGRATION_TESTS") != "1",
    reason=(
        "Integration tests hit the network; "
        "set COLORBREW_RUN_INTEGRATION_TESTS=1 to run them"
    ),
)


class _PaletteHandler(BaseHTTPRequestHandler):
    """Minimal handler that serves precomputed JSON payloads by path."""

    _payloads: dict[str, bytes] = {}

    def log_message(self, format: str, *args: Any) -> None:  # noqa: ARG002
        """Silence request logging to keep test output clean."""
        return

    def do_GET(self) -> None:
        """Serve a palette JSON payload or 404."""
        payload = self._payloads.get(self.path)
        if payload is None:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload)


def _start_server(payloads: dict[str, dict[str, str]]) -> HTTPServer:
    """Start a background HTTP server and return its bound instance."""
    _PaletteHandler._payloads = {
        path: json.dumps(data, sort_keys=True).encode()
        for path, data in payloads.items()
    }
    server = HTTPServer(("127.0.0.1", 0), _PaletteHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


@pytest.fixture(scope="module")
def palette_server():
    """Yield the base URL of a server serving material and tailwind JSON."""
    server = _start_server(
        {
            "/material.json": MATERIAL_COLORS,
            "/tailwind.json": TAILWIND_COLORS,
        }
    )
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.parametrize(
    ("family", "path", "expected_key"),
    [
        ("material", "/material.json", "blue-600"),
        ("tailwind", "/tailwind.json", "sky-500"),
    ],
)
def test_get_palette_from_remote_source(
    family: str,
    path: str,
    expected_key: str,
    palette_server: str,
) -> None:
    """``get_palette`` can load a palette from an external JSON URL."""
    palette = get_palette(
        family,
        source="api",
        allow_network=True,
        url=f"{palette_server}{path}",
        timeout=5.0,
    )
    assert palette.system == family
    assert palette.source == "api"
    assert expected_key in palette
    assert palette[expected_key].hex.startswith("#")


@pytest.mark.parametrize(
    ("family", "path"),
    [
        ("material", "/material.json"),
        ("tailwind", "/tailwind.json"),
    ],
)
def test_refresh_palette_fetches_remote(
    family: str,
    path: str,
    palette_server: str,
) -> None:
    """``refresh_palette`` fetches from an external URL without caching."""
    palette = refresh_palette(
        family,
        url=f"{palette_server}{path}",
        write_cache=False,
        timeout=5.0,
    )
    assert palette.system == family
    assert palette.source == "api"
    assert len(palette) > 0
