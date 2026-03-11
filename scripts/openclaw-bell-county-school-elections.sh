#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# OpenClaw CLI: Bell County school districts — crawl for superintendent
# candidates and upcoming elected positions (board, trustee, election dates).
#
# Prerequisites: OpenClaw gateway running, OPENCLAW_GATEWAY_TOKEN set, jq.
#
# Usage:
#   ./scripts/openclaw-bell-county-school-elections.sh
#   ./scripts/openclaw-bell-county-school-elections.sh --out _data/bell_county_school_elections.json
# -----------------------------------------------------------------------------
set -euo pipefail

INDEX_URL="https://www.bellcountytx.com/about_us/school_districts/index.php"
OUT_FILE="${PWD}/_data/bell_county_school_elections.json"
MAX_ELECTION_PAGES_PER_DISTRICT=8

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT_FILE="$2"; shift 2 ;;
    -h|--help) head -18 "$0" | tail -14; exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

OUT_FILE="$(cd "$(dirname "$OUT_FILE")" && pwd)/$(basename "$OUT_FILE")"
mkdir -p "$(dirname "$OUT_FILE")"

if ! openclaw health &>/dev/null; then
  echo "OpenClaw gateway not reachable. Start with: openclaw gateway run"
  exit 1
fi

RESULTS_TMP=$(mktemp)
trap 'rm -f "$RESULTS_TMP"' EXIT

# Known Bell County school districts (from official index)
DISTRICT_NAMES=(Academy Bartlett Belton "Copperas Cove" Florence Gatesville Holland Killeen Lampasas Moody Rogers Rosebud Salado Temple Troy)
DISTRICT_URLS=(
  "http://www.academyisd.net/"
  "http://www.bartlett.txed.net/"
  "http://www.bisd.net/site/default.aspx?PageID=1"
  "http://www.ccisd.com/"
  "http://www.florenceisd.net/"
  "http://www.gatesvilleisd.org/"
  "http://www.hollandisd.org/"
  "https://www.killeenisd.org/"
  "https://www.lisdtx.org/"
  "http://www.moodyisd.org/"
  "http://www.rogersisd.org/"
  "http://www.rlisd.org/"
  "http://www.saladoisd.org/"
  "http://www.tisd.org/"
  "http://www.troyisd.org/"
)

