from datetime import date
from uuid import uuid4

import pytest

from sport_training.models.workout import Workout, WorkoutType


def test_workout_positive_duration():
    Workout(id=uuid4(), athlete_id=uuid4(), date=date.today(), duration_minutes=1, type=WorkoutType.CARDIO)


def test_workout_invalid_duration():
    with pytest.raises(ValueError):
        Workout(
            id=uuid4(),
            athlete_id=uuid4(),
            date=date.today(),
            duration_minutes=0,
            type=WorkoutType.CARDIO,
        )


@pytest.mark.parametrize("minutes", [1, 15, 90, 120])
def test_workout_durations(minutes):
    w = Workout(
        id=uuid4(),
        athlete_id=uuid4(),
        date=date.today(),
        duration_minutes=minutes,
        type=WorkoutType.FLEXIBILITY,
    )
    assert w.duration_minutes == minutes


@pytest.mark.parametrize("t", list(WorkoutType))
def test_workout_types_roundtrip(t):
    w = Workout(id=uuid4(), athlete_id=uuid4(), date=date.today(), duration_minutes=20, type=t)
    assert w.type == t
