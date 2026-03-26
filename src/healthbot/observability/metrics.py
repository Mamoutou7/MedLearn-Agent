"""Lightweight in-process metrics registry for the API and agent workflow."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from threading import Lock
from typing import Dict


@dataclass
class TimerStats:
    count: int = 0
    total_ms: float = 0.0
    max_ms: float = 0.0

    def observe(self, value_ms: float) -> None:
        self.count += 1
        self.total_ms += value_ms
        if value_ms > self.max_ms:
            self.max_ms = value_ms

    @property
    def avg_ms(self) -> float:
        if self.count == 0:
            return 0.0
        return self.total_ms / self.count


class MetricsRegistry:
    def __init__(self) -> None:
        self._counters: Counter[str] = Counter()
        self._timers: dict[str, TimerStats] = {}
        self._gauges: dict[str, float] = {}
        self._lock = Lock()

    def increment(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counters[name] += value

    def observe(self, name: str, value_ms: float) -> None:
        with self._lock:
            stats = self._timers.setdefault(name, TimerStats())
            stats.observe(round(value_ms, 2))

    def set_gauge(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name] = value

    def snapshot(self) -> Dict[str, Dict[str, float | int]]:
        with self._lock:
            timers = {
                name: {
                    "count": stats.count,
                    "avg_ms": round(stats.avg_ms, 2),
                    "max_ms": round(stats.max_ms, 2),
                    "total_ms": round(stats.total_ms, 2),
                }
                for name, stats in self._timers.items()
            }
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "timers": timers,
            }

    def render_prometheus(self) -> str:
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

            for name, stats in sorted(self._timers.items()):
                metric = name.replace(".", "_")

                lines.append(f"# TYPE {metric}_count counter")
                lines.append(f"{metric}_count {stats.count}")

                lines.append(f"# TYPE {metric}_sum gauge")
                lines.append(f"{metric}_sum {round(stats.total_ms, 4)}")

                lines.append(f"# TYPE {metric}_avg gauge")
                lines.append(f"{metric}_avg {round(stats.avg_ms, 4)}")

                lines.append(f"# TYPE {metric}_max gauge")
                lines.append(f"{metric}_max {round(stats.max_ms, 4)}")

            return "\n".join(lines) + "\n"


metrics = MetricsRegistry()