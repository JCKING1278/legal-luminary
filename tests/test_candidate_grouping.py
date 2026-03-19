import os
import sys


# Make sure we can import the scripts module directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import enrich_candidates_with_serpapi as enrich


def test_election_phase_up_for_office_true():
    assert enrich._election_phase_up_for_office({"election_phase": "primary_2026"}) is True
    assert enrich._election_phase_up_for_office({"election_phase": "runoff_2026"}) is True
    assert enrich._election_phase_up_for_office({"election_phase": "general_2026"}) is True


def test_election_phase_up_for_office_false():
    assert enrich._election_phase_up_for_office({"election_phase": "seated"}) is False


def test_pick_office_incumbent_name_incumbent_wins():
    group = [
        {"name": "Opponent A", "status": "candidate"},
        {"name": "Incumbent B", "status": "incumbent"},
    ]
    assert enrich._pick_office_incumbent_name(group) == "Incumbent B"


def test_extract_group_city_state_function_killeen_mayor():
    cand = {
        "position": "Mayor, City of Killeen",
        "office": "Killeen Mayor",
        "jurisdiction": "Killeen",
    }
    city, state, func = enrich._extract_group_city_state_function(cand)
    assert city == "Killeen"
    assert state == "Texas"
    assert func == "Executive"


def test_office_sort_key_incumbent_first_within_office():
    office = "Bell County Commissioner P2"
    group_city = ""
    group_function = "CountyAdministration"

    incumbent = {
        "id": 99,
        "status": "incumbent",
        "office": office,
        "group_city": group_city,
        "group_function": group_function,
    }
    challenger = {
        "id": 1,
        "status": "candidate",
        "office": office,
        "group_city": group_city,
        "group_function": group_function,
    }

    incumbent_key = enrich._office_sort_key(
        incumbent,
        office=office,
        group_city=group_city,
        group_function=group_function,
    )
    challenger_key = enrich._office_sort_key(
        challenger,
        office=office,
        group_city=group_city,
        group_function=group_function,
    )

    assert incumbent_key < challenger_key

