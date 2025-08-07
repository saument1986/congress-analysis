import requests

API_KEY = "6D8iAE8QLvwmU7uEfoUnSZcqkqPzdpgp9NXPNww9"

# Let's try a specific bill we know exists - H.R. 1 (usually a major bill)
congress = 119
bill_type = 'hr'
number = 1

print(f"Getting details for H.R.{number}...")

# First get basic info
bill_url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{number}"
bill_params = {
    'api_key': API_KEY,
    'format': 'json'
}

bill_response = requests.get(bill_url, bill_params)
if bill_response.status_code == 200:
    bill_data = bill_response.json()['bill']
    print(f"Title: {bill_data['title']}")
    print(f"Introduced: {bill_data['introducedDate']}")
    print()

    # Now try to get text
    text_url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{number}/text"
    text_params = {
        'api_key': API_KEY,
        'format': 'json'
    }

    text_response = requests.get(text_url, text_params)
    text_data = text_response.json()

    if 'textVersions' in text_data and text_data['textVersions']:
        print("✅ Found bill text!")
        version = text_data['textVersions'][0]
        print(f"Version: {version['type']}")
        
        # Get the actual text URL
        if 'formats' in version and version['formats']:
            text_url = version['formats'][0]['url']
            print(f"Text URL: {text_url}")
            
            # Download first 500 characters as sample
            text_content = requests.get(text_url).text
            print("\nFirst 500 characters:")
            print(text_content[:500])
            print("...")
    else:
        print("❌ Still no text available")
else:
    print(f"❌ Bill not found: {bill_response.status_code}")
