"""
Text extraction utilities for legal documents.

Ported from Free Law Project Doctor (doctor/lib/text_extraction.py).
Used for fallback PDF extraction when Doctor service is unavailable.
"""

import re
from typing import Optional


def insert_whitespace(content: str, word: dict, prev: dict) -> str:
    """
    Insert whitespace after or before word based on OCR layout.

    :param content: The text extracted so far
    :param word: The OCR extraction object (dict with line_num, par_num, left, top, width, height)
    :param prev: The previous word object extracted
    :return: The content with the whitespace appended
    """
    is_new_line = prev.get("line_num", 0) != word.get("line_num", 0)
    is_new_par = prev.get("par_num", 0) != word.get("par_num", 0)
    prev_end = prev.get("left", 1) + prev.get("width", 1)

    if is_new_line or is_new_par:
        vertical_gap = word.get("top", 0) - (
            prev.get("top", 0) + prev.get("height", 0)
        )
        content += "\n\n" if vertical_gap > 100 else "\n"
        prev_end = 0

    content += " " * int((word.get("left", 0) - prev_end) / 25)
    return content


def get_word(word_dict: dict, width: float, strip_margin: bool) -> str:
    """
    Append word to content, applying OCR confidence and margin filters.

    :param word_dict: the word object from tesseract
    :param width: The width of the document
    :param strip_margin: should we strip the margin
    :return: The text with space
    """
    pixels_per_inch = width / 8.5
    if strip_margin:
        left_margin = 1 * pixels_per_inch
        right_margin = 7.5 * pixels_per_inch
    else:
        left_margin = 0.5 * pixels_per_inch
        right_margin = 8.0 * pixels_per_inch

    word = word_dict.get("text", "")
    conf = word_dict.get("conf", 0)

    no_confidence = 0
    very_low_confidence = 5
    low_confidence = 40
    short_word_len = 3
    long_word_len = 20

    if (
        word_dict.get("left", 0) + word_dict.get("width", 0) < left_margin
        and conf < low_confidence
    ):
        word = " " * len(word)
    elif (conf == no_confidence and len(word) <= short_word_len) or word_dict.get(
        "left", 1
    ) == 0:
        word = " " * len(word)
    elif conf < very_low_confidence and (
        len(word) <= short_word_len or len(word) > long_word_len
    ):
        word = "□" * len(word)
    elif conf < low_confidence and word_dict.get("left", 0) > right_margin:
        word = "□" * len(word)

    return f"{word} "


def remove_excess_whitespace(document: str) -> str:
    """
    Remove excess whitespace from OCR output.
    Shifts text left if possible.
    """
    if not document:
        return ""
    m = re.findall(r"(^ +)", document, re.MULTILINE)
    if m:
        shift_left = len(min(m))
        pattern = f"(^ {{{shift_left}}})"
        document = re.sub(pattern, "", document, flags=re.MULTILINE)
        document = re.sub(r"^ +$", "", document, flags=re.MULTILINE)
    return document.strip("\n")


def adjust_caption_lines(page_text: str) -> str:
    """
    Adjust alignment of ) or : or § used in legal captions.
    § for Texas courts, : for NY, ) for many courts.
    """
    for separator in [r")", "§", ":"]:
        pattern = rf"(.* +{re.escape(separator)} .*\n)"
        matches = list(re.finditer(pattern, page_text))
        central_matches = [
            match.group().rindex(separator)
            for match in matches
            if 30 <= match.group().rindex(separator) <= 70
        ]
        if len(central_matches) < 3:
            continue
        longest = max(central_matches)
        page = []
        for row in page_text.splitlines():
            index = row.find(f" {separator}")
            if index >= 0:
                addition = (longest - index) * " "
                row = row.replace(f" {separator}", f"{addition}{separator}")
            page.append(row)
        return "\n".join(page)
    return page_text


def cleanup_content(content: str, page_number: int) -> str:
    """
    Reduce legal document line clutter.
    Removes floating pipes, right-side artifacts, shifts left.
    """
    # Remove " | " at end of line (floating pipe)
    content = re.sub(r" \| *\n", "\n", content, flags=re.MULTILINE)
    # Also match Doctor-style: 4+ spaces + pipe + space at EOL
    content = re.sub(r"\s{4,}\| *$", "", content, flags=re.MULTILINE)

    pattern = r"\s{10,}[a-zA-Z0-9|] $"
    content = re.sub(pattern, "", content, flags=re.MULTILINE)

    content = remove_excess_whitespace(content)
    if page_number == 1:
        content = adjust_caption_lines(content)

    return f"{content}\n"
