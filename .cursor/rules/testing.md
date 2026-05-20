# Testing strategy (pytest + coverage)

## Commands

```bash
pip install -e ".[dev]"
mkdir -p reports
pytest --cov=sport_training --cov-report=xml --cov-report=html --junitxml=reports/junit.xml
```

- **`coverage.xml`** — for SonarQube / SonarCloud (`sonar.python.coverage.reportPaths`).
- **`htmlcov/`** — HTML report for manual inspection of uncovered lines.
- **`reports/junit.xml`** — JUnit XML for Sonar and CI (`sonar.junit.reportPaths`).

## Practices

- **Unit tests**: isolated tests for models, `clamp`, strategies.
- **Integration tests**: `WorkoutLogService` with real `InMemory*` repositories and a test listener.
- **Mocks**: use `unittest.mock.Mock(spec_set=Protocol)` for repositories when simulating storage failures (rare with in-memory stores).

## Course requirements

- Keep **fail_under=70** in `pyproject.toml` (`[tool.coverage.report]`).
- Target **200+** tests: use `@pytest.mark.parametrize` for edge cases and separate files per use-case scenario.
