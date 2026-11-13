import pytest

from engine.game import Game
from engine.rules import RULES, RULES_BY_ID, SEARCH_RULES, RuleError, get_rule, successors
from engine.state import INITIAL, State, all_states


def test_ten_rules_exist():
    assert [r.id for r in RULES] == [f"R{k}" for k in range(1, 11)]


def test_state_bounds():
    with pytest.raises(ValueError):
        State(5, 0)
    with pytest.raises(ValueError):
        State(0, 4)
    with pytest.raises(ValueError):
        State(-1, 0)


def test_state_parse():
    assert State.parse("(2, 3)") == State(2, 3)
    with pytest.raises(ValueError):
        State.parse("abc")


@pytest.mark.parametrize("rule,before,after", [
    ("R1", State(0, 2), State(4, 2)),
    ("R2", State(3, 0), State(3, 3)),
    ("R5", State(3, 2), State(0, 2)),
    ("R6", State(3, 2), State(3, 0)),
    ("R7", State(2, 3), State(4, 1)),
    ("R8", State(4, 0), State(1, 3)),
    ("R8", State(2, 2), State(1, 3)),
    ("R9", State(1, 3), State(4, 0)),
    ("R10", State(1, 2), State(0, 3)),
])
def test_valid_transformations(rule, before, after):
    assert get_rule(rule).apply(before) == after


def test_discard_rules():
    assert RULES_BY_ID["R3"].apply(State(4, 1), 3) == State(1, 1)
    assert RULES_BY_ID["R4"].apply(State(0, 3), 2) == State(0, 1)


@pytest.mark.parametrize("rule,state", [
    ("R1", State(4, 0)), ("R2", State(0, 3)), ("R5", State(0, 2)), ("R6", State(2, 0)),
    ("R7", State(1, 2)), ("R7", State(4, 0)),     # not enough water / empty source
    ("R8", State(1, 1)), ("R8", State(0, 3)),
    ("R9", State(3, 3)), ("R9", State(2, 0)),
    ("R10", State(2, 3)), ("R10", State(0, 2)),
])
def test_invalid_preconditions(rule, state):
    r = get_rule(rule)
    assert not r.applicable(state)
    assert r.explain(state)
    with pytest.raises(RuleError):
        r.apply(state)


def test_discard_validation():
    r3 = RULES_BY_ID["R3"]
    assert not r3.applicable(State(2, 0))             # no amount
    assert not r3.applicable(State(2, 0), 3)          # more than present
    assert not r3.applicable(State(0, 0), 1)          # empty jug
    with pytest.raises(RuleError):
        r3.apply(State(2, 0), 0)


def test_invariants_hold_for_every_rule_and_state():
    for s in all_states():
        for rule in RULES:
            amounts = [None] if not rule.needs_amount else range(0, 6)
            for a in amounts:
                if rule.applicable(s, a):
                    t = rule.apply(s, a)                       # State() validates bounds
                    if rule.id in ("R7", "R8", "R9", "R10"):   # pours conserve water
                        assert t.i + t.j == s.i + s.j


def test_search_rules_exclude_discards():
    assert {r.id for r in SEARCH_RULES} == {"R1", "R2", "R5", "R6", "R7", "R8", "R9", "R10"}
    assert all(r.id not in ("R3", "R4") for r, _ in successors(State(4, 3)))


def test_get_rule_tokens():
    assert get_rule("r7").id == get_rule("7").id == "R7"
    with pytest.raises(KeyError):
        get_rule("R11")


def test_game_play_undo_and_win():
    g = Game()
    for rid in ["R1", "R8", "R6", "R10", "R1", "R8"]:
        g.apply(rid)
    assert g.won and g.moves == 6 and g.state == State(2, 3)
    g.undo()
    assert g.state == State(4, 1) and not g.won
    with pytest.raises(RuleError):
        Game().apply("R5")
    g.reset()
    assert g.state == INITIAL and g.moves == 0
