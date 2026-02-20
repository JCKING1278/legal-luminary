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
    "executablePath": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
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
 texas_data_crawler.js texas_data_pipeline.py pipeline.yml
