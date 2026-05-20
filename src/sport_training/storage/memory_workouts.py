from __future__ import annotations

from uuid import UUID

from sport_training.models.workout import Workout


class InMemoryWorkoutRepository:
    def __init__(self) -> None:
        self._items: list[Workout] = []

    def save(self, workout: Workout) -> None:
        self._items = [w for w in self._items if w.id != workout.id]
        self._items.append(workout)

    def find_by_athlete(self, athlete_id: UUID) -> list[Workout]:
        return [w for w in self._items if w.athlete_id == athlete_id]
