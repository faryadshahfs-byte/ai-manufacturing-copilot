import re
from typing import Any


TOP_LEVEL_SECTIONS = {
    "1": "Introduction",
    "2": "Safety",
    "3": "Product Overview",
    "4": "Mechanical Installation",
    "5": "Electrical Installation",
    "6": "Starting the Drive",
    "7": "Wiring Configuration Examples",
    "8": "Maintenance, Diagnostics, and Troubleshooting",
    "9": "Specifications",
    "10": "Appendix",
}


HEADING_PATTERN = re.compile(
    r"^(?P<number>\d+(?:\.\d+){0,3})\s+(?P<title>.+)$"
)


MEASUREMENT_VALUE_PATTERN = re.compile(
    r"^[+-]?\d+(?:\.\d+)?\s*"
    r"(?:kW|W|MW|Hz|kHz|A|mA|V|mV|RPM|%|°C|°F)$",
    re.IGNORECASE,
)


DISPLAY_ARTIFACT_PATTERN = re.compile(
    r"^[+-]?\d+(?:\.\d+)?\s*[A-Za-z%°]+"
    r"(?:\s*[+-]?\d+(?:\.\d+)?\s*[A-Za-z%°]+)+$",
    re.IGNORECASE,
)


def detect_heading(line: str):
    line = line.strip()

    if not line:
        return None

    # Equipment display values are not headings.
    if MEASUREMENT_VALUE_PATTERN.fullmatch(line):
        return None

    # PDF extraction can concatenate multiple display values.
    if DISPLAY_ARTIFACT_PATTERN.fullmatch(line):
        return None

    match = HEADING_PATTERN.match(line)

    if not match:
        return None

    number = match.group("number")
    title = match.group("title").strip()

    if len(title) > 120:
        return None

    if re.search(r"\s\d+$", title):
        return None

    level = number.count(".") + 1

    if level == 1:
        expected_title = TOP_LEVEL_SECTIONS.get(number)

        if expected_title is None:
            return None

        if title != expected_title:
            return None

    return {
        "level": level,
        "number": number,
        "title": title,
        "heading": f"{number} {title}",
    }


def _split_large_text(
    text: str,
    page_number: int,
    chunk_size: int,
) -> list[dict]:
    """
    Split one oversized paragraph while preserving its page number.
    """

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip(),
    )

    results = []
    current = ""

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        candidate = (
            f"{current} {sentence}".strip()
            if current
            else sentence
        )

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            results.append(
                {
                    "text": current,
                    "page_start": page_number,
                    "page_end": page_number,
                }
            )

        if len(sentence) <= chunk_size:
            current = sentence

        else:
            start = 0

            while start < len(sentence):

                piece = sentence[
                    start:start + chunk_size
                ].strip()

                if piece:
                    results.append(
                        {
                            "text": piece,
                            "page_start": page_number,
                            "page_end": page_number,
                        }
                    )

                start += chunk_size

            current = ""

    if current:
        results.append(
            {
                "text": current,
                "page_start": page_number,
                "page_end": page_number,
            }
        )

    return results


def _split_blocks(
    blocks: list[tuple[int, str]],
    chunk_size: int,
) -> list[dict]:
    """
    Convert page-aware paragraph blocks into chunks while
    retaining accurate source page boundaries.
    """

    output = []

    current_parts = []
    current_length = 0
    current_page_start = None
    current_page_end = None

    for page_number, text in blocks:

        text = text.strip()

        if not text:
            continue

        # Oversized individual paragraph.
        if len(text) > chunk_size:

            if current_parts:
                output.append(
                    {
                        "text": "\n\n".join(
                            current_parts
                        ).strip(),
                        "page_start": current_page_start,
                        "page_end": current_page_end,
                    }
                )

                current_parts = []
                current_length = 0
                current_page_start = None
                current_page_end = None

            output.extend(
                _split_large_text(
                    text,
                    page_number,
                    chunk_size,
                )
            )

            continue

        separator_length = 2 if current_parts else 0

        if (
            current_parts
            and current_length
            + separator_length
            + len(text)
            > chunk_size
        ):

            output.append(
                {
                    "text": "\n\n".join(
                        current_parts
                    ).strip(),
                    "page_start": current_page_start,
                    "page_end": current_page_end,
                }
            )

            current_parts = []
            current_length = 0
            current_page_start = None
            current_page_end = None

        if not current_parts:
            current_page_start = page_number

        current_parts.append(text)
        current_length += (
            (2 if len(current_parts) > 1 else 0)
            + len(text)
        )
        current_page_end = page_number

    if current_parts:
        output.append(
            {
                "text": "\n\n".join(
                    current_parts
                ).strip(),
                "page_start": current_page_start,
                "page_end": current_page_end,
            }
        )

    return output


