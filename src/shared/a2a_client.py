# HTTP client for A2A inter-agent communication
import httpx
import logging
from typing import Any
from shared.config import INTERNAL_API_KEY

logger = logging.getLogger(__name__)


class A2AClient:
    """
    Lightweight async HTTP client that adds the internal auth header
    and handles errors uniformly across agent calls.
    """

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "x-api-key": INTERNAL_API_KEY,
            "Content-Type": "application/json",
        }
        self.timeout = timeout

    async def get(self, path: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(
                f"{self.base_url}{path}", headers=self.headers
            )
            if r.status_code >= 400:
                try:
                    data = r.json()
                    detail = data.get("detail")
                    if detail:
                        if isinstance(detail, list):
                            messages = [f"{item.get('msg')}" for item in detail]
                            raise ValueError(", ".join(messages))
                        raise ValueError(str(detail))
                except Exception as ex:
                    if isinstance(ex, ValueError):
                        raise ex
            r.raise_for_status()
            return r.json()

    async def post(self, path: str, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}{path}", json=payload, headers=self.headers
            )
            if r.status_code >= 400:
                try:
                    data = r.json()
                    detail = data.get("detail")
                    if detail:
                        if isinstance(detail, list):
                            messages = [f"{item.get('msg')}" for item in detail]
                            raise ValueError(", ".join(messages))
                        raise ValueError(str(detail))
                except Exception as ex:
                    if isinstance(ex, ValueError):
                        raise ex
            r.raise_for_status()
            return r.json()

    async def fetch_agent_card(self) -> dict:
        """Fetch the A2A Agent Card from /.well-known/agent-card"""
        return await self.get("/.well-known/agent-card")