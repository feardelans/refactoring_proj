from sport_training.utils.formatting import compact_title, session_summary


def test_session_summary_typical_cardio_uk():
    assert "кардіо" in session_summary("cardio", 45, locale="uk")
    assert "45" in session_summary("cardio", 45, locale="uk")


def test_session_summary_strength_english():
    text = session_summary("strength", 40, locale="en")
    assert "strength" in text
    assert "40" in text


def test_compact_title_nonempty():
    assert compact_title("  Morning run  ") == "Morning run"
