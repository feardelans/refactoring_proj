"""Пріоритизація заявок на обмежений слот (наприклад, тренер / зал)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class MembershipTier(IntEnum):
    BASIC = 1
    PREMIUM = 2
    ELITE = 3


@dataclass(frozen=True)
class SlotRequest:
    athlete_id: str
    tier: MembershipTier
    arrival_order: int  # менше — раніше в черзі при однаковому tier


def compare_slot_requests(a: SlotRequest, b: SlotRequest) -> int:
    """
    Порівняння у стилі cmp для `functools.cmp_to_key`: від'ємне — `a` раніше за `b` у черзі.

    Спочатку вищий tier, потім менший arrival_order.
    """
    if a.tier != b.tier:
        return int(b.tier) - int(a.tier)
    return a.arrival_order - b.arrival_order


def sort_slot_requests(requests: list[SlotRequest]) -> list[SlotRequest]:
    """Стабільне сортування заявок за пріоритетом (копія списку)."""
    from functools import cmp_to_key

    return sorted(requests, key=cmp_to_key(compare_slot_requests))
