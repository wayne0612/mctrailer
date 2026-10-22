"""Minimal streamable-http client for McDonald's official MCP (mcd-mcp).

Stdlib only. The MCP token is read from the environment variable MCD_MCP_TOKEN
and is NEVER written to disk, logged, or echoed by this module. When the token
is absent or the service is unreachable, callers must fall back to demo data
(see normalize_mcp.py) instead of pretending a live call succeeded.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

DEFAULT_URL = "https://mcp.mcd.cn"
PROTOCOL_VERSION = "2024-11-05"


class McdMcpError(RuntimeError):
    """Raised when the MCP handshake or a tool call fails."""


class McdMcpClient:
    def __init__(self, token: str | None = None, url: str = DEFAULT_URL, timeout: int = 25):
        self.url = url
        self.timeout = timeout
        self._token = token or os.environ.get("MCD_MCP_TOKEN")
        self._session: str | None = None

    # -- availability -----------------------------------------------------
    def has_token(self) -> bool:
        return bool(self._token)

    def _require_token(self) -> str:
        if not self._token:
            raise McdMcpError(
                "MCD_MCP_TOKEN is not set. Set the env var (see mcp-config.example.json) "
                "to enable LIVE menu/price lookups; otherwise use demo fixtures."
            )
        return self._token

    # -- transport --------------------------------------------------------
    def _post(self, payload: dict) -> dict:
        """POST a JSON-RPC message, transparently handling text/event-stream."""
        self._require_token()
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json, text/event-stream")
        req.add_header("Authorization", "Bearer " + self._token)
        if self._session:
            req.add_header("Mcp-Session-Id", self._session)
        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout)
        except urllib.error.HTTPError as exc:  # 401 invalid token, 429 rate-limit, etc.
            body = exc.read().decode("utf-8", "replace")[:300]
            raise McdMcpError(f"HTTP {exc.code} from MCP server: {body}") from exc
        except urllib.error.URLError as exc:
            raise McdMcpError(f"network error reaching MCP server: {exc}") from exc

        sid = resp.headers.get("Mcp-Session-Id")
        if sid:
            self._session = sid
        body = resp.read().decode("utf-8", "replace")
        ctype = resp.headers.get("Content-Type", "")
        if "text/event-stream" in ctype:
            for line in body.splitlines():
                if line.startswith("data:"):
                    chunk = line[5:].strip()
                    try:
                        obj = json.loads(chunk)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(obj, dict) and ("result" in obj or "error" in obj):
                        return obj
            raise McdMcpError("no JSON-RPC result in event-stream response")
        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise McdMcpError(f"non-JSON response from MCP server: {body[:200]}") from exc

    # -- MCP methods ------------------------------------------------------
    def initialize(self) -> dict:
        msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "mctrailer", "version": "1.0.0"},
            },
        }
        resp = self._post(msg)
        if "error" in resp:
            raise McdMcpError(f"initialize failed: {resp['error']}")
        # best-effort initialized notification (ignored on failure)
        try:
            self._post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        except McdMcpError:
            pass
        return resp.get("result", {})

    def list_tools(self) -> list:
        resp = self._post({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        return resp.get("result", {}).get("tools", [])

    def call_tool(self, name: str, arguments: dict) -> dict:
        """Return the raw MCP tool result (has content[]/structuredContent/isError)."""
        self.initialize()
        resp = self._post(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments or {}},
            }
        )
        if "error" in resp:
            raise McdMcpError(f"tool call failed: {resp['error']}")
        return resp.get("result", {})
