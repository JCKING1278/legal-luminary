#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# OpenClaw CLI: Bell County school districts — crawl calendar sections for
# this week's upcoming events and compile _data/upcoming_events.json
#
# Prerequisites: OpenClaw gateway running, OPENCLAW_GATEWAY_TOKEN set.
#
# Usage:
#   ./scripts/openclaw-bell-county-calendars.sh
#   ./scripts/openclaw-bell-county-calendars.sh --out /path/to/upcoming_events.json
# -----------------------------------------------------------------------------
set -euo pipefail

INDEX_URL="https://www.bellcountytx.com/about_us/school_districts/index.php"
OUT_FILE="${PWD}/_data/upcoming_events.json"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT_FILE="$2"; shift 2 ;;
    -h|--help) head -18 "$0" | tail -14; exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Resolve out file to absolute path and ensure _data exists
OUT_FILE="$(cd "$(dirname "$OUT_FILE")" && pwd)/$(basename "$OUT_FILE")"
mkdir -p "$(dirname "$OUT_FILE")"

# Current week (Monday–Sunday) in ISO format
if date -v-mon +%Y-%m-%d &>/dev/null; then
  WEEK_START=$(date -v-mon +%Y-%m-%d)
  WEEK_END=$(date -v-mon -v+6d +%Y-%m-%d)
else
  WEEK_START=$(date -d "monday this week" +%Y-%m-%d 2>/dev/null || date +%Y-%m-%d)
  WEEK_END=$(date -d "sunday this week" +%Y-%m-%d 2>/dev/null || date -d "+6 days" +%Y-%m-%d)
fi

if ! openclaw health &>/dev/null; then
  echo "OpenClaw gateway not reachable. Start with: openclaw gateway run"
  exit 1
fi

# Temp file to accumulate district results (JSONL: one JSON object per district)
RESULTS_TMP=$(mktemp)
trap 'rm -f "$RESULTS_TMP"' EXIT

echo "[bell-cal] Opening index: ${INDEX_URL}"
openclaw browser open "${INDEX_URL}"
sleep 3

# Extract district links: external links from the School Districts list (exclude bellcountytx.com)
DISTRICTS_JSON=$(openclaw browser evaluate --fn '() => {
  const out = [];
  const anchors = document.querySelectorAll("a[href^=\"http\"]");
  const skip = "bellcountytx.com";
  for (const a of anchors) {
    try {
      const href = a.href;
      if (href.includes(skip)) continue;
      const text = (a.textContent || "").trim();
      if (text.length < 2 || text.length > 80) continue;
      out.push({ name: text, url: href });
    } catch (e) {}
  }
  return JSON.stringify(out);
}' 2>/dev/null || echo "[]")

# Parse district list (expect names like Academy, Bartlett, Belton, ...)
DISTRICT_NAMES=()
DISTRICT_URLS=()
if command -v jq &>/dev/null; then
  while IFS= read -r obj; do
    name=$(echo "$obj" | jq -r '.name // empty')
    url=$(echo "$obj" | jq -r '.url // empty')
    [[ -z "$name" || -z "$url" ]] && continue
    [[ "$url" == *"bellcountytx"* ]] && continue
    DISTRICT_NAMES+=("$name")
    DISTRICT_URLS+=("$url")
  done < <(echo "$DISTRICTS_JSON" | jq -c '.[]' 2>/dev/null)
fi

