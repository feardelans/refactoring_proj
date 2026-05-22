from __future__ import annotations

from typing import Protocol
from uuid import UUID

from sport_training.models.plan import TrainingPlan


class PlanRepository(Protocol):
    def save(self, plan: TrainingPlan) -> None: ...

    def find_by_id(self, plan_id: UUID) -> TrainingPlan | None: ...

    def find_by_athlete(self, athlete_id: UUID) -> list[TrainingPlan]: ...
