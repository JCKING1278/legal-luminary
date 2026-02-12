"""
Human test questions for the Legal Luminary agent.

These map to SPEC §9 (Human Test Questions). Each test runs the appropriate
validator with the query that a human might ask; mocks are used for external
APIs so tests run without network.
"""

import pytest
from unittest.mock import patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from state import create_initial_state, ContentType
from validators.news_validator import validate_news_source
from validators.judge_validator import validate_judge
from validators.official_validator import validate_official
from validators.election_validator import validate_election
from validators.law_validator import validate_law
from validators.court_doc_validator import validate_court_document
from validators.template_validator import validate_legal_template
from validators.notary_validator import validate_notary


# Human question test cases: (content_type, query, expect_verified, description)
HUMAN_QUESTION_CASES = [
    # H1: news source
    ("news_source", "https://www.supremecourt.gov/opinions/slipopinions.aspx", True, "Is this news site trustworthy?"),
    # H2: judge
    ("judge", "Chief Justice John Roberts", True, "Is Chief Justice John Roberts a real judge?"),
    # H3: official
    ("official", "Senator Ted Cruz, Texas", True, "Is Ted Cruz really a U.S. Senator from Texas?"),
    # H4: election
    ("election", "2024 Presidential Election", True, "When was the 2024 presidential election?"),
    # H5: law
    ("law", "Texas Penal Code Chapter 22", True, "What does Texas Penal Code Chapter 22 say?"),
    # H6: court document
    ("court_document", "Brown v. Board of Education, 347 U.S. 483 (1954)", True, "Can you verify this court case?"),
    # H7: legal template
    ("legal_template", "AO 440 - Summons in a Civil Action", True, "Is federal form AO 440 the right summons form?"),
    # H8: notary (positive: a name that could be in DB — we mock as found)
    ("notary_public", "Jane Smith, Austin TX", True, "Is [Name] a notary in Texas?"),
    # H9: judge fabricated
    ("judge", "Judge Marcus Thornberry, Supreme Court", False, "Was Judge Marcus Thornberry on the Supreme Court?"),
    # H10: notary negative test (Scott Weeden must NOT be found per rubric)
    ("notary_public", "Scott Weeden", False, "Is Scott Weeden a Texas notary?"),
]


def _validation_key(content_type: str) -> str:
    """Map content_type to state key for validation result."""
    return {
        "news_source": "news_validation",
        "judge": "judge_validation",
        "official": "official_validation",
        "election": "election_validation",
        "law": "law_validation",
        "court_document": "court_doc_validation",
        "legal_template": "template_validation",
        "notary_public": "notary_validation",
    }[content_type]


@pytest.mark.parametrize("content_type,query,expect_verified,description", HUMAN_QUESTION_CASES)
def test_human_question_news(content_type, query, expect_verified, description):
    if content_type != "news_source":
        pytest.skip("news_source only")
    state = create_initial_state(content_type, query)
    with patch("validators.news_validator._llm_credibility_check", return_value=0.9 if expect_verified else 0.2):
        result = validate_news_source(state)
    key = _validation_key(content_type)
    assert result[key]["is_valid"] is expect_verified


@pytest.mark.parametrize("content_type,query,expect_verified,description", HUMAN_QUESTION_CASES)
def test_human_question_judge(content_type, query, expect_verified, description):
    if content_type != "judge":
        pytest.skip("judge only")
    state = create_initial_state(content_type, query)
    with patch("validators.judge_validator._search_courtlistener_judges",
               return_value={"found": expect_verified, "name": "John Roberts" if expect_verified else "", "court": "Supreme Court", "url": ""}):
        with patch("validators.judge_validator._llm_judge_verification", return_value=0.95 if expect_verified else 0.1):
            result = validate_judge(state)
    key = _validation_key(content_type)
    assert result[key]["is_valid"] is expect_verified


@pytest.mark.parametrize("content_type,query,expect_verified,description", HUMAN_QUESTION_CASES)
def test_human_question_official(content_type, query, expect_verified, description):
    if content_type != "official":
        pytest.skip("official only")
    state = create_initial_state(content_type, query)
    with patch("validators.official_validator._search_congress_members",
               return_value={"found": expect_verified, "name": "Ted Cruz", "state": "TX", "party": "R", "url": ""}):
        with patch("validators.official_validator._search_fec_candidates",
                   return_value={"found": expect_verified, "name": "CRUZ, TED", "url": ""}):
            with patch("validators.official_validator._llm_official_verification", return_value=0.95 if expect_verified else 0.1):
                result = validate_official(state)
    key = _validation_key(content_type)
    assert result[key]["is_valid"] is expect_verified


