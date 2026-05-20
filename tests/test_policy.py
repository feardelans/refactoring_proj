from datetime import date
from uuid import uuid4

import pytest

from sport_training.models.workout import Workout, WorkoutType
from sport_training.services.policy import UniformProgressStrategy, WeightedProgressStrategy


def _w(t: WorkoutType) -> Workout:
    return Workout(
        id=uuid4(), athlete_id=uuid4(), date=date.today(), duration_minutes=30, type=t
    )


def test_uniform_always_one():
    s = UniformProgressStrategy()
    for t in WorkoutType:
        assert s.progress_points(_w(t)) == 1


@pytest.mark.parametrize("t,expected", [(WorkoutType.STRENGTH, 2), (WorkoutType.CARDIO, 1), (WorkoutType.FLEXIBILITY, 1)])
def test_weighted_points(t, expected):
    s = WeightedProgressStrategy()
    assert s.progress_points(_w(t)) == expected