def chunk_pages(
    pages: list[dict[str, Any]],
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[dict[str, Any]]:
    """
    Create structure-aware, page-aware chunks.

    Important properties:
    - Headings remain inside the chunk text.
    - Each chunk keeps the metadata that was active when its
      content was parsed.
    - Page ranges are calculated from the actual source blocks.
    - Measurement/display values cannot become headings.
    """

    chunks = []

    current_section = None
    current_subsection = None
    current_subsubsection = None

    pending_blocks: list[tuple[int, str]] = []
    current_paragraph_lines: list[str] = []
    current_paragraph_page = None

    chunk_counter = 1

    def close_paragraph():
        nonlocal current_paragraph_lines
        nonlocal current_paragraph_page

        if current_paragraph_lines:
            text = "\n".join(
                current_paragraph_lines
            ).strip()

            if text:
                pending_blocks.append(
                    (
                        current_paragraph_page,
                        text,
                    )
                )

        current_paragraph_lines = []
        current_paragraph_page = None

    def flush_pending():
        nonlocal pending_blocks
        nonlocal chunk_counter

        close_paragraph()

        if not pending_blocks:
            return

        split_chunks = _split_blocks(
            pending_blocks,
            chunk_size,
        )

        for item in split_chunks:

            text = item["text"].strip()

            if not text:
                continue

            chunks.append(
                {
                    "chunk_id": (
                        f"chunk-{chunk_counter:04d}"
                    ),
                    "source": (
                        "danfoss_vlt_fc302_operating_guide.pdf"
                    ),
                    "page_number": item["page_start"],
                    "page_start": item["page_start"],
                    "page_end": item["page_end"],
                    "section": current_section,
                    "subsection": current_subsection,
                    "subsubsection": current_subsubsection,
                    "text": text,
                }
            )

            chunk_counter += 1

        pending_blocks = []

    for page in pages:

        page_number = page.get("page_number")
        text = (page.get("text") or "").strip()

        if page_number is None or page_number < 9:
            continue

        if not text:
            continue

        for raw_line in text.splitlines():

            line = raw_line.strip()

            if not line:

                close_paragraph()
                continue

            heading = detect_heading(line)

            if heading:

                # Finish content belonging to the previous hierarchy.
                flush_pending()

                level = heading["level"]

                if level == 1:

                    current_section = heading["heading"]
                    current_subsection = None
                    current_subsubsection = None

                elif level == 2:

                    if current_section is not None:
                        current_subsection = heading["heading"]
                        current_subsubsection = None

                elif level >= 3:

                    if current_subsection is not None:
                        current_subsubsection = heading["heading"]

                # Keep the heading itself in the chunk text.
                current_paragraph_lines = [
                    heading["heading"]
                ]
                current_paragraph_page = page_number

                continue

            if current_paragraph_page is None:
                current_paragraph_page = page_number

            current_paragraph_lines.append(line)

        # Close only the current paragraph at a page boundary.
        # Do not flush pending blocks because the same section/
        # subsection may continue onto the next page.
        close_paragraph()

    # Final content.
    flush_pending()

    return chunks
