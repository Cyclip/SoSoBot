import requests
import os
import dotenv
import json

dotenv.load_dotenv()
KEY = os.getenv("GOOGLE_API")

url = "https://www.googleapis.com/customsearch/v1"
query = "white cat"

params = {
    "q": query,
    "safe": "off",
    "num": 10,
    "key": KEY,
    "cx": "015418243597773804934:it6asz9vcss",
    "searchType": "image",
}

r = requests.get(url, params=params)
r = json.loads(r.text)
data = [
    {"url": i["link"], "title": i["title"], "websiteUrl": i["image"]["contextLink"]}
    for i in r["items"]
]
