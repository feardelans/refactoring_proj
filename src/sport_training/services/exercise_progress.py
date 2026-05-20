from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sport_training.models.exercise import Exercise, ExerciseGoal, ExerciseLog
from sport_training.models.user import UserRole
from sport_training.services.events import GoalAchievedEvent, GoalEventPublisher
from sport_training.storage.exercise_goal_repository import ExerciseGoalRepository
from sport_training.storage.exercise_log_repository import ExerciseLogRepository
from sport_training.storage.exercise_repository import ExerciseRepository
from sport_training.storage.user_repository import UserRepository


@dataclass(frozen=True)
class ExerciseProgressSnapshot:
    goals: tuple[ExerciseGoal, ...]
    total_logged: int


class ExerciseProgressService:
    def __init__(
        self,
        users: UserRepository,
        exercises: ExerciseRepository,
        goals: ExerciseGoalRepository,
        logs: ExerciseLogRepository,
        events: GoalEventPublisher,
    ) -> None:
        self._users = users
        self._exercises = exercises
        self._goals = goals
        self._logs = logs
        self._events = events

    def register_exercise(self, acting_user_id: UUID, exercise: Exercise) -> None:
        self._require_active_user(acting_user_id)
        self._exercises.save(exercise)

    def set_goal(self, acting_user_id: UUID, goal: ExerciseGoal) -> None:
        actor = self._require_active_user(acting_user_id)
        self._require_exercise(goal.exercise_id)
        self._authorize_for_athlete(actor, goal.athlete_id, acting_user_id)
        self._goals.save(goal)

    def log_exercise(self, acting_user_id: UUID, log: ExerciseLog) -> None:
        actor = self._require_active_user(acting_user_id)
        self._require_exercise(log.exercise_id)
        self._authorize_for_athlete(actor, log.athlete_id, acting_user_id)

        self._logs.save(log)
        for goal in self._goals.find_by_athlete_and_exercise(log.athlete_id, log.exercise_id):
            was_achieved = goal.is_achieved()
            goal.increment_completed(log.amount)
            self._goals.save(goal)
            if not was_achieved and goal.is_achieved():
                self._events.publish_achieved(
                    GoalAchievedEvent(
                        goal_id=goal.id,
                        athlete_id=goal.athlete_id,
                        title=goal.title,
                    )
                )

    def get_progress(self, athlete_id: UUID, exercise_id: UUID) -> ExerciseProgressSnapshot:
        goals = tuple(self._goals.find_by_athlete_and_exercise(athlete_id, exercise_id))
        total_logged = sum(
            log.amount for log in self._logs.find_by_athlete_and_exercise(athlete_id, exercise_id)
        )
        return ExerciseProgressSnapshot(goals=goals, total_logged=total_logged)

    def _require_active_user(self, user_id: UUID):
        user = self._users.find_by_id(user_id)
        if user is None:
            msg = "user not found"
            raise ValueError(msg)
        if user.blocked:
            msg = "user is blocked"
            raise RuntimeError(msg)
        return user

    def _require_exercise(self, exercise_id: UUID) -> None:
        if self._exercises.find_by_id(exercise_id) is None:
            msg = "exercise not found"
            raise ValueError(msg)

    def _authorize_for_athlete(self, actor, athlete_id: UUID, acting_user_id: UUID) -> None:
        if athlete_id != acting_user_id and actor.role != UserRole.COACH:
            msg = "only coach can act for another athlete"
            raise RuntimeError(msg)
