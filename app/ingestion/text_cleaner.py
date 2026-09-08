import re


DANFOSS_HEADER_PATTERNS = [
    re.compile(r"^.*Operating Guide.*VLT.*AutomationDrive FC 302.*$"),
    re.compile(r"^.*TroubleshootingOperating Guide.*$"),
    re.compile(r"^AQ275652476278en-000101.*$"),
    re.compile(r"^.*Danfoss A/S.*$"),
]


def is_danfoss_header_footer(line: str) -> bool:
    """
    Detect recurring Danfoss PDF header/footer artifacts.
    """

    line = line.strip()

    if not line:
        return False

    for pattern in DANFOSS_HEADER_PATTERNS:
        if pattern.match(line):
            return True

    return False


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text while preserving technical meaning.
    """

    if not text:
        return ""

    # Normalize line endings.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove recurring Danfoss PDF header/footer artifacts.
    lines = []

    for line in text.split("\n"):

        stripped = line.strip()

        if is_danfoss_header_footer(stripped):
            continue

        lines.append(stripped)

    text = "\n".join(lines)

    # Remove leftover Danfoss header fragments.
    # Only remove the exact unnumbered fragment so that
    # "8 Maintenance, Diagnostics, and Troubleshooting"
    # remains untouched.
    text = re.sub(
        r"(?<!\d)Maintenance,\s*Diagnostics,\s*and\s*$",
        "",
        text,
        flags=re.MULTILINE,
    )

    # Repair words broken across PDF line breaks.
    text = re.sub(r"(?<=\w)-\n(?=\w)", "", text)

    # Normalize spaces and tabs.
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Fix spaces before punctuation.
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)

    # Remove leading/trailing whitespace from lines.
    lines = [line.strip() for line in text.split("\n")]

    # Remove empty lines at beginning/end.
    while lines and not lines[0]:
        lines.pop(0)

    while lines and not lines[-1]:
        lines.pop()

    return "\n".join(lines)
