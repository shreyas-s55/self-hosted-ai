"""Runtime health check utility.

The gateway's own ``/health`` endpoint always returns ``ok`` when the
process is running.  This module provides a utility for checking the
upstream runtime health — useful for startup probes or status endpoints
that want to surface downstream health.
"""

import asyncio

import httpx

from lib.gateway.deployment import GatewayDeploymentRegistry


async def check_runtime_health(runtime_url: str) -> bool:
    """Return ``True`` if the runtime health endpoint is reachable.

    Derives the health URL from the runtime base URL by stripping the
    ``/v1`` path suffix (e.g. ``http://vllm:8000/v1`` → ``http://vllm:8000/health``).

    Args:
        runtime_url: The runtime's OpenAI-compatible base URL.

    Returns:
        ``True`` if the runtime responds with HTTP 200, ``False`` otherwise.
    """
    base = runtime_url.rstrip("/")
    if base.endswith("/v1"):
        base = base[:-3]
    health_url = f"{base}/health"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(health_url)
            return response.status_code == 200
    except httpx.HTTPError:
        return False


async def check_deployments_health(
    deployments: GatewayDeploymentRegistry,
) -> dict[str, str]:
    """Return health status for each configured deployment alias."""

    aliases = deployments.aliases()
    checks = [
        check_runtime_health(deployments.resolve(alias).runtime_url)
        for alias in aliases
    ]

    results = await asyncio.gather(*checks, return_exceptions=True)

    status: dict[str, str] = {}

    for alias, result in zip(aliases, results):
        if isinstance(result, Exception):
            status[alias] = "unhealthy"
        else:
            status[alias] = "healthy" if result else "unhealthy"

    return status
