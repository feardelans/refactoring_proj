from datetime import date, timedelta
from uuid import uuid4

import pytest

from sport_training.models.goal import TrainingGoal
from sport_training.models.user import User, UserRole
from sport_training.models.workout import Workout, WorkoutType
from sport_training.services.events import GoalAchievedEvent, GoalEventPublisher
from sport_training.services.policy import UniformProgressStrategy, WeightedProgressStrategy
from sport_training.services.workout_log import WorkoutLogService
from sport_training.storage.memory_goals import InMemoryGoalRepository
from sport_training.storage.memory_users import InMemoryUserRepository
from sport_training.storage.memory_workouts import InMemoryWorkoutRepository


def _workout(athlete_id, wtype=WorkoutType.CARDIO, minutes=30, d=None):
    return Workout(
        id=uuid4(),
        athlete_id=athlete_id,
        date=d or date.today(),
        duration_minutes=minutes,
        type=wtype,
    )


class _CollectListener:
    def __init__(self) -> None:
        self.events: list[GoalAchievedEvent] = []

    def on_goal_achieved(self, event: GoalAchievedEvent) -> None:
        self.events.append(event)


def test_log_updates_goal_and_emits_event():
    athlete_id = uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=athlete_id, display_name="A", role=UserRole.ATHLETE))
    goals = InMemoryGoalRepository()
    gid = uuid4()
    goals.save(TrainingGoal(id=gid, athlete_id=athlete_id, title="5x", target_workouts=1))
    workouts = InMemoryWorkoutRepository()
    publisher = GoalEventPublisher()
    collector = _CollectListener()
    publisher.subscribe(collector)
    svc = WorkoutLogService(users, workouts, goals, UniformProgressStrategy(), publisher)
    svc.log_workout(athlete_id, _workout(athlete_id))
    assert goals.find_by_id(gid) is not None
    assert goals.find_by_id(gid).is_achieved()
    assert len(collector.events) == 1
    assert collector.events[0].goal_id == gid


def test_coach_can_log_for_athlete():
    coach_id = uuid4()
    athlete_id = uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=coach_id, display_name="C", role=UserRole.COACH))
    users.save(User(id=athlete_id, display_name="A", role=UserRole.ATHLETE))
    goals = InMemoryGoalRepository()
    workouts = InMemoryWorkoutRepository()
    publisher = GoalEventPublisher()
    svc = WorkoutLogService(users, workouts, goals, UniformProgressStrategy(), publisher)
    svc.log_workout(coach_id, _workout(athlete_id))
    assert workouts.find_by_athlete(athlete_id)


def test_non_coach_cannot_log_for_other():
    u1, u2 = uuid4(), uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=u1, display_name="A", role=UserRole.ATHLETE))
    users.save(User(id=u2, display_name="B", role=UserRole.ATHLETE))
    svc = WorkoutLogService(
        users, InMemoryWorkoutRepository(), InMemoryGoalRepository(), UniformProgressStrategy(), GoalEventPublisher()
    )
    with pytest.raises(RuntimeError):
        svc.log_workout(u1, _workout(u2))


def test_user_not_found_raises():
    svc = WorkoutLogService(
        InMemoryUserRepository(),
        InMemoryWorkoutRepository(),
        InMemoryGoalRepository(),
        UniformProgressStrategy(),
        GoalEventPublisher(),
    )
    with pytest.raises(ValueError):
        svc.log_workout(uuid4(), _workout(uuid4()))


def test_already_achieved_goal_does_not_emit_second_event():
    athlete_id = uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=athlete_id, display_name="A", role=UserRole.ATHLETE))
    goals = InMemoryGoalRepository()
    gid = uuid4()
    goals.save(TrainingGoal(id=gid, athlete_id=athlete_id, title="done", target_workouts=1))
    publisher = GoalEventPublisher()
    collector = _CollectListener()
    publisher.subscribe(collector)
    svc = WorkoutLogService(users, InMemoryWorkoutRepository(), goals, UniformProgressStrategy(), publisher)
    svc.log_workout(athlete_id, _workout(athlete_id))
    assert len(collector.events) == 1
    svc.log_workout(athlete_id, _workout(athlete_id))
    assert len(collector.events) == 1


def test_blocked_user_rejected():
    uid = uuid4()
    users = InMemoryUserRepository()
    u = User(id=uid, display_name="A", role=UserRole.ATHLETE)
    u.set_blocked(True)
    users.save(u)
    svc = WorkoutLogService(
        users, InMemoryWorkoutRepository(), InMemoryGoalRepository(), UniformProgressStrategy(), GoalEventPublisher()
    )
    with pytest.raises(RuntimeError):
        svc.log_workout(uid, _workout(uid))


def test_weighted_strategy_two_points_strength():
    athlete_id = uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=athlete_id, display_name="A", role=UserRole.ATHLETE))
    goals = InMemoryGoalRepository()
    gid = uuid4()
    goals.save(TrainingGoal(id=gid, athlete_id=athlete_id, title="t", target_workouts=2, completed_workouts=0))
    publisher = GoalEventPublisher()
    collector = _CollectListener()
    publisher.subscribe(collector)
    svc = WorkoutLogService(
        users, InMemoryWorkoutRepository(), goals, WeightedProgressStrategy(), publisher
    )
    svc.log_workout(athlete_id, _workout(athlete_id, WorkoutType.STRENGTH))
    g = goals.find_by_id(gid)
    assert g.completed_workouts == 2
    assert g.is_achieved()
    assert len(collector.events) == 1


@pytest.mark.parametrize("day_offset", range(30))
def test_workout_across_week_dates(day_offset):
    athlete_id = uuid4()
    d = date.today() - timedelta(days=day_offset)
    w = _workout(athlete_id, d=d)
    assert w.date == d
