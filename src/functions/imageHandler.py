import requests
import re
import json


def getImageLinks(query, next="i.js", nsfw=False):
    """
    Messy code to scrape image urls from DuckDuckGo
    outputting the links, titles, image and website
    url.

    Usage:
        getImageLinks(str query, str next, bool nsfw)
        getImageLinks("white cat")
        getImageLinks("brown cat", next="i.js", nsfw=False)

    Return value:
        [
            {
                "title": "Image title",
                "url": "Image source url",
                "websiteUrl": "Image url link"
            }
        ]
    """
    url = f"https://{'safe.' if not nsfw else ''}duckduckgo.com/"
    params = {"q": query, "kp": -2}

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
        ("p", "-2"),
        ("iar", "images"),
        ("iax", "images"),
        ("ia", "images"),
    )

    def getBatch(requestUrl):
        tmpr = requestUrl + "?" + "&".join([f"{i[0]}={i[1]}" for i in params2])
        print(tmpr)
        res = requests.get(
            tmpr,
            headers=headers,
        )  # , params=params2)
        data = json.loads(res.text)

        images = [
            {"title": i["title"], "url": i["image"], "websiteUrl": i["url"]}
            for i in data["results"]
        ]
        return images, data["next"]

    images = []

    requestUrl = url + next
    batch, next = getBatch(requestUrl)
    images += batch

    return images, next
