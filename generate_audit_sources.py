import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

GOOGLE_SEARCH_HOSTS = {"google.com", "www.google.com", "news.google.com"}
SEARCH_ENGINE_HOST_HINTS = (
    "google.",
    "duckduckgo.",
    "search.brave.com",
    "ecosia.org",
    "bing.com",
    "search.yahoo.com",
)


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _extract_front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    front = {}
    i = 1
    while i < len(lines):
        line = lines[i]
        if line.strip() == "---":
            break
        if ":" in line:
            k, v = line.split(":", 1)
            front[k.strip()] = v.strip().strip('"').strip("'")
        i += 1
    return front


def _hostname(url: str) -> str:
    try:
        return urlparse(url).hostname or ""
    except Exception:
        return ""


def _is_google_search_url(url: str) -> bool:
    host = _hostname(url)
    if host not in GOOGLE_SEARCH_HOSTS:
        return False
    parsed = urlparse(url)
    return parsed.path.startswith("/search")


def _is_search_url(url: str) -> bool:
    host = _hostname(url)
    if any(h in host for h in SEARCH_ENGINE_HOST_HINTS):
        parsed = urlparse(url)
        return parsed.path.startswith("/search") or "search" in parsed.path
    return False


def _search_query(url: str) -> str:
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        for key in ("q", "query", "p"):
            val = qs.get(key)
            if val:
                return " ".join(val)
    except Exception:
        pass
    return ""


def _search_query_has_geo(search_query: str, city: str) -> bool:
    q = search_query.lower()
    city_l = city.lower().strip()
    return ("central texas" in q) or (city_l and city_l in q)


def _collect_urls(front: dict, candidate_data: dict, sources_data: dict) -> list[tuple[str, str]]:
    urls: list[tuple[str, str]] = []

    candidate_website = front.get("candidate_website") or candidate_data.get("candidate_website")
    if candidate_website:
        urls.append(("candidate_website", str(candidate_website)))

    for s in candidate_data.get("social_links", []) or []:
        urls.append(("social_links", str(s)))
    for n in candidate_data.get("news_mentions", []) or []:
        if isinstance(n, dict) and n.get("url"):
            urls.append(("news_mentions", str(n["url"])))

    for s in sources_data.get("sources", []) or []:
        if isinstance(s, dict) and s.get("url"):
            urls.append(("sources_json", str(s["url"])))
        elif isinstance(s, str):
            urls.append(("sources_json", s))

    # de-duplicate while preserving first source label
    seen = {}
    for label, url in urls:
        if url not in seen:
            seen[url] = label
    return [(label, url) for url, label in seen.items()]


def audit():
    candidates_dir = Path("_candidates")
    data_path = Path("_data/audit_sources.json")
    candidate_data_dir = Path("_data/candidates")
    result = {}

    for file in sorted(candidates_dir.glob("*.md")):
        slug = file.stem
        front = _extract_front_matter(file)
        city = str(front.get("city", "")).strip()
        candidate_data_file = next(
            candidate_data_dir.glob(f"**/{slug}.json"),
            Path(""),
        )
        candidate_data = _load_json(candidate_data_file) if candidate_data_file else {}

        src_file = Path(f"_data/sources_{slug}.json")
        src_data = _load_json(src_file)
        source_urls = _collect_urls(front, candidate_data, src_data)

        google_search_urls = [u for _, u in source_urls if _is_google_search_url(u)]
        search_urls = [u for _, u in source_urls if _is_search_url(u)]
        direct_urls = [u for _, u in source_urls if not _is_search_url(u)]

        missing_geo_queries = []
        for u in search_urls:
            q = _search_query(u)
            if not _search_query_has_geo(q, city):
                suffix = "central texas" if not city else city
                missing_geo_queries.append(
                    {
                        "url": u,
                        "search_query": q,
                        "recommended_query": f"{q} {suffix}".strip(),
                    }
                )

        total_sources = len(source_urls)
        effective_source_count = max(0, total_sources - len(google_search_urls))
        penalty_google_search = len(google_search_urls) * 10
        penalty_missing_geo = len(missing_geo_queries) * 5
        quality_score = max(0, 100 - penalty_google_search - penalty_missing_geo)

        verified = effective_source_count >= 2 and len(google_search_urls) == 0
        result[slug] = {
            "city": city,
            "source_count_total": total_sources,
            "source_count_effective": effective_source_count,
            "direct_source_count": len(direct_urls),
            "google_search_url_count": len(google_search_urls),
            "search_url_count": len(search_urls),
            "quality_score": quality_score,
            "verified": verified,
            "grading_penalties": {
                "google_search_urls": penalty_google_search,
                "missing_geo_search_terms": penalty_missing_geo,
            },
            "google_search_urls": google_search_urls,
            "search_queries_missing_geo": missing_geo_queries,
            "notes": "Effective source count excludes google.com/search URLs.",
        }

    data_path.parent.mkdir(parents=True, exist_ok=True)
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Audit written to {data_path}")


if __name__ == "__main__":
    audit()
