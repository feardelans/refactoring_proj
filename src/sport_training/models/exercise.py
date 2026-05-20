from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass
class Exercise:
    id: UUID
    name: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            msg = "name must not be empty"
            raise ValueError(msg)


@dataclass
class ExerciseGoal:
    id: UUID
    athlete_id: UUID
    exercise_id: UUID
    title: str
    target_amount: int
    completed_amount: int = 0

    def __post_init__(self) -> None:
        if self.target_amount <= 0:
            msg = "target_amount must be positive"
            raise ValueError(msg)
        if self.completed_amount < 0 or self.completed_amount > self.target_amount:
            msg = "completed_amount out of range"
            raise ValueError(msg)

    def increment_completed(self, amount: int) -> None:
        if amount <= 0:
            return
        remaining = self.target_amount - self.completed_amount
        self.completed_amount += min(amount, remaining)

    def is_achieved(self) -> bool:
        return self.completed_amount >= self.target_amount


@dataclass(frozen=True)
class ExerciseLog:
    id: UUID
    athlete_id: UUID
    exercise_id: UUID
    date: date
    amount: int

    def __post_init__(self) -> None:
        if self.amount <= 0:
            msg = "amount must be positive"
            raise ValueError(msg)
