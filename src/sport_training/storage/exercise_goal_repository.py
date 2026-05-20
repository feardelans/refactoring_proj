from __future__ import annotations

from typing import Protocol
from uuid import UUID

from sport_training.models.exercise import ExerciseGoal


class ExerciseGoalRepository(Protocol):
    def save(self, goal: ExerciseGoal) -> None: ...

    def find_by_id(self, goal_id: UUID) -> ExerciseGoal | None: ...

    def find_by_athlete(self, athlete_id: UUID) -> list[ExerciseGoal]: ...

    def find_by_athlete_and_exercise(
        self, athlete_id: UUID, exercise_id: UUID
    ) -> list[ExerciseGoal]: ...
