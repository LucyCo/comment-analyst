from pprint import pprint
import json
#from serverless_sdk import tag_event
from statistics import mean, median
import asyncio
import requests
import concurrent.futures
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

querystring = {"print": "pretty"}

def make_request(url):
    try:
        return requests.get(url, data=querystring)
    except:
        return None

async def fetch_all(urls):
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(urls)) as executor:
        print(urls)
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


loop = asyncio.get_event_loop()

analyzer = SentimentIntensityAnalyzer()

stats = {"positive": [], "negative": [], "neutral": [], "mixed": []}

allStoryUrls = []


def sentiment(event, context):
    #tag_event('comment-analyst', 'sentiment')
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
    urls.append("https://hacker-news.firebaseio.com/v0/topstories.json")
    results = loop.run_until_complete(fetch_all(urls))
    print("hi")
    print(results)
    storyIdList = results[0]


    for storyId in storyIdList:
        allStoryUrls.append("https://hacker-news.firebaseio.com/v0/item/" + str(storyId) + ".json")

    results = loop.run_until_complete(fetch_all(allStoryUrls))

    pprint('results')
    pprint(results)
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
        commentUrls.append("https://hacker-news.firebaseio.com/v0/item/" + str(commentId) + ".json")
    result = fetch_all(commentUrls)
    for comment in result:
        updateSentiments(comment["text"])
        getComments(comment["kids"])

print(sentiment({"queryStringParameters": {"phrase": "corona"}}, None))
