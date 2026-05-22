from datetime import date
from uuid import uuid4

import pytest

from sport_training.models.plan import PlannedSession, PlanStatus, TrainingPlan
from sport_training.models.user import User, UserRole
from sport_training.models.workout import Workout, WorkoutType
from sport_training.services.plan_tracking import PlanTrackingService
from sport_training.storage.memory_planned_sessions import InMemoryPlannedSessionRepository
from sport_training.storage.memory_plans import InMemoryPlanRepository
from sport_training.storage.memory_users import InMemoryUserRepository


def _service(
    users: InMemoryUserRepository | None = None,
    plans: InMemoryPlanRepository | None = None,
    sessions: InMemoryPlannedSessionRepository | None = None,
) -> PlanTrackingService:
    return PlanTrackingService(
        users or InMemoryUserRepository(),
        plans or InMemoryPlanRepository(),
        sessions or InMemoryPlannedSessionRepository(),
    )


def test_create_plan():
    uid = uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=uid, display_name="A", role=UserRole.ATHLETE))
    plans = InMemoryPlanRepository()
    svc = _service(users=users, plans=plans)
    pid = uuid4()
    svc.create_plan(uid, TrainingPlan(id=pid, athlete_id=uid, title="Тиждень 1"))
    assert plans.find_by_id(pid) is not None


def test_add_planned_session_requires_plan():
    uid = uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=uid, display_name="A", role=UserRole.ATHLETE))
    svc = _service(users=users)
    with pytest.raises(ValueError, match="plan not found"):
        svc.add_planned_session(
            uid,
            PlannedSession(
                id=uuid4(),
                plan_id=uuid4(),
                athlete_id=uid,
                scheduled_date=date.today(),
                workout_type=WorkoutType.STRENGTH,
            ),
        )


def test_mark_completed_and_missed():
    uid = uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=uid, display_name="A", role=UserRole.ATHLETE))
    plans = InMemoryPlanRepository()
    sessions = InMemoryPlannedSessionRepository()
    pid = uuid4()
    plans.save(TrainingPlan(id=pid, athlete_id=uid, title="P"))
    sid = uuid4()
    sessions.save(
        PlannedSession(
            id=sid,
            plan_id=pid,
            athlete_id=uid,
            scheduled_date=date.today(),
            workout_type=WorkoutType.CARDIO,
        )
    )
    svc = _service(users=users, plans=plans, sessions=sessions)
    svc.mark_completed(uid, sid)
    s = sessions.find_by_id(sid)
    assert s is not None
    assert s.status == PlanStatus.COMPLETED

    sid2 = uuid4()
    sessions.save(
        PlannedSession(
            id=sid2,
            plan_id=pid,
            athlete_id=uid,
            scheduled_date=date.today(),
            workout_type=WorkoutType.FLEXIBILITY,
        )
    )
    svc.mark_missed(uid, sid2)
    assert sessions.find_by_id(sid2).status == PlanStatus.MISSED


def test_complete_matching_on_workout():
    uid = uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=uid, display_name="A", role=UserRole.ATHLETE))
    plans = InMemoryPlanRepository()
    sessions = InMemoryPlannedSessionRepository()
    pid = uuid4()
    plans.save(TrainingPlan(id=pid, athlete_id=uid, title="P"))
    sid = uuid4()
    today = date.today()
    sessions.save(
        PlannedSession(
            id=sid,
            plan_id=pid,
            athlete_id=uid,
            scheduled_date=today,
            workout_type=WorkoutType.STRENGTH,
        )
    )
    svc = _service(users=users, plans=plans, sessions=sessions)
    n = svc.complete_matching_sessions(
        Workout(
            id=uuid4(),
            athlete_id=uid,
            date=today,
            duration_minutes=30,
            type=WorkoutType.STRENGTH,
        )
    )
    assert n == 1
    assert sessions.find_by_id(sid).status == PlanStatus.COMPLETED


def test_plan_summary_counts():
    uid = uuid4()
    users = InMemoryUserRepository()
    users.save(User(id=uid, display_name="A", role=UserRole.ATHLETE))
    plans = InMemoryPlanRepository()
    sessions = InMemoryPlannedSessionRepository()
    pid = uuid4()
    plans.save(TrainingPlan(id=pid, athlete_id=uid, title="Місяць"))
    for wtype in (WorkoutType.STRENGTH, WorkoutType.CARDIO, WorkoutType.FLEXIBILITY):
        sessions.save(
            PlannedSession(
                id=uuid4(),
                plan_id=pid,
                athlete_id=uid,
                scheduled_date=date.today(),
                workout_type=wtype,
            )
        )
    s_done = uuid4()
    sessions.save(
        PlannedSession(
            id=s_done,
            plan_id=pid,
            athlete_id=uid,
            scheduled_date=date.today(),
            workout_type=WorkoutType.STRENGTH,
            status=PlanStatus.COMPLETED,
        )
    )
    svc = _service(users=users, plans=plans, sessions=sessions)
    summaries = svc.list_plan_summaries(uid)
    assert len(summaries) == 1
    summary = summaries[0]
    assert summary.title == "Місяць"
    assert summary.planned_count == 3
    assert summary.completed_count == 1
