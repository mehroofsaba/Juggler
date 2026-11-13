"""The ten textbook production rules for the 4 L / 3 L Water Jug Problem.

Every rule is an independent object with
  * an id and name,
  * a precondition (explain() returns None when applicable, else the reason),
  * a state transformation (apply()).

R3 and R4 discard an arbitrary quantity. They are available in manual play
but excluded from AI search (SEARCH_RULES) - otherwise the AI could reach the
goal instantly by just throwing water away.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from .state import CAP_A, CAP_B, State


class RuleError(Exception):
    """Raised when a rule is applied to a state that violates its precondition."""


@dataclass(frozen=True)
class Rule:
    id: str
    name: str
    formula: str
    description: str
    check: Callable[[State, Optional[int]], Optional[str]]
    transform: Callable[[State, Optional[int]], State]
    needs_amount: bool = False

    def explain(self, s: State, amount: Optional[int] = None) -> Optional[str]:
        """None if the rule applies to `s`; otherwise a human-readable reason."""
        return self.check(s, amount)

    def applicable(self, s: State, amount: Optional[int] = None) -> bool:
        return self.check(s, amount) is None

    def apply(self, s: State, amount: Optional[int] = None) -> State:
        reason = self.check(s, amount)
        if reason is not None:
            raise RuleError(f"{self.id} cannot be applied to {s}: {reason}")
        return self.transform(s, amount)


# ---- preconditions / transformations -------------------------------------

def _c1(s, a): return None if s.i < CAP_A else f"the {CAP_A}L jug is already full"
def _t1(s, a): return State(CAP_A, s.j)

def _c2(s, a): return None if s.j < CAP_B else f"the {CAP_B}L jug is already full"
def _t2(s, a): return State(s.i, CAP_B)

def _discard_check(level, label):
    def check(s, a):
        have = level(s)
        if have == 0:
            return f"the {label} jug is empty"
        if a is None:
            return "this rule needs an amount to discard"
        if not (1 <= a <= have):
            return f"amount must be between 1 and {have}"
        return None
    return check

def _t3(s, a): return State(s.i - a, s.j)
def _t4(s, a): return State(s.i, s.j - a)

def _c5(s, a): return None if s.i > 0 else f"the {CAP_A}L jug is already empty"
def _t5(s, a): return State(0, s.j)

def _c6(s, a): return None if s.j > 0 else f"the {CAP_B}L jug is already empty"
def _t6(s, a): return State(s.i, 0)

def _c7(s, a):
    if s.j == 0: return f"the {CAP_B}L jug is empty"
    if s.i + s.j < CAP_A: return f"i + j = {s.i + s.j} < {CAP_A}: not enough water to fill the {CAP_A}L jug"
    return None
def _t7(s, a): return State(CAP_A, s.j - (CAP_A - s.i))

def _c8(s, a):
    if s.i == 0: return f"the {CAP_A}L jug is empty"
    if s.i + s.j < CAP_B: return f"i + j = {s.i + s.j} < {CAP_B}: not enough water to fill the {CAP_B}L jug"
    return None
def _t8(s, a): return State(s.i - (CAP_B - s.j), CAP_B)

def _c9(s, a):
    if s.j == 0: return f"the {CAP_B}L jug is empty"
    if s.i + s.j > CAP_A: return f"i + j = {s.i + s.j} > {CAP_A}: all of it would not fit in the {CAP_A}L jug"
    return None
def _t9(s, a): return State(s.i + s.j, 0)

def _c10(s, a):
    if s.i == 0: return f"the {CAP_A}L jug is empty"
    if s.i + s.j > CAP_B: return f"i + j = {s.i + s.j} > {CAP_B}: all of it would not fit in the {CAP_B}L jug"
    return None
def _t10(s, a): return State(0, s.i + s.j)


RULES: tuple[Rule, ...] = (
    Rule("R1", "Fill 4L jug", "(i, j) -> (4, j)   if i < 4",
         "Fill the four-litre jug from the tap.", _c1, _t1),
    Rule("R2", "Fill 3L jug", "(i, j) -> (i, 3)   if j < 3",
         "Fill the three-litre jug from the tap.", _c2, _t2),
    Rule("R3", "Discard from 4L jug", "(i, j) -> (i - d, j)   if i > 0, 0 < d <= i",
         "Pour away a chosen quantity d from the four-litre jug. Manual play only.",
         _discard_check(lambda s: s.i, "4L"), _t3, needs_amount=True),
    Rule("R4", "Discard from 3L jug", "(i, j) -> (i, j - d)   if j > 0, 0 < d <= j",
         "Pour away a chosen quantity d from the three-litre jug. Manual play only.",
         _discard_check(lambda s: s.j, "3L"), _t4, needs_amount=True),
    Rule("R5", "Empty 4L jug", "(i, j) -> (0, j)   if i > 0",
         "Empty the four-litre jug on the ground.", _c5, _t5),
    Rule("R6", "Empty 3L jug", "(i, j) -> (i, 0)   if j > 0",
         "Empty the three-litre jug on the ground.", _c6, _t6),
    Rule("R7", "Pour 3L -> 4L until 4L full", "(i, j) -> (4, j - (4 - i))   if i + j >= 4, j > 0",
         "Pour from the three-litre jug into the four-litre jug until the latter is full.", _c7, _t7),
    Rule("R8", "Pour 4L -> 3L until 3L full", "(i, j) -> (i - (3 - j), 3)   if i + j >= 3, i > 0",
         "Pour from the four-litre jug into the three-litre jug until the latter is full.", _c8, _t8),
    Rule("R9", "Pour all 3L -> 4L", "(i, j) -> (i + j, 0)   if i + j <= 4, j > 0",
         "Pour all water from the three-litre jug into the four-litre jug.", _c9, _t9),
    Rule("R10", "Pour all 4L -> 3L", "(i, j) -> (0, i + j)   if i + j <= 3, i > 0",
         "Pour all water from the four-litre jug into the three-litre jug.", _c10, _t10),
)

RULES_BY_ID = {r.id: r for r in RULES}
SEARCH_RULES: tuple[Rule, ...] = tuple(r for r in RULES if not r.needs_amount)


def get_rule(token: str) -> Rule:
    """Look up a rule by 'R7', 'r7' or '7'."""
    t = token.strip().upper()
    if t.isdigit():
        t = "R" + t
    if t not in RULES_BY_ID:
        raise KeyError(f"Unknown rule '{token}'. Use R1 .. R10.")
    return RULES_BY_ID[t]


def successors(s: State, rules=SEARCH_RULES) -> list[tuple[Rule, State]]:
    """All (rule, next_state) pairs reachable in one step, in rule order.

    Rules whose result equals the current state are skipped (no-ops).
    """
    out = []
    for rule in rules:
        if rule.applicable(s):
            nxt = rule.apply(s)
            if nxt != s:
                out.append((rule, nxt))
    return out
