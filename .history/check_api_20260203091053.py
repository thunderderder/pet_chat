import requests
import json

api_key = "sk_56f40c3c_4711e351bc6e7b71802f7eaa888fbdf6ac9b"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

base_urls = [
    "https://ai-builders.space/backend",
    "https://student-api.ai-builders.space/backend",
    "https://api.ai-builders.space/backend",
    "https://ai-builders.space",
    "https://ai-builders.space/api",
    "https://student-backend.ai-builders.space"
]

print("Testing API connectivity...")

for base_url in base_urls:
    url = f"{base_url}/v1/models"
    try:
        print(f"Trying {url}...")
        response = requests.get(url, headers=headers, timeout=5, verify=False)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"SUCCESS! Valid Base URL: {base_url}")
                # print("Models:", data)
                break
            except:
                print(f"Response not JSON: {response.text[:100]}...")
        else:
            print(f"Failed with status {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
