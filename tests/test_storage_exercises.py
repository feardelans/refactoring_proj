from datetime import date
from uuid import uuid4

import pytest

from sport_training.models.exercise import Exercise, ExerciseGoal, ExerciseLog
from sport_training.storage.memory_exercise_goals import InMemoryExerciseGoalRepository
from sport_training.storage.memory_exercise_logs import InMemoryExerciseLogRepository
from sport_training.storage.memory_exercises import InMemoryExerciseRepository


def test_memory_exercises_save_and_find():
    repo = InMemoryExerciseRepository()
    eid = uuid4()
    repo.save(Exercise(id=eid, name="Push-ups"))
    assert repo.find_by_id(eid) is not None
    assert len(repo.find_all()) == 1


@pytest.mark.parametrize("idx", range(20))
def test_memory_exercises_find_by_id(idx):
    repo = InMemoryExerciseRepository()
    eid = uuid4()
    repo.save(Exercise(id=eid, name=f"Exercise {idx}"))
    assert repo.find_by_id(eid).name == f"Exercise {idx}"


def test_memory_exercise_goals_find_by_athlete_and_exercise():
    repo = InMemoryExerciseGoalRepository()
    aid, eid1, eid2 = uuid4(), uuid4(), uuid4()
    repo.save(
        ExerciseGoal(
            id=uuid4(), athlete_id=aid, exercise_id=eid1, title="g1", target_amount=10
        )
    )
    repo.save(
        ExerciseGoal(
            id=uuid4(), athlete_id=aid, exercise_id=eid2, title="g2", target_amount=20
        )
    )
    repo.save(
        ExerciseGoal(
            id=uuid4(), athlete_id=uuid4(), exercise_id=eid1, title="other", target_amount=5
        )
    )
    assert len(repo.find_by_athlete(aid)) == 2
    assert len(repo.find_by_athlete_and_exercise(aid, eid1)) == 1


def test_memory_exercise_logs_find_by_athlete():
    repo = InMemoryExerciseLogRepository()
    aid = uuid4()
    eid = uuid4()
    repo.save(
        ExerciseLog(id=uuid4(), athlete_id=aid, exercise_id=eid, date=date.today(), amount=10)
    )
    repo.save(
        ExerciseLog(id=uuid4(), athlete_id=uuid4(), exercise_id=eid, date=date.today(), amount=5)
    )
    assert len(repo.find_by_athlete(aid)) == 1
    assert len(repo.find_by_athlete_and_exercise(aid, eid)) == 1
