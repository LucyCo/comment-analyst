import json
from serverless_sdk import tag_event
from statistics import mean, median
import asyncio
import concurrent.futures
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

querystring = {"print": "pretty"}

headers = {
    'x-rapidapi-host': "community-hacker-news-v1.p.rapidapi.com",
    'x-rapidapi-key': "70a9a1e646mshfbe352366d4e248p1026d2jsn434e37469a13"
}

def make_request(url):
    return requests.get(url, headers=headers)

async def fetch_all(urls):
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(urls)) as executor:
        print(urls)
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                executor,
                make_request(url),
                url
            )
            for url in urls
        ]
        for response in await asyncio.gather(*futures):
            pass


loop = asyncio.get_event_loop()

# async def fetch_single_url(url):
#     response = loop.run_in_executor(None, requests.get, url)
#     return await response.text()


# async def fetch_urls(urls):
#     async with aiohttp.ClientSession() as session:
#         results = [await fetch_single_url(session, url) for url in urls]
#     return results

analyzer = SentimentIntensityAnalyzer()

stats = {"positive": [], "negative": [], "neutral": [], "mixed": []}

allStoryUrls = []


def sentiment(event, context):
    tag_event('comment-analyst', 'sentiment')
    phrase = event.get('queryStringParameters', {}).get('phrase')
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
    urls.append("https://community-hacker-news-v1.p.rapidapi.com/topstories.json")
    results = loop.run_until_complete(fetch_all(urls))
    print("hi")
    print(results)
    storyIdList = results[0]


    for storyId in storyIdList:
        allStoryUrls.append("https://community-hacker-news-v1.p.rapidapi.com/item/" + str(storyId) + ".json")

    results = loop.run_until_complete(fetch_all(allStoryUrls))

    allDirectStoryKidsId = [];

    for story in results:
        print(story.get("title"))
        if story.get("title").find(pharse) != -1 and story.get("kids") is not None:
            for commentId in story.get("kids"):
                allDirectStoryKidsId.append(commentId)

    getComments(allDirectStoryKidsId)

    sum = len(stats["positive"])
    output = {"comments":sum}
    if sum != 0:
        for attr in stats:
            dict = {
            'avg':mean(stats[attr]),
            'median':median(stats[attr])
            }
        output[attr] = dict
    return output


def updateSentiments(text):
    result = analyzer.polarity_scores(text)
    stats["positive"].append(result["pos"])
    stats["negative"].append(result["neg"])
    stats["neutral"].append(result["neu"])
    stats["mixed"].append(result["compound"])


def getComments(commentIds):
    if commentIds == []:
        return
    commentUrls = [];
    for commentId in commentIds:
        commentUrls.append("https://community-hacker-news-v1.p.rapidapi.com/item/" + str(commentId) + ".json")
    result = fetch_all(commentUrls)
    for comment in result:
        updateSentiments(comment["text"])
        getComments(comment["kids"])

# print(sentiment({"queryStringParameters": {"phrase": "corona"}}, None))

