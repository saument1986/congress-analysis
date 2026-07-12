# Architecture Overview

## System Design

The legislation tracker is a **push-based ETL pipeline** running on two machines:

### Machine 1: Desktop (Ubuntu Linux)
- **Hermes Agent** orchestrates the workflow via daily cron jobs
- **Gemma 4 12B** (local on AMD RX 6800 GPU) performs LLM summarization
- **DeepSeek V4 Flash** via OpenRouter acts as fallback when GPU is busy
- **Honcho** stores user preferences and state between runs
- Generates HTML output locally before deploying

### Machine 2: Raspberry Pi 5
- **Caddy** serves the static HTML site on port 8083
- No database — purely static files, zero maintenance
- Accessible via Tailscale on home network

### Pipeline Flow

```
[1] Daily Cron Trigger (8AM ET)
         ↓
[2] Change Detection
    ├── Read state.json (stored hashes from last run)
    ├── Fetch RSS feeds
    ├── Compare MD5 hashes
    └── If unchanged → update timestamp, deploy, EXIT
         ↓ (only if changed)
[3] Fetch
    ├── Congress.gov RSS (most-viewed + all bills)
    ├── FL Senate RSS
    └── Brevard Clerk website scrape
         ↓
[4] Parse & Summarize
    ├── Extract bill number, title, status, committee
    ├── LLM generates: What It Does / Financial Impact / Who's Affected
    └── Assign impact score 1-10 + topic tags
         ↓
[5] Generate HTML
    ├── Dark theme with responsive CSS
    ├── Bill cards with full analysis
    ├── Subject filter tabs
    ├── Coming Up section
    └── Resources sidebar
         ↓
[6] Deploy
    └── SCP → Raspberry Pi → Caddy serves instantly
```

## Data Flow

```
RSS/Web ──→ Hermes Cron ──→ LLM (Gemma/DeepSeek) ──→ HTML ──→ SCP ──→ Pi/Caddy
                                                                           │
                                                                      ┌────┴────┐
                                                                      │ Browser │
                                                                      └─────────┘
```

## Key Design Decisions

**Why Raspberry Pi + Caddy over cloud hosting?**
- Zero recurring costs
- No cloud vendor lock-in
- Valuable Linux admin experience
- Full control over the stack

**Why change detection before LLM?**
- Congressional recess periods (weeks with no activity)
- OpenRouter token costs add up
- Change detection is a simple hash comparison — near-zero cost

**Why inline CSS/JS over a framework?**
- Single HTML file, zero dependencies
- Nothing to break or maintain
- Loads instantly, works everywhere