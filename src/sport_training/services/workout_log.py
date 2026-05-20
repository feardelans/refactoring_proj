from __future__ import annotations

from uuid import UUID

from sport_training.models.user import UserRole
from sport_training.models.workout import Workout
from sport_training.services.events import GoalAchievedEvent, GoalEventPublisher
from sport_training.services.policy import WorkoutProgressStrategy
from sport_training.storage.goal_repository import GoalRepository
from sport_training.storage.user_repository import UserRepository
from sport_training.storage.workout_repository import WorkoutRepository


class WorkoutLogService:
    def __init__(
        self,
        users: UserRepository,
        workouts: WorkoutRepository,
        goals: GoalRepository,
        progress_strategy: WorkoutProgressStrategy,
        events: GoalEventPublisher,
    ) -> None:
        self._users = users
        self._workouts = workouts
        self._goals = goals
        self._progress_strategy = progress_strategy
        self._events = events

    def log_workout(self, acting_user_id: UUID, workout: Workout) -> None:
        actor = self._users.find_by_id(acting_user_id)
        if actor is None:
            msg = "user not found"
            raise ValueError(msg)
        if actor.blocked:
            msg = "user is blocked"
            raise RuntimeError(msg)
        if workout.athlete_id != acting_user_id and actor.role != UserRole.COACH:
            msg = "only coach can log for another athlete"
            raise RuntimeError(msg)

        self._workouts.save(workout)
        points = self._progress_strategy.progress_points(workout)
        for goal in self._goals.find_by_athlete(workout.athlete_id):
            was_achieved = goal.is_achieved()
            goal.increment_completed(points)
            self._goals.save(goal)
            if not was_achieved and goal.is_achieved():
                self._events.publish_achieved(
                    GoalAchievedEvent(goal_id=goal.id, athlete_id=goal.athlete_id, title=goal.title)
                )