@pytest.mark.parametrize("content_type,query,expect_verified,description", HUMAN_QUESTION_CASES)
def test_human_question_election(content_type, query, expect_verified, description):
    if content_type != "election":
        pytest.skip("election only")
    state = create_initial_state(content_type, query)
    with patch("validators.election_validator._search_fec_elections",
               return_value={"found": expect_verified, "election": "President", "cycle": "2024", "url": ""}):
        with patch("validators.election_validator._llm_election_verification", return_value=0.9 if expect_verified else 0.1):
            result = validate_election(state)
    key = _validation_key(content_type)
    assert result[key]["is_valid"] is expect_verified


@pytest.mark.parametrize("content_type,query,expect_verified,description", HUMAN_QUESTION_CASES)
def test_human_question_law(content_type, query, expect_verified, description):
    if content_type != "law":
        pytest.skip("law only")
    state = create_initial_state(content_type, query)
    with patch("validators.law_validator._search_congress_bills",
               return_value={"found": expect_verified, "title": "Penal Code", "url": ""}):
        with patch("validators.law_validator._llm_law_verification", return_value=0.95 if expect_verified else 0.1):
            result = validate_law(state)
    key = _validation_key(content_type)
    assert result[key]["is_valid"] is expect_verified


@pytest.mark.parametrize("content_type,query,expect_verified,description", HUMAN_QUESTION_CASES)
def test_human_question_court_doc(content_type, query, expect_verified, description):
    if content_type != "court_document":
        pytest.skip("court_document only")
    state = create_initial_state(content_type, query)
    with patch("validators.court_doc_validator._search_courtlistener_opinions",
               return_value={"found": expect_verified, "case_name": "Brown v. Board of Education", "url": ""}):
        with patch("validators.court_doc_validator._search_courtlistener_dockets", return_value={"found": False}):
            with patch("validators.court_doc_validator._llm_court_doc_verification", return_value=0.95 if expect_verified else 0.1):
                result = validate_court_document(state)
    key = _validation_key(content_type)
    assert result[key]["is_valid"] is expect_verified


@pytest.mark.parametrize("content_type,query,expect_verified,description", HUMAN_QUESTION_CASES)
def test_human_question_template(content_type, query, expect_verified, description):
    if content_type != "legal_template":
        pytest.skip("legal_template only")
    state = create_initial_state(content_type, query)
    reg = {"found": expect_verified, "registry": "Federal Court Forms", "url": "https://uscourts.gov/forms"}
    with patch("validators.template_validator._check_form_registry", return_value=reg):
        with patch("validators.template_validator._llm_template_assessment", return_value=0.85 if expect_verified else 0.2):
            result = validate_legal_template(state)
    key = _validation_key(content_type)
    if expect_verified:
        assert result[key]["is_valid"] is True
    else:
        assert result[key]["is_valid"] is False


@pytest.mark.parametrize("content_type,query,expect_verified,description", HUMAN_QUESTION_CASES)
def test_human_question_notary(content_type, query, expect_verified, description):
    if content_type != "notary_public":
        pytest.skip("notary_public only")
    state = create_initial_state(content_type, query)
    # Mock notary search: validator imports search_notaries from services.notary_finder inside function
    from services.notary_finder import NotaryRecord
    mock_results = []
    if expect_verified:
        mock_results = [
            NotaryRecord(notary_id="1", first_name="Jane", last_name="Smith", effective_date="", expire_date="2026-01-01", address="Austin, TX", email_address="", surety_company="", agency=""),
        ]
    with patch("services.notary_finder.search_notaries", return_value=mock_results):
        result = validate_notary(state)
    key = _validation_key(content_type)
    assert result[key]["is_valid"] is expect_verified


def test_scott_weeden_notary_negative():
    """Rubric: Scott Weeden must NOT be found in TX SOS Notary database (negative test)."""
    state = create_initial_state("notary_public", "Scott Weeden")
    with patch("services.notary_finder.search_notaries", return_value=[]):
        result = validate_notary(state)
    assert result["notary_validation"]["is_valid"] is False
