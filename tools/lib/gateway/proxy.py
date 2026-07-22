"""Runtime proxy.

Forwards requests from gateway routes to the upstream inference runtime.
"""

from __future__ import annotations

from typing import AsyncIterator

import httpx
from fastapi import Request
from fastapi.responses import Response, StreamingResponse


class RuntimeProxy:
    """Transparent HTTP proxy to the upstream inference runtime."""

    def __init__(self, runtime_url: str) -> None:
        self._client = httpx.AsyncClient(
            base_url=runtime_url,
            timeout=httpx.Timeout(
                connect=10.0,
                read=300.0,
                write=30.0,
                pool=10.0,
            ),
        )

    async def forward(
        self,
        *,
        request: Request,
        path: str,
        body: bytes,
        stream: bool,
    ) -> Response | StreamingResponse:
        """Forward a request to the runtime."""

        headers = _safe_headers(request.headers)

        if stream:
            return StreamingResponse(
                self._stream(path, body, headers),
                media_type="text/event-stream",
            )

        upstream = await self._client.post(
            path,
            content=body,
            headers=headers,
        )

        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            media_type=upstream.headers.get("content-type"),
        )

    async def _stream(
        self,
        path: str,
        body: bytes,
        headers: dict[str, str],
    ) -> AsyncIterator[bytes]:
        async with self._client.stream(
            "POST",
            path,
            content=body,
            headers=headers,
        ) as upstream:
            async for chunk in upstream.aiter_raw():
                yield chunk

    async def close(self) -> None:
        await self._client.aclose()


def _safe_headers(headers: httpx.Headers) -> dict[str, str]:
    excluded = frozenset(
        {
            "host",
            "content-length",
            "transfer-encoding",
            "connection",
        }
    )

    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in excluded
    }