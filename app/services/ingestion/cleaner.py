import re


def clean_text(text: str) -> str:
    """
    Normalize extracted PDF text.

    - Normalize line endings
    - Remove excessive spaces
    - Remove excessive blank lines
    - Preserve meaningful line breaks
    """

    if not text:
        return ""

    # Normalize Windows/Mac line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove spaces and tabs at the beginning/end of each line
    lines = [
        re.sub(r"[ \t]+", " ", line).strip()
        for line in text.split("\n")
    ]

    # Remove completely empty lines
    lines = [line for line in lines if line]

    # Rebuild the text
    return "\n".join(lines)