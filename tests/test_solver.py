import pytest

from algorithms.bfs import bfs
from algorithms.dfs import dfs
from algorithms.solver import (TEXTBOOK_RULES, TEXTBOOK_STATES, compare, solve,
                               state_space, validate_textbook, verify_path)
from engine.state import INITIAL, State, all_states


def test_bfs_finds_shortest_path():
    r = bfs()
    assert r.found and r.path[0] == INITIAL and r.path[-1].is_goal()
    assert r.path_length == 6          # textbook optimum
    assert len(r.rules) == r.path_length


def test_dfs_finds_valid_solution():
    r = dfs()
    assert r.found and r.path[0] == INITIAL and r.path[-1].is_goal()
    assert r.path_length >= bfs().path_length      # never shorter than BFS


def test_paths_are_made_of_legal_transitions():
    for r in (bfs(), dfs()):
        assert verify_path(r.path, r.rules) == r.rules
        assert len(verify_path(r.path)) == r.path_length


def test_verify_path_rejects_illegal_step():
    with pytest.raises(ValueError):
        verify_path([State(0, 0), State(2, 0)])
    with pytest.raises(ValueError):
        verify_path([State(0, 0), State(4, 0)], ["R2"])


def test_metrics_are_real():
    r = solve("bfs")
    assert r.explored == len(r.trace) > 0
    assert r.generated >= r.explored
    assert r.max_frontier >= 1
    assert r.time_ms >= 0 and r.peak_memory_kb is not None
    assert r.generated == sum(len(t.children) for t in r.trace)


def test_start_already_goal():
    r = bfs(State(2, 0))
    assert r.found and r.path_length == 0


def test_unknown_algorithm():
    with pytest.raises(KeyError):
        solve("astar")


def test_compare_runs_both():
    names = [r.algorithm for r in compare()]
    assert names == ["BFS", "DFS"]


def test_textbook_sequence():
    steps = validate_textbook()
    assert len(steps) == 6
    assert [s[0] for s in steps] == TEXTBOOK_RULES
    assert steps[-1][2] == TEXTBOOK_STATES[-1] == State(2, 3)
    assert verify_path(TEXTBOOK_STATES, TEXTBOOK_RULES) == TEXTBOOK_RULES


def test_state_space_is_valid_subset():
    ss = state_space()
    assert set(ss.states) <= set(all_states())
    assert len(ss.states) == 14                     # 14 of the 20 pairs are reachable
    assert State(1, 1) not in ss.states
    assert ss.dead_ends == []
    assert all(s.is_goal() for s in ss.goal_states)
    assert ss.levels[INITIAL] == 0
