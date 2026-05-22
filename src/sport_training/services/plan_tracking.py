from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sport_training.models.plan import PlannedSession, PlanStatus, TrainingPlan
from sport_training.models.user import UserRole
from sport_training.models.workout import Workout
from sport_training.storage.plan_repository import PlanRepository
from sport_training.storage.planned_session_repository import PlannedSessionRepository
from sport_training.storage.user_repository import UserRepository


@dataclass(frozen=True)
class PlanSummary:
    plan_id: UUID
    title: str
    planned_count: int
    completed_count: int
    missed_count: int


@dataclass(frozen=True)
class PlanDetail:
    plan: TrainingPlan
    sessions: tuple[PlannedSession, ...]


class PlanTrackingService:
    def __init__(
        self,
        users: UserRepository,
        plans: PlanRepository,
        sessions: PlannedSessionRepository,
    ) -> None:
        self._users = users
        self._plans = plans
        self._sessions = sessions

    def create_plan(self, acting_user_id: UUID, plan: TrainingPlan) -> None:
        actor = self._require_active_user(acting_user_id)
        self._authorize_for_athlete(actor.role, plan.athlete_id, acting_user_id)
        self._plans.save(plan)

    def add_planned_session(self, acting_user_id: UUID, session: PlannedSession) -> None:
        actor = self._require_active_user(acting_user_id)
        self._authorize_for_athlete(actor.role, session.athlete_id, acting_user_id)
        if self._plans.find_by_id(session.plan_id) is None:
            msg = "plan not found"
            raise ValueError(msg)
        self._sessions.save(session)

    def mark_completed(self, acting_user_id: UUID, session_id: UUID) -> None:
        session = self._require_session(acting_user_id, session_id)
        session.mark_completed()
        self._sessions.save(session)

    def mark_missed(self, acting_user_id: UUID, session_id: UUID) -> None:
        session = self._require_session(acting_user_id, session_id)
        session.mark_missed()
        self._sessions.save(session)

    def complete_matching_sessions(self, workout: Workout) -> int:
        matches = self._sessions.find_planned_for_athlete_on_date(
            workout.athlete_id, workout.date, workout.type
        )
        for session in matches:
            session.mark_completed()
            self._sessions.save(session)
        return len(matches)

    def list_plan_summaries(self, athlete_id: UUID) -> list[PlanSummary]:
        summaries: list[PlanSummary] = []
        for plan in self._plans.find_by_athlete(athlete_id):
            sessions = self._sessions.find_by_plan(plan.id)
            planned = sum(1 for s in sessions if s.status == PlanStatus.PLANNED)
            completed = sum(1 for s in sessions if s.status == PlanStatus.COMPLETED)
            missed = sum(1 for s in sessions if s.status == PlanStatus.MISSED)
            summaries.append(
                PlanSummary(
                    plan_id=plan.id,
                    title=plan.title,
                    planned_count=planned,
                    completed_count=completed,
                    missed_count=missed,
                )
            )
        return summaries

    def get_plan_detail(self, athlete_id: UUID, plan_id: UUID) -> PlanDetail | None:
        plan = self._plans.find_by_id(plan_id)
        if plan is None or plan.athlete_id != athlete_id:
            return None
        sessions = tuple(self._sessions.find_by_plan(plan_id))
        return PlanDetail(plan=plan, sessions=sessions)

    def _require_session(self, acting_user_id: UUID, session_id: UUID) -> PlannedSession:
        actor = self._require_active_user(acting_user_id)
        session = self._sessions.find_by_id(session_id)
        if session is None:
            msg = "session not found"
            raise ValueError(msg)
        self._authorize_for_athlete(actor.role, session.athlete_id, acting_user_id)
        return session

    def _require_active_user(self, user_id: UUID):
        user = self._users.find_by_id(user_id)
        if user is None:
            msg = "user not found"
            raise ValueError(msg)
        if user.blocked:
            msg = "user is blocked"
            raise RuntimeError(msg)
        return user

    def _authorize_for_athlete(
        self, role: UserRole, athlete_id: UUID, acting_user_id: UUID
    ) -> None:
        if athlete_id != acting_user_id and role != UserRole.COACH:
            msg = "only coach can act for another athlete"
            raise RuntimeError(msg)
