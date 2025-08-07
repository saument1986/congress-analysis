#!/usr/bin/env python3
"""
Weekly Congressional Bill Summary
Analyzes recent bills and creates plain English summary
"""

import requests
import subprocess
import re
from datetime import datetime, timedelta
import os

# Configuration
API_KEY = "6D8iAE8QLvwmU7uEfoUnSZcqkqPzdpgp9NXPNww9"
BASE_URL = "https://api.congress.gov/v3"
FABRIC_PATH = "/mnt/media/intelligence/fabric/fabric"

def clean_html_text(html_text):
    """Remove HTML tags from text"""
    clean = re.sub(r'<[^>]*>', '', html_text)
    return clean.strip()

def is_important_bill(bill):
    """Filter for significant bills"""
    title = bill['title'].lower()
    
    # Skip boring bills
    skip_words = ['post office', 'naming', 'designating', 'commemorat', 'honoring']
    if any(word in title for word in skip_words):
        return False
    
    # Look for important bills
    important_words = [
        'appropriation', 'budget', 'tax', 'defense', 'security', 'reform',
        'healthcare', 'infrastructure', 'energy', 'immigration', 'trade',
        'compensation', 'veterans', 'education', 'environment'
    ]
    
    if any(word in title for word in important_words):
        return True
    
    # Also keep if it has recent significant action
    latest_action = bill.get('latestAction', {}).get('text', '').lower()
    if any(word in latest_action for word in ['passed', 'committee', 'floor']):
        return True
    
    return False

def get_recent_bills():
    """Get bills with recent activity"""
    print("Fetching recent bills...")
    
    url = f"{BASE_URL}/bill"
    params = {
        'api_key': API_KEY,
        'format': 'json',
        'limit': 50,
        'sort': 'updateDate+desc'
    }
    
    response = requests.get(url, params=params)
    return response.json()

def get_bill_text(congress, bill_type, number):
    """Get clean bill text"""
    print(f"Getting text for {bill_type.upper()}.{number}...")
    
    text_url = f"{BASE_URL}/bill/{congress}/{bill_type}/{number}/text"
    params = {
        'api_key': API_KEY,
        'format': 'json'
    }
    
    response = requests.get(text_url, params)
    text_data = response.json()
    
    if 'textVersions' in text_data and text_data['textVersions']:
        version = text_data['textVersions'][0]
        if 'formats' in version and version['formats']:
            bill_text_url = version['formats'][0]['url']
            full_text = requests.get(bill_text_url).text
            return clean_html_text(full_text)
    
    return None

def analyze_with_fabric(bill_text):
    """Analyze bill text with fabric"""
    try:
        cmd = f"echo '{bill_text}' | {FABRIC_PATH} --pattern extract_wisdom"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Analysis failed: {e}"

def create_weekly_summary():
    """Main function to create weekly summary"""
    today = datetime.now()
    week_start = today - timedelta(days=7)
    
    # Get recent bills
    recent_data = get_recent_bills()
    all_bills = recent_data.get('bills', [])
    
    # Filter for important bills
    important_bills = [bill for bill in all_bills if is_important_bill(bill)][:8]
    
    print(f"Found {len(important_bills)} important bills to analyze...")
    
    # Start building the summary
    summary = f"""# Congressional Week Summary: {week_start.strftime('%B %d')} - {today.strftime('%B %d, %Y')}

*Automated analysis of significant congressional activity*

---

"""
    
    analyzed_count = 0
    for bill in important_bills:
        congress = bill['congress']
        bill_type = bill['type'].lower()
        number = bill['number']
        
        # Get bill text
        bill_text = get_bill_text(congress, bill_type, number)
        
        if bill_text and len(bill_text) > 500:  # Only analyze if we have substantial text
            # Analyze with fabric
            analysis = analyze_with_fabric(bill_text)
            
            # Add to summary
            summary += f"""## {bill_type.upper()}.{number} - {bill['title']}

**Status:** {bill.get('latestAction', {}).get('text', 'No recent action')}
**Last Updated:** {bill.get('updateDate', 'Unknown')}

**Plain English Analysis:**
{analysis}

---

"""
            analyzed_count += 1
            
            if analyzed_count >= 5:  # Limit to 5 bills for weekly summary
                break
    
    # Add footer
    summary += f"""
*This analysis was automatically generated using congressional data and AI analysis.*  
*Source: Congress.gov API*  
*Generated on: {today.strftime('%Y-%m-%d %H:%M')}*
"""
    
    return summary

def push_to_github(summary_content):
    """Save summary and push to GitHub"""
    today = datetime.now()
    filename = f"weekly-summary-{today.strftime('%Y-%m-%d')}.md"
    
    # Save locally
    with open(filename, 'w') as f:
        f.write(summary_content)
    
    print(f"Saved summary to {filename}")
    
    # Git commands (you'll need to set up the repo first)
    try:
        subprocess.run(['git', 'add', filename], check=True)
        subprocess.run(['git', 'commit', '-m', f'Weekly summary: {today.strftime("%Y-%m-%d")}'], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("✅ Pushed to GitHub successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        print("You may need to set up the GitHub repository first")

if __name__ == "__main__":
    print("Starting weekly congressional analysis...")
    summary = create_weekly_summary()
    
    print("\nWeekly Summary Created:")
    print("=" * 50)
    print(summary[:500] + "...")
    print("=" * 50)
    
    push_to_github(summary)
    print("Weekly analysis complete!")
