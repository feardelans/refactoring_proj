from __future__ import annotations

from uuid import UUID

from sport_training.models.exercise import ExerciseLog


class InMemoryExerciseLogRepository:
    def __init__(self) -> None:
        self._logs: list[ExerciseLog] = []

    def save(self, log: ExerciseLog) -> None:
        self._logs.append(log)

    def find_by_athlete(self, athlete_id: UUID) -> list[ExerciseLog]:
        return [log for log in self._logs if log.athlete_id == athlete_id]

    def find_by_athlete_and_exercise(
        self, athlete_id: UUID, exercise_id: UUID
    ) -> list[ExerciseLog]:
        return [
            log
            for log in self._logs
            if log.athlete_id == athlete_id and log.exercise_id == exercise_id
        ]
