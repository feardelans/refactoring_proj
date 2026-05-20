from __future__ import annotations

from typing import Protocol

from sport_training.models.workout import Workout, WorkoutType


class WorkoutProgressStrategy(Protocol):
    def progress_points(self, workout: Workout) -> int: ...


class UniformProgressStrategy:
    def progress_points(self, workout: Workout) -> int:
        return 1


class WeightedProgressStrategy:
    def progress_points(self, workout: Workout) -> int:
        return 2 if workout.type == WorkoutType.STRENGTH else 1
