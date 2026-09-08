import re
from typing import Any


HEADING_PATTERN = re.compile(
    r"^(?P<number>\d+(?:\.\d+){0,3})\s+(?P<title>.+)$"
)


def detect_heading(line: str):
    """
    Detect numbered engineering-document headings.

    Examples:
        8 Maintenance, Diagnostics, and Troubleshooting
        8.3 Status Messages
        8.3.1 Status Message Overview
        8.4.48 ALARM 50 AMA calibration failed
    """

    line = line.strip()

    if not line:
        return None

    match = HEADING_PATTERN.match(line)

    if not match:
        return None

    number = match.group("number")
    title = match.group("title").strip()

    # Ignore Contents entries that normally end with a page number.
    if re.search(r"\s\d+$", title):
        return None

    # Ignore unusually long numbered sentences.
    if len(title) > 120:
        return None

    lower_title = title.lower()

    ignored_prefixes = (
        "position.",
        "operating mode.",
        "reference site.",
        "operation status.",
    )

    if lower_title.startswith(ignored_prefixes):
        return None

    level = number.count(".") + 1

    return {
        "level": level,
        "number": number,
        "title": title,
        "heading": f"{number} {title}",
    }


def split_text(text: str, chunk_size: int = 1200) -> list[str]:
    """
    Split text while trying to preserve paragraph and sentence boundaries.
    """

    text = text.strip()

    if not text:
        return []

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]

    chunks = []
    current = ""

    for paragraph in paragraphs:

        candidate = (
            f"{current}\n\n{paragraph}".strip()
            if current
            else paragraph
        )

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = ""

        if len(paragraph) <= chunk_size:
            current = paragraph
            continue

        sentences = re.split(
            r"(?<=[.!?])\s+",
            paragraph,
        )

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
            else:

                if current:
                    chunks.append(current)

                if len(sentence) > chunk_size:

                    start = 0

                    while start < len(sentence):

                        piece = sentence[
                            start:start + chunk_size
                        ].strip()

                        if piece:
                            chunks.append(piece)

                        start += chunk_size

                    current = ""

                else:
                    current = sentence

    if current:
        chunks.append(current)

    return chunks


def chunk_pages(
    pages: list[dict[str, Any]],
    source: str | None = None,
    chunk_size: int = 1200,
    chunk_overlap: int = 200,
) -> list[dict[str, Any]]:
    """
    Create structure-aware chunks from document pages.

    Numbered headings define the document hierarchy.
    Heading-only blocks are not stored as chunks.

    Metadata:
        section
        subsection
        subsubsection
        page_start
        page_end
    """

    del chunk_overlap  # retained for API compatibility

    chunks = []

    current_section = None
    current_subsection = None
    current_subsubsection = None

    current_block = []

    block_start_page = None
    block_end_page = None

    block_section = None
    block_subsection = None
    block_subsubsection = None

    # Tracks whether the current block contains actual content
    # in addition to its heading.
    block_has_content = False

    chunk_counter = 1

    def flush_block():
        nonlocal current_block
        nonlocal block_start_page
        nonlocal block_end_page
        nonlocal block_section
        nonlocal block_subsection
        nonlocal block_subsubsection
        nonlocal block_has_content
        nonlocal chunk_counter

        # Do not create chunks for heading-only blocks.
        if not current_block or not block_has_content:
            current_block = []
            block_start_page = None
            block_end_page = None
            block_section = None
            block_subsection = None
            block_subsubsection = None
            block_has_content = False
            return

        block_text = "\n".join(current_block).strip()

        if not block_text:
            current_block = []
            block_start_page = None
            block_end_page = None
            block_has_content = False
            return

        text_chunks = split_text(
            block_text,
            chunk_size=chunk_size,
        )

        for text_chunk in text_chunks:

            chunks.append(
                {
                    "chunk_id": f"chunk-{chunk_counter:04d}",
                    "source": source,
                    "page_number": block_start_page,
                    "page_start": block_start_page,
                    "page_end": block_end_page,
                    "section": block_section,
                    "subsection": block_subsection,
                    "subsubsection": block_subsubsection,
                    "text": text_chunk,
                }
            )

            chunk_counter += 1

        current_block = []
        block_start_page = None
        block_end_page = None
        block_section = None
        block_subsection = None
        block_subsubsection = None
        block_has_content = False

    for page in pages:

        page_number = page["page_number"]

        # Skip cover and Contents pages.
        if page_number < 9:
            continue

        text = page.get("text", "").strip()

        if not text:
            continue

        lines = text.splitlines()

        for raw_line in lines:

            line = raw_line.strip()

            if not line:
                if current_block:
                    current_block.append("")
                continue

            heading = detect_heading(line)

            if heading:

                # Finish the previous block only if it contains
                # actual content.
                flush_block()

                level = heading["level"]
                heading_text = heading["heading"]

                if level == 1:

                    current_section = heading_text
                    current_subsection = None
                    current_subsubsection = None

                elif level == 2:

                    current_subsection = heading_text
                    current_subsubsection = None

                else:

                    current_subsubsection = heading_text

                block_section = current_section
                block_subsection = current_subsection
                block_subsubsection = current_subsubsection

                block_start_page = page_number
                block_end_page = page_number

                current_block.append(heading_text)

                # This is only a heading so far.
                block_has_content = False

            else:

                # Content before a new heading continues the
                # existing document hierarchy.
                if block_start_page is None:

                    block_start_page = page_number

                    block_section = current_section
                    block_subsection = current_subsection
                    block_subsubsection = current_subsubsection

                block_end_page = page_number

                current_block.append(line)

                # We now have actual content.
                block_has_content = True

        if current_block:
            block_end_page = page_number

    # Flush the final block.
    flush_block()

    return chunks