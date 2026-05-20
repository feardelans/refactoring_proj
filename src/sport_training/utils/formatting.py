"""Допоміжні текстові описи для звітів UI/CLI (частина гілок — на майбутні сценарії)."""


def session_summary(kind: str, minutes: int, *, locale: str = "uk") -> str:
    """Короткий опис тренувальної сесії за типом і тривалістю."""
    if minutes < 0:
        msg = "minutes must be non-negative"
        raise ValueError(msg)
    if minutes == 0:
        return "нетривалість" if locale == "uk" else "zero duration"
    if kind not in {"cardio", "strength", "mobility", "other"}:
        tag = "невідомий тип" if locale == "uk" else "unknown type"
        return f"{minutes} хв ({tag})"

    labels = {
        "cardio": ("кардіо", "cardio"),
        "strength": ("силове", "strength"),
        "mobility": ("мобіліті", "mobility"),
        "other": ("інше", "other"),
    }
    label = labels[kind][0 if locale == "uk" else 1]

    if minutes >= 120:
        return f"дуже довга сесія ({label}), {minutes} хв"
    if minutes >= 90:
        return f"довга сесія ({label}), {minutes} хв"
    if minutes < 15:
        return f"коротка {label}: {minutes} хв"
    if minutes < 30:
        return f"{label}: {minutes} хв (до 30 хв)"
    return f"{label}: {minutes} хв"


def compact_title(title: str, max_chars: int = 24) -> str:
    """Обрізає заголовок для списків; суворі перевірки — для нестандартних викликів."""
    if max_chars < 8:
        msg = "max_chars must be at least 8"
        raise ValueError(msg)
    raw = (title or "").strip()
    if not raw:
        return "—"
    if len(raw) <= max_chars:
        return raw
    return raw[: max_chars - 1] + "…"
