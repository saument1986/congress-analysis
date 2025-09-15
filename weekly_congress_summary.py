#!/usr/bin/env python3
"""
Secure Weekly Congressional Bill Analysis
Filters for high-impact bills, compresses with local AI, optionally polishes with Claude
"""

import requests
import subprocess
import re
import time
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment
CONGRESS_API_KEY = os.getenv("CONGRESS_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
FABRIC_PATH = os.getenv("FABRIC_PATH")

# Validation
if not CONGRESS_API_KEY:
    raise SystemExit("❌ Missing CONGRESS_API_KEY in .env file")
if not FABRIC_PATH:
    raise SystemExit("❌ Missing FABRIC_PATH in .env file")

BASE_URL = "https://api.congress.gov/v3"

def clean_html_text(html_text):
    """Remove HTML tags from text"""
    clean = re.sub(r'<[^>]*>', '', html_text)
    return clean.strip()

def calculate_impact_score(bill):
    """Calculate impact score (0-10) based on real-world effects"""
    score = 0
    title = bill['title'].lower()
    
    # High impact indicators (+2 each)
    high_impact = [
        'appropriation', 'budget', 'tax', 'spending', 'fund',
        'social security', 'medicare', 'medicaid', 'veterans',
        'immigration', 'border', 'defense', 'security',
        'infrastructure', 'healthcare', 'education'
    ]
    score += sum(2 for word in high_impact if word in title)
    
    # Medium impact (+1 each)
    medium_impact = [
        'reform', 'act', 'authorization', 'benefits',
        'housing', 'employment', 'environment', 'energy'
    ]
    score += sum(1 for word in medium_impact if word in title)
    
    # Recent passage bonus (+2)
    latest_action = bill.get('latestAction', {}).get('text', '').lower()
    if any(word in latest_action for word in ['passed', 'enacted', 'signed']):
        score += 2
    
    # Committee action bonus (+1)
    if 'committee' in latest_action:
        score += 1
    
    return min(score, 10)  # Cap at 10

def filter_high_impact_bills(bills):
    """Filter for bills with impact score >= 4"""
    filtered = []
    
    for bill in bills:
        title = bill['title'].lower()
        
        # Skip ceremonial/naming bills (auto score 0)
        skip_words = [
            'post office', 'naming', 'designating', 'commemorat', 'honoring',
            'name the', 'rename', 'redesignate', 'medal', 'coin', 'stamp',
            'national day', 'national week', 'national month', 'awareness'
        ]
        if any(word in title for word in skip_words):
            continue
        
        # Calculate impact score
        impact_score = calculate_impact_score(bill)
        
        # Keep high-impact bills only
        if impact_score >= 4:
            bill['impact_score'] = impact_score
            filtered.append(bill)
            print(f"✅ Impact {impact_score}: {bill['type']}.{bill['number']} - {title[:60]}...")
    
    # Sort by impact score (highest first)
    return sorted(filtered, key=lambda x: x['impact_score'], reverse=True)

def get_recent_bills():
    """Get bills with recent activity"""
    print("📡 Fetching recent bills from Congress.gov...")
    
    url = f"{BASE_URL}/bill"
    params = {
        'api_key': CONGRESS_API_KEY,
        'format': 'json',
        'limit': 100,  # Get more to filter better
        'sort': 'updateDate+desc'
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_bill_text(congress, bill_type, number):
    """Get clean bill text with size limits"""
    print(f"📄 Getting text for {bill_type.upper()}.{number}...")
    
    text_url = f"{BASE_URL}/bill/{congress}/{bill_type}/{number}/text"
    params = {
        'api_key': CONGRESS_API_KEY,
        'format': 'json'
    }
    
    response = requests.get(text_url, params)
    print(f"🔍 Text API status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"⚠️  Failed to get text metadata for {bill_type.upper()}.{number}")
        return None
        
    text_data = response.json()
    
    if 'textVersions' in text_data and text_data['textVersions']:
        version = text_data['textVersions'][0]
        print(f"🔍 Found text version: {version.get('type', 'unknown')}")
        
        if 'formats' in version and version['formats']:
            bill_text_url = version['formats'][0]['url']
            print(f"🔍 Fetching full text from: {bill_text_url[:80]}...")
            
            text_response = requests.get(bill_text_url)
            if text_response.status_code != 200:
                print(f"⚠️  Failed to fetch bill text (status: {text_response.status_code})")
                return None
                
            full_text = text_response.text
            clean_text = clean_html_text(full_text)
            
            print(f"🔍 Clean text length: {len(clean_text):,} chars")
            
            # Skip bills that are too large (>200k chars = rate limit risk)
            if len(clean_text) > 200000:
                print(f"⚠️  Skipping {bill_type.upper()}.{number} - too large ({len(clean_text):,} chars)")
                return None
            
            print(f"✅ Retrieved text for {bill_type.upper()}.{number}")
            return clean_text
        else:
            print(f"⚠️  No text formats available for {bill_type.upper()}.{number}")
    else:
        print(f"⚠️  No text versions available for {bill_type.upper()}.{number}")
    
    return None

def compress_with_fabric(bill_info, bill_text):
    """Compress bill using local Fabric + Dolphin Llama 3"""
    try:
        print(f"🧠 Compressing {bill_info['type']}.{bill_info['number']} with local AI...")
        
        # Prepare input with metadata + text
        input_data = f"""
BILL: {bill_info['type']}.{bill_info['number']} - {bill_info['title']}
STATUS: {bill_info.get('latestAction', {}).get('text', 'Unknown')}
SPONSOR: {bill_info.get('sponsor', {}).get('firstName', '')} {bill_info.get('sponsor', {}).get('lastName', '')}
IMPACT_SCORE: {bill_info.get('impact_score', 0)}

BILL TEXT:
{bill_text[:50000]}  # Limit to first 50k chars for processing
"""
        
        # Save to temp file
        temp_file = '/tmp/bill_compress.txt'
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(input_data)
        
        # Use Fabric with structure extraction pattern
        cmd = f"cat {temp_file} | {FABRIC_PATH} --pattern extract_bill_struct"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        print(f"🔍 Fabric exit code: {result.returncode}")
        print(f"🔍 Fabric output length: {len(result.stdout)} chars")
        
        if result.stderr:
            print(f"⚠️  Fabric stderr: {result.stderr[:200]}")
        
        # Clean up
        os.remove(temp_file)
        
        # Try to parse JSON
        if result.returncode == 0 and result.stdout.strip():
            try:
                compressed_data = json.loads(result.stdout.strip())
                print(f"✅ Successfully compressed {bill_info['type']}.{bill_info['number']}")
                return compressed_data
            except json.JSONDecodeError as e:
                print(f"⚠️  Failed to parse JSON from Fabric: {e}")
                print(f"Raw output: {result.stdout[:300]}...")
                return None
        else:
            print(f"⚠️  Fabric command failed or no output")
            return None
            
    except Exception as e:
        print(f"❌ Local compression failed: {e}")
        return None

def polish_with_claude(compressed_data):
    """Optional polish with Claude API (low token usage)"""
    if not ANTHROPIC_API_KEY:
        print("⏭️  Skipping Claude polish (no API key)")
        return compressed_data
    
    try:
        print("✨ Polishing with Claude...")
        
        # Send only the small JSON to Claude
        prompt = f"""Please improve this bill analysis with plain English explanations:

{json.dumps(compressed_data, indent=2)}

Add these fields:
- "plain_english": ["2-3 bullet points explaining what this bill actually does"]
- "taxpayer_impact": "Simple cost explanation for regular people"
- "why_matters": "Why citizens should care about this"
- "watch_next": "What to watch for next"

Keep additions concise. Return valid JSON only."""

        # Simple Claude API call (you'd implement this based on Anthropic's client)
        # For now, return original data
        print("🔄 Claude integration placeholder - returning original data")
        return compressed_data
        
    except Exception as e:
        print(f"⚠️  Claude polish failed: {e}")
        return compressed_data

def create_weekly_summary(analyzed_bills, all_high_impact_bills):
    """Generate markdown summary from analyzed bills with chamber breakdown"""
    today = datetime.now()
    week_start = today - timedelta(days=7)
    
    # Chamber analysis
    house_bills = [b for b in all_high_impact_bills if b['type'].upper().startswith('H')]
    senate_bills = [b for b in all_high_impact_bills if b['type'].upper().startswith('S')]
    
    house_avg_score = sum(b.get('impact_score', 0) for b in house_bills) / len(house_bills) if house_bills else 0
    senate_avg_score = sum(b.get('impact_score', 0) for b in senate_bills) / len(senate_bills) if senate_bills else 0
    
    summary = f"""# Congressional Week Summary: {week_start.strftime('%B %d')} - {today.strftime('%B %d, %Y')}

*High-impact bills affecting regular Americans - automatically analyzed*

## Weekly Activity Overview

**📊 Chamber Breakdown:**
- **House:** {len(house_bills)} high-impact bills (avg score: {house_avg_score:.1f}/10)
- **Senate:** {len(senate_bills)} high-impact bills (avg score: {senate_avg_score:.1f}/10)

**🏛️ This Week's Focus:** {"House-heavy week" if len(house_bills) > len(senate_bills) else "Senate-heavy week" if len(senate_bills) > len(house_bills) else "Balanced activity"}

---

"""
    
    for bill_data in analyzed_bills:
        bill_id = bill_data.get('bill_id', 'Unknown')
        title = bill_data.get('title', 'No title')
        status = bill_data.get('status', 'Unknown status')
        
        # Determine chamber
        chamber = "🏛️ House" if bill_id.upper().startswith('H') else "🏛️ Senate"
        
        summary += f"""## {bill_id} - {title}

**Chamber:** {chamber}
**Status:** {status}
**Impact Score:** {bill_data.get('impact_score', 'N/A')}/10

### What It Does
"""
        
        # Add provisions
        provisions = bill_data.get('provisions', [])
        for provision in provisions[:3]:  # Max 3
            summary += f"- {provision}\n"
        
        # Add spending info
        spending = bill_data.get('spending', [])
        if spending:
            summary += f"\n### Financial Impact\n"
            for item in spending[:3]:
                summary += f"- {item}\n"
        
        # Add who benefits/affected
        benefits = bill_data.get('who_benefits', [])
        affected = bill_data.get('who_affected', [])
        
        if benefits or affected:
            summary += f"\n### Who's Affected\n"
            if benefits:
                summary += f"**Benefits:** {', '.join(benefits[:3])}\n"
            if affected:
                summary += f"**Affected:** {', '.join(affected[:3])}\n"
        
        summary += "\n---\n\n"
    
    # Add footer
    summary += f"""
*Analysis generated on {today.strftime('%Y-%m-%d at %H:%M')}*  
*Source: Congress.gov API + Local AI Analysis*  
*High-impact bills only (score ≥ 4/10)*
"""
    
    return summary

def main():
    """Main pipeline: filter → compress → polish → publish"""
    print("🚀 Starting secure weekly congressional analysis...")
    
    # Step 1: Get and filter bills
    recent_data = get_recent_bills()
    all_bills = recent_data.get('bills', [])
    high_impact_bills = filter_high_impact_bills(all_bills)
    
    print(f"📊 Found {len(high_impact_bills)} high-impact bills (from {len(all_bills)} total)")
    
    if not high_impact_bills:
        print("ℹ️  No high-impact bills found this week")
        return
    
    # Step 2: Analyze bills that actually have text available
    analyzed_bills = []
    bills_processed = 0
    
    for bill in high_impact_bills[:10]:  # Check more bills to find ones with text
        congress = bill['congress']
        bill_type = bill['type'].lower()
        number = bill['number']
        
        # Get bill text
        bill_text = get_bill_text(congress, bill_type, number)
        
        if bill_text:
            # Compress with local AI
            compressed = compress_with_fabric(bill, bill_text)
            
            if compressed:
                # Optional Claude polish
                polished = polish_with_claude(compressed)
                analyzed_bills.append(polished)
                print(f"✅ Successfully analyzed {bill['type']}.{bill['number']}")
                
                # Rate limiting
                time.sleep(5)  # 5 seconds between bills
                
                # Stop after analyzing 3 bills successfully
                if len(analyzed_bills) >= 3:
                    break
        
        bills_processed += 1
        print(f"🔄 Processed {bills_processed} bills, analyzed {len(analyzed_bills)} successfully")
    
    # Step 3: Generate summary
    if analyzed_bills:
        summary = create_weekly_summary(analyzed_bills, high_impact_bills)
        
        # Save to file
        today = datetime.now()
        filename = f"weekly-summary-{today.strftime('%Y-%m-%d')}.md"
        
        with open(filename, 'w') as f:
            f.write(summary)
        
        print(f"📝 Summary saved to {filename}")
        
        # Git commit and push
        try:
            subprocess.run(['git', 'add', filename], check=True)
            subprocess.run(['git', 'commit', '-m', f'Weekly summary: {today.strftime("%Y-%m-%d")}'], check=True)
            subprocess.run(['git', 'push'], check=True)
            print("📤 Pushed to GitHub successfully!")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git error: {e}")
    
    print("🎉 Weekly analysis complete!")

if __name__ == "__main__":
    main()
