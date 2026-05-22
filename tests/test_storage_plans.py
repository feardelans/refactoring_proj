from datetime import date
from uuid import uuid4

from sport_training.models.plan import PlannedSession, PlanStatus, TrainingPlan
from sport_training.models.workout import WorkoutType
from sport_training.storage.memory_planned_sessions import InMemoryPlannedSessionRepository
from sport_training.storage.memory_plans import InMemoryPlanRepository


def test_plan_and_session_repositories():
    uid = uuid4()
    pid = uuid4()
    plans = InMemoryPlanRepository()
    plans.save(TrainingPlan(id=pid, athlete_id=uid, title="W1"))
    assert plans.find_by_athlete(uid)[0].title == "W1"

    sessions = InMemoryPlannedSessionRepository()
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
    found = sessions.find_planned_for_athlete_on_date(uid, today, WorkoutType.STRENGTH)
    assert len(found) == 1
    found[0].status = PlanStatus.COMPLETED
    sessions.save(found[0])
    assert sessions.find_planned_for_athlete_on_date(uid, today, WorkoutType.STRENGTH) == []
