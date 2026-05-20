# Сервіс управління тренуванням (Python, In-Memory)

<!-- Badges: Sonar project key `feardelans_refactoring_proj` (org + repo on SonarCloud). If your Project Key differs, update project= and id= in the URLs below. -->

[![CI](https://github.com/feardelans/refactoring_proj/actions/workflows/ci-pipeline.yml/badge.svg?branch=main)](https://github.com/feardelans/refactoring_proj/actions/workflows/ci-pipeline.yml?query=branch%3Amain)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=feardelans_refactoring_proj&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=feardelans_refactoring_proj)
[![Coverage](https://img.shields.io/badge/coverage-%3E70%25-brightgreen)](https://github.com/feardelans/refactoring_proj)

Облік тренувань, цілей і планів без зовнішньої БД та зовнішніх API. Якість: **SonarQube / SonarCloud**, **pytest-cov** (мінімум **70%** для здачі; локально зазвичай **~90%+** рядків — частина гілок у `utils/formatting.py` залишена для подальших тестів).

**UML, діаграми та розгорнутий опис алгоритмів** — у окремому звіті; у репозиторії залишається технічна частина (код, тести, CI).

## Встановлення та тести

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
mkdir -p reports
pytest --cov=sport_training --cov-report=xml --cov-report=html --junitxml=reports/junit.xml
```

Артефакти:

- `coverage.xml` — для SonarQube
- `htmlcov/index.html` — HTML покриття
- `reports/junit.xml` — результати тестів (JUnit)

## Структура

- `src/sport_training/` — `models`, `services`, `storage`, `utils`
- `tests/` — **330+** модульних та інтеграційних тестів (орієнтир **200+** виконано)
- `.cursor/rules/` — правила для ШІ-агентів
- `.github/workflows/ci-pipeline.yml` — CI: pytest + coverage + **upload-artifact**. Sonar запускається **лише якщо** в репозиторії є secret **`SONAR_TOKEN`**.

### SonarCloud (новий репозиторій `refactoring_proj`)

1. [sonarcloud.io](https://sonarcloud.io) → **Analyze new project** → імпортуй **`feardelans/refactoring_proj`** (очікуваний ключ: **`feardelans_refactoring_proj`**).
2. **Administration → Analysis Method** → вимкни **Automatic Analysis** (лише CI).
3. GitHub **`refactoring_proj`** → **Settings → Secrets → Actions** → secret **`SONAR_TOKEN`** (токен з SonarCloud → My Account → Security).
4. Push на `main` або **Actions → Re-run all jobs**.

## Домен (коротко)

Актори: **спортсмен**, **тренер**. Сценарії: запис тренування, цілі, блокування, подія досягнення цілі. Патерни: **Strategy** (`WorkoutProgressStrategy`), **Observer** (`GoalEventPublisher`). Алгоритми штрафу за серію та пріоритет черги слота: `utils/penalties.py`, `utils/priority.py`.
