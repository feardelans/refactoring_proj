import pytest

from sport_training.utils.mathutils import clamp


@pytest.mark.parametrize(
    "value,low,high,expected",
    [
        (5, 0, 10, 5),
        (-1, 0, 10, 0),
        (100, 0, 10, 10),
        (0, 0, 0, 0),
        (3, 3, 3, 3),
    ],
)
def test_clamp_examples(value, low, high, expected):
    assert clamp(value, low, high) == expected


@pytest.mark.parametrize("v", range(-12, 13))
def test_clamp_monotonic_bounds(v):
    assert clamp(v, 0, 10) == max(0, min(10, v))
