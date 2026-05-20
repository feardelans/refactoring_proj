from __future__ import annotations

from uuid import UUID

from sport_training.models.exercise import Exercise


class InMemoryExerciseRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, Exercise] = {}

    def save(self, exercise: Exercise) -> None:
        self._by_id[exercise.id] = exercise

    def find_by_id(self, exercise_id: UUID) -> Exercise | None:
        return self._by_id.get(exercise_id)

    def find_all(self) -> list[Exercise]:
        return list(self._by_id.values())
