import requests

API_KEY = "6D8iAE8QLvwmU7uEfoUnSZcqkqPzdpgp9NXPNww9"

url = "https://api.congress.gov/v3/bill"
params = {
    'api_key': API_KEY,
    'format': 'json',
    'limit': 1
}

response = requests.get(url, params=params)
data = response.json()

print("Success!")
print(f"Bill number: {data['bills'][0]['number']}")
print(f"Title: {data['bills'][0]['title']}")
