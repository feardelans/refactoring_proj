import pytest

from sport_training.cli import main, run_demo, run_interactive


def test_run_demo_completes(capsys):
    run_demo()
    out = capsys.readouterr().out
    assert "Sport Training" in out
    assert "Демо завершено" in out


def test_main_demo_exit_zero():
    assert main(["demo"]) == 0


def test_interactive_quit(capsys):
    inputs = iter(["Іван", "0"])
    run_interactive(input_fn=lambda _: next(inputs))
    out = capsys.readouterr().out
    assert "Іван" in out
    assert "До побачення" in out


def test_interactive_log_workout_flow(capsys):
    """Вправа → ціль → запис → перегляд прогресу → вихід."""
    inputs = iter(
        [
            "Аня",
            "5",  # додати вправу
            "Присідання",
            "6",  # ціль по вправі
            "1",  # вправа
            "100 присідань",
            "100",
            "7",  # запис
            "1",  # атлет
            "1",  # вправа
            "20",
            "8",  # прогрес
            "1",
            "0",
        ]
    )
    run_interactive(input_fn=lambda _: next(inputs))
    out = capsys.readouterr().out
    assert "Присідання" in out
    assert "20/100" in out or "Усього записано: 20" in out


def test_interactive_plan_flow(capsys):
    """План → сесія → перегляд → вихід."""
    inputs = iter(
        [
            "Богдан",
            "9",  # створити план
            "Тиждень 1",
            "10",  # додати сесію
            "1",  # план
            "",  # дата сьогодні
            "1",  # strength
            "11",  # перегляд планів
            "0",
        ]
    )
    run_interactive(input_fn=lambda _: next(inputs))
    out = capsys.readouterr().out
    assert "Тиждень 1" in out
    assert "заплановано 1" in out


def test_interactive_workout_history_and_active_goals(capsys):
    inputs = iter(
        [
            "Марія",
            "3",  # ціль
            "10 тренувань",
            "10",
            "1",  # запис тренування
            "1",  # атлет
            "30",  # хв
            "1",  # strength
            "2",  # історія
            "4",  # активні цілі
            "0",
        ]
    )
    run_interactive(input_fn=lambda _: next(inputs))
    out = capsys.readouterr().out
    assert "strength" in out
    assert "30 хв" in out
    assert "10 тренувань" in out
    assert "1/10" in out or "2/10" in out


def test_main_default_is_interactive(monkeypatch):
    ran: list[bool] = []
    monkeypatch.setattr("sport_training.cli.run_interactive", lambda: ran.append(True))
    assert main([]) == 0
    assert ran
