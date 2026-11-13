"""Result containers and measurement helpers shared by the search algorithms."""
from __future__ import annotations

import time
import tracemalloc
from dataclasses import dataclass, field
from typing import Optional

from engine.state import State


@dataclass
class TraceStep:
    """One node expansion, recorded exactly as the search performed it."""
    order: int                      # expansion number (1-based)
    state: State
    depth: int
    frontier_size: int              # frontier size right after expansion
    children: list[tuple[str, State, str]] = field(default_factory=list)
    # children: (rule_id, child_state, status) status in {"new", "seen"}


@dataclass
class SearchResult:
    algorithm: str
    start: State
    goal: int
    found: bool
    path: list[State] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)   # rules[k] turns path[k] into path[k+1]
    trace: list[TraceStep] = field(default_factory=list)
    generated: int = 0              # successor states produced
    explored: int = 0               # states expanded
    max_frontier: int = 0
    time_ms: float = 0.0
    peak_memory_kb: Optional[float] = None

    @property
    def path_length(self) -> int:
        return max(len(self.path) - 1, 0)

    @property
    def depth(self) -> int:
        """Deepest level reached during the search."""
        return max((t.depth for t in self.trace), default=0)


def timed(fn, *args, **kwargs):
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    return result, (time.perf_counter() - t0) * 1000.0


def peak_memory_kb(fn, *args, **kwargs) -> float:
    tracemalloc.start()
    try:
        fn(*args, **kwargs)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return peak / 1024.0
