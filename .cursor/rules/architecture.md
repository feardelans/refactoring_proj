# Architecture (In-Memory)

## Purpose

The `sport_training` package models workout logging and goal progress without persistent storage. Data lives in in-memory repository instances (typically one instance per test or short-lived scenario).

## Layers

1. **`models`** — immutable or simple domain structures (`Workout` is frozen; `TrainingGoal` enforces invariants).
2. **`storage`** — `Protocol` interfaces (`GoalRepository`, etc.) and `InMemory*Repository` classes backed by collections (`dict`, `list`).
3. **`services`** — orchestration: `WorkoutLogService` depends on repository interfaces, progress strategy (`services/policy.py`), and event publisher (`services/events.py`).
4. **`utils`** — pure functions with no I/O.

## GoF patterns

- **Strategy** — `WorkoutProgressStrategy`: different point accrual per workout.
- **Observer** — `GoalAchievementListener` + `GoalEventPublisher`: react when a goal is achieved.

## SOLID

- **DIP**: services depend on repository abstractions, not concrete databases.
- **SRP**: progress rules (strategy), entity persistence (repositories), and workout logging (service) are separate responsibilities.
