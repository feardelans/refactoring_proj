from datetime import date
from uuid import uuid4

import pytest

from sport_training.models.plan import PlannedSession, PlanStatus, TrainingPlan
from sport_training.models.workout import WorkoutType


def test_planned_session_mark_completed_and_missed():
    s = PlannedSession(
        id=uuid4(),
        plan_id=uuid4(),
        athlete_id=uuid4(),
        scheduled_date=date.today(),
        workout_type=WorkoutType.CARDIO,
    )
    s.mark_completed()
    assert s.status == PlanStatus.COMPLETED

    s2 = PlannedSession(
        id=uuid4(),
        plan_id=uuid4(),
        athlete_id=uuid4(),
        scheduled_date=date.today(),
        workout_type=WorkoutType.FLEXIBILITY,
    )
    s2.mark_missed()
    assert s2.status == PlanStatus.MISSED


def test_cannot_mark_completed_twice():
    s = PlannedSession(
        id=uuid4(),
        plan_id=uuid4(),
        athlete_id=uuid4(),
        scheduled_date=date.today(),
        workout_type=WorkoutType.STRENGTH,
        status=PlanStatus.COMPLETED,
    )
    with pytest.raises(ValueError, match="already completed"):
        s.mark_completed()
