from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from uuid import UUID

from sport_training.models.workout import WorkoutType


class PlanStatus(str, Enum):
    PLANNED = "planned"
    COMPLETED = "completed"
    MISSED = "missed"


@dataclass
class TrainingPlan:
    id: UUID
    athlete_id: UUID
    title: str

    def __post_init__(self) -> None:
        if not self.title.strip():
            msg = "title must not be empty"
            raise ValueError(msg)


@dataclass
class PlannedSession:
    id: UUID
    plan_id: UUID
    athlete_id: UUID
    scheduled_date: date
    workout_type: WorkoutType
    status: PlanStatus = PlanStatus.PLANNED

    def mark_completed(self) -> None:
        if self.status == PlanStatus.COMPLETED:
            msg = "session already completed"
            raise ValueError(msg)
        self.status = PlanStatus.COMPLETED

    def mark_missed(self) -> None:
        if self.status == PlanStatus.COMPLETED:
            msg = "cannot mark completed session as missed"
            raise ValueError(msg)
        self.status = PlanStatus.MISSED