TOTAL=${#DISTRICT_NAMES[@]}
echo "[bell-elections] Crawling ${TOTAL} districts for superintendent candidates and upcoming elected positions."

# Optional: try to get district links from index (same as calendars script)
echo "[bell-elections] Opening index: ${INDEX_URL}"
openclaw browser open "${INDEX_URL}"
sleep 3
DISTRICTS_FROM_PAGE=$(openclaw browser evaluate --fn '() => {
  const out = [];
  for (const a of document.querySelectorAll("a[href^=\"http\"]")) {
    if (a.href.includes("bellcountytx.com")) continue;
    const t = (a.textContent || "").trim();
    if (t.length >= 2 && t.length <= 80) out.push({ name: t, url: a.href });
  }
  return JSON.stringify(out);
}' 2>/dev/null || echo "[]")

if command -v jq &>/dev/null && [[ -n "$DISTRICTS_FROM_PAGE" ]] && [[ "$(echo "$DISTRICTS_FROM_PAGE" | jq 'length')" -gt 0 ]]; then
  DISTRICT_NAMES=()
  DISTRICT_URLS=()
  while IFS= read -r obj; do
    n=$(echo "$obj" | jq -r '.name // empty')
    u=$(echo "$obj" | jq -r '.url // empty')
    [[ -n "$n" && -n "$u" ]] && DISTRICT_NAMES+=("$n") && DISTRICT_URLS+=("$u")
  done < <(echo "$DISTRICTS_FROM_PAGE" | jq -c '.[]' 2>/dev/null)
  TOTAL=${#DISTRICT_NAMES[@]}
fi

for i in "${!DISTRICT_NAMES[@]}"; do
  name="${DISTRICT_NAMES[$i]}"
  url="${DISTRICT_URLS[$i]}"
  echo "[bell-elections] ($((i+1))/${TOTAL}) ${name}: ${url}"

  openclaw browser navigate "$url"
  sleep 2

  # Step 1: Find election/superintendent/board-related links on this site
  ELECTION_LINKS_JSON=$(openclaw browser evaluate --fn '() => {
    const keywords = ["election", "superintendent", "school board", "trustee", "trustees", "candidate", "candidates", "board of", "running for", "filing", "ballot", "bond", "board election"];
    const seen = new Set();
    const out = [];
    for (const a of document.querySelectorAll("a[href]")) {
      const h = (a.getAttribute("href") || "").toLowerCase();
      const t = (a.textContent || "").toLowerCase().replace(/\s+/g, " ");
      let match = false;
      for (const k of keywords) { if (h.includes(k) || t.includes(k)) { match = true; break; } }
      if (!match) continue;
      try {
        const full = new URL(a.href, location.origin).href;
        if (!full.startsWith("http") || seen.has(full)) continue;
        seen.add(full);
        out.push({ url: full, text: t.slice(0, 100) });
      } catch (e) {}
    }
    return JSON.stringify(out.slice(0, 12));
  }' 2>/dev/null || echo "[]")

  # Step 2: Extract superintendent and election info from current page (homepage)
  EXTRACT_JSON=$(openclaw browser evaluate --fn '() => {
    const body = document.body ? document.body.innerText : "";
    const bodyLo = body.toLowerCase();
    const superintendent_candidates = [];
    const upcoming_elections = [];
    const lines = body.split(/\n/).map(l => l.trim()).filter(l => l.length > 0);

    const superMatch = body.match(/superintendent\s*[:\-]\s*([^\n]+)/i) || body.match(/Dr\.\s+[\w\s]+\s*,\s*Superintendent/i);
    if (superMatch) superintendent_candidates.push({ name: superMatch[1].replace(/\s+/g, " ").slice(0, 120), role: "current_superintendent", source: "homepage" });

    const runForSuper = body.match(/running\s+for\s+superintendent[:\s]*([^\n]+)/gi) || body.match(/candidates?\s+for\s+superintendent[:\s]*([^\n]+)/gi);
    if (runForSuper) for (const m of runForSuper) {
      const name = m.replace(/.*(?:running\s+for|candidates?\s+for)\s+superintendent[:\s]*/i, "").replace(/\s+/g, " ").trim().slice(0, 120);
      if (name.length > 2) superintendent_candidates.push({ name: name, role: "candidate", source: "homepage" });
    }

    for (const line of lines) {
      const l = line.toLowerCase();
      if (l.includes("trustee") && (l.includes("place") || l.includes("position") || l.includes("seat")) && line.length < 150)
        upcoming_elections.push({ position: line.slice(0, 150), election_date: null, candidates: [], source: "homepage" });
      if ((l.includes("election date") || l.includes("election day") || l.includes("voting")) && /\d{1,2}[\/\-]\d{1,2}/.test(line))
        upcoming_elections.push({ position: "Election", election_date: line.replace(/\s+/g, " ").slice(0, 120), candidates: [], source: "homepage" });
      if (l.includes("candidate filing") || l.includes("filing deadline"))
        upcoming_elections.push({ position: "Candidate filing", election_date: line.replace(/\s+/g, " ").slice(0, 120), candidates: [], source: "homepage" });
    }

    const listItems = document.querySelectorAll("li, .candidate-name, .board-member, .trustee-name, [class*=\"candidate\"], [class*=\"trustee\"]");
    for (const el of listItems) {
      const t = (el.textContent || "").trim();
      if (t.length < 5 || t.length > 200) continue;
      const tlo = t.toLowerCase();
      if (tlo.includes("superintendent") && !tlo.includes("assistant")) superintendent_candidates.push({ name: t.replace(/\s+/g, " ").slice(0, 120), role: "mentioned", source: "homepage" });
      if ((tlo.includes("place") || tlo.includes("position")) && (tlo.includes("trustee") || tlo.includes("board"))) upcoming_elections.push({ position: t.slice(0, 150), election_date: null, candidates: [], source: "homepage" });
    }

    return JSON.stringify({ superintendent_candidates: superintendent_candidates.slice(0, 20), upcoming_elections: upcoming_elections.slice(0, 15) });
  }' 2>/dev/null || echo '{"superintendent_candidates":[],"upcoming_elections":[]}')

  # Step 3: Visit up to MAX_ELECTION_PAGES_PER_DISTRICT election-related links and merge findings
  PAGES_VISITED=0
  if command -v jq &>/dev/null && [[ -n "$ELECTION_LINKS_JSON" ]]; then
    while IFS= read -r linkUrl; do
      [[ -z "$linkUrl" || "$linkUrl" == "null" ]] && continue
      [[ "$PAGES_VISITED" -ge "$MAX_ELECTION_PAGES_PER_DISTRICT" ]] && break
      echo "[bell-elections]   -> election page: ${linkUrl:0:60}..."
      openclaw browser navigate "$linkUrl"
      sleep 2
      PAGE_EXTRACT=$(openclaw browser evaluate --fn '() => {
        const body = document.body ? document.body.innerText : "";
        const superintendent_candidates = [];
        const upcoming_elections = [];
        const lines = body.split(/\n/).map(l => l.trim()).filter(l => l.length > 0);
        for (const line of lines) {
          const l = line.toLowerCase();
          if (l.includes("superintendent") && !l.includes("assistant") && line.length < 150)
            superintendent_candidates.push({ name: line.replace(/\s+/g, " ").slice(0, 120), role: "candidate_or_incumbent", source: "election_page" });
          if (l.includes("trustee") && (l.includes("place") || l.includes("position")) && line.length < 150)
            upcoming_elections.push({ position: line.slice(0, 150), election_date: null, candidates: [], source: "election_page" });
          if ((l.includes("election date") || l.includes("may ") || l.includes("november")) && /\d{1,2}[\/\-]\d{1,2}/.test(line))
            upcoming_elections.push({ position: "Election", election_date: line.replace(/\s+/g, " ").slice(0, 120), candidates: [], source: "election_page" });
          if (l.includes("filing deadline") || l.includes("candidate filing"))
            upcoming_elections.push({ position: "Candidate filing", election_date: line.replace(/\s+/g, " ").slice(0, 120), candidates: [], source: "election_page" });
        }
        document.querySelectorAll("li, .candidate, [class*=\"candidate\"], [class*=\"trustee\"]").forEach(el => {
          const t = (el.textContent || "").trim();
          if (t.length > 4 && t.length < 200 && (t.toLowerCase().includes("superintendent") || t.toLowerCase().includes("trustee") || t.toLowerCase().includes("place")))
            upcoming_elections.push({ position: t.slice(0, 150), election_date: null, candidates: [], source: "election_page" });
        });
        return JSON.stringify({ superintendent_candidates: superintendent_candidates.slice(0, 10), upcoming_elections: upcoming_elections.slice(0, 10) });
      }' 2>/dev/null || echo '{"superintendent_candidates":[],"upcoming_elections":[]}')
      if command -v jq &>/dev/null && echo "$PAGE_EXTRACT" | jq -e . &>/dev/null; then
        EXTRACT_JSON=$(echo "$EXTRACT_JSON" | jq --argjson page "$PAGE_EXTRACT" '.superintendent_candidates += ($page.superintendent_candidates // []) | .upcoming_elections += ($page.upcoming_elections // [])' 2>/dev/null || echo "$EXTRACT_JSON")
      fi
      PAGES_VISITED=$((PAGES_VISITED + 1))
    done < <(echo "$ELECTION_LINKS_JSON" | jq -r '.[].url' 2>/dev/null | head -n "$MAX_ELECTION_PAGES_PER_DISTRICT")
  fi

  # Dedupe and write one JSON object per district to RESULTS_TMP
  SUPER_JSON=$(echo "$EXTRACT_JSON" | jq -c '.superintendent_candidates // []' 2>/dev/null || echo "[]")
  ELEC_JSON=$(echo "$EXTRACT_JSON" | jq -c '.upcoming_elections // []' 2>/dev/null || echo "[]")
  jq -n \
    --arg name "$name" \
    --arg url "$url" \
    --argjson super "$SUPER_JSON" \
    --argjson elections "$ELEC_JSON" \
    '{ district_name: $name, district_url: $url, superintendent_candidates: $super, upcoming_elections: $elections }' >> "$RESULTS_TMP" 2>/dev/null || true
done

# Build final bell_county_school_elections.json
GENERATED=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if [[ ! -s "$RESULTS_TMP" ]]; then
  jq -n \
    --arg generated "$GENERATED" \
    --arg source "$INDEX_URL" \
    '{ generated_utc: $generated, source_index_url: $source, districts: [] }' > "$OUT_FILE"
else
  jq -n --rawfile raw "$RESULTS_TMP" \
    --arg generated "$GENERATED" \
    --arg source "$INDEX_URL" \
    '($raw | split("\n") | map(select(length>0) | fromjson)) as $districts |
     { generated_utc: $generated, source_index_url: $source,
       districts: ($districts | map({
         district_name: .district_name,
         district_url: .district_url,
         superintendent_candidates: .superintendent_candidates,
         upcoming_elections: .upcoming_elections
       })) }' > "$OUT_FILE"
fi

echo "[bell-elections] Wrote ${OUT_FILE}"
echo "[bell-elections] Superintendent mentions: $(jq '[.districts[].superintendent_candidates | length] | add // 0' "$OUT_FILE" 2>/dev/null); upcoming_elections entries: $(jq '[.districts[].upcoming_elections | length] | add // 0' "$OUT_FILE" 2>/dev/null)"
