# Congress & Policy Analysis Tracker

> **Self-hosted legislation tracking and bill analysis platform** — automatically fetches, summarizes, and publishes federal and state legislative data with AI-powered analysis.

[![Built with Hermes Agent](https://img.shields.io/badge/built%20with-Hermes%20Agent-8B5CF6)](https://github.com/NousResearch/hermes-agent)
[![Self-Hosted](https://img.shields.io/badge/self--hosted-Raspberry%20Pi-C51A4A)](https://www.raspberrypi.com/)
[![LLM](https://img.shields.io/badge/LLM-Gemma%20%7C%20DeepSeek-4285F4)]()

---

## 🔍 What It Does

A fully automated pipeline that tracks legislation across government levels, summarizes bills in plain English, and publishes results to a clean, responsive website — no manual effort required.

**Tracks:**
- **Federal** — Congress.gov (House & Senate bills)
- **Florida** — State Senate & House legislation
- **Brevard County** — Commission meetings & agenda items

**Live site:** Self-hosted on a Raspberry Pi 5, served via Caddy

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **AI Bill Summaries** | Every bill is analyzed: What It Does / Financial Impact / Who's Affected / Impact Score 1-10 |
| **Smart Change Detection** | Compares RSS feed hashes daily — only runs LLM summarization when bills actually change. Saves token costs during congressional recess. |
| **Keyword Alerts** | Flags bills matching tracked keywords (space, port, broadband, property tax) |
| **Subject Filtering** | Filter bills by category: Defense/Space, Tech/Privacy, Housing, Energy, Healthcare, Immigration, Civil Rights |
| **Coming Up Section** | Shows scheduled floor votes and upcoming hearings |
| **Source Filtering** | Toggle between Federal, Florida, and Brevard County items |
| **Weekly Digest** | Automated week-in-review summary sent to Telegram |
| **Impact Scoring** | Every bill gets a 1-10 impact rating based on scope, cost, and affected population |
| **Backlinks** | Direct links to original bill text on Congress.gov |
| **Resources Sidebar** | Quick links to Congress.gov, FlockHopper, FL Senate, Brevard Clerk, ALPR Maps |

---

## 🏗️ Architecture

```
┌──────────────────────────────┐
│     Hermes Agent (LLM)       │
│  ┌──────────┐ ┌───────────┐  │
│  │  Gemma   │ │ DeepSeek  │  │
│  │ (Local)  │ │ (Fallback)│  │
│  └────┬─────┘ └─────┬─────┘  │
│       │              │        │
│  ┌────┴──────────────┴───┐   │
│  │    Daily Cron (8AM)   │   │
│  └──────────┬────────────┘   │
└─────────────┼────────────────┘
              │
    ┌─────────┴─────────┐
    │  Change Detection │ ← RSS feed hash comparison
    └─────────┬─────────┘
              │
    ┌─────────┴─────────┐
    │  Fetch + Parse    │ ← Congress.gov / FL Senate RSS
    └─────────┬─────────┘
              │
    ┌─────────┴─────────┐
    │  LLM Summarize    │ ← Structured bill analysis
    └─────────┬─────────┘
              │
    ┌─────────┴─────────┐
    │  Generate HTML    │ ← Dark-themed responsive site
    └─────────┬─────────┘
              │
    ┌─────────┴─────────┐
    │  SCP → Raspberry Pi│
    └─────────┬─────────┘
              │
    ┌─────────┴─────────┐
    │  Caddy Web Server │ ← Serves at port 8083
    └───────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Agent** | Hermes Agent (Nous Research) |
| **LLM** | Gemma 4 12B (local, AMD RX 6800) + DeepSeek V4 Flash (OpenRouter fallback) |
| **Web Server** | Caddy on Raspberry Pi 5 |
| **Automation** | Hermes Cron (daily at 8AM ET) |
| **Memory** | Honcho (cross-session user modeling) |
| **Data Sources** | Congress.gov RSS, FL Senate RSS, Brevard Clerk website |
| **Host OS** | Ubuntu Linux (desktop) + Raspberry Pi OS (server) |

---

## 📋 Bill Analysis Format

Every bill is analyzed with a consistent structure:

```
Bill Number: S.2296 — NDAA FY2026
Status: Signed into law — Public Law 119-60

What It Does:
  Sets FY2026 funding and policy for the DoD, military
  construction, and energy defense activities.

Financial Impact:
  Authorizes ~$895B+ for defense programs.

Who's Affected:
  Military service members, defense contractors, Space Coast
  aerospace industry, national security community.

Impact Score: 9/10
```

This format was designed for quick scanning — the most relevant information at a glance.

---

## 🚀 How It Runs

The entire pipeline runs automatically with zero manual intervention:

1. **Daily at 8AM ET**, a Hermes cron job triggers
2. **Change detection** checks RSS feed hashes against stored state
3. **If unchanged** — just updates the timestamp on the site (seconds, no tokens used)
4. **If changed** — fetches new items, summarizes with Gemma/DeepSeek, generates HTML, deploys via SCP
5. **Site updates instantly** — Caddy serves the new content

A separate **weekly digest** cron runs Saturdays at 9AM ET for a week-in-review.

---

## 💡 Why This Exists

Built to solve a specific problem: legislation is hard to track across multiple levels of government. Congress.gov is dense, Florida's legislative site is difficult to navigate, and Brevard County publishes agendas in PDF. This pipeline aggregates all three into a single, readable, searchable site with AI-powered summaries that cut through the legalese.

---

## 🔧 Self-Hosting Notes

- Desktop runs Ubuntu with an AMD RX 6800 for local LLM inference
- Pi 5 serves the website via Caddy (Docker-free — native binary)
- Tailscale provides secure access from anywhere
- Costs: ~$0/day in OpenRouter tokens (change detection keeps usage minimal)
- No cloud services, no subscriptions, no vendor lock-in

---

## 📚 Skills Demonstrated

- **Linux Administration** — Caddy, SSH, systemd, firewalls
- **DevOps / Automation** — Cron-driven CI/CD pipeline, change detection
- **AI/LLM Integration** — Structured prompt engineering, model fallback chaining
- **Web Development** — Responsive HTML/CSS/JS, dark theme, inline JS filtering
- **Network Engineering** — Raspberry Pi as a production web server
- **Data Pipeline** — ETL workflow: fetch → parse → summarize → publish
- **Git** — Version control, documentation, project management

---

## 📁 Repository Structure

```
├── README.md              ← This file
├── docs/
│   └── ARCHITECTURE.md    ← Detailed system design
├── scripts/
│   └── deploy.sh          ← Deployment workflow (sanitized)
├── assets/
│   └── screenshot.png     ← Site preview
├── congress_api_test.py   ← Early prototype scripts
├── filter_bills.py
├── get_bills.py
├── get_bill_text.py
├── get_older_bill.py
├── save_bill_for_fabric.py
├── simple_test.py
├── weekly_congress_summary.py
├── weekly_congress_summary_old.py
└── weekly-summary-*.md    ← Historical weekly summaries
```

---

*Built by [Scott Aument](https://github.com/saument1986) — Cloud/Network Engineering student at WGU, systems administrator*
