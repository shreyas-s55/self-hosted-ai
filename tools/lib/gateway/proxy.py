"""Runtime proxy.

Forwards requests from gateway routes to the upstream inference runtime.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

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
        runtime_url: str | None = None,
    ) -> Response | StreamingResponse:
        """Forward a request to the runtime."""

        headers = _safe_headers(request.headers)
        target_url = _build_target_url(runtime_url, path)

        print("\n========== GATEWAY REQUEST ==========")
        print("Target:", target_url)

        try:
            print(body.decode("utf-8"))
        except UnicodeDecodeError:
            print(body)

        if stream:
            return StreamingResponse(
                self._stream(target_url, body, headers),
                media_type="text/event-stream",
            )

        upstream = await self._client.post(
            target_url,
            content=body,
            headers=headers,
        )

        if upstream.status_code >= 400:
            print("\n========== UPSTREAM RESPONSE ==========")
            print("Status:", upstream.status_code)
            print(dict(upstream.headers))
            print("\n========== UPSTREAM ERROR BODY ==========")
            print(upstream.text)

        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            media_type=upstream.headers.get("content-type"),
        )

    async def _stream(
        self,
        url: str,
        body: bytes,
        headers: dict[str, str],
    ) -> AsyncIterator[bytes]:
        async with self._client.stream(
            "POST",
            url,
            content=body,
            headers=headers,
        ) as upstream:

            if upstream.status_code >= 400:
                print("\n========== STREAM RESPONSE ==========")
                print("Status:", upstream.status_code)
                print(dict(upstream.headers))

                error = await upstream.aread()

                print("\n========== STREAM ERROR BODY ==========")
                print(error.decode(errors="replace"))

                yield error
                return

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


def _build_target_url(runtime_url: str | None, path: str) -> str:
    if runtime_url:
        return f"{runtime_url.rstrip('/')}{path}"
    return path