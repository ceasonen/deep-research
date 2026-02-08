"""Abstract search engine interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseSearchEngine(ABC):
    name = "base"

    @abstractmethod
    async def search(self, query: str, max_results: int = 8) -> list[dict]:
        raise NotImplementedError
