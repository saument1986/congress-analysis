import requests

API_KEY = "6D8iAE8QLvwmU7uEfoUnSZcqkqPzdpgp9NXPNww9"

# First, get a recent important bill
url = "https://api.congress.gov/v3/bill"
params = {
    'api_key': API_KEY,
    'format': 'json',
    'limit': 5,
    'sort': 'updateDate+desc'
}

response = requests.get(url, params=params)
bills = response.json()['bills']

# Pick the first bill
bill = bills[0]
congress = bill['congress']
bill_type = bill['type'].lower()  # 'hr' or 's'
number = bill['number']

print(f"Getting text for {bill_type.upper()}.{number}: {bill['title'][:60]}...")
print()

# Now get the bill text
text_url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{number}/text"
text_params = {
    'api_key': API_KEY,
    'format': 'json'
}

text_response = requests.get(text_url, text_params)
text_data = text_response.json()

if 'textVersions' in text_data and text_data['textVersions']:
    print("✅ Bill text available!")
    version = text_data['textVersions'][0]
    print(f"Version: {version['type']}")
    print(f"Date: {version['date']}")
    
    # This is what you'll feed to fabric
    print("\nText URL for fabric:")
    if 'formats' in version and version['formats']:
        for format_info in version['formats']:
            if format_info['type'] == 'Formatted Text':
                print(format_info['url'])
                break
else:
    print("❌ No text available for this bill yet")
