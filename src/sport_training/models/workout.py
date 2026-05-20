from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from uuid import UUID


class WorkoutType(str, Enum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"


@dataclass(frozen=True)
class Workout:
    id: UUID
    athlete_id: UUID
    date: date
    duration_minutes: int
    type: WorkoutType

    def __post_init__(self) -> None:
        if self.duration_minutes <= 0:
            msg = "duration_minutes must be positive"
            raise ValueError(msg)