# If jq gave us nothing, use known list from Bell County page
if [[ ${#DISTRICT_NAMES[@]} -eq 0 ]]; then
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
fi

TOTAL=${#DISTRICT_NAMES[@]}
echo "[bell-cal] Found ${TOTAL} districts. Week: ${WEEK_START} – ${WEEK_END}"

for i in "${!DISTRICT_NAMES[@]}"; do
  name="${DISTRICT_NAMES[$i]}"
  url="${DISTRICT_URLS[$i]}"
  echo "[bell-cal] ($((i+1))/${TOTAL}) ${name}: ${url}"

  openclaw browser navigate "$url"
  sleep 2

  # Find calendar URL: link whose href or text contains calendar/events
  CALENDAR_PAYLOAD=$(openclaw browser evaluate --fn '() => {
    const weekStart = "'"${WEEK_START}"'";
    const weekEnd = "'"${WEEK_END}"'";
    let calendarUrl = null;
    for (const a of document.querySelectorAll("a[href]")) {
      const h = (a.getAttribute("href") || "").toLowerCase();
      const t = (a.textContent || "").toLowerCase();
      if (h.includes("calendar") || t.includes("calendar") || t.includes("calendars") || (t.includes("event") && (h.includes("event") || h.includes("calendar")))) {
        try {
          const full = new URL(a.href, location.origin).href;
          if (full.startsWith("http")) { calendarUrl = full; break; }
        } catch (e) {}
      }
    }
    const events = [];
    const bodyText = document.body ? document.body.innerText : "";
    const dateRe = /(\d{1,2})[\/\-](\d{1,2})[\/\-]?(\d{2,4})?|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}/gi;
    const monthNum = { jan:1,feb:2,mar:3,apr:4,may:5,jun:6,jul:7,aug:8,sep:9,oct:10,nov:11,dec:12 };
    function inWeek(yr, mo, day) {
      const d = yr + "-" + String(mo).padStart(2,"0") + "-" + String(day).padStart(2,"0");
      return d >= weekStart && d <= weekEnd;
    }
    const rows = document.querySelectorAll("[data-date], .event, .calendar-event, .event-item, .event-list li, table.events tr, .view-content .views-row");
    for (const el of rows) {
      const dateAttr = el.getAttribute("data-date") || el.getAttribute("datetime");
      let dateStr = null;
      if (dateAttr) {
        dateStr = dateAttr.split("T")[0].split(" ")[0];
        if (dateStr.length === 10 && dateStr >= weekStart && dateStr <= weekEnd) {
          const title = (el.querySelector("a, .title, .event-title, td:last-child") || el).textContent.trim().slice(0, 200);
          const link = (el.querySelector("a[href]") || {}).href || "";
          if (title) events.push({ date: dateStr, title: title, url: link || null });
        }
      }
    }
    if (events.length === 0 && bodyText) {
      const m = bodyText.match(dateRe);
      if (m) {
        const snippet = bodyText.slice(Math.max(0, bodyText.indexOf(m[0]) - 20), bodyText.indexOf(m[0]) + 120);
        events.push({ date: weekStart, title: snippet.replace(/\s+/g, " ").trim().slice(0, 200), url: null });
      }
    }
    return JSON.stringify({ calendarUrl: calendarUrl, events: events });
  }' 2>/dev/null || echo '{"calendarUrl":null,"events":[]}')

  # If we found a calendar link, navigate and re-extract events
  CALENDAR_URL=$(echo "$CALENDAR_PAYLOAD" | jq -r '.calendarUrl // empty' 2>/dev/null)
  if [[ -n "$CALENDAR_URL" && "$CALENDAR_URL" != "null" ]]; then
    echo "[bell-cal]   -> calendar: ${CALENDAR_URL}"
    openclaw browser navigate "$CALENDAR_URL"
    sleep 2
    CALENDAR_PAYLOAD=$(openclaw browser evaluate --fn '() => {
      const weekStart = "'"${WEEK_START}"'";
      const weekEnd = "'"${WEEK_END}"'";
      const events = [];
      for (const el of document.querySelectorAll("[data-date], .event, .calendar-event, .event-item, .event-list li, table tr, .view-content .views-row")) {
        const dateAttr = el.getAttribute("data-date") || el.getAttribute("datetime");
        if (!dateAttr) continue;
        const dateStr = dateAttr.split("T")[0].split(" ")[0];
        if (dateStr.length !== 10 || dateStr < weekStart || dateStr > weekEnd) continue;
        const title = (el.querySelector("a, .title, .event-title, td") || el).textContent.trim().slice(0, 200);
        const link = (el.querySelector("a[href]") || {}).href || null;
        if (title) events.push({ date: dateStr, title: title, url: link });
      }
      return JSON.stringify({ calendarUrl: "'"${CALENDAR_URL}"'", events: events });
    }' 2>/dev/null || echo "$CALENDAR_PAYLOAD")
  fi

  EVENTS_JSON=$(echo "$CALENDAR_PAYLOAD" | jq -c '.events // []' 2>/dev/null || echo "[]")
  CAL_FINAL=$(echo "$CALENDAR_PAYLOAD" | jq -r '.calendarUrl // null' 2>/dev/null)

  # Append one line per district for merging
  jq -n \
    --arg name "$name" \
    --arg url "$url" \
    --arg calendarUrl "${CAL_FINAL:-}" \
    --argjson events "$EVENTS_JSON" \
    '{ district_name: $name, district_url: $url, calendar_url: (if $calendarUrl == "" or $calendarUrl == "null" then null else $calendarUrl end), events: $events }' >> "$RESULTS_TMP" 2>/dev/null || true
done

# Build final upcoming_events.json (parse JSONL temp file)
GENERATED=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if [[ ! -s "$RESULTS_TMP" ]]; then
  jq -n \
    --arg generated "$GENERATED" \
    --arg week_start "$WEEK_START" \
    --arg week_end "$WEEK_END" \
    --arg source "$INDEX_URL" \
    '{ generated_utc: $generated, week_start: $week_start, week_end: $week_end, source_index_url: $source, districts: [] }' > "$OUT_FILE"
else
  jq -n --rawfile raw "$RESULTS_TMP" \
    --arg generated "$GENERATED" \
    --arg week_start "$WEEK_START" \
    --arg week_end "$WEEK_END" \
    --arg source "$INDEX_URL" \
    '($raw | split("\n") | map(select(length>0) | fromjson)) as $districts |
     {
       generated_utc: $generated,
       week_start: $week_start,
       week_end: $week_end,
       source_index_url: $source,
       districts: ($districts | map({
         district_name: .district_name,
         district_url: .district_url,
         calendar_url: .calendar_url,
         events: .events
       }))
     }' > "$OUT_FILE"
fi

echo "[bell-cal] Wrote ${OUT_FILE}"
echo "[bell-cal] Districts: ${TOTAL}; total events: $(jq '[.districts[].events | length] | add // 0' "$OUT_FILE" 2>/dev/null || echo "0")"
