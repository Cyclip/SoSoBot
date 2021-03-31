import requests
import json
import os
import dotenv
from mezmorize import Cache
import praw

dotenv.load_dotenv()
KEY = os.getenv("GOOGLE_API")
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")

url = "https://www.googleapis.com/customsearch/v1"

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
)

cache = Cache(CACHE_TYPE="filesystem", CACHE_DIR="cache")


def getSubreddit(srname):
    return reddit.subreddit(srname)


@cache.memoize(60)
def getPosts(subreddit, sorting, filter_nsfw):
    """
    Function to get Reddit posts via their API
    PRAW.

    Usage:
        getPosts(
            reddit.subreddit subreddit,
            str sorting,
            bool filter_nsfw
        )

    Examples:
        getPosts(
            reddit.subreddit('all'),
            'hot',
            True
        )
    """
    posts = []
    sortingFunc = getattr(subreddit, sorting)

    for submission in sortingFunc(limit=100):
        if filter_nsfw and submission.over_18:
            continue
        if submission.stickied:
            continue

        isText = submission.is_self

        if isText:
            content = submission.selftext
        else:
            content = submission.url
            if content.startswith("https://v.redd.it/"):
                continue

        posts.append(
            {
                "title": submission.title,
                "isText": isText,
                "content": content,
                "score": submission.score,
                "comments": submission.num_comments,
                "subredditName": subreddit.display_name,
            }
        )

    return posts


@cache.memoize(150)
def getImageLinks(query, nsfw=False, batches=2):
    """
    Code utilising Google's API to scrape image urls
    outputting the links, titles, image and website
    url.

    Usage:
        getImageLinks(str query,
                      bool nsfw,
                      int batches)

    Examples:
        getImageLinks("white cat")

        getImageLinks("brown cat",
                      nsfw=False)

        getImageLinks("war imagery",
                      nsfw=True,
                      batches=3)

    Return value:
        [
            {
                "title": "Image title",
                "url": "Image source url",
                "websiteUrl": "Image url link"
            }
        ]
    """

    def getBatch(start=1):
        params = {
            "q": query,
            "safe": "OFF" if nsfw else "ACTIVE",
            "num": 10,
            "key": KEY,
            "cx": "015418243597773804934:it6asz9vcss",
            "searchType": "image",
            "start": start,
        }

        r = requests.get(url, params=params)
        r = json.loads(r.text)
        data = [
            {
                "url": i["link"],
                "title": i["title"],
                "websiteUrl": i["image"]["contextLink"],
            }
            for i in r["items"]
        ]
        return data

    start = 1
    data = []
    for i in range(batches):
        data += getBatch(start=start)
        start += 10
    return data
