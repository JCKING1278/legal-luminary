#!/usr/bin/env python3
"""
Aho-Corasick Confidence Tracker for Legal Luminary

This module implements an Aho-Corasick automaton to track patterns that contribute
to confidence scoring and project milestones. When patterns are found in files,
they boost the confidence rating based on milestone alignment.

Usage:
    from aho_corasick_confidence import AhoCorasickConfidenceTracker
    tracker = AhoCorasickConfidenceTracker()
    tracker.analyze_file("path/to/file.md")
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class Milestone(Enum):
    """Project milestones that contribute to confidence scoring."""

    M1_INIT = auto()  # Project initialization and structure
    M2_VERIFY = auto()  # Source verification and content validation
    M3_COVERAGE = auto()  # Code coverage and testing infrastructure
    M4_VV = auto()  # Full V&V testing and deployment


@dataclass
class PatternRule:
    """Represents a confidence pattern with associated milestone."""

    pattern: str
    description: str
    confidence_boost: float
    milestone: Milestone
    category: str = "general"


@dataclass
class MatchResult:
    """Result of a pattern match."""

    pattern: str
    description: str
    line_number: int
    context: str
    confidence_boost: float
    milestone: Milestone


@dataclass
class FileAnalysis:
    """Analysis result for a single file."""

    filepath: str
    total_boost: float = 0.0
    matches: list = field(default_factory=list)
    milestone_contributions: dict = field(default_factory=dict)
    categories_found: set = field(default_factory=set)


class AhoCorasickAutomaton:
    """
    Aho-Corasick automaton for multi-pattern string matching.

    This implementation builds a trie with failure links for efficient
    pattern matching across multiple patterns simultaneously.
    """

    class Node:
        """Trie node for the automaton."""

        def __init__(self):
            self.children: dict = {}
            self.fail: Optional["AhoCorasickAutomaton.Node"] = None
            self.output: list = []  # Patterns that end at this node
            self.pattern_rules: list = []

    def __init__(self):
        self.root = self.Node()
        self.patterns: list[PatternRule] = []

    def add_pattern(self, rule: PatternRule) -> None:
        """Add a pattern to the automaton."""
        node = self.root
        for char in rule.pattern:
            if char not in node.children:
                node.children[char] = self.Node()
            node = node.children[char]
            node.pattern_rules.append(rule)
        node.output.append(rule.pattern)
        self.patterns.append(rule)

    def build(self) -> None:
        """Build failure links using BFS."""
        from collections import deque

        queue = deque()

        for child in self.root.children.values():
            child.fail = self.root
            queue.append(child)

        while queue:
            current = queue.popleft()

            for char, child in current.children.items():
                queue.append(child)

                fail_state = current.fail
                while fail_state and char not in fail_state.children:
                    fail_state = fail_state.fail

                child.fail = (
                    fail_state.children.get(char, self.root)
                    if fail_state
                    else self.root
                )
                child.output.extend(child.fail.output)
                child.pattern_rules.extend(child.fail.pattern_rules)

    def search(self, text: str) -> list[tuple[str, int, list[PatternRule]]]:
        """
        Search for all patterns in text.

        Returns:
            List of (matched_pattern, end_position, rules) tuples
        """
        results = []
        node = self.root

        for i, char in enumerate(text):
            while node is not None and char not in node.children:
                node = node.fail

            if node is None:
                node = self.root
                continue

            node = node.children.get(char, self.root)

            for rule in node.pattern_rules:
                results.append((rule.pattern, i, [rule]))

            for pattern in node.output:
                if node.pattern_rules:
                    continue
                for p_rule in self.patterns:
                    if p_rule.pattern == pattern:
                        results.append((pattern, i, [p_rule]))
                        break

        return results


class ConfidencePatternLibrary:
    """Library of patterns that contribute to confidence scoring."""

    MILESTONE_M1_PATTERNS = [
        PatternRule(
            "---", "Frontmatter delimiter", 0.01, Milestone.M1_INIT, "structure"
        ),
        PatternRule(
            "layout:", "Jekyll layout defined", 0.005, Milestone.M1_INIT, "structure"
        ),
        PatternRule(
            "permalink:", "Permalink defined", 0.005, Milestone.M1_INIT, "structure"
        ),
        PatternRule("title:", "Title metadata", 0.003, Milestone.M1_INIT, "metadata"),
        PatternRule(
            "description:", "Description metadata", 0.003, Milestone.M1_INIT, "metadata"
        ),
        PatternRule("# ", "Markdown heading", 0.002, Milestone.M1_INIT, "format"),
        PatternRule("| ", "Table row", 0.002, Milestone.M1_INIT, "format"),
    ]

    MILESTONE_M2_PATTERNS = [
        PatternRule(
            "sources:", "Sources section", 0.05, Milestone.M2_VERIFY, "verification"
        ),
        PatternRule("url:", "Source URL", 0.03, Milestone.M2_VERIFY, "verification"),
        PatternRule(
            "evidence:",
            "Evidence description",
            0.05,
            Milestone.M2_VERIFY,
            "verification",
        ),
        PatternRule(
            "visited: true", "Source visited", 0.03, Milestone.M2_VERIFY, "verification"
        ),
        PatternRule(
            "confirmed: true",
            "Source confirmed",
            0.05,
            Milestone.M2_VERIFY,
            "verification",
        ),
        PatternRule(
            "CONFIDENCE SCORE:",
            "Confidence header",
            0.04,
            Milestone.M2_VERIFY,
            "metadata",
        ),
        PatternRule(
            "QFA_STATE:", "QFA state tracking", 0.03, Milestone.M2_VERIFY, "qfa"
        ),
        PatternRule(
            "AHO_CORASICK:", "Aho-Corasick tracking", 0.05, Milestone.M2_VERIFY, "qfa"
        ),
        PatternRule(
            "bellcountytx.com",
            "Bell County official",
            0.02,
            Milestone.M2_VERIFY,
            "source",
        ),
        PatternRule(
            "capitol.texas.gov",
            "Texas legislature",
            0.02,
            Milestone.M2_VERIFY,
            "source",
        ),
        PatternRule(
            "justice.bellcounty.texas.gov",
            "Bell County courts",
            0.02,
            Milestone.M2_VERIFY,
            "source",
        ),
        PatternRule(
            "Fort Cavazos", "Fort Cavazos content", 0.03, Milestone.M2_VERIFY, "content"
        ),
        PatternRule(
            "Fort Hood", "Fort Hood content", 0.03, Milestone.M2_VERIFY, "content"
        ),
    ]

    MILESTONE_M3_PATTERNS = [
        PatternRule("def ", "Python function", 0.003, Milestone.M3_COVERAGE, "code"),
        PatternRule("class ", "Python class", 0.003, Milestone.M3_COVERAGE, "code"),
        PatternRule("import ", "Python import", 0.001, Milestone.M3_COVERAGE, "code"),
        PatternRule(
            "from ", "Python from import", 0.001, Milestone.M3_COVERAGE, "code"
        ),
        PatternRule(
            "async def", "Async function", 0.002, Milestone.M3_COVERAGE, "code"
        ),
        PatternRule("test", "Test reference", 0.002, Milestone.M3_COVERAGE, "testing"),
        PatternRule(
            "assert ", "Assert statement", 0.002, Milestone.M3_COVERAGE, "testing"
        ),
        PatternRule(
            "pytest", "Pytest framework", 0.003, Milestone.M3_COVERAGE, "testing"
        ),
        PatternRule(
            "unittest", "Unit test framework", 0.003, Milestone.M3_COVERAGE, "testing"
        ),
        PatternRule(
            "coverage", "Coverage tool", 0.004, Milestone.M3_COVERAGE, "coverage"
        ),
        PatternRule("_test.py", "Test file", 0.003, Milestone.M3_COVERAGE, "coverage"),
        PatternRule(
            "validate", "Validation function", 0.003, Milestone.M3_COVERAGE, "quality"
        ),
    ]

    MILESTONE_M4_PATTERNS = [
        PatternRule(
            "V&V_INTEGRATION:",
            "V&V integration",
            0.004,
            Milestone.M4_VV,
            "verification",
        ),
        PatternRule(
            "MILESTONE:", "Milestone tracking", 0.003, Milestone.M4_VV, "tracking"
        ),
        PatternRule(
            "LAST_UPDATED:", "Last update timestamp", 0.002, Milestone.M4_VV, "metadata"
        ),
        PatternRule(
            "verified_at:",
            "Verification timestamp",
            0.003,
            Milestone.M4_VV,
            "verification",
        ),
        PatternRule(
            "CODE_REFACTOR:", "Code refactoring", 0.003, Milestone.M4_VV, "quality"
        ),
        PatternRule(
            "_confidence", "Confidence metadata", 0.004, Milestone.M4_VV, "metadata"
        ),
        PatternRule(
            "data_metadata", "Data metadata", 0.003, Milestone.M4_VV, "metadata"
        ),
        PatternRule(
            "next_review:", "Review scheduled", 0.003, Milestone.M4_VV, "process"
        ),
        PatternRule(
            "decay_rate:", "Decay rate defined", 0.002, Milestone.M4_VV, "quality"
        ),
        PatternRule(
            "human_validated",
            "Human validation",
            0.005,
            Milestone.M4_VV,
            "verification",
        ),
    ]

    ALL_PATTERNS = (
        MILESTONE_M1_PATTERNS
        + MILESTONE_M2_PATTERNS
        + MILESTONE_M3_PATTERNS
        + MILESTONE_M4_PATTERNS
    )

    @classmethod
    def build_automaton(cls) -> AhoCorasickAutomaton:
        """Build and return an Aho-Corasick automaton with all patterns."""
        automaton = AhoCorasickAutomaton()
        for rule in cls.ALL_PATTERNS:
            automaton.add_pattern(rule)
        automaton.build()
        return automaton


class AhoCorasickConfidenceTracker:
    """
    High-level tracker using Aho-Corasick for confidence scoring.

    This tracker:
    1. Builds an Aho-Corasick automaton with milestone-aligned patterns
    2. Analyzes files for pattern matches
    3. Calculates confidence boosts based on matches
    4. Tracks contribution to project milestones
    """

    def __init__(self):
        self.automaton = ConfidencePatternLibrary.build_automaton()
        self.file_history: dict[str, float] = {}

    def analyze_file(self, filepath: str, content: str) -> FileAnalysis:
        """
        Analyze a file for confidence-contributing patterns.

        Uses UNIQUE pattern matches only - each pattern contributes once
        regardless of how many times it appears in the file.

        Args:
            filepath: Path to the file being analyzed
            content: Content of the file

        Returns:
            FileAnalysis with match details and confidence boost
        """
        analysis = FileAnalysis(filepath=filepath)

        matches = self.automaton.search(content)

        milestone_boosts = {m: 0.0 for m in Milestone}
        category_boosts = {}
        unique_patterns_found = set()

        for pattern, pos, rules in matches:
            for rule in rules:
                if pattern not in unique_patterns_found:
                    unique_patterns_found.add(pattern)

                    analysis.matches.append(
                        MatchResult(
                            pattern=rule.pattern,
                            description=rule.description,
                            line_number=content[:pos].count("\n") + 1,
                            context=self._get_context(content, pos, rule.pattern),
                            confidence_boost=rule.confidence_boost,
                            milestone=rule.milestone,
                        )
                    )

                    milestone_boosts[rule.milestone] += rule.confidence_boost
                    analysis.categories_found.add(rule.category)

                    if rule.category not in category_boosts:
                        category_boosts[rule.category] = 0.0
                    category_boosts[rule.category] += rule.confidence_boost

        analysis.milestone_contributions = {
            m.name: round(boost, 4) for m, boost in milestone_boosts.items()
        }
        analysis.total_boost = round(sum(milestone_boosts.values()), 4)

        return analysis

    def _get_context(self, text: str, pos: int, pattern: str, window: int = 40) -> str:
        """Get surrounding context for a match."""
        start = max(0, pos - window)
        end = min(len(text), pos + len(pattern) + window)
        context = text[start:end].replace("\n", " ").strip()
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        return context

    def get_milestone_progress(self) -> dict[str, dict]:
        """Get progress toward each milestone based on file analysis."""
        return {
            "M1_INIT": {
                "name": "Project Initialization",
                "target": 0.10,
                "current": 0.0,
            },
            "M2_VERIFY": {
                "name": "Source Verification",
                "target": 0.15,
                "current": 0.0,
            },
            "M3_COVERAGE": {"name": "Code Coverage", "target": 0.18, "current": 0.0},
            "M4_VV": {"name": "V&V Testing", "target": 0.20, "current": 0.0},
        }

    def calculate_final_confidence(self, base: float, analysis: FileAnalysis) -> float:
        """
        Calculate final confidence score incorporating Aho-Corasick matches.

        Formula:
        C_final = C_base + Σ(Aho-Corasick boosts) + milestone bonuses

        Args:
            base: Base confidence score (0.5 - 0.707)
            analysis: File analysis result

        Returns:
            Final confidence score (capped at 1.0)
        """
        m2_contribution = analysis.milestone_contributions.get("M2_VERIFY", 0)
        m4_contribution = analysis.milestone_contributions.get("M4_VV", 0)

        milestone_bonus = 0.0
        if m2_contribution >= 0.10:
            milestone_bonus += 0.05
        if m4_contribution >= 0.05:
            milestone_bonus += 0.04

        final = base + analysis.total_boost + milestone_bonus
        return min(1.0, round(final, 4))


def main():
    """CLI for Aho-Corasick confidence analysis."""
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description="Aho-Corasick confidence tracker for Legal Luminary"
    )
    parser.add_argument("filepath", help="File to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--base", type=float, default=0.707, help="Base confidence")
    args = parser.parse_args()

    tracker = AhoCorasickConfidenceTracker()

    filepath = Path(args.filepath)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        return 1

    content = filepath.read_text(encoding="utf-8")
    analysis = tracker.analyze_file(str(filepath), content)

    final_confidence = tracker.calculate_final_confidence(args.base, analysis)

    if args.json:
        result = {
            "filepath": str(filepath),
            "base_confidence": args.base,
            "aho_corasick_boost": analysis.total_boost,
            "final_confidence": final_confidence,
            "milestone_contributions": analysis.milestone_contributions,
            "categories_found": list(analysis.categories_found),
            "match_count": len(analysis.matches),
            "matches": [
                {
                    "pattern": m.pattern,
                    "description": m.description,
                    "line": m.line_number,
                    "boost": m.confidence_boost,
                    "milestone": m.milestone.name,
                }
                for m in analysis.matches[:20]
            ],
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"File: {filepath}")
        print(f"Base Confidence: {args.base}")
        print(f"Aho-Corasick Boost: +{analysis.total_boost}")
        print(f"Final Confidence: {final_confidence}")
        print()
        print("Milestone Contributions:")
        for milestone, boost in analysis.milestone_contributions.items():
            if boost > 0:
                print(f"  {milestone}: +{boost}")
        print()
        print(f"Categories Found: {', '.join(analysis.categories_found)}")
        print(f"Total Matches: {len(analysis.matches)}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
