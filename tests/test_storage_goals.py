from uuid import uuid4

import pytest

from sport_training.models.goal import TrainingGoal
from sport_training.storage.memory_goals import InMemoryGoalRepository


def test_memory_goals_save_and_find():
    repo = InMemoryGoalRepository()
    aid = uuid4()
    g = TrainingGoal(id=uuid4(), athlete_id=aid, title="t", target_workouts=3)
    repo.save(g)
    assert len(repo.find_by_athlete(aid)) == 1


def test_memory_goals_bulk_same_athlete():
    repo = InMemoryGoalRepository()
    aid = uuid4()
    for i in range(10):
        repo.save(TrainingGoal(id=uuid4(), athlete_id=aid, title=str(i), target_workouts=1))
    assert len(repo.find_by_athlete(aid)) == 10


@pytest.mark.parametrize("idx", range(50))
def test_memory_goals_find_by_id(idx):
    repo = InMemoryGoalRepository()
    gid = uuid4()
    repo.save(TrainingGoal(id=gid, athlete_id=uuid4(), title=f"t{idx}", target_workouts=1))
    assert repo.find_by_id(gid) is not None
