#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# OpenClaw CLI automation: crawl https://www.sll.texas.gov
#
# Prerequisites:
#   - OpenClaw gateway running (e.g. openclaw gateway run)
#   - OPENCLAW_GATEWAY_TOKEN (and OPENCLAW_GATEWAY_PASSWORD if required) set
#
# Usage:
#   ./scripts/openclaw-sll-crawl.sh [--max-pages N] [--out-dir DIR]
#
# Options:
#   --max-pages N   Cap number of internal pages to snapshot (default: 20)
#   --out-dir DIR   Output directory for snapshots/screenshots (default: ./crawl-out/sll.texas.gov)
#   --screenshot    Capture full-page screenshots in addition to snapshots
#   --no-follow     Only crawl the homepage (no link following)
# -----------------------------------------------------------------------------
set -euo pipefail

BASE_URL="https://www.sll.texas.gov"
MAX_PAGES=20
OUT_DIR="${PWD}/crawl-out/sll.texas.gov"
DO_SCREENSHOT=false
FOLLOW_LINKS=true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --max-pages)   MAX_PAGES="$2";  shift 2 ;;
    --out-dir)     OUT_DIR="$2";   shift 2 ;;
    --screenshot)  DO_SCREENSHOT=true; shift ;;
    --no-follow)   FOLLOW_LINKS=false; shift ;;
    -h|--help)
      head -25 "$0" | tail -20
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

mkdir -p "$OUT_DIR"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
PAGES_DIR="${OUT_DIR}/${TIMESTAMP}"
mkdir -p "$PAGES_DIR"

# Check gateway is reachable
if ! openclaw health &>/dev/null; then
  echo "OpenClaw gateway not reachable. Start it with: openclaw gateway run"
  exit 1
fi

echo "[crawl] Opening ${BASE_URL} ..."
openclaw browser open "${BASE_URL}"
sleep 3

# Homepage snapshot + optional screenshot
openclaw browser snapshot --out "${PAGES_DIR}/index.json" --limit 800
echo "[crawl] Saved snapshot: ${PAGES_DIR}/index.json"
if "$DO_SCREENSHOT"; then
  openclaw browser screenshot --full-page 2>/dev/null || openclaw browser screenshot
  echo "[crawl] Screenshot captured (check gateway media dir if not in PAGES_DIR)"
fi

if ! "$FOLLOW_LINKS"; then
  echo "[crawl] --no-follow: skipping link discovery. Done."
  exit 0
fi

# Get same-origin links via page evaluate (no ref = whole document)
LINKS_JSON=$(openclaw browser evaluate --fn '() => {
  const seen = new Set();
  return JSON.stringify(
    [...document.querySelectorAll("a[href]")]
      .map(a => { try { return new URL(a.href, location.origin); } catch { return null; } })
      .filter(u => u && u.origin === "https://www.sll.texas.gov" && u.pathname !== "/" && !seen.has(u.pathname) && (seen.add(u.pathname), true))
      .slice(0, 500)
      .map(u => u.href)
  );
}' 2>/dev/null || echo "[]")

# Parse and cap at MAX_PAGES (prefer jq; fallback for bash)
TO_VISIT=()
if command -v jq &>/dev/null; then
  while IFS= read -r u; do [[ -n "$u" ]] && TO_VISIT+=("$u"); done < <(echo "$LINKS_JSON" | jq -r '.[]' 2>/dev/null | head -n "$MAX_PAGES")
else
  while IFS= read -r line; do
    [[ -n "$line" && "$line" != "[]" ]] && TO_VISIT+=("$line"); done < <(echo "$LINKS_JSON" | grep -oE 'https://www\.sll\.texas\.gov[^"]*' | sort -u | head -n "$MAX_PAGES")
fi

COUNT=${#TO_VISIT[@]}
echo "[crawl] Discovered ${COUNT} internal links to visit (max ${MAX_PAGES})"

for i in "${!TO_VISIT[@]}"; do
  url="${TO_VISIT[$i]}"
  path_slug=$(echo "$url" | sed -E 's|https://www\.sll\.texas\.gov||' | tr '/' '_' | sed 's/^_//')
  [[ -z "$path_slug" ]] && path_slug="index"
  safe_name=$(echo "$path_slug" | tr -cd '[:alnum:]_.-' | head -c 120)
  echo "[crawl] ($((i+1))/${COUNT}) $url -> ${safe_name}"
  openclaw browser navigate "$url"
  sleep 2
  openclaw browser snapshot --out "${PAGES_DIR}/${safe_name}.json" --limit 600
  if "$DO_SCREENSHOT"; then
    openclaw browser screenshot 2>/dev/null || true
  fi
done

echo "[crawl] Done. Output: ${PAGES_DIR}"
echo "[crawl] Snapshot count: $(find "${PAGES_DIR}" -name '*.json' 2>/dev/null | wc -l)"
