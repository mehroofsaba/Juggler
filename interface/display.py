"""Rendering helpers: every visual is built from real engine / search data."""
from __future__ import annotations

from rich import box
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from algorithms.metrics import SearchResult
from algorithms.solver import StateSpace
from engine.rules import RULES, Rule
from engine.state import CAP_A, CAP_B, GOAL_A, State

CYAN, BLUE, SILVER, GREEN = "cyan", "dodger_blue2", "grey82", "green3"

_LETTERS = {
    "J": ["     ██╗", "     ██║", "     ██║", "██   ██║", "╚█████╔╝", " ╚════╝ "],
    "U": ["██╗   ██╗", "██║   ██║", "██║   ██║", "██║   ██║", "╚██████╔╝", " ╚═════╝ "],
    "G": [" ██████╗ ", "██╔════╝ ", "██║  ███╗", "██║   ██║", "╚██████╔╝", " ╚═════╝ "],
    "L": ["██╗     ", "██║     ", "██║     ", "██║     ", "███████╗", "╚══════╝"],
    "E": ["███████╗", "██╔════╝", "█████╗  ", "██╔══╝  ", "███████╗", "╚══════╝"],
    "R": ["██████╗ ", "██╔══██╗", "██████╔╝", "██╔══██╗", "██║  ██║", "╚═╝  ╚═╝"],
}


def banner() -> Panel:
    rows = ["".join(_LETTERS[c][r] for c in "JUGGLER") for r in range(6)]
    title = Text("\n".join(rows), style=f"bold {CYAN}")
    sub = Text("\nAn interactive terminal laboratory for the Water Jug Problem\n"
               "production rules  ·  state-space search  ·  BFS / DFS\n"
               "EXPERIMENT 4L/3L  ·  START (0,0)  ·  GOAL i = 2", style=SILVER, justify="center")
    return Panel(Align.center(Group(Align.center(title), Align.center(sub))),
                 border_style=BLUE, box=box.DOUBLE, padding=(1, 2))


# ---- jugs ----------------------------------------------------------------

def jug_text(level: int, cap: int, label: str, goal: bool = False) -> Text:
    t = Text()
    t.append(f"   {label}\n", style=f"bold {CYAN}")
    for row in range(cap, 0, -1):
        t.append(f"{row} ", style="grey50")
        t.append("│", style=SILVER)
        if level >= row:
            t.append("≈≈≈≈≈≈" if row == level else "▓▓▓▓▓▓", style=BLUE if row != level else CYAN)
        else:
            t.append("      ")
        t.append("│\n", style=SILVER)
    t.append("  ╰──────╯\n", style=SILVER)
    t.append(f"  {level}/{cap} L", style=f"bold {GREEN}" if goal else "bold white")
    return t


def jugs_group(i: int, j: int, goal: int = GOAL_A) -> Table:
    grid = Table.grid(padding=(0, 6))
    grid.add_column()
    grid.add_column()
    grid.add_row(jug_text(i, CAP_A, "4L JUG", goal=(i == goal)), jug_text(j, CAP_B, "3L JUG"))
    return grid


def jugs_panel(i: int, j: int, title: str = "", subtitle: str = "", goal: int = GOAL_A) -> Panel:
    reached = i == goal
    return Panel(Align.center(jugs_group(i, j, goal)), title=title or f"STATE ({i},{j})",
                 subtitle=subtitle or ("GOAL REACHED" if reached else ""),
                 border_style=GREEN if reached else BLUE)


# ---- rules ---------------------------------------------------------------

def rules_table() -> Table:
    t = Table(title="PRODUCTION RULES", box=box.SIMPLE_HEAD, header_style=f"bold {CYAN}")
    for col in ("ID", "Rule", "Transformation", "Used by AI"):
        t.add_column(col)
    for r in RULES:
        t.add_row(r.id, r.name, r.formula, "no (manual only)" if r.needs_amount else "yes")
    return t


