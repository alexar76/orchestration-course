"""Lightweight AIMarket-compatible hub for M4/M7 labs (~5 MB deps, no git clones).

Uses only uvicorn + httpx. For the full SDK cycle (M8 ``hire()``) use
``courselib.economy.embedded_sandbox(mode=\"full\")``.
"""

from __future__ import annotations

import contextlib
import json
import os
import socket
import threading
import time
from pathlib import Path
from typing import Any, Iterator

import httpx

from courselib.trust import sign_receipt, verify_receipt

# Dev default for the local teaching hub. Override in any shared/networked
# deployment so receipts can't be forged: export COURSE_HUB_LITE_SECRET=...
_HUB_SECRET = os.environ.get("COURSE_HUB_LITE_SECRET", "course-hub-lite-dev-secret")
_CAPABILITIES = [
    {
        "product_id": "prod-translate",
        "capability_id": "translate.multi@v2",
        "price_per_call_usd": 0.01,
        "description": "Translate text (course demo)",
    },
    {
        "product_id": "prod-summarize",
        "capability_id": "summarize@v1",
        "price_per_call_usd": 0.005,
        "description": "Summarize text (course demo)",
    },
]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class _ThreadedUvicorn:
    def __init__(self, app: Any, port: int):
        import uvicorn

        class _Server(uvicorn.Server):
            def install_signal_handlers(self) -> None:
                pass

        self.port = port
        self._server = _Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
        self._thread = threading.Thread(target=self._server.run, daemon=True)

    def start(self, ready_path: str = "", timeout: float = 15.0) -> None:
        self._thread.start()
        deadline = time.time() + timeout
        base = f"http://127.0.0.1:{self.port}"
        while time.time() < deadline:
            if getattr(self._server, "started", False):
                if not ready_path:
                    return
                try:
                    if httpx.get(base + ready_path, timeout=1.0).status_code < 500:
                        return
                except Exception:
                    pass
            time.sleep(0.05)
        raise TimeoutError(f"hub-lite on :{self.port} did not become ready")

    def stop(self) -> None:
        self._server.should_exit = True
        self._thread.join(timeout=5.0)


def _build_app() -> Any:
    from fastapi import FastAPI

    app = FastAPI(title="course-hub-lite")

    @app.get("/.well-known/ai-market.json")
    async def well_known() -> dict:
        return {"name": "course-hub-lite", "protocol": "v2-lite", "capabilities": len(_CAPABILITIES)}

    @app.get("/ai-market/v2/discover")
    async def discover(q: str = "", limit: int = 8) -> dict:
        qlow = q.lower()
        hits = [
            c for c in _CAPABILITIES
            if not qlow or qlow in c["capability_id"].lower() or qlow in c["description"].lower()
        ]
        return {"matches": hits[:limit]}

    @app.post("/ai-market/v2/invoke")
    async def invoke(body: dict) -> dict:
        product_id = body.get("product_id", "")
        capability_id = body.get("capability_id", "")
        payload = body.get("payload") or {}
        cap = next(
            (c for c in _CAPABILITIES if c["product_id"] == product_id and c["capability_id"] == capability_id),
            None,
        )
        if cap is None:
            return {"success": False, "error": "capability not found"}
        text = (payload.get("input") or payload.get("text") or "")
        output = {
            "output": {
                "served_by": "course-hub-lite",
                "capability": capability_id,
                "product": product_id,
                "echo": text,
            }
        }
        receipt = sign_receipt(
            {
                "product_id": product_id,
                "capability_id": capability_id,
                "price_usd": cap["price_per_call_usd"],
                "payload_hash": json.dumps(payload, sort_keys=True),
            },
            _HUB_SECRET,
        )
        return {
            "success": True,
            "price_usd": cap["price_per_call_usd"],
            "result": output,
            "receipt": receipt,
        }

    return app


class HubLiteClient:
    """Thin HTTP client for the embedded hub-lite."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def well_known(self) -> dict[str, Any]:
        return httpx.get(self.base_url + "/.well-known/ai-market.json", timeout=5.0).json()

    def discover(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        r = httpx.get(
            self.base_url + "/ai-market/v2/discover",
            params={"q": query, "limit": limit},
            timeout=5.0,
        )
        return r.json().get("matches", [])

    def invoke(self, product_id: str, capability_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        r = httpx.post(
            self.base_url + "/ai-market/v2/invoke",
            json={"product_id": product_id, "capability_id": capability_id, "payload": payload},
            timeout=10.0,
        )
        return r.json()

    def verify_receipt(self, receipt: dict[str, Any]) -> bool:
        return verify_receipt(receipt, _HUB_SECRET)


@contextlib.contextmanager
def embedded_hub_lite() -> Iterator[HubLiteClient]:
    """Boot hub-lite in-process and yield a client (~2 s cold start)."""
    server = _ThreadedUvicorn(_build_app(), _free_port())
    server.start(ready_path="/.well-known/ai-market.json")
    client = HubLiteClient(f"http://127.0.0.1:{server.port}")
    try:
        yield client
    finally:
        server.stop()
