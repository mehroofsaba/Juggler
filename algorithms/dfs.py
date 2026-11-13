"""Depth First Search: explicit stack, visited set, parent references.

DFS finds *a* solution, not necessarily the shortest one.
"""
from __future__ import annotations

from engine.rules import successors
from engine.state import GOAL_A, INITIAL, State

from .bfs import reconstruct
from .metrics import SearchResult, TraceStep


def dfs(start: State = INITIAL, goal: int = GOAL_A) -> SearchResult:
    res = SearchResult("DFS", start, goal, found=False)
    parent: dict = {}
    depth: dict = {}
    stack = [(start, None, None, 0)]       # (state, parent_state, rule_id, depth)
    res.max_frontier = 1

    while stack:
        current, par, rule_id, d = stack.pop()
        if current in parent:               # already visited via an earlier branch
            continue
        parent[current] = None if par is None else (par, rule_id)
        depth[current] = d
        res.explored += 1
        step = TraceStep(res.explored, current, d, 0)

        if current.is_goal(goal):
            step.frontier_size = len(stack)
            res.trace.append(step)
            res.found = True
            res.path, res.rules = reconstruct(parent, current)
            return res

        children = successors(current)
        for rule, nxt in children:
            res.generated += 1
            step.children.append((rule.id, nxt, "seen" if nxt in parent else "new"))
        # push in reverse so the lowest-numbered rule is explored first
        for rule, nxt in reversed(children):
            if nxt not in parent:
                stack.append((nxt, current, rule.id, d + 1))

        step.frontier_size = len(stack)
        res.max_frontier = max(res.max_frontier, len(stack))
        res.trace.append(step)

    return res
