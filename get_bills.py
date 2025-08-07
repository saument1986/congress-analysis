import requests

API_KEY = "6D8iAE8QLvwmU7uEfoUnSZcqkqPzdpgp9NXPNww9"

# Get 10 recent bills instead of 1
url = "https://api.congress.gov/v3/bill"
params = {
    'api_key': API_KEY,
    'format': 'json',
    'limit': 10,
    'sort': 'updateDate+desc'
}

response = requests.get(url, params=params)
data = response.json()

print(f"Found {len(data['bills'])} bills:")
print()

for bill in data['bills']:
    print(f"H.R./S. {bill['number']}")
    print(f"Title: {bill['title'][:80]}...")
    print(f"Last updated: {bill['updateDate']}")
    print("-" * 50)
