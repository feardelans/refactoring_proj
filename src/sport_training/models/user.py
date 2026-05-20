from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID


class UserRole(str, Enum):
    ATHLETE = "athlete"
    COACH = "coach"


@dataclass
class User:
    id: UUID
    display_name: str
    role: UserRole
    blocked: bool = False

    def set_blocked(self, value: bool) -> None:
        self.blocked = value
