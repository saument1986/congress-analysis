import requests

API_KEY = "6D8iAE8QLvwmU7uEfoUnSZcqkqPzdpgp9NXPNww9"

# Get H.R. 1 text
congress = 119
bill_type = 'hr'
number = 1

# Get the text URL
text_url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{number}/text"
text_params = {
    'api_key': API_KEY,
    'format': 'json'
}

text_response = requests.get(text_url, text_params)
text_data = text_response.json()

if 'textVersions' in text_data and text_data['textVersions']:
    version = text_data['textVersions'][0]
    bill_text_url = version['formats'][0]['url']
    
    # Download the full bill text
    print("Downloading bill text...")
    full_text = requests.get(bill_text_url).text
    
    # Save to file for fabric
    filename = f"hr{number}_text.txt"
    with open(filename, 'w') as f:
        f.write(full_text)
    
    print(f"✅ Saved bill text to {filename}")
    print(f"File size: {len(full_text)} characters")
    print("\nNow you can analyze it with fabric:")
    print(f"cat {filename} | fabric --pattern analyze_bill")
else:
    print("❌ No text available")
