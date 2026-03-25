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


def _has_valid_headshot_url(value) -> bool:
    if value is None:
        return False
    if not isinstance(value, str):
        return False
    v = value.strip()
    if not v:
        return False
    return v.lower() != "null"


def test_no_two_people_share_same_headshot_within_office():
    """
    Hard invariant:
    - Within the same `office_group_key`, each distinct person must have a unique
      non-null `headshot_url`.

    This catches both:
    - Incumbent photo reuse on challengers
    - Accidental aliasing where two separate people get the same headshot asset
    """

    candidates = _load_candidates()

    # office_group_key -> headshot_url -> set(names)
    seen = {}
    for c in candidates:
        office_group_key = c.get("office_group_key")
        name = c.get("name")
        headshot_url = c.get("headshot_url")

        if not office_group_key or not name or not _has_valid_headshot_url(headshot_url):
            continue

        seen.setdefault(office_group_key, {}).setdefault(headshot_url, set()).add(name)

    violations = []
    for office_group_key, by_url in seen.items():
        for headshot_url, names in by_url.items():
            if len(names) > 1:
                violations.append((office_group_key, headshot_url, sorted(names)))

    assert not violations, (
        "Found duplicate headshot_url assigned to multiple people within the same office.\n"
        + "\n".join(
            f"- office_group_key={office_key}: {names} share headshot_url={url}"
            for office_key, url, names in violations
        )
    )