def rule_check_table(state: State) -> Table:
    t = Table(title=f"RULES vs STATE {state}", box=box.SIMPLE_HEAD, header_style=f"bold {CYAN}")
    for col in ("Rule", "Applicable", "Result / reason"):
        t.add_column(col)
    for r in RULES:
        amount = 1 if r.needs_amount else None
        why = r.explain(state, amount)
        if why is None:
            note = f"{r.apply(state, amount)}" + ("  (testing with d = 1)" if r.needs_amount else "")
            t.add_row(f"{r.id} {r.name}", Text("yes", style=GREEN), note)
        else:
            t.add_row(f"{r.id} {r.name}", Text("no", style="red"), why)
    return t


def move_line(rule: Rule, before: State, after: State, amount=None) -> Text:
    extra = f" (d={amount})" if amount is not None else ""
    return Text.assemble((f"{rule.id}", f"bold {CYAN}"), f" {rule.name}{extra}:  ",
                         (str(before), SILVER), "  →  ", (str(after), f"bold {GREEN}"))


# ---- search output -------------------------------------------------------

def trace_table(res: SearchResult, limit: int = 40) -> Table:
    t = Table(title=f"{res.algorithm} EXPLORATION ORDER", box=box.SIMPLE_HEAD,
              header_style=f"bold {CYAN}")
    for col in ("#", "Expanded", "Depth", "Generated (rule → state)", "Frontier"):
        t.add_column(col)
    for step in res.trace[:limit]:
        kids = "  ".join(f"{rid}→{st}{'' if tag == 'new' else '*'}" for rid, st, tag in step.children)
        t.add_row(str(step.order), str(step.state), str(step.depth), kids or "-", str(step.frontier_size))
    if len(res.trace) > limit:
        t.caption = f"... {len(res.trace) - limit} more expansions (* = already visited)"
    else:
        t.caption = "* = already visited"
    return t


def path_table(res: SearchResult) -> Table:
    t = Table(title=f"{res.algorithm} SOLUTION PATH", box=box.SIMPLE_HEAD, header_style=f"bold {CYAN}")
    for col in ("Step", "Rule", "State"):
        t.add_column(col)
    t.add_row("0", "-", str(res.path[0]))
    for k, rid in enumerate(res.rules, start=1):
        t.add_row(str(k), rid, str(res.path[k]))
    return t


def metrics_table(results: list[SearchResult]) -> Table:
    t = Table(title="ALGORITHM LABORATORY", box=box.SIMPLE_HEAD, header_style=f"bold {CYAN}")
    t.add_column("Metric")
    for r in results:
        t.add_column(r.algorithm, justify="right")
    rows = [
        ("Solution found", lambda r: "yes" if r.found else "no"),
        ("Path length (transitions)", lambda r: str(r.path_length)),
        ("States generated", lambda r: str(r.generated)),
        ("States explored", lambda r: str(r.explored)),
        ("Max frontier size", lambda r: str(r.max_frontier)),
        ("Search depth reached", lambda r: str(r.depth)),
        ("Execution time (ms)", lambda r: f"{r.time_ms:.3f}"),
        ("Peak memory (KiB)", lambda r: "-" if r.peak_memory_kb is None else f"{r.peak_memory_kb:.1f}"),
    ]
    for label, fn in rows:
        t.add_row(label, *[fn(r) for r in results])
    return t


def state_space_table(ss: StateSpace) -> Table:
    out = {}
    for a, rid, b in ss.edges:
        out.setdefault(a, []).append(f"{rid}→{b}")
    t = Table(title="REACHABLE STATE SPACE", box=box.SIMPLE_HEAD, header_style=f"bold {CYAN}")
    for col in ("Level", "State", "Goal?", "Reaches goal", "Outgoing transitions"):
        t.add_column(col)
    for s in sorted(ss.states, key=lambda x: (ss.levels[x], x)):
        t.add_row(str(ss.levels[s]), str(s), Text("GOAL", style=GREEN) if s.is_goal() else "",
                  "yes" if s in ss.can_reach_goal else "NO (dead end)", "  ".join(out.get(s, [])))
    return t
