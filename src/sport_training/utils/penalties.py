"""Розрахунок штрафних очок за пропуск після серії тренувань."""

from __future__ import annotations


def missed_streak_penalty_points(streak_before_miss: int, *, base: int = 1, cap: int = 5) -> int:
    """
    Повертає величину штрафу (очки, що знімаються з прогресу або додаються до «боргу»).

    :param streak_before_miss: довжина серії **успішних** тренувань без пропуску до моменту пропуску.
    :param base: мінімальний штраф.
    :param cap: верхня межа додаткового штрафу від серії.
    """
    if streak_before_miss < 0:
        msg = "streak_before_miss must be non-negative"
        raise ValueError(msg)
    if base < 0:
        msg = "base must be non-negative"
        raise ValueError(msg)
    if cap < 0:
        msg = "cap must be non-negative"
        raise ValueError(msg)
    return base + min(streak_before_miss, cap)
