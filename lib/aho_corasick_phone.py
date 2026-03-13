"""
Aho-Corasick automaton to find repeating digits in phone numbers.

Finds all occurrences of consecutive repeated digits (e.g. "00", "11", "222")
in a digit string in a single pass.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Iterator


@dataclass
class Node:
    """Trie node for Aho-Corasick."""

    char: str | None = None  # edge label from parent
    parent: Node | None = None
    children: dict[str, Node] = field(default_factory=dict)
    fail: Node | None = None
    output: list[str] = field(default_factory=list)  # patterns ending at this node
    depth: int = 0


def build_automaton(patterns: list[str]) -> Node:
    """
    Build an Aho-Corasick automaton for the given patterns.
    Returns the root node.
    """
    root = Node(depth=0)

    # Build trie
    for pat in patterns:
        node = root
        for c in pat:
            if c not in node.children:
                child = Node(char=c, parent=node, depth=node.depth + 1)
                node.children[c] = child
            node = node.children[c]
        node.output.append(pat)

    # BFS to set failure links
    q: deque[Node] = deque()
    for child in root.children.values():
        child.fail = root
        q.append(child)

    while q:
        node = q.popleft()
        for char, child in node.children.items():
            q.append(child)
            fail = node.fail
            while fail is not None and char not in fail.children:
                fail = fail.parent.fail if fail.parent else None
            if fail is None:
                child.fail = root
            else:
                child.fail = fail.children[char]
            # Inherit output from fail link for overlapping matches
            child.output = list(child.output)
            if child.fail.output:
                child.output.extend(child.fail.output)

    return root


def search(text: str, root: Node) -> Iterator[tuple[int, str]]:
    """
    Search for all pattern occurrences in text.
    Yields (end_index, pattern) for each match.
    end_index is the index of the last character of the match (0-based).
    """
    node = root
    for i, c in enumerate(text):
        while node is not None and c not in node.children:
            node = node.fail
        if node is None:
            node = root
            continue
        node = node.children[c]
        for pat in node.output:
            yield (i, pat)


def repeating_digit_patterns(min_length: int = 2, max_length: int = 2) -> list[str]:
    """Generate patterns for repeating digits: 00, 11, ..., 99 or longer runs."""
    patterns: list[str] = []
    for d in "0123456789":
        for length in range(min_length, max_length + 1):
            patterns.append(d * length)
    return patterns


def find_repeating_digits(
    phone: str,
    min_run: int = 2,
    max_run: int = 10,
) -> list[tuple[int, str, str]]:
    """
    Find all repeating-digit runs in a phone number string.

    Only considers digit characters; non-digits are skipped during matching
    (positions are reported in the original string).

    Args:
        phone: String that may contain digits, spaces, dashes, parens, etc.
        min_run: Minimum run length (default 2, e.g. "11").
        max_run: Maximum run length to pre-build patterns for (default 10).

    Returns:
        List of (end_index, digit, run) e.g. (5, "1", "11") for "11" ending at index 5.
    """
    digit_positions: list[tuple[int, str]] = []  # (index, digit)
    for i, c in enumerate(phone):
        if c in "0123456789":
            digit_positions.append((i, c))
    digit_string = "".join(d for _, d in digit_positions)
    if not digit_string:
        return []

    patterns = repeating_digit_patterns(min_length=min_run, max_length=max_run)
    root = build_automaton(patterns)

    results: list[tuple[int, str, str]] = []
    for end_idx_digit, pat in search(digit_string, root):
        # Map back to position in original string
        orig_end = digit_positions[end_idx_digit][0]
        digit = pat[0]
        results.append((orig_end, digit, pat))
    return results


def search_text(
    text: str,
    min_run: int = 2,
    max_run: int = 2,
    context_chars: int = 40,
) -> list[tuple[int, str, str, str]]:
    """
    Find repeating digits in arbitrary text (e.g. web page content).

    Returns list of (end_index, digit, run, context_snippet).
    """
    matches = find_repeating_digits(text, min_run=min_run, max_run=max_run)
    results: list[tuple[int, str, str, str]] = []
    for end_pos, digit, run in matches:
        start = max(0, end_pos - len(run) - context_chars)
        end = min(len(text), end_pos + 1 + context_chars)
        snippet = text[start:end].replace("\n", " ")
        if len(snippet) > 2 * context_chars + len(run):
            snippet = "..." + snippet + "..."
        results.append((end_pos, digit, run, snippet))
    return results


def main() -> None:
    """Demo: find repeating digits in a few phone numbers."""
    examples = [
        "512-555-1133",
        "(512) 555-1111",
        "800-222-3333",
        "1234567890",
        "no repeats 512-555-1234",
    ]
    for phone in examples:
        matches = find_repeating_digits(phone)
        print(f"  {phone!r}")
        if matches:
            for end_pos, digit, run in matches:
                print(f"    -> repeated '{digit}': {run!r} ending at index {end_pos}")
        else:
            print("    -> no repeating digits")
        print()


if __name__ == "__main__":
    main()
