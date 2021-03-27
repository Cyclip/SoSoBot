import requests
import re
import json

query = "white cat"
url = "https://duckduckgo.com/"
params = {"q": query}

headers = {
    "authority": "duckduckgo.com",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "sec-fetch-dest": "empty",
    "x-requested-with": "XMLHttpRequest",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "referer": "https://duckduckgo.com/",
    "accept-language": "en-US,en;q=0.9",
}

res = requests.post(url, data=params)
searchObj = re.search(r"vqd=([\d-]+)\&", res.text, re.M | re.I)

params2 = (
    ("l", "us-en"),
    ("o", "json"),
    ("q", query),
    ("vqd", searchObj.group(1)),
    ("f", ",,,"),
    ("p", "1"),
    ("v7exp", "a"),
)

requestUrl = url + "i.js"
res = requests.get(requestUrl, headers=headers, params=params2)
data = json.loads(res.text)

links = [i["image"] for i in data["results"]]
with open("links.txt", "w") as f:
    f.write("\n".join(links))
