"""Lightweight in-process metrics registry for the API and agent workflow."""

from __future__ import annotations

from collections import Counter, defaultdict
from threading import Lock
from typing import Dict


class MetricsRegistry:
    """Thread-safe metrics store for counters, gauges and simple timings."""

    def __init__(self) -> None:
        self._counters: Counter[str] = Counter()
        self._timers: defaultdict[str, list[float]] = defaultdict(list)
        self._gauges: dict[str, float] = {}
        self._lock = Lock()

    def increment(self, name: str, value: int = 1) -> None:
        """Increment a named counter."""
        with self._lock:
            self._counters[name] += value

    def observe(self, name: str, value_ms: float) -> None:
        """Record a duration in milliseconds."""
        with self._lock:
            self._timers[name].append(round(value_ms, 2))

    def set_gauge(self, name: str, value: float) -> None:
        """Set or replace a gauge value."""
        with self._lock:
            self._gauges[name] = value

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
                "gauges": dict(self._gauges),
                "timers": timers,
            }

    def render_prometheus(self) -> str:
        """Render metrics using Prometheus text exposition format."""
        with self._lock:
            lines: list[str] = []

            for name, value in sorted(self._counters.items()):
                metric = name.replace(".", "_")
                lines.append(f"# TYPE {metric} counter")
                lines.append(f"{metric} {value}")

            for name, value in sorted(self._gauges.items()):
                metric = name.replace(".", "_")
                lines.append(f"# TYPE {metric} gauge")
                lines.append(f"{metric} {value}")

            for name, values in sorted(self._timers.items()):
                metric = name.replace(".", "_")
                count = len(values)
                total = round(sum(values), 4) if values else 0.0
                max_value = max(values) if values else 0.0
                avg_value = round(total / count, 4) if count else 0.0

                lines.append(f"# TYPE {metric}_count counter")
                lines.append(f"{metric}_count {count}")
                lines.append(f"# TYPE {metric}_sum gauge")
                lines.append(f"{metric}_sum {total}")
                lines.append(f"# TYPE {metric}_avg gauge")
                lines.append(f"{metric}_avg {avg_value}")
                lines.append(f"# TYPE {metric}_max gauge")
                lines.append(f"{metric}_max {max_value}")

            return "\n".join(lines) + "\n"


metrics = MetricsRegistry()