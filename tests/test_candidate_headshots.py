from pathlib import Path

import yaml


def _load_candidates():
    root = Path(__file__).resolve().parent.parent
    path = root / "_data" / "candidates.yml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("candidates", [])


def _by_name(candidates, name):
    for c in candidates:
        if c.get("name") == name:
            return c
    return None


def _incumbent_record_for_office(candidates, office_group_key, incumbent_name):
    """Match candidate-card.html: pool by office_group_key and name == office_incumbent_name."""
    for c in candidates:
        if c.get("office_group_key") == office_group_key and c.get("name") == incumbent_name:
            return c
    return None


def test_commissioner_p4_challengers_do_not_reuse_incumbent_headshot():
    candidates = _load_candidates()
    louie = _incumbent_record_for_office(
        candidates, "Bell County Commissioner P4", "Louie Minor"
    )
    curtis = _by_name(candidates, "Curtis Emmons")
    ernest = _by_name(candidates, "Ernest Wilkerson")

    assert louie is not None
    assert curtis is not None
    assert ernest is not None

    louie_headshot = louie.get("headshot_url")
    assert louie_headshot, "Incumbent headshot should exist for comparison."

    assert curtis.get("headshot_url") != louie_headshot
    assert ernest.get("headshot_url") != louie_headshot


def test_justice_p4_place2_challengers_do_not_reuse_incumbent_headshot():
    candidates = _load_candidates()
    incumbent = _incumbent_record_for_office(
        candidates, "Bell JP P4 Place 2", "Beatrice Cox"
    )
    latasha = _by_name(candidates, "Latasha Carroway Quarles")
    nicola = _by_name(candidates, "Nicola J. James")
    jessica = _by_name(candidates, "Jessica A. Gonzalez")

    assert incumbent is not None
    assert latasha is not None
    assert nicola is not None
    assert jessica is not None

    incumbent_headshot = incumbent.get("headshot_url")
    assert incumbent_headshot, "Incumbent headshot should exist for comparison."

    assert latasha.get("headshot_url") != incumbent_headshot
    assert nicola.get("headshot_url") != incumbent_headshot
    assert jessica.get("headshot_url") != incumbent_headshot
