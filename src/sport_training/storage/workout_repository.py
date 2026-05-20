from __future__ import annotations

from typing import Protocol
from uuid import UUID

from sport_training.models.workout import Workout


class WorkoutRepository(Protocol):
    def save(self, workout: Workout) -> None: ...

    def find_by_athlete(self, athlete_id: UUID) -> list[Workout]: ...
