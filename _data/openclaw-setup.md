# OpenClaw Configuration - Owner Needs to Run

## Current Setup
- HPCC: Running OpenClaw gateway on port 18789 (SSH tunnel active)
- Mac: Need to run browser commands locally

## Commands to run as OWNER (not root):

```bash
# 1. Kill any existing OpenClaw processes
pkill -f openclaw 2>/dev/null

# 2. Set up SSH tunnel to HPCC
ssh -q -i ~/.ssh/id_rsa -L 18789:localhost:18789 -N -f sweeden@login.hpcc.ttu.edu

# 3. Set environment variables
export OPENCLAW_GATEWAY_TOKEN=feddc25e700fbc524608e299ba026322c13172e17a91230bd2566f439ec0ca60
export OPENCLAW_GATEWAY_PASSWORD=Quantum7Bridge

# 4. Configure and start local gateway with Chrome
cat > ~/.openclaw/openclaw.json << 'EOF'
{
  "browser": {
    "executablePath": "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "noSandbox": true
  },
  "gateway": {
    "mode": "local"
  }
}
EOF

# 5. Start gateway
openclaw gateway run &

# 6. Wait for gateway to start, then open browser
sleep 5
openclaw browser open https://data.texas.gov
```

## Alternative: Use Chrome Extension Profile
If Chrome extension is installed:
- Open Chrome manually
- Click OpenClaw extension to attach
- Use: openclaw browser --browser-profile chrome open https://data.texas.gov

### "Relay not reachable" (http://127.0.0.1:18792)
The **browser extension** talks to the **relay** on port **18792**, not the gateway (18789). The relay is started by the **same process** as the gateway and only runs when the gateway runs **on this machine**.

- **If you only use the SSH tunnel** from HPCC: the relay (18792) is on HPCC, so the extension on your Mac cannot reach it. Either:
  1. **Run the gateway locally** so the relay is on your Mac (recommended for extension use):
     ```bash
     # Kill tunnel if it was only for gateway CLI
     openclaw gateway run
     # Then in Chrome, extension should connect to 127.0.0.1:18792
     ```
  2. **Tunnel the relay port too** (extension may still have auth issues with remote relay):
     ```bash
     ssh -q -i ~/.ssh/id_rsa -L 18789:localhost:18789 -L 18792:localhost:18792 -N -f sweeden@login.hpcc.ttu.edu
     ```
- **If the gateway is already running locally** and you still see "relay not reachable":
  - Check that the relay port is open: `lsof -i :18792`
  - Restart the gateway: `pkill -f openclaw; openclaw gateway run &`
  - In the extension options, set the relay URL to `http://127.0.0.1:18792` and use the same token as `OPENCLAW_GATEWAY_TOKEN`

## Crawl Texas State Law Library (sll.texas.gov)

Automation script uses the OpenClaw browser CLI to crawl [Texas State Law Library](https://www.sll.texas.gov): open homepage, snapshot, discover same-origin links, then visit and snapshot up to N pages.

**Prereqs:** Gateway running (`openclaw gateway run`), token/password set.

```bash
# From repo root
./scripts/openclaw-sll-crawl.sh

# Options
./scripts/openclaw-sll-crawl.sh --max-pages 10 --out-dir ./my-crawl
./scripts/openclaw-sll-crawl.sh --no-follow          # homepage only
./scripts/openclaw-sll-crawl.sh --screenshot          # also capture screenshots
```

Output: `./crawl-out/sll.texas.gov/<timestamp>/*.json` (snapshots). Optional screenshots go to gateway media dir unless configured otherwise.

### Schedule with OpenClaw cron (Gateway)

If the gateway is running and has cron support, add a job to run the crawl (e.g. weekly):

```bash
# List existing jobs
openclaw cron list

# Add a job (syntax depends on your gateway; example)
openclaw cron add --name sll-crawl --schedule "0 8 * * 1" --command "cd /path/to/ll && ./scripts/openclaw-sll-crawl.sh --max-pages 15"

# Run once for testing
openclaw cron run sll-crawl
```

Note: Cron runs on the **gateway host**. If the gateway is on HPCC and the script lives on your Mac, either run the crawl from a Mac-scheduled cron (e.g. `crontab -e`) when the tunnel is up, or deploy the script to HPCC and use `openclaw cron add` there.

## Bell County school districts — upcoming events (upcoming_events.json)

Automation script visits each official [Bell County school district](https://www.bellcountytx.com/about_us/school_districts/index.php) (Academy, Bartlett, Belton, Copperas Cove, Florence, Gatesville, Holland, Killeen, Lampasas, Moody, Rogers, Rosebud, Salado, Temple, Troy), finds each site’s calendar/events section, and compiles **this week’s** upcoming events into `_data/upcoming_events.json`.

**Prereqs:** Gateway running, token set. `jq` required for JSON building.

```bash
# From repo root (default output: _data/upcoming_events.json)
./scripts/openclaw-bell-county-calendars.sh

# Custom output path
./scripts/openclaw-bell-county-calendars.sh --out ./_data/upcoming_events.json
```

**Output schema:** `generated_utc`, `week_start`, `week_end`, `source_index_url`, and `districts[]` with `district_name`, `district_url`, `calendar_url`, and `events[]` (`date`, `title`, `url`). Event extraction is best-effort (sites vary; uses `[data-date]`, `.event`, calendar tables, etc.).

## Bell County school districts — superintendent & elections (bell_county_school_elections.json)

Crawls each official [Bell County school district](https://www.bellcountytx.com/about_us/school_districts/index.php) site to find **who is running for superintendent** and **upcoming elected positions** (trustee places, board seats, election dates, filing deadlines). For each district the script:

1. Opens the district homepage and extracts superintendent mentions and election-related lines (e.g. “Election date”, “Candidate filing”, “Trustee Place X”).
2. Finds and visits up to 8 election-related pages per district (links containing “election”, “superintendent”, “school board”, “trustee”, “candidate”, “filing”, “ballot”, etc.) and merges findings.

**Prereqs:** Gateway running, token set, `jq` installed.

```bash
# From repo root (writes _data/bell_county_school_elections.json)
./scripts/openclaw-bell-county-school-elections.sh

# Custom output path
./scripts/openclaw-bell-county-school-elections.sh --out _data/bell_county_school_elections.json
```

**Output schema:** `generated_utc`, `source_index_url`, and `districts[]` with `district_name`, `district_url`, `superintendent_candidates[]` (each: `name`, `role` e.g. current_superintendent/candidate/mentioned, `source` e.g. homepage/election_page), and `upcoming_elections[]` (each: `position`, `election_date`, `candidates`, `source`). Extraction is best-effort across varying district site structures.
