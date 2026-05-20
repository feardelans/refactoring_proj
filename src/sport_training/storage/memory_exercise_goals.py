from __future__ import annotations

from uuid import UUID

from sport_training.models.exercise import ExerciseGoal


class InMemoryExerciseGoalRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, ExerciseGoal] = {}

    def save(self, goal: ExerciseGoal) -> None:
        self._by_id[goal.id] = goal

    def find_by_id(self, goal_id: UUID) -> ExerciseGoal | None:
        return self._by_id.get(goal_id)

    def find_by_athlete(self, athlete_id: UUID) -> list[ExerciseGoal]:
        return [g for g in self._by_id.values() if g.athlete_id == athlete_id]

    def find_by_athlete_and_exercise(
        self, athlete_id: UUID, exercise_id: UUID
    ) -> list[ExerciseGoal]:
        return [
            g
            for g in self._by_id.values()
            if g.athlete_id == athlete_id and g.exercise_id == exercise_id
        ]
