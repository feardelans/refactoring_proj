from uuid import uuid4

import pytest

from sport_training.models.user import User, UserRole
from sport_training.models.workout import Workout, WorkoutType
from sport_training.storage.memory_users import InMemoryUserRepository
from sport_training.storage.memory_workouts import InMemoryWorkoutRepository


def test_memory_users_roundtrip():
    r = InMemoryUserRepository()
    uid = uuid4()
    r.save(User(id=uid, display_name="n", role=UserRole.COACH))
    assert r.find_by_id(uid) is not None


@pytest.mark.parametrize("i", range(20))
def test_memory_users_many(i):
    r = InMemoryUserRepository()
    uid = uuid4()
    r.save(User(id=uid, display_name=f"u{i}", role=UserRole.ATHLETE))
    assert r.find_by_id(uid).display_name == f"u{i}"


def test_memory_workouts_replace_by_id():
    r = InMemoryWorkoutRepository()
    aid = uuid4()
    from datetime import date

    wid = uuid4()
    w1 = Workout(id=wid, athlete_id=aid, date=date.today(), duration_minutes=30, type=WorkoutType.CARDIO)
    w2 = Workout(id=wid, athlete_id=aid, date=date.today(), duration_minutes=45, type=WorkoutType.CARDIO)
    r.save(w1)
    r.save(w2)
    found = r.find_by_athlete(aid)
    assert len(found) == 1
    assert found[0].duration_minutes == 45


@pytest.mark.parametrize("n", range(15))
def test_memory_workouts_list_grows(n):
    r = InMemoryWorkoutRepository()
    aid = uuid4()
    from datetime import date

    for k in range(n + 1):
        r.save(
            Workout(
                id=uuid4(),
                athlete_id=aid,
                date=date.today(),
                duration_minutes=20,
                type=WorkoutType.STRENGTH,
            )
        )
    assert len(r.find_by_athlete(aid)) == n + 1
