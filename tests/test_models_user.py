from uuid import uuid4

import pytest

from sport_training.models.user import User, UserRole


def test_user_blocked_toggle():
    u = User(id=uuid4(), display_name="n", role=UserRole.ATHLETE)
    assert not u.blocked
    u.set_blocked(True)
    assert u.blocked


@pytest.mark.parametrize("role", list(UserRole))
def test_user_roles(role):
    u = User(id=uuid4(), display_name="x", role=role)
    assert u.role == role
