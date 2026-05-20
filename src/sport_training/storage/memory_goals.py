from __future__ import annotations

from uuid import UUID

from sport_training.models.goal import TrainingGoal


class InMemoryGoalRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, TrainingGoal] = {}

    def save(self, goal: TrainingGoal) -> None:
        self._by_id[goal.id] = goal

    def find_by_id(self, goal_id: UUID) -> TrainingGoal | None:
        return self._by_id.get(goal_id)

    def find_by_athlete(self, athlete_id: UUID) -> list[TrainingGoal]:
        return [g for g in self._by_id.values() if g.athlete_id == athlete_id]
