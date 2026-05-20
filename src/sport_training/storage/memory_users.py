from __future__ import annotations

from uuid import UUID

from sport_training.models.user import User


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, User] = {}

    def save(self, user: User) -> None:
        self._by_id[user.id] = user

    def find_by_id(self, user_id: UUID) -> User | None:
        return self._by_id.get(user_id)
