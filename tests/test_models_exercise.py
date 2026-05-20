from datetime import date
from uuid import uuid4

import pytest

from sport_training.models.exercise import Exercise, ExerciseGoal, ExerciseLog


def test_exercise_requires_non_empty_name():
    with pytest.raises(ValueError, match="name must not be empty"):
        Exercise(id=uuid4(), name="   ")


def test_exercise_goal_increment_caps():
    eid = uuid4()
    g = ExerciseGoal(
        id=uuid4(),
        athlete_id=uuid4(),
        exercise_id=eid,
        title="100 push-ups",
        target_amount=100,
    )
    g.increment_completed(150)
    assert g.completed_amount == 100
    assert g.is_achieved()


@pytest.mark.parametrize("target", list(range(1, 21)))
def test_exercise_goal_target_positive(target):
    g = ExerciseGoal(
        id=uuid4(),
        athlete_id=uuid4(),
        exercise_id=uuid4(),
        title="t",
        target_amount=target,
    )
    assert g.target_amount == target


def test_exercise_goal_invalid_target_zero():
    with pytest.raises(ValueError):
        ExerciseGoal(
            id=uuid4(),
            athlete_id=uuid4(),
            exercise_id=uuid4(),
            title="t",
            target_amount=0,
        )


def test_exercise_goal_invalid_completed_negative():
    with pytest.raises(ValueError):
        ExerciseGoal(
            id=uuid4(),
            athlete_id=uuid4(),
            exercise_id=uuid4(),
            title="t",
            target_amount=10,
            completed_amount=-1,
        )


def test_exercise_goal_invalid_completed_over_target():
    with pytest.raises(ValueError):
        ExerciseGoal(
            id=uuid4(),
            athlete_id=uuid4(),
            exercise_id=uuid4(),
            title="t",
            target_amount=10,
            completed_amount=11,
        )


def test_exercise_log_requires_positive_amount():
    with pytest.raises(ValueError, match="amount must be positive"):
        ExerciseLog(
            id=uuid4(),
            athlete_id=uuid4(),
            exercise_id=uuid4(),
            date=date.today(),
            amount=0,
        )


def test_exercise_log_stores_fields():
    aid, eid = uuid4(), uuid4()
    log = ExerciseLog(
        id=uuid4(),
        athlete_id=aid,
        exercise_id=eid,
        date=date(2026, 1, 15),
        amount=25,
    )
    assert log.athlete_id == aid
    assert log.exercise_id == eid
    assert log.amount == 25
