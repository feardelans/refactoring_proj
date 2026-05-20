"""Тести пріоритету черги на слот."""

import pytest

from sport_training.utils.priority import (
    MembershipTier,
    SlotRequest,
    compare_slot_requests,
    sort_slot_requests,
)


def test_elite_before_basic():
    elite = SlotRequest("a", MembershipTier.ELITE, arrival_order=5)
    basic = SlotRequest("b", MembershipTier.BASIC, arrival_order=0)
    assert compare_slot_requests(elite, basic) < 0


def test_same_tier_earlier_arrival_first():
    first = SlotRequest("a", MembershipTier.PREMIUM, arrival_order=1)
    second = SlotRequest("b", MembershipTier.PREMIUM, arrival_order=9)
    assert compare_slot_requests(first, second) < 0


def test_sort_orders_by_tier_then_arrival():
    r = [
        SlotRequest("b", MembershipTier.BASIC, 0),
        SlotRequest("e", MembershipTier.ELITE, 100),
        SlotRequest("p1", MembershipTier.PREMIUM, 5),
        SlotRequest("p0", MembershipTier.PREMIUM, 1),
    ]
    ordered = sort_slot_requests(r)
    assert [x.athlete_id for x in ordered] == ["e", "p0", "p1", "b"]


@pytest.mark.parametrize("tier", list(MembershipTier))
def test_single_request_sort_stable(tier):
    one = [SlotRequest("x", tier, 0)]
    assert sort_slot_requests(one) == one
