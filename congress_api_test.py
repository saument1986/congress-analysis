#!/usr/bin/env python3
“””
Congress API Examples for Weekly Bill Analysis
Replace YOUR_API_KEY with your actual key from api.congress.gov
“””

import requests
import json
from datetime import datetime, timedelta

# Your API key

API_KEY = “6D8iAE8QLvwmU7uEfoUnSZcqkqPzdpgp9NXPNww9”
BASE_URL = “https://api.congress.gov/v3”

def get_recent_bills():
“”“Get bills with recent activity (last 7 days)”””

```
# Calculate date range for last week
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

# Format dates for API (YYYY-MM-DD)
start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

url = f"{BASE_URL}/bill"
params = {
    'api_key': API_KEY,
    'format': 'json',
    'limit': 50,  # Get 50 most recent
    'fromDateTime': f"{start_str}T00:00:00Z",
    'toDateTime': f"{end_str}T23:59:59Z",
    'sort': 'updateDate+desc'  # Most recent first
}

response = requests.get(url, params=params)
return response.json()
```

def get_bill_details(congress, bill_type, bill_number):
“”“Get detailed info for a specific bill”””

```
url = f"{BASE_URL}/bill/{congress}/{bill_type}/{bill_number}"
params = {
    'api_key': API_KEY,
    'format': 'json'
}

response = requests.get(url, params=params)
return response.json()
```

def get_bill_text(congress, bill_type, bill_number):
“”“Get the actual text of a bill”””

```
url = f"{BASE_URL}/bill/{congress}/{bill_type}/{bill_number}/text"
params = {
    'api_key': API_KEY,
    'format': 'json'
}

response = requests.get(url, params=params)
return response.json()
```

def get_bill_actions(congress, bill_type, bill_number):
“”“Get actions taken on a bill (committee, votes, etc.)”””

```
url = f"{BASE_URL}/bill/{congress}/{bill_type}/{bill_number}/actions"
params = {
    'api_key': API_KEY,
    'format': 'json',
    'limit': 20
}

response = requests.get(url, params=params)
return response.json()
```

def filter_significant_bills(bills_data):
“”“Filter for bills worth analyzing”””

```
significant_bills = []

for bill in bills_data.get('bills', []):
    # Look for signs of significance
    title = bill.get('title', '').lower()
    
    # Skip if it's just a naming/commemorative bill
    skip_keywords = ['post office', 'naming', 'commemorat', 'honoring']
    if any(keyword in title for keyword in skip_keywords):
        continue
        
    # Look for important bills
    important_keywords = [
        'appropriation', 'budget', 'tax', 'defense', 'healthcare', 
        'infrastructure', 'security', 'reform', 'act', 'authorization'
    ]
    
    if any(keyword in title for keyword in important_keywords):
        significant_bills.append(bill)
        
    # Also include bills with recent major actions
    if bill.get('latestAction', {}).get('actionCode'):
        significant_bills.append(bill)

return significant_bills[:10]  # Return top 10
```

# Example usage for your weekly script

def weekly_analysis():
“”“Main function to run weekly analysis”””

```
print("Fetching recent bills...")
recent_bills = get_recent_bills()

print("Filtering for significant bills...")
significant = filter_significant_bills(recent_bills)

bills_for_analysis = []

for bill in significant:
    congress = bill['congress']
    bill_type = bill['type'].lower()  # 'hr', 's', etc.
    number = bill['number']
    
    print(f"Getting details for {bill_type.upper()}.{number}...")
    
    # Get detailed info
    details = get_bill_details(congress, bill_type, number)
    
    # Get bill text for fabric analysis
    text_response = get_bill_text(congress, bill_type, number)
    
    # Get recent actions
    actions = get_bill_actions(congress, bill_type, number)
    
    bill_data = {
        'basic_info': bill,
        'details': details,
        'text': text_response,
        'actions': actions
    }
    
    bills_for_analysis.append(bill_data)

return bills_for_analysis
```

# Helper function to extract bill text for fabric

def extract_text_for_fabric(bill_data):
“”“Extract the actual bill text to send to fabric”””

```
text_versions = bill_data.get('text', {}).get('textVersions', [])

if not text_versions:
    return "No text available"

# Get the most recent version
latest_version = text_versions[0]

# The API gives you URLs to the actual text files
text_url = latest_version.get('formats', [{}])[0].get('url', '')

if text_url:
    # Download the actual bill text
    response = requests.get(text_url)
    return response.text

return "Text not available"
```

# Quick test function

def test_api():
“”“Test your API key and connection”””

```
url = f"{BASE_URL}/bill"
params = {
    'api_key': API_KEY,
    'format': 'json',
    'limit': 1
}

try:
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("✅ API connection successful!")
        print(f"Sample bill: {response.json()['bills'][0]['title']}")
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Connection error: {e}")
```

if **name** == “**main**”:
# Test your API key first
test_api()

```
# Then run weekly analysis
# weekly_bills = weekly_analysis()
# print(f"Found {len(weekly_bills)} bills for analysis")
```
