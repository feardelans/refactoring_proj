from datetime import date
from uuid import uuid4

import pytest

from sport_training.models.exercise import Exercise, ExerciseGoal, ExerciseLog
from sport_training.models.user import User, UserRole
from sport_training.services.events import GoalAchievedEvent, GoalEventPublisher
from sport_training.services.exercise_progress import ExerciseProgressService
from sport_training.storage.memory_exercise_goals import InMemoryExerciseGoalRepository
from sport_training.storage.memory_exercise_logs import InMemoryExerciseLogRepository
from sport_training.storage.memory_exercises import InMemoryExerciseRepository
from sport_training.storage.memory_users import InMemoryUserRepository


class _CollectListener:
    def __init__(self) -> None:
        self.events: list[GoalAchievedEvent] = []

    def on_goal_achieved(self, event: GoalAchievedEvent) -> None:
        self.events.append(event)


def _service(
    users: InMemoryUserRepository | None = None,
    exercises: InMemoryExerciseRepository | None = None,
    goals: InMemoryExerciseGoalRepository | None = None,
    logs: InMemoryExerciseLogRepository | None = None,
    publisher: GoalEventPublisher | None = None,
) -> ExerciseProgressService:
    return ExerciseProgressService(
        users or InMemoryUserRepository(),
        exercises or InMemoryExerciseRepository(),
        goals or InMemoryExerciseGoalRepository(),
        logs or InMemoryExerciseLogRepository(),
        publisher or GoalEventPublisher(),
    )


def test_register_exercise():
    uid = uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=uid, display_name="A", role=UserRole.ATHLETE))
    exercises = InMemoryExerciseRepository()
    svc = _service(users=users, exercises=exercises)
    eid = uuid4()
    svc.register_exercise(uid, Exercise(id=eid, name="Squats"))
    assert exercises.find_by_id(eid) is not None


def test_set_goal_for_exercise():
    uid = uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=uid, display_name="A", role=UserRole.ATHLETE))
    exercises = InMemoryExerciseRepository()
    eid = uuid4()
    exercises.save(Exercise(id=eid, name="Pull-ups"))
    goals = InMemoryExerciseGoalRepository()
    svc = _service(users=users, exercises=exercises, goals=goals)
    gid = uuid4()
    svc.set_goal(uid, ExerciseGoal(id=gid, athlete_id=uid, exercise_id=eid, title="50", target_amount=50))
    assert goals.find_by_id(gid) is not None


def test_log_exercise_updates_goal_and_emits_event():
    uid = uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=uid, display_name="A", role=UserRole.ATHLETE))
    exercises = InMemoryExerciseRepository()
    eid = uuid4()
    exercises.save(Exercise(id=eid, name="Push-ups"))
    goals = InMemoryExerciseGoalRepository()
    gid = uuid4()
    goals.save(
        ExerciseGoal(id=gid, athlete_id=uid, exercise_id=eid, title="30 reps", target_amount=30)
    )
    logs = InMemoryExerciseLogRepository()
    publisher = GoalEventPublisher()
    collector = _CollectListener()
    publisher.subscribe(collector)
    svc = _service(users=users, exercises=exercises, goals=goals, logs=logs, publisher=publisher)
    svc.log_exercise(
        uid,
        ExerciseLog(id=uuid4(), athlete_id=uid, exercise_id=eid, date=date.today(), amount=30),
    )
    assert goals.find_by_id(gid).is_achieved()
    assert len(collector.events) == 1
    assert collector.events[0].goal_id == gid


def test_log_exercise_only_updates_matching_exercise_goals():
    uid = uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=uid, display_name="A", role=UserRole.ATHLETE))
    exercises = InMemoryExerciseRepository()
    eid1, eid2 = uuid4(), uuid4()
    exercises.save(Exercise(id=eid1, name="A"))
    exercises.save(Exercise(id=eid2, name="B"))
    goals = InMemoryExerciseGoalRepository()
    gid1, gid2 = uuid4(), uuid4()
    goals.save(ExerciseGoal(id=gid1, athlete_id=uid, exercise_id=eid1, title="g1", target_amount=10))
    goals.save(ExerciseGoal(id=gid2, athlete_id=uid, exercise_id=eid2, title="g2", target_amount=10))
    svc = _service(users=users, exercises=exercises, goals=goals)
    svc.log_exercise(
        uid,
        ExerciseLog(id=uuid4(), athlete_id=uid, exercise_id=eid1, date=date.today(), amount=5),
    )
    assert goals.find_by_id(gid1).completed_amount == 5
    assert goals.find_by_id(gid2).completed_amount == 0


def test_coach_can_log_for_athlete():
    coach_id, athlete_id = uuid4(), uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=coach_id, display_name="C", role=UserRole.COACH))
    users.save(User(id=athlete_id, display_name="A", role=UserRole.ATHLETE))
    exercises = InMemoryExerciseRepository()
    eid = uuid4()
    exercises.save(Exercise(id=eid, name="Plank"))
    logs = InMemoryExerciseLogRepository()
    svc = _service(users=users, exercises=exercises, logs=logs)
    svc.log_exercise(
        coach_id,
        ExerciseLog(id=uuid4(), athlete_id=athlete_id, exercise_id=eid, date=date.today(), amount=1),
    )
    assert len(logs.find_by_athlete(athlete_id)) == 1


def test_non_coach_cannot_log_for_other():
    u1, u2 = uuid4(), uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=u1, display_name="A", role=UserRole.ATHLETE))
    users.save(User(id=u2, display_name="B", role=UserRole.ATHLETE))
    exercises = InMemoryExerciseRepository()
    eid = uuid4()
    exercises.save(Exercise(id=eid, name="X"))
    svc = _service(users=users, exercises=exercises)
    with pytest.raises(RuntimeError):
        svc.log_exercise(
            u1,
            ExerciseLog(id=uuid4(), athlete_id=u2, exercise_id=eid, date=date.today(), amount=5),
        )


def test_log_unknown_exercise_rejected():
    uid = uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=uid, display_name="A", role=UserRole.ATHLETE))
    svc = _service(users=users)
    with pytest.raises(ValueError, match="exercise not found"):
        svc.log_exercise(
            uid,
            ExerciseLog(id=uuid4(), athlete_id=uid, exercise_id=uuid4(), date=date.today(), amount=5),
        )


def test_get_progress_returns_goal_and_log_totals():
    uid = uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=uid, display_name="A", role=UserRole.ATHLETE))
    exercises = InMemoryExerciseRepository()
    eid = uuid4()
    exercises.save(Exercise(id=eid, name="Burpees"))
    goals = InMemoryExerciseGoalRepository()
    goals.save(ExerciseGoal(id=uuid4(), athlete_id=uid, exercise_id=eid, title="100", target_amount=100))
    logs = InMemoryExerciseLogRepository()
    logs.save(ExerciseLog(id=uuid4(), athlete_id=uid, exercise_id=eid, date=date.today(), amount=20))
    logs.save(ExerciseLog(id=uuid4(), athlete_id=uid, exercise_id=eid, date=date.today(), amount=15))
    svc = _service(users=users, exercises=exercises, goals=goals, logs=logs)
    progress = svc.get_progress(uid, eid)
    assert progress.total_logged == 35
    assert progress.goals[0].target_amount == 100
    assert progress.goals[0].completed_amount == 0
