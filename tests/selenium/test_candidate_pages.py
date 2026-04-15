import json
from pathlib import Path

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

CASES = json.loads(Path(__file__).with_name("candidate_ui_cases.json").read_text(encoding="utf-8"))


@pytest.mark.integration
@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_candidate_page_content_visible(stealth_chrome: WebDriver, case: dict) -> None:
    driver = stealth_chrome
    driver.get(case["page_url"])
    body = driver.find_element(By.CSS_SELECTOR, case.get("selector_hint", "body"))
    assert case["assertion_text"] in body.text
