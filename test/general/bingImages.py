import requests
import json

endpoint = "https://api.cognitive.microsoft.com/bing/v5.0/search"
query = "white cat"

params = {
"q": query,
"safeSearch": "Off"
}

headers = {
"accept": "application/json, text/javascript, */*; q=0.01",
}

res = requests.get(
endpoint,
params=params,
headers=headers
)
