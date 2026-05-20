from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class TrainingGoal:
    id: UUID
    athlete_id: UUID
    title: str
    target_workouts: int
    completed_workouts: int = 0

    def __post_init__(self) -> None:
        if self.target_workouts <= 0:
            msg = "target_workouts must be positive"
            raise ValueError(msg)
        if self.completed_workouts < 0 or self.completed_workouts > self.target_workouts:
            msg = "completed_workouts out of range"
            raise ValueError(msg)

    def increment_completed(self, points: int = 1) -> None:
        for _ in range(points):
            if self.is_achieved():
                return
            self.completed_workouts += 1

    def is_achieved(self) -> bool:
        return self.completed_workouts >= self.target_workouts
