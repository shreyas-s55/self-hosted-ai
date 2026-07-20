"""Runtime proxy.

Forwards requests from gateway routes to the upstream inference runtime.
The proxy is runtime-agnostic: it communicates via the OpenAI HTTP API
and requires only a base URL.

Routes call :meth:`RuntimeProxy.forward` and receive a ``Response`` or
``StreamingResponse`` — they never interact with the runtime directly.
"""

import json
from typing import AsyncIterator

import httpx
from fastapi import Request
from fastapi.responses import Response, StreamingResponse


class RuntimeProxy:
    """Transparent HTTP proxy to the upstream inference runtime.

    Args:
        runtime_url: Base URL of the runtime's OpenAI-compatible API,
            e.g. ``http://vllm:8000/v1``.
    """

    def __init__(self, runtime_url: str) -> None:
        self._client = httpx.AsyncClient(
            base_url=runtime_url,
            timeout=httpx.Timeout(connect=10.0, read=300.0, write=30.0, pool=10.0),
        )

    async def forward(self, request: Request, path: str) -> Response | StreamingResponse:
        """Forward an incoming request to the runtime and return the response.

        Streaming requests (``"stream": true`` in the body) are proxied as
        ``text/event-stream`` Server-Sent Events.  Non-streaming requests
        block and return the full response body.

        Args:
            request: The incoming FastAPI request.
            path: Path on the runtime to forward to (e.g. ``"/chat/completions"``).

        Returns:
            A FastAPI ``Response`` or ``StreamingResponse``.
        """
        body = await request.body()
        headers = _safe_headers(request.headers)

        if _is_streaming(body):
            return StreamingResponse(
                self._stream(path, body, headers),
                media_type="text/event-stream",
            )

        upstream = await self._client.post(path, content=body, headers=headers)
        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            media_type=upstream.headers.get("content-type"),
        )

    async def _stream(
        self, path: str, body: bytes, headers: dict[str, str]
    ) -> AsyncIterator[bytes]:
        async with self._client.stream(
            "POST", path, content=body, headers=headers
        ) as upstream:
            async for chunk in upstream.aiter_raw():
                yield chunk

    async def close(self) -> None:
        """Close the underlying HTTP client connection pool."""
        await self._client.aclose()


# ── Helpers ───────────────────────────────────────────────────────────────────


def _safe_headers(headers: httpx.Headers) -> dict[str, str]:
    """Strip hop-by-hop headers that must not be forwarded."""
    excluded = frozenset({"host", "content-length", "transfer-encoding", "connection"})
    return {k: v for k, v in headers.items() if k.lower() not in excluded}


def _is_streaming(body: bytes) -> bool:
    """Return ``True`` if the request body requests a streaming response."""
    try:
        return bool(json.loads(body).get("stream", False))
    except (json.JSONDecodeError, AttributeError):
        return False
