"""Lightweight in-process metrics registry for the API and agent workflow."""

from __future__ import annotations

from collections import Counter, defaultdict
from threading import Lock
from typing import Dict


class MetricsRegistry:
    """Thread-safe metrics store for counters and simple timings."""

    def __init__(self) -> None:
        self._counters: Counter[str] = Counter()
        self._timers: defaultdict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def increment(self, name: str, value: int = 1) -> None:
        """Increment a named counter."""
        with self._lock:
            self._counters[name] += value

    def observe(self, name: str, value_ms: float) -> None:
        """Record a duration in milliseconds."""
        with self._lock:
            self._timers[name].append(round(value_ms, 2))

    def snapshot(self) -> Dict[str, Dict[str, float | int]]:
        """Return current metrics snapshot."""
        with self._lock:
            timers = {
                name: {
                    "count": len(values),
                    "avg_ms": round(sum(values) / len(values), 2) if values else 0.0,
                    "max_ms": max(values) if values else 0.0,
                }
                for name, values in self._timers.items()
            }
            return {
                "counters": dict(self._counters),
                "timers": timers,
            }


metrics = MetricsRegistry()
