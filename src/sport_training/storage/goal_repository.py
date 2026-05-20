from __future__ import annotations

from typing import Protocol
from uuid import UUID

from sport_training.models.goal import TrainingGoal


class GoalRepository(Protocol):
    def save(self, goal: TrainingGoal) -> None: ...

    def find_by_id(self, goal_id: UUID) -> TrainingGoal | None: ...

    def find_by_athlete(self, athlete_id: UUID) -> list[TrainingGoal]: ...
