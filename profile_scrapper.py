# pip install googlesearch-python

from googlesearch import search
import requests

def get_profiles(query, limit=30):
    urls = []
    for url in search(query, num_results=60):
        if "linkedin.com/in/" in url:
            urls.append(url.split("?")[0]) 
        if len(urls) >= limit:
            break
    return list(set(urls))

# creating a list for LinkedIn profiles of startup founders in India
query = 'site:linkedin.com/in "founder" AND India'
seed_list = get_profiles(query, limit=30)
print("Found profiles:", seed_list)

# Bright Data API to scrape the profiles
BRIGHTDATA_API_KEY = "6ebe71bfd9a916c33e8d9bca308aab49a2b2f6956df0dd4f0d6e7153c86fbefd"
DATASET_ID = "gd_l1viktl72bvl7bjuj0"

formatted_input = [{"url": url} for url in seed_list]
headers = {
    "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
    "Content-Type": "application/json",
}

params = {
    "dataset_id": DATASET_ID,
    "include_errors": "true",
}

data = {
    "deliver": {
        "type": "api_pull"
    },
    "input": formatted_input,
}

response = requests.post("https://api.brightdata.com/datasets/v3/trigger",
                         headers=headers, params=params, json=data)

try:
    print("Triggered Bright Data scrape.")
    print(response.json())
except Exception as e:
    print("Error decoding Bright Data response:", e)
    print("Status code:", response.status_code)
    print("Raw text:", response.text[:500])
