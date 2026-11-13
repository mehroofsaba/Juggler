"""Manual-play session: the player applies production rules one at a time."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .rules import Rule, get_rule
from .state import GOAL_A, INITIAL, State


@dataclass(frozen=True)
class Move:
    rule: Rule
    before: State
    after: State
    amount: Optional[int] = None


class Game:
    def __init__(self, start: State = INITIAL, goal: int = GOAL_A) -> None:
        self.start = start
        self.goal = goal
        self.state = start
        self.history: list[Move] = []

    @property
    def moves(self) -> int:
        return len(self.history)

    @property
    def won(self) -> bool:
        return self.state.is_goal(self.goal)

    def apply(self, rule_token: str, amount: Optional[int] = None) -> Move:
        """Apply a rule. Raises KeyError for unknown rules, RuleError if inapplicable."""
        rule = get_rule(rule_token)
        after = rule.apply(self.state, amount)
        move = Move(rule, self.state, after, amount)
        self.history.append(move)
        self.state = after
        return move

    def undo(self) -> Optional[Move]:
        if not self.history:
            return None
        move = self.history.pop()
        self.state = move.before
        return move

    def reset(self) -> None:
        self.state = self.start
        self.history.clear()
