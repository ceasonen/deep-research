"""A tiny in-memory TTL cache for query-level results."""

from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any


@dataclass
class CacheEntry:
    expires_at: float
    value: Any


class TTLCache:
    def __init__(self, ttl_seconds: int = 1800, max_size: int = 1024) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._data: OrderedDict[str, CacheEntry] = OrderedDict()

    def get(self, key: str) -> Any | None:
        entry = self._data.get(key)
        if not entry:
            return None

        if entry.expires_at < time.time():
            self._data.pop(key, None)
            return None

        self._data.move_to_end(key)
        return entry.value

    def set(self, key: str, value: Any) -> None:
        if key in self._data:
            self._data.move_to_end(key)

        self._data[key] = CacheEntry(expires_at=time.time() + self.ttl_seconds, value=value)

        while len(self._data) > self.max_size:
            self._data.popitem(last=False)
