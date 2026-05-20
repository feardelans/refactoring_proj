from __future__ import annotations

from typing import Protocol
from uuid import UUID

from sport_training.models.exercise import ExerciseLog


class ExerciseLogRepository(Protocol):
    def save(self, log: ExerciseLog) -> None: ...

    def find_by_athlete(self, athlete_id: UUID) -> list[ExerciseLog]: ...

    def find_by_athlete_and_exercise(
        self, athlete_id: UUID, exercise_id: UUID
    ) -> list[ExerciseLog]: ...
