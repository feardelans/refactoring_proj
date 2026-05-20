from uuid import uuid4

from sport_training.services.events import GoalAchievedEvent, GoalEventPublisher


class _L:
    def __init__(self) -> None:
        self.n = 0

    def on_goal_achieved(self, event: GoalAchievedEvent) -> None:
        self.n += 1
        self.last = event


def test_publisher_notifies_all():
    pub = GoalEventPublisher()
    a, b = _L(), _L()
    pub.subscribe(a)
    pub.subscribe(b)
    e = GoalAchievedEvent(goal_id=uuid4(), athlete_id=uuid4(), title="x")
    pub.publish_achieved(e)
    assert a.n == 1 and b.n == 1
