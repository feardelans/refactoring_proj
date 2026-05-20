from uuid import uuid4

import pytest

from sport_training.models.goal import TrainingGoal


def test_goal_increment_caps():
    g = TrainingGoal(id=uuid4(), athlete_id=uuid4(), title="x", target_workouts=2)
    g.increment_completed(10)
    assert g.completed_workouts == 2
    assert g.is_achieved()


@pytest.mark.parametrize("target", list(range(1, 26)))
def test_goal_target_positive(target):
    g = TrainingGoal(id=uuid4(), athlete_id=uuid4(), title="t", target_workouts=target)
    assert g.target_workouts == target


@pytest.mark.parametrize("completed", [0, 1, 3])
@pytest.mark.parametrize("target", [5])
def test_goal_valid_completed(completed, target):
    g = TrainingGoal(
        id=uuid4(), athlete_id=uuid4(), title="t", target_workouts=target, completed_workouts=completed
    )
    assert g.completed_workouts == completed


def test_goal_invalid_target_zero():
    with pytest.raises(ValueError):
        TrainingGoal(id=uuid4(), athlete_id=uuid4(), title="t", target_workouts=0)


def test_goal_invalid_completed_negative():
    with pytest.raises(ValueError):
        TrainingGoal(
            id=uuid4(), athlete_id=uuid4(), title="t", target_workouts=3, completed_workouts=-1
        )


def test_goal_invalid_completed_over_target():
    with pytest.raises(ValueError):
        TrainingGoal(
            id=uuid4(), athlete_id=uuid4(), title="t", target_workouts=2, completed_workouts=3
        )
