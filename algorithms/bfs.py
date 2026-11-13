"""Breadth First Search: FIFO queue, visited set, parent references."""
from __future__ import annotations

from collections import deque

from engine.rules import successors
from engine.state import GOAL_A, INITIAL, State

from .metrics import SearchResult, TraceStep


def reconstruct(parent: dict, end: State):
    """Walk parent links back to the start. Returns (path, rule_ids)."""
    path, rules = [end], []
    while parent[path[-1]] is not None:
        prev, rule_id = parent[path[-1]]
        rules.append(rule_id)
        path.append(prev)
    path.reverse()
    rules.reverse()
    return path, rules


def bfs(start: State = INITIAL, goal: int = GOAL_A) -> SearchResult:
    res = SearchResult("BFS", start, goal, found=False)
    parent = {start: None}
    depth = {start: 0}
    frontier = deque([start])
    res.max_frontier = 1

    if start.is_goal(goal):
        res.found, res.path = True, [start]
        return res

    while frontier:
        current = frontier.popleft()
        res.explored += 1
        step = TraceStep(res.explored, current, depth[current], 0)

        for rule, nxt in successors(current):
            res.generated += 1
            if nxt in parent:
                step.children.append((rule.id, nxt, "seen"))
                continue
            parent[nxt] = (current, rule.id)
            depth[nxt] = depth[current] + 1
            step.children.append((rule.id, nxt, "new"))
            if nxt.is_goal(goal):          # goal test on generation: shortest by edges
                step.frontier_size = len(frontier)
                res.trace.append(step)
                res.found = True
                res.path, res.rules = reconstruct(parent, nxt)
                return res
            frontier.append(nxt)

        step.frontier_size = len(frontier)
        res.max_frontier = max(res.max_frontier, len(frontier))
        res.trace.append(step)

    return res
