"""
Text utility helpers.

- clean_text: normalize and trim user-provided text.
- is_bad_text: simple content filter to detect banned words.
"""


def clean_text(text: str | None) -> str:
    """
    Normalize and trim text.

    Args:
        text: Raw text (can be None).

    Returns:
        A stripped string, or an empty string if input is None/empty.
    """
    if not text:
        return ""
    return text.strip()


def is_bad_text(text: str) -> bool:
    """
    Check whether the given text contains any banned words.

    Note:
        This is a very simple implementation based on substring matching.
        You can extend this list or use a more advanced approach later.

    Args:
        text: Input text to evaluate.

    Returns:
        True if the text contains any banned word, False otherwise.
    """
    banned_words = ["کلمه بد", "فحش", "ممنوع"]
    lowered = text.lower()
    return any(word in lowered for word in banned_words)
