from __future__ import annotations

from datetime import date
from typing import Protocol
from uuid import UUID

from sport_training.models.plan import PlannedSession, PlanStatus
from sport_training.models.workout import WorkoutType


class PlannedSessionRepository(Protocol):
    def save(self, session: PlannedSession) -> None: ...

    def find_by_id(self, session_id: UUID) -> PlannedSession | None: ...

    def find_by_plan(self, plan_id: UUID) -> list[PlannedSession]: ...

    def find_planned_for_athlete_on_date(
        self, athlete_id: UUID, on_date: date, workout_type: WorkoutType
    ) -> list[PlannedSession]: ...
