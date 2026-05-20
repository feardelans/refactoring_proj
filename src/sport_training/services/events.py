from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class GoalAchievedEvent:
    goal_id: UUID
    athlete_id: UUID
    title: str


class GoalAchievementListener(Protocol):
    def on_goal_achieved(self, event: GoalAchievedEvent) -> None: ...


class GoalEventPublisher:
    def __init__(self) -> None:
        self._listeners: list[GoalAchievementListener] = []

    def subscribe(self, listener: GoalAchievementListener) -> None:
        self._listeners.append(listener)

    def publish_achieved(self, event: GoalAchievedEvent) -> None:
        for listener in list(self._listeners):
            listener.on_goal_achieved(event)
