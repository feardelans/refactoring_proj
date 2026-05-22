from __future__ import annotations

from datetime import date
from uuid import UUID

from sport_training.models.plan import PlannedSession, PlanStatus
from sport_training.models.workout import WorkoutType


class InMemoryPlannedSessionRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, PlannedSession] = {}

    def save(self, session: PlannedSession) -> None:
        self._by_id[session.id] = session

    def find_by_id(self, session_id: UUID) -> PlannedSession | None:
        return self._by_id.get(session_id)

    def find_by_plan(self, plan_id: UUID) -> list[PlannedSession]:
        return [s for s in self._by_id.values() if s.plan_id == plan_id]

    def find_planned_for_athlete_on_date(
        self, athlete_id: UUID, on_date: date, workout_type: WorkoutType
    ) -> list[PlannedSession]:
        return [
            s
            for s in self._by_id.values()
            if s.athlete_id == athlete_id
            and s.scheduled_date == on_date
            and s.workout_type == workout_type
            and s.status == PlanStatus.PLANNED
        ]
