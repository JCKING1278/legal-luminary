"""
Text extraction unit tests.

Ported from Free Law Project Doctor (doctor/tests.py).
Tests insert_whitespace, get_word, remove_excess_whitespace, cleanup_content.
"""

import pytest
from unittest.mock import patch

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.text_extraction import (
    insert_whitespace,
    get_word,
    remove_excess_whitespace,
    cleanup_content,
    adjust_caption_lines,
)


class TestInsertWhitespace:
    """Ported from Doctor: TestRecapWhitespaceInsertions"""

    def test_insert_whitespace_new_line(self):
        content = "foo"
        word = {"line_num": 2, "par_num": 1, "left": 50, "top": 200, "width": 10, "height": 20}
        prev = {"line_num": 1, "par_num": 1, "left": 10, "top": 100, "width": 30, "height": 20}
        result = insert_whitespace(content, word, prev)
        # (50-0)/25 = 2 spaces after newline when prev_end=0
        assert result == "foo\n  "

    def test_insert_whitespace_new_paragraph(self):
        content = "foo"
        word = {"line_num": 1, "par_num": 2, "left": 50, "top": 200, "width": 10, "height": 20}
        prev = {"line_num": 2, "par_num": 1, "left": 10, "top": 100, "width": 30, "height": 20}
        result = insert_whitespace(content, word, prev)
        assert result == "foo\n  "

    def test_insert_whitespace_vertical_gap(self):
        content = "foo"
        word = {"line_num": 2, "par_num": 1, "left": 50, "top": 300, "width": 10, "height": 20}
        prev = {"line_num": 1, "par_num": 1, "left": 10, "top": 100, "width": 30, "height": 20}
        result = insert_whitespace(content, word, prev)
        assert result == "foo\n\n  "

    def test_insert_whitespace_horizontal_gap(self):
        content = "foo"
        word = {"line_num": 1, "par_num": 1, "left": 200, "top": 100, "width": 10, "height": 20}
        prev = {"line_num": 1, "par_num": 1, "left": 10, "top": 100, "width": 30, "height": 20}
        result = insert_whitespace(content, word, prev)
        assert result == "foo "

    def test_insert_whitespace_no_gap(self):
        content = "foo"
        word = {"line_num": 1, "par_num": 1, "left": 50, "top": 100, "width": 10, "height": 20}
        prev = {"line_num": 1, "par_num": 1, "left": 40, "top": 100, "width": 10, "height": 20}
        result = insert_whitespace(content, word, prev)
        assert result == "foo"


class TestGetWord:
    """Ported from Doctor: TestOCRConfidenceTests"""

    def test_confidence_zero(self):
        word_dict = {"text": "foo", "conf": 0, "left": 10, "width": 30}
        result = get_word(word_dict, 612, True)
        assert result == " "

    def test_confidence_low_and_in_margin(self):
        word_dict = {"text": "foo", "conf": 30, "left": 5, "width": 20}
        result = get_word(word_dict, 612, True)
        assert result == " "

    def test_confidence_below_threshold_short_word(self):
        word_dict = {"text": "foo", "conf": 3, "left": 200, "width": 20}
        result = get_word(word_dict, 612, True)
        assert result == "□□□ "

    def test_confidence_below_threshold_long_word(self):
        word_dict = {"text": "foobarbazfoobarbazfoobar", "conf": 3, "left": 200, "width": 200}
        result = get_word(word_dict, 612, True)
        assert "□" in result

    def test_confidence_below_threshold_in_right_margin(self):
        word_dict = {"text": "foo", "conf": 30, "left": 580, "width": 10}
        result = get_word(word_dict, 612, True)
        assert result == "□□□ "

    def test_valid_word_high_confidence(self):
        word_dict = {"text": "foo", "conf": 90, "left": 50, "width": 20}
        result = get_word(word_dict, 612, True)
        assert result == "foo "

    def test_word_on_left_edge(self):
        word_dict = {"text": "foo", "conf": 50, "left": 0, "width": 20}
        result = get_word(word_dict, 612, True)
        assert result == " "


class TestWhiteSpaceRemoval:
    """Ported from Doctor: TestWhiteSpaceRemoval"""

    def test_left_shift(self):
        document = """
 foo
 bar
 foo
 bar"""
        expected_result = """ foo
bar
foo
bar"""
        result = remove_excess_whitespace(document)
        assert result == expected_result

    def test_left_shift_when_artifact_exists(self):
        document = """
 foo
 bar
 | foo
 bar"""
        expected_result = """ foo
 bar
| foo
 bar"""
        result = remove_excess_whitespace(document)
        assert result == expected_result


class TestCleanupContent:
    """Ported from Doctor: TestCleanupContent"""

    def test_remove_floating_pipes(self):
        content = "This is a test line | \nAnother line"
        expected_result = "This is a test line\nAnother line\n"
        result = cleanup_content(content, 2)
        assert result == expected_result

    def test_remove_floating_artifacts_right_side(self):
        content = "This is a test line e \nAnother line"
        expected_result = "This is a test line\nAnother line\n"
        result = cleanup_content(content, 2)
        assert result == expected_result

    def test_remove_floating_pipes_and_artifacts(self):
        content = "This is a test line | and the content continues\nThis is another test line e \nFinal line"
        expected_result = "This is a test line | and the content continues\nThis is another test line\nFinal line\n"
        result = cleanup_content(content, 2)
        assert result == expected_result

    def test_no_floating_pipes_or_artifacts(self):
        content = "This is a test line JW-6\nAnother line\n"
        expected_result = "This is a test line JW-6\nAnother line\n\n"
        result = cleanup_content(content, 2)
        assert result == expected_result

    def test_adjust_caption(self):
        content = """ 10
 LESLIE MASSEY, ) Case No.: 2:16-cv-05001 GJS
 )
 oe ) PROPOSED} ORDER AWARDING
 12 Plaintiff, ) EQUAL ACCESS TO JUSTICE ACT
 ) ATTORNEY FEES AND EXPENSES
 13 VS. ) PURSUANT TO 28 U.S.C. § 2412(d)
 NANCY A. BERRYHILL, Acting ) AND COSTS PURSUANT TO 28
 14 || Commissioner of Social Security, ) U.S.C. § 1920
 15 Defendant )
 16 ) """
        result = adjust_caption_lines(content)
        assert "10" in result and "LESLIE MASSEY" in result
