from __future__ import annotations

from typing import Protocol
from uuid import UUID

from sport_training.models.user import User


class UserRepository(Protocol):
    def save(self, user: User) -> None: ...

    def find_by_id(self, user_id: UUID) -> User | None: ...
