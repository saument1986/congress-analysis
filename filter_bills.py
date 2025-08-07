import requests

API_KEY = "6D8iAE8QLvwmU7uEfoUnSZcqkqPzdpgp9NXPNww9"

def is_important_bill(bill):
    title = bill['title'].lower()
    
    # Skip boring bills
    skip_words = ['post office', 'naming', 'designating', 'commemorat']
    if any(word in title for word in skip_words):
        return False
    
    # Look for important bills
    important_words = ['appropriation', 'budget', 'tax', 'defense', 'security', 'reform']
    if any(word in title for word in important_words):
        return True
    
    # Also keep if it's a numbered act (like "H.R. 1234 Act")
    if ' act' in title:
        return True
    
    return False

# Get bills
url = "https://api.congress.gov/v3/bill"
params = {
    'api_key': API_KEY,
    'format': 'json',
    'limit': 20,
    'sort': 'updateDate+desc'
}

response = requests.get(url, params=params)
data = response.json()

important_bills = []
for bill in data['bills']:
    if is_important_bill(bill):
        important_bills.append(bill)

print(f"Found {len(important_bills)} important bills out of {len(data['bills'])} total:")
print()

for bill in important_bills:
    print(f"H.R./S. {bill['number']}")
    print(f"Title: {bill['title']}")
    print(f"Last updated: {bill['updateDate']}")
    print("-" * 80)
