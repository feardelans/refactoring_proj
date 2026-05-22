from __future__ import annotations

from uuid import UUID

from sport_training.models.plan import TrainingPlan


class InMemoryPlanRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, TrainingPlan] = {}

    def save(self, plan: TrainingPlan) -> None:
        self._by_id[plan.id] = plan

    def find_by_id(self, plan_id: UUID) -> TrainingPlan | None:
        return self._by_id.get(plan_id)

    def find_by_athlete(self, athlete_id: UUID) -> list[TrainingPlan]:
        return [p for p in self._by_id.values() if p.athlete_id == athlete_id]
