"""Unified solver API, independent path verification, state-space generation
and textbook-solution validation."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from engine.rules import RULES_BY_ID, RuleError, get_rule, successors
from engine.state import GOAL_A, INITIAL, State

from .bfs import bfs
from .dfs import dfs
from .metrics import SearchResult, peak_memory_kb, timed

ALGORITHMS = {"bfs": bfs, "dfs": dfs}

# The verified textbook sequence (6 transitions).
TEXTBOOK_RULES = ["R1", "R8", "R6", "R10", "R1", "R8"]
TEXTBOOK_STATES = [State(0, 0), State(4, 0), State(1, 3), State(1, 0),
                   State(0, 1), State(4, 1), State(2, 3)]


def solve(name: str, start: State = INITIAL, goal: int = GOAL_A,
          measure_memory: bool = True) -> SearchResult:
    """Run a search by name ('bfs' / 'dfs') and attach real timing + memory."""
    key = name.lower()
    if key not in ALGORITHMS:
        raise KeyError(f"Unknown algorithm '{name}'. Choose from: {', '.join(ALGORITHMS)}")
    fn = ALGORITHMS[key]
    result, ms = timed(fn, start, goal)
    result.time_ms = ms
    if measure_memory:
        result.peak_memory_kb = peak_memory_kb(fn, start, goal)
    return result


def compare(start: State = INITIAL, goal: int = GOAL_A) -> list[SearchResult]:
    return [solve(n, start, goal) for n in ALGORITHMS]


def verify_path(path: list[State], rule_ids: list[str] | None = None) -> list[str]:
    """Check that every consecutive pair is joined by a legal production rule.

    Returns the rule ids that justify each transition. If `rule_ids` is given,
    each claimed rule must actually produce the next state. Raises ValueError
    on any illegal transition.
    """
    used = []
    for k in range(len(path) - 1):
        a, b = path[k], path[k + 1]
        if rule_ids is not None:
            claimed = get_rule(rule_ids[k])
            try:
                ok = claimed.apply(a) == b
            except RuleError:
                ok = False
            if not ok:
                raise ValueError(f"Step {k + 1}: {claimed.id} does not turn {a} into {b}")
            used.append(claimed.id)
        else:
            match = [r.id for r, nxt in successors(a) if nxt == b]
            if not match:
                raise ValueError(f"Step {k + 1}: no rule turns {a} into {b}")
            used.append(match[0])
    return used


def validate_textbook() -> list[tuple[str, State, State]]:
    """Apply the textbook rules one by one from (0,0); returns (rule, before, after).

    Raises AssertionError if any state differs from the textbook or the goal is missed.
    """
    s, steps = INITIAL, []
    for k, rid in enumerate(TEXTBOOK_RULES):
        nxt = RULES_BY_ID[rid].apply(s)
        assert nxt == TEXTBOOK_STATES[k + 1], f"{rid}: got {nxt}, expected {TEXTBOOK_STATES[k + 1]}"
        steps.append((rid, s, nxt))
        s = nxt
    assert s.is_goal(), f"final state {s} is not a goal"
    return steps


@dataclass
class StateSpace:
    states: list[State]
    edges: list[tuple[State, str, State]]
    goal_states: list[State]
    can_reach_goal: set
    dead_ends: list[State]          # reachable states from which no goal is reachable
    levels: dict                    # state -> BFS level from the start


def state_space(start: State = INITIAL, goal: int = GOAL_A) -> StateSpace:
    """Exhaustively generate every state reachable from `start` with the search rules."""
    levels = {start: 0}
    edges = []
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        for rule, nxt in successors(cur):
            edges.append((cur, rule.id, nxt))
            if nxt not in levels:
                levels[nxt] = levels[cur] + 1
                queue.append(nxt)

    rev: dict = {}
    for a, _, b in edges:
        rev.setdefault(b, []).append(a)
    goals = [s for s in levels if s.is_goal(goal)]
    good = set(goals)
    q = deque(goals)
    while q:
        node = q.popleft()
        for p in rev.get(node, []):
            if p not in good:
                good.add(p)
                q.append(p)

    states = sorted(levels)
    dead = [s for s in states if s not in good]
    return StateSpace(states, edges, goals, good, dead, levels)
