"""State representation for the Water Jug Problem.

A state is an ordered pair (i, j):
    i = litres in the 4-litre jug   (0 <= i <= 4)
    j = litres in the 3-litre jug   (0 <= j <= 3)
"""
from __future__ import annotations

import re
from dataclasses import dataclass

CAP_A = 4          # capacity of the large jug
CAP_B = 3          # capacity of the small jug
GOAL_A = 2         # goal: exactly 2 L in the 4 L jug


@dataclass(frozen=True, order=True)
class State:
    i: int
    j: int

    def __post_init__(self) -> None:
        if not (isinstance(self.i, int) and isinstance(self.j, int)):
            raise ValueError("State quantities must be integers")
        if not (0 <= self.i <= CAP_A):
            raise ValueError(f"i must satisfy 0 <= i <= {CAP_A}, got {self.i}")
        if not (0 <= self.j <= CAP_B):
            raise ValueError(f"j must satisfy 0 <= j <= {CAP_B}, got {self.j}")

    def is_goal(self, goal: int = GOAL_A) -> bool:
        return self.i == goal

    def __str__(self) -> str:
        return f"({self.i},{self.j})"

    @classmethod
    def parse(cls, text: str) -> "State":
        """Parse '2,3', '(2,3)' or '2 3' into a State."""
        nums = re.findall(r"-?\d+", text)
        if len(nums) != 2:
            raise ValueError("Enter a state as two numbers, e.g. 2,3")
        return cls(int(nums[0]), int(nums[1]))


INITIAL = State(0, 0)


def all_states() -> list[State]:
    """Every state that satisfies the capacity constraints."""
    return [State(i, j) for i in range(CAP_A + 1) for j in range(CAP_B + 1)]
