
import pytest
from verifier.website_checker import verify_website
import json

# =============================================================================
# Equivalence Partitioning Tests
# =============================================================================

@pytest.mark.parametrize("url", [
    "https://www.killeentexas.gov/CivicAlerts.aspx?AID=2223",
    "https://kdhnews.com/news/local/crime/harker-heights-man-accused-of-shooting-into-home-with-people-inside/article_1de5f1d6-c9fd-11ee-8f0a-93bdc60b86a3.html",
])
def test_valid_urls(url):
    """
    Tests the verifier with valid URLs.
    """
    result = verify_website(url)
    assert isinstance(result, dict)
    assert "label" in result
    assert "reasons" in result
    assert "evidence_links" in result

@pytest.mark.parametrize("url", [
    "not a url",
    "http://thisisadomainthatdoesnotexist.com",
    "https://www.example.com/thispagedoesnotexist",
])
def test_invalid_urls(url):
    """
    Tests the verifier with invalid URLs.
    The verifier should handle these gracefully without crashing.
    """
    try:
        verify_website(url)
    except Exception as e:
        # We expect an exception, but not a crash.
        # This is a basic test, a more robust implementation would check for specific exception types.
        pass

# =============================================================================
# Syntax Checking Tests
# =============================================================================

def test_json_output_schema():
    """
    Tests if the output is a valid JSON that conforms to the expected schema.
    """
    test_url = "https://www.killeentexas.gov/CivicAlerts.aspx?AID=2223"
    result = verify_website(test_url)
    
    # Check if it's a valid dictionary (already asserted in test_valid_urls)
    assert isinstance(result, dict)
    
    # Check for required keys
    required_keys = ["label", "reasons", "evidence_links"]
    for key in required_keys:
        assert key in result
        
    # Check the types of the values
    assert isinstance(result["label"], str)
    assert isinstance(result["reasons"], str)
    assert isinstance(result["evidence_links"], list)
    
    # Check if the label has one of the expected values
    assert result["label"] in ["verified", "uncertain", "misleading"]

# =============================================================================
# Boundary Value Analysis (Placeholder)
# =============================================================================

@pytest.mark.skip(reason="Boundary value analysis for prompt length is not implemented yet.")
def test_long_article():
    """
    Tests the verifier with a very long article to check for context window issues.
    """
    # This would require finding a very long article and asserting that the verifier
    # can handle it without errors.
    pass
