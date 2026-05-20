"""Тести алгоритму штрафу за пропуск."""

import pytest

from sport_training.utils.penalties import missed_streak_penalty_points


@pytest.mark.parametrize(
    "streak,base,cap,expected",
    [
        (0, 1, 5, 1),
        (3, 1, 5, 4),
        (10, 1, 5, 6),
        (0, 0, 0, 0),
        (100, 2, 3, 5),
    ],
)
def test_penalty_table(streak, base, cap, expected):
    assert missed_streak_penalty_points(streak, base=base, cap=cap) == expected


def test_penalty_negative_streak_raises():
    with pytest.raises(ValueError, match="non-negative"):
        missed_streak_penalty_points(-1)


@pytest.mark.parametrize("bad_base", [-1, -5])
def test_penalty_negative_base_raises(bad_base):
    with pytest.raises(ValueError, match="base"):
        missed_streak_penalty_points(0, base=bad_base)


@pytest.mark.parametrize("bad_cap", [-1])
def test_penalty_negative_cap_raises(bad_cap):
    with pytest.raises(ValueError, match="cap"):
        missed_streak_penalty_points(0, cap=bad_cap)
