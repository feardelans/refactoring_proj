"""Консоль: інтерактивне меню та автодемо."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from uuid import UUID, uuid4

from sport_training.models.exercise import Exercise, ExerciseGoal, ExerciseLog
from sport_training.models.goal import TrainingGoal
from sport_training.models.plan import PlannedSession, TrainingPlan
from sport_training.models.user import User, UserRole
from sport_training.models.workout import Workout, WorkoutType
from sport_training.services.events import GoalAchievedEvent, GoalEventPublisher
from sport_training.services.exercise_progress import ExerciseProgressService
from sport_training.services.plan_tracking import PlanTrackingService
from sport_training.services.policy import WeightedProgressStrategy
from sport_training.services.workout_log import WorkoutLogService
from sport_training.storage.memory_exercise_goals import InMemoryExerciseGoalRepository
from sport_training.storage.memory_exercise_logs import InMemoryExerciseLogRepository
from sport_training.storage.memory_exercises import InMemoryExerciseRepository
from sport_training.storage.memory_goals import InMemoryGoalRepository
from sport_training.storage.memory_planned_sessions import InMemoryPlannedSessionRepository
from sport_training.storage.memory_plans import InMemoryPlanRepository
from sport_training.storage.memory_users import InMemoryUserRepository
from sport_training.storage.memory_workouts import InMemoryWorkoutRepository
from sport_training.storage.workout_repository import WorkoutRepository

InputFn = Callable[[str], str]
PrintFn = Callable[[str], None]

WORKOUT_TYPES = {
    "1": WorkoutType.STRENGTH,
    "2": WorkoutType.CARDIO,
    "3": WorkoutType.FLEXIBILITY,
}


class _PrintListener:
    def __init__(self, print_fn: PrintFn) -> None:
        self._print = print_fn

    def on_goal_achieved(self, event: GoalAchievedEvent) -> None:
        self._print(f"  → Ціль досягнута: {event.title!r}")


@dataclass
class AppSession:
    athlete_id: UUID
    coach_id: UUID
    workout_svc: WorkoutLogService
    exercise_svc: ExerciseProgressService
    plan_svc: PlanTrackingService
    goals: InMemoryGoalRepository
    workouts: WorkoutRepository
    exercises: InMemoryExerciseRepository
    plans: InMemoryPlanRepository


def create_session(
    athlete_name: str,
    print_fn: PrintFn = print,
) -> AppSession:
    athlete_id = uuid4()
    coach_id = uuid4()

    users = InMemoryUserRepository()
    users.save(User(id=athlete_id, display_name=athlete_name, role=UserRole.ATHLETE))
    users.save(User(id=coach_id, display_name="Тренер", role=UserRole.COACH))

    publisher = GoalEventPublisher()
    publisher.subscribe(_PrintListener(print_fn))

    goals = InMemoryGoalRepository()
    workouts = InMemoryWorkoutRepository()
    exercises = InMemoryExerciseRepository()
    plans = InMemoryPlanRepository()
    planned_sessions = InMemoryPlannedSessionRepository()

    return AppSession(
        athlete_id=athlete_id,
        coach_id=coach_id,
        workout_svc=WorkoutLogService(
            users,
            workouts,
            goals,
            WeightedProgressStrategy(),
            publisher,
        ),
        exercise_svc=ExerciseProgressService(
            users,
            exercises,
            InMemoryExerciseGoalRepository(),
            InMemoryExerciseLogRepository(),
            publisher,
        ),
        plan_svc=PlanTrackingService(users, plans, planned_sessions),
        goals=goals,
        workouts=workouts,
        exercises=exercises,
        plans=plans,
    )


def _read_int(prompt: str, input_fn: InputFn, *, low: int, high: int) -> int:
    while True:
        raw = input_fn(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print(f"  Введіть число від {low} до {high}.")
            continue
        if low <= value <= high:
            return value
        print(f"  Число має бути від {low} до {high}.")


def _read_positive_int(prompt: str, input_fn: InputFn) -> int:
    while True:
        raw = input_fn(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("  Введіть ціле додатне число.")
            continue
        if value > 0:
            return value
        print("  Число має бути > 0.")


def _acting_user_id(session: AppSession, input_fn: InputFn) -> UUID:
    print("  Хто виконує дію? 1 — атлет  2 — тренер")
    choice = _read_int("  > ", input_fn, low=1, high=2)
    return session.athlete_id if choice == 1 else session.coach_id


def _read_date(prompt: str, input_fn: InputFn, print_fn: PrintFn) -> date:
    while True:
        raw = input_fn(prompt).strip()
        if not raw:
            return date.today()
        try:
            parts = raw.split("-")
            if len(parts) != 3:
                raise ValueError
            y, m, d = (int(p) for p in parts)
            return date(y, m, d)
        except ValueError:
            print_fn("  Формат дати: РРРР-ММ-ДД (або Enter — сьогодні).")


def _pick_plan(session: AppSession, input_fn: InputFn, print_fn: PrintFn) -> UUID | None:
    items = session.plans.find_by_athlete(session.athlete_id)
    if not items:
        print_fn("  Немає планів. Спочатку створіть план (п. 9).")
        return None
    print_fn("  Плани:")
    for i, plan in enumerate(items, start=1):
        print_fn(f"    {i}. {plan.title}")
    idx = _read_int("  Номер плану: ", input_fn, low=1, high=len(items))
    return items[idx - 1].id


def _pick_exercise(session: AppSession, input_fn: InputFn, print_fn: PrintFn) -> UUID | None:
    items = session.exercises.find_all()
    if not items:
        print_fn("  Немає вправ. Спочатку додайте вправу (п. 5).")
        return None
    print_fn("  Вправи:")
    for i, ex in enumerate(items, start=1):
        print_fn(f"    {i}. {ex.name}")
    idx = _read_int("  Номер вправи: ", input_fn, low=1, high=len(items))
    return items[idx - 1].id


def _menu_print(print_fn: PrintFn) -> None:
    print_fn(
        "\n--- Меню ---\n"
        "  1. Записати тренування\n"
        "  2. Історія тренувань\n"
        "  3. Додати ціль (тренування)\n"
        "  4. Активні цілі тренувань\n"
        "  5. Додати вправу\n"
        "  6. Поставити ціль по вправі\n"
        "  7. Записати виконання вправи\n"
        "  8. Переглянути прогрес по вправі\n"
        "  9. Створити план тренувань\n"
        "  10. Додати заплановане тренування до плану\n"
        "  11. Переглянути плани\n"
        "  12. Позначити заплановане (виконано / пропущено)\n"
        "  13. Автодемо (готовий сценарій)\n"
        "  0. Вихід"
    )


def _handle_log_workout(session: AppSession, input_fn: InputFn, print_fn: PrintFn) -> None:
    acting = _acting_user_id(session, input_fn)
    minutes = _read_positive_int("  Тривалість (хв): ", input_fn)
    print_fn("  Тип: 1-strength  2-cardio  3-flexibility")
    wtype = WORKOUT_TYPES[str(_read_int("  > ", input_fn, low=1, high=3))]
    try:
        workout = Workout(
            id=uuid4(),
            athlete_id=session.athlete_id,
            date=date.today(),
            duration_minutes=minutes,
            type=wtype,
        )
        session.workout_svc.log_workout(acting, workout)
        matched = session.plan_svc.complete_matching_sessions(workout)
        print_fn("  Тренування збережено.")
        if matched:
            print_fn(f"  У плані позначено виконаними: {matched} запланованих сесій.")
    except (ValueError, RuntimeError) as exc:
        print_fn(f"  Помилка: {exc}")


def _handle_add_training_goal(session: AppSession, input_fn: InputFn, print_fn: PrintFn) -> None:
    title = input_fn("  Назва цілі: ").strip() or "Ціль"
    target = _read_positive_int("  Скільки тренувань (ціль): ", input_fn)
    session.goals.save(
        TrainingGoal(
            id=uuid4(),
            athlete_id=session.athlete_id,
            title=title,
            target_workouts=target,
        )
    )
    print_fn("  Ціль додано.")


def _handle_list_workout_history(session: AppSession, print_fn: PrintFn) -> None:
    workouts = session.workouts.find_by_athlete(session.athlete_id)
    if not workouts:
        print_fn("  Тренувань ще немає.")
        return
    ordered = sorted(workouts, key=lambda w: (w.date, str(w.id)), reverse=True)
    print_fn(f"  Записів: {len(ordered)} (новіші зверху)")
    for w in ordered:
        print_fn(f"  • {w.date}  {w.type.value}  —  {w.duration_minutes} хв")


def _handle_list_active_training_goals(session: AppSession, print_fn: PrintFn) -> None:
    goals = [
        g
        for g in session.goals.find_by_athlete(session.athlete_id)
        if not g.is_achieved()
    ]
    if not goals:
        print_fn("  Активних цілей немає.")
        return
    for g in goals:
        print_fn(f"  • {g.title}: {g.completed_workouts}/{g.target_workouts}")


def _handle_add_exercise(session: AppSession, input_fn: InputFn, print_fn: PrintFn) -> None:
    name = input_fn("  Назва вправи: ").strip()
    if not name:
        print_fn("  Назва не може бути порожньою.")
        return
    try:
        session.exercise_svc.register_exercise(
            session.athlete_id,
            Exercise(id=uuid4(), name=name),
        )
        print_fn(f"  Вправу «{name}» додано.")
    except (ValueError, RuntimeError) as exc:
        print_fn(f"  Помилка: {exc}")


def _handle_set_exercise_goal(session: AppSession, input_fn: InputFn, print_fn: PrintFn) -> None:
    exercise_id = _pick_exercise(session, input_fn, print_fn)
    if exercise_id is None:
        return
    title = input_fn("  Назва цілі: ").strip() or "Ціль"
    target = _read_positive_int("  Цільова кількість: ", input_fn)
    try:
        session.exercise_svc.set_goal(
            session.athlete_id,
            ExerciseGoal(
                id=uuid4(),
                athlete_id=session.athlete_id,
                exercise_id=exercise_id,
                title=title,
                target_amount=target,
            ),
        )
        print_fn("  Ціль по вправі збережено.")
    except (ValueError, RuntimeError) as exc:
        print_fn(f"  Помилка: {exc}")


def _handle_log_exercise(session: AppSession, input_fn: InputFn, print_fn: PrintFn) -> None:
    exercise_id = _pick_exercise(session, input_fn, print_fn)
    if exercise_id is None:
        return
    acting = _acting_user_id(session, input_fn)
    amount = _read_positive_int("  Кількість (повторень/одиниць): ", input_fn)
    try:
        session.exercise_svc.log_exercise(
            acting,
            ExerciseLog(
                id=uuid4(),
                athlete_id=session.athlete_id,
                exercise_id=exercise_id,
                date=date.today(),
                amount=amount,
            ),
        )
        print_fn("  Запис збережено.")
    except (ValueError, RuntimeError) as exc:
        print_fn(f"  Помилка: {exc}")


def _handle_create_plan(session: AppSession, input_fn: InputFn, print_fn: PrintFn) -> None:
    title = input_fn("  Назва плану: ").strip()
    if not title:
        print_fn("  Назва не може бути порожньою.")
        return
    try:
        session.plan_svc.create_plan(
            session.athlete_id,
            TrainingPlan(id=uuid4(), athlete_id=session.athlete_id, title=title),
        )
        print_fn("  План створено.")
    except (ValueError, RuntimeError) as exc:
        print_fn(f"  Помилка: {exc}")


def _handle_add_planned_session(session: AppSession, input_fn: InputFn, print_fn: PrintFn) -> None:
    plan_id = _pick_plan(session, input_fn, print_fn)
    if plan_id is None:
        return
    on_date = _read_date("  Дата (РРРР-ММ-ДД, Enter=сьогодні): ", input_fn, print_fn)
    print_fn("  Тип: 1-strength  2-cardio  3-flexibility")
    wtype = WORKOUT_TYPES[str(_read_int("  > ", input_fn, low=1, high=3))]
    try:
        session.plan_svc.add_planned_session(
            session.athlete_id,
            PlannedSession(
                id=uuid4(),
                plan_id=plan_id,
                athlete_id=session.athlete_id,
                scheduled_date=on_date,
                workout_type=wtype,
            ),
        )
        print_fn("  Заплановане тренування додано.")
    except (ValueError, RuntimeError) as exc:
        print_fn(f"  Помилка: {exc}")


def _handle_list_plans(session: AppSession, print_fn: PrintFn) -> None:
    summaries = session.plan_svc.list_plan_summaries(session.athlete_id)
    if not summaries:
        print_fn("  Планів немає.")
        return
    for summary in summaries:
        print_fn(
            f"\n  План «{summary.title}»: "
            f"заплановано {summary.planned_count}, "
            f"виконано {summary.completed_count}, "
            f"пропущено {summary.missed_count}"
        )
        detail = session.plan_svc.get_plan_detail(session.athlete_id, summary.plan_id)
        if detail is None:
            continue
        for s in detail.sessions:
            print_fn(
                f"    • {s.scheduled_date} {s.workout_type.value}: {s.status.value}"
            )


def _pick_planned_session(
    session: AppSession,
    plan_id: UUID,
    input_fn: InputFn,
    print_fn: PrintFn,
) -> UUID | None:
    detail = session.plan_svc.get_plan_detail(session.athlete_id, plan_id)
    if detail is None or not detail.sessions:
        print_fn("  У плані немає запланованих сесій.")
        return None
    print_fn("  Сесії:")
    for i, s in enumerate(detail.sessions, start=1):
        print_fn(f"    {i}. {s.scheduled_date} {s.workout_type.value} — {s.status.value}")
    idx = _read_int("  Номер сесії: ", input_fn, low=1, high=len(detail.sessions))
    return detail.sessions[idx - 1].id


def _handle_mark_planned_session(session: AppSession, input_fn: InputFn, print_fn: PrintFn) -> None:
    plan_id = _pick_plan(session, input_fn, print_fn)
    if plan_id is None:
        return
    session_id = _pick_planned_session(session, plan_id, input_fn, print_fn)
    if session_id is None:
        return
    print_fn("  Статус: 1 — виконано  2 — пропущено")
    choice = _read_int("  > ", input_fn, low=1, high=2)
    try:
        if choice == 1:
            session.plan_svc.mark_completed(session.athlete_id, session_id)
            print_fn("  Позначено як виконано.")
        else:
            session.plan_svc.mark_missed(session.athlete_id, session_id)
            print_fn("  Позначено як пропущено.")
    except (ValueError, RuntimeError) as exc:
        print_fn(f"  Помилка: {exc}")


def _handle_exercise_progress(session: AppSession, input_fn: InputFn, print_fn: PrintFn) -> None:
    exercise_id = _pick_exercise(session, input_fn, print_fn)
    if exercise_id is None:
        return
    progress = session.exercise_svc.get_progress(session.athlete_id, exercise_id)
    ex = session.exercises.find_by_id(exercise_id)
    print_fn(f"\n  Вправа: {ex.name if ex else '?'}")
    for g in progress.goals:
        print_fn(f"  • {g.title}: {g.completed_amount}/{g.target_amount}")
    print_fn(f"  Усього записано: {progress.total_logged}")


def run_interactive(
    input_fn: InputFn | None = None,
    print_fn: PrintFn | None = None,
) -> None:
    read = input_fn or input
    out = print_fn or print

    out("=== Sport Training (in-memory) ===")
    name = read("Ім'я атлета: ").strip() or "Атлет"
    session = create_session(name, out)
    out(f"Сесію розпочато для «{name}». Дані зникнуть після виходу.\n")

    handlers: dict[int, Callable[[], None]] = {
        1: lambda: _handle_log_workout(session, read, out),
        2: lambda: _handle_list_workout_history(session, out),
        3: lambda: _handle_add_training_goal(session, read, out),
        4: lambda: _handle_list_active_training_goals(session, out),
        5: lambda: _handle_add_exercise(session, read, out),
        6: lambda: _handle_set_exercise_goal(session, read, out),
        7: lambda: _handle_log_exercise(session, read, out),
        8: lambda: _handle_exercise_progress(session, read, out),
        9: lambda: _handle_create_plan(session, read, out),
        10: lambda: _handle_add_planned_session(session, read, out),
        11: lambda: _handle_list_plans(session, out),
        12: lambda: _handle_mark_planned_session(session, read, out),
        13: lambda: run_demo(),
    }

    while True:
        _menu_print(out)
        choice = _read_int("\nОберіть пункт: ", read, low=0, high=13)
        if choice == 0:
            out("До побачення.")
            break
        handlers[choice]()


def run_demo() -> None:
    """Прогін сценаріїв: тренування + вправи (in-memory)."""
    athlete_id = uuid4()
    coach_id = uuid4()
    exercise_id = uuid4()

    users = InMemoryUserRepository()
    users.save(User(id=athlete_id, display_name="Атлет", role=UserRole.ATHLETE))
    users.save(User(id=coach_id, display_name="Тренер", role=UserRole.COACH))

    goals = InMemoryGoalRepository()
    training_goal_id = uuid4()
    goals.save(
        TrainingGoal(
            id=training_goal_id,
            athlete_id=athlete_id,
            title="3 тренування",
            target_workouts=3,
        )
    )

    publisher = GoalEventPublisher()
    publisher.subscribe(_PrintListener(print))

    workout_svc = WorkoutLogService(
        users,
        InMemoryWorkoutRepository(),
        goals,
        WeightedProgressStrategy(),
        publisher,
    )

    exercises = InMemoryExerciseRepository()
    exercise_goals = InMemoryExerciseGoalRepository()
    exercise_logs = InMemoryExerciseLogRepository()
    exercise_svc = ExerciseProgressService(
        users, exercises, exercise_goals, exercise_logs, publisher
    )
    plans = InMemoryPlanRepository()
    planned_sessions = InMemoryPlannedSessionRepository()
    plan_svc = PlanTrackingService(users, plans, planned_sessions)
    plan_id = uuid4()

    print("=== Sport Training — демо ===\n")

    print("0. План тренувань на тиждень")
    plan_svc.create_plan(athlete_id, TrainingPlan(id=plan_id, athlete_id=athlete_id, title="Тиждень 1"))
    for wtype in (WorkoutType.STRENGTH, WorkoutType.CARDIO, WorkoutType.STRENGTH):
        plan_svc.add_planned_session(
            athlete_id,
            PlannedSession(
                id=uuid4(),
                plan_id=plan_id,
                athlete_id=athlete_id,
                scheduled_date=date.today(),
                workout_type=wtype,
            ),
        )
    summaries = plan_svc.list_plan_summaries(athlete_id)
    print(f"   Сесій у плані: {summaries[0].planned_count} заплановано")

    print("1. Реєстрація вправи")
    exercise_svc.register_exercise(athlete_id, Exercise(id=exercise_id, name="Віджимання"))
    print("   Вправа: Віджимання")

    print("\n2. Ціль по вправі (50 повторень)")
    exercise_svc.set_goal(
        athlete_id,
        ExerciseGoal(
            id=uuid4(),
            athlete_id=athlete_id,
            exercise_id=exercise_id,
            title="50 віджимань",
            target_amount=50,
        ),
    )

    print("\n3. Тренування (атлет, силове — 2 очки з WeightedStrategy)")
    for i in range(2):
        w = Workout(
            id=uuid4(),
            athlete_id=athlete_id,
            date=date.today(),
            duration_minutes=45,
            type=WorkoutType.STRENGTH,
        )
        workout_svc.log_workout(athlete_id, w)
        plan_svc.complete_matching_sessions(w)
        g = goals.find_by_id(training_goal_id)
        assert g is not None
        print(f"   Тренування {i + 1}: прогрес цілі «3 тренування» = {g.completed_workouts}/3")

    print("\n4. Тренування від тренера за атлета")
    w_cardio = Workout(
        id=uuid4(),
        athlete_id=athlete_id,
        date=date.today(),
        duration_minutes=30,
        type=WorkoutType.CARDIO,
    )
    workout_svc.log_workout(coach_id, w_cardio)
    plan_svc.complete_matching_sessions(w_cardio)
    summary = plan_svc.list_plan_summaries(athlete_id)[0]
    print(
        f"   План «{summary.title}»: виконано {summary.completed_count}, "
        f"заплановано {summary.planned_count}"
    )
    g = goals.find_by_id(training_goal_id)
    assert g is not None
    print(f"   Ціль тренувань: {g.completed_workouts}/3, досягнута={g.is_achieved()}")

    print("\n5. Запис вправи (25 повторень)")
    exercise_svc.log_exercise(
        athlete_id,
        ExerciseLog(
            id=uuid4(),
            athlete_id=athlete_id,
            exercise_id=exercise_id,
            date=date.today(),
            amount=25,
        ),
    )

    print("\n6. Прогрес по вправі")
    progress = exercise_svc.get_progress(athlete_id, exercise_id)
    for goal in progress.goals:
        print(f"   {goal.title}: {goal.completed_amount}/{goal.target_amount}")
    print(f"   Усього записано: {progress.total_logged}")

    print("\n=== Демо завершено ===")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sport-training",
        description="In-memory консоль: тренування, цілі, плани, вправи.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="interactive",
        choices=["interactive", "demo"],
        help="interactive — меню з вводом; demo — автосценарій",
    )
    args = parser.parse_args(argv)

    if args.command == "demo":
        run_demo()
    else:
        run_interactive()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
