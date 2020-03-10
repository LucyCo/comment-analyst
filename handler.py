import json
from serverless_sdk import tag_event
from statistics import mean, median
import asyncio
import requests
import concurrent.futures
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime

TIMEOUT_SECONDS = 25

GET_QUERY = event.get('queryStringParameters', {}).get('phrase', '').lower()

HACKER_NEWS_PREFIX = "https://hacker-news.firebaseio.com/v0/"

HACKER_NEWS_ITEM_PATH = "item/"

TOP_STORIES = "topstories"

JSON_SUFFIX = ".json"

timestamp = datetime.timestamp(datetime.now())

loop = asyncio.get_event_loop()

analyzer = SentimentIntensityAnalyzer()

stats = {"positive": [], "negative": [], "neutral": [], "mixed": []}

allStoryUrls = []

def make_request(url):
    if datetime.timestamp(datetime.now()) > timestamp + TIMEOUT_SECONDS:
        return None
    try:
        return requests.get(url)
    except:
        return None

async def fetch_all(urls):
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(urls)) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                executor,
                make_request,
                url
            )
            for url in urls
        ]
        responses = []
        for response in await asyncio.gather(*futures):
            try:
                res = response.json()
            except:
                continue
            responses.append(res)
    return responses


def sentiment(event, context):
    tag_event('comment-analyst', 'sentiment')
    phrase = GET_QUERY
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": True
    }

    try:
        body = run(phrase)
    except Exception as exc:
        body = {"error": str(exc)}

    if body is None:
        body = "Internal error!"

    response = {
        "statusCode": 200,
         "headers": headers,
         "body": json.dumps(body)
    }
    return response


def run(phrase):
    urls = []
    urls.append(HACKER_NEWS_PREFIX + TOP_STORIES + JSON_SUFFIX)
    results = loop.run_until_complete(fetch_all(urls))
    storyIdList = results[0]


    for storyId in storyIdList:
        allStoryUrls.append(HACKER_NEWS_PREFIX + HACKER_NEWS_ITEM_PREFIX + str(storyId) + JSON_SUFFIX)

    results = loop.run_until_complete(fetch_all(allStoryUrls))

    allDirectStoryKidsId = [];

    for story in results:
        if story.get("title").lower().find(phrase) != -1 and story.get("kids") is not None:
            for commentId in story.get("kids", []):
                allDirectStoryKidsId.append(commentId)

    getComments(allDirectStoryKidsId)

    sum = len(stats["positive"])
    output = {"comments":sum}
    if sum != 0:
        for attr in stats:
            dict = {
            'avg':"%.3f" % mean(stats[attr]),
            'median':"%.3f" % median(stats[attr])
            }
            output[attr] = dict
    return output


def updateSentiments(text):
    if not text:
        return
    result = analyzer.polarity_scores(text)
    stats["positive"].append(result["pos"])
    stats["negative"].append(result["neg"])
    stats["neutral"].append(result["neu"])
    stats["mixed"].append(result["compound"])


def getComments(commentIds):
    if not commentIds:
        return
    commentUrls = [];
    for commentId in commentIds:
        commentUrls.append(HACKER_NEWS_PREFIX + HACKER_NEWS_ITEM_PATH + str(commentId) + JSON_SUFFIX)
    result = loop.run_until_complete(fetch_all(commentUrls))
    for comment in result:
        updateSentiments(comment.get("text"))
        getComments(comment.get("kids", []))
