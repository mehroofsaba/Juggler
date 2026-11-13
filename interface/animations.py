"""Transition animations. Frames interpolate between the real before/after states."""
from __future__ import annotations

import time

from rich.console import Console
from rich.live import Live

from engine.state import State

from .display import jugs_panel


def pour(console: Console, before: State, after: State, label: str = "",
         enabled: bool = True, delay: float = 0.12) -> None:
    """Animate before -> after, then leave the final frame on screen.

    Falls back to a single static frame when animation is disabled or the
    output is not an interactive terminal.
    """
    if not enabled or not console.is_terminal:
        console.print(jugs_panel(after.i, after.j, subtitle=label))
        return
    steps = max(abs(after.i - before.i), abs(after.j - before.j), 1)
    with Live(console=console, refresh_per_second=20, transient=False) as live:
        for k in range(steps + 1):
            f = k / steps
            i = round(before.i + (after.i - before.i) * f)
            j = round(before.j + (after.j - before.j) * f)
            live.update(jugs_panel(i, j, subtitle=label if k == steps else "pouring..."))
            time.sleep(delay)


def thinking(console: Console, text: str, enabled: bool = True, seconds: float = 0.6) -> None:
    """Short loading indicator (skipped when animation is unavailable)."""
    if not enabled or not console.is_terminal:
        return
    with console.status(f"[cyan]{text}[/cyan]", spinner="dots"):
        time.sleep(seconds)
