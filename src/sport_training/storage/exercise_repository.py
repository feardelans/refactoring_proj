from __future__ import annotations

from typing import Protocol
from uuid import UUID

from sport_training.models.exercise import Exercise


class ExerciseRepository(Protocol):
    def save(self, exercise: Exercise) -> None: ...

    def find_by_id(self, exercise_id: UUID) -> Exercise | None: ...

    def find_all(self) -> list[Exercise]: ...
