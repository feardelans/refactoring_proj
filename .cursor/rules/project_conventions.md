# Project conventions

- **Code language**: Python 3.11+; English symbol names; Ukrainian is fine in docs or user-facing messages when needed.
- **Layout**: all production code under `src/sport_training/`; tests only under `tests/`.
- **Dependency inversion**: services accept `Protocol` repositories; tests use in-memory implementations or mocks.
- **New algorithms**: implement as pure functions in `utils/` or as a service plus tests; document in the report or README when needed.
