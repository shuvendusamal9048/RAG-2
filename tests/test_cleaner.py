from app.services.ingestion.cleaner import clean_text


def test_clean_text():
    raw_text = (
        "Employee     Leave     Policy\r\n"
        "\r\n"
        "\r\n"
        "Casual     Leave\r\n"
        "\r\n"
        "Sick     Leave"
    )

    cleaned_text = clean_text(raw_text)

    assert cleaned_text == (
        "Employee Leave Policy\n"
        "Casual Leave\n"
        "Sick Leave"
    )


def test_clean_empty_text():
    assert clean_text("") == ""
    assert clean_text("   ") == ""


def test_clean_text_preserves_line_breaks():
    raw_text = "Line One\n\nLine Two\n\n\nLine Three"

    cleaned_text = clean_text(raw_text)

    assert cleaned_text == (
        "Line One\n"
        "Line Two\n"
        "Line Three"
    )