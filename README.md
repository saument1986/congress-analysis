# Congressional Bill Analysis - Weekly Summaries

**Automated plain-English analysis of significant congressional bills**

## What This Does

This project automatically analyzes recent Congressional activity and produces weekly summaries that explain:

- **What bills actually do** (beyond the political marketing)
- **Who benefits** from the legislation  
- **Real-world impact** on regular citizens
- **Financial costs** and who pays
- **Current status** and next steps

## Why This Exists

Congressional bills are deliberately written in complex legal language that's hard for regular people to understand. This automation cuts through the jargon to show what our elected officials are actually voting on.

## How It Works

### Smart Filtering System
1. **Impact Scoring** - Bills rated 0-10 based on real-world effects
2. **Focus on People** - Only analyzes bills that affect finances, benefits, or daily life
3. **Skip Ceremonial** - Automatically filters out "naming post offices" type bills
4. **Threshold** - Only bills scoring ≥4/10 get full analysis

### Two-Stage Analysis Pipeline
1. **Local Compression** - Dolphin Llama 3 + Fabric extracts key facts to JSON
2. **Optional Polish** - Claude API adds plain English explanations (low token cost)
3. **Rate Limited** - Smart delays prevent API overload
4. **Secure** - API keys in environment variables, never committed

### Weekly Automation
- Runs every Sunday at 8:05 PM via cron
- Generates markdown summaries
- Auto-commits to GitHub
- Shows only high-impact legislation

## Development Journey

This project evolved through several iterations to become a production-ready system:

1. **Initial API Integration** - Basic Congress.gov connectivity and bill fetching
2. **AI Analysis Integration** - Added Fabric framework for bill text analysis  
3. **Filtering Improvements** - Focused on bills that actually affect people's lives
4. **Security Hardening** - Environment variables, rate limiting, error handling
5. **Impact Scoring System** - Smart filtering based on real-world effects and costs

See the [commit history](https://github.com/saument1986/congress-analysis/commits/main) for detailed development progression.

## Sample Output

Recent analysis includes bills on:
- Social Security benefit calculations (Score: 6/10)
- Energy worker health compensation (Score: 5/10) 
- Rural housing loan limits (Score: 4/10)
- Small business R&D tax credits (Score: 4/10)

## Features

- ✅ Automated weekly analysis
- ✅ Impact-based filtering (score ≥4/10)
- ✅ Plain English explanations
- ✅ Politically neutral analysis
- ✅ Financial impact focus
- ✅ Secure API key management
- ✅ Rate limiting & error handling
- ✅ Two-stage AI pipeline

## Tech Stack

- **Python 3** - Core automation
- **Congress.gov API** - Official bill data
- **Fabric AI Framework** - Local text analysis
- **Anthropic Claude API** - Optional polish (low-cost)
- **GitHub Actions** - Automated publishing
- **Cron** - Weekly scheduling

## Project Structure
congress-analysis/
├── weekly_congress_summary.py    # Main analysis script
├── .env                         # API keys (not committed)
├── weekly-summaries/            # Generated analyses
├── fabric-patterns/             # Custom AI patterns
└── README.md                   # This file

---

*Making democracy more accessible through automated analysis of legislation that actually matters.*
