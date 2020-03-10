import json
from serverless_sdk import tag_event
from statistics import mean, median
import asyncio
import requests
import concurrent.futures
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime

TIMEOUT_SECONDS = 25

STATUS_CODE_SUCCESS = 200
STATUS_CODE_FAILED = 408
STATUS_CODE_PART = 416

QUERY_STR_PARAMS = "queryStringParameters"
QUERY_PHRASE = "phrase"

SERVERLESS_TAG_1 = "comment-analyst"
SERVERLESS_TAG_2 = "sentiment"

HACKER_NEWS_PREFIX = "https://hacker-news.firebaseio.com/v0/"
HACKER_NEWS_ITEM_PATH = "item/"
HACKER_NEWS_TOP_STORIES = "topstories"
HACKER_NEWS_TITLE = "title"
HACKER_NEWS_KIDS = "kids"
HACKER_NEWS_TEXT = "text"

JSON_SUFFIX = ".json"

SENTIMENT_POS = "positive"
SENTIMENT_NEG = "negative"
SENTIMENT_NEU = "neutral"
SENTIMENT_MIX = "mixed"

VADER_POS = "pos"
VADER_NEG = "neg"
VADER_NEU = "neu"
VADER_MIX = "compound"

STATS_COMMENTS = "comments"
STATS_AVG = "avg"
STATS_MED = "median"


timestamp = datetime.timestamp(datetime.now())

loop = asyncio.get_event_loop()

analyzer = SentimentIntensityAnalyzer()

stats = {SENTIMENT_POS: [], SENTIMENT_NEG: [], SENTIMENT_NEU: [], SENTIMENT_MIX: []}

all_story_urls = []

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

            for url
            in urls
        ]
        responses = []

        for response in await asyncio.gather(*futures):
            try:
                res = response.json()
            except:
                continue

            responses.append(res)

    return responses

def get_query_params(event):
    return event.get(QUERY_STR_PARAMS, {}).get(QUERY_PHRASE, '').lower()


def sentiment(event, context):
    tag_event(SERVERLESS_TAG_1, SERVERLESS_TAG_2)
    phrase = get_query_params(event)
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": True
    }

    status_code = STATUS_CODE_SUCCESS

    try:
        body = run(phrase)
    except Exception as exc:
        if not body:
            body = {"error": str(exc)}
            status_code = STATUS_CODE_FAILED
        else:
            status_code = STATUS_CODE_PART

    response = {
        "statusCode": status_code,
         "headers": headers,
         "body": json.dumps(body)
    }

    return response


def run(phrase):
    urls = []
    urls.append(HACKER_NEWS_PREFIX + HACKER_NEWS_TOP_STORIES + JSON_SUFFIX)
    results = loop.run_until_complete(fetch_all(urls))
    story_id_list = results[0]

    for story_id in story_id_list:
        all_story_urls.append(get_url_from_id(story_id))

    results = loop.run_until_complete(fetch_all(all_story_urls))

    all_direct_story_kids_id = []

    for story in results:
        if story.get(HACKER_NEWS_TITLE).lower().find(phrase) != -1 and story.get(HACKER_NEWS_KIDS) is not None:
            for comment_id in story.get(HACKER_NEWS_KIDS, []):
                all_direct_story_kids_id.append(comment_id)

    get_comments(all_direct_story_kids_id)

    sum = len(stats[SENTIMENT_POS])
    output = {STATS_COMMENTS:sum}

    if sum != 0:
        for attr in stats:
            data = {
                STATS_AVG: "%.3f" % mean(stats[attr]),
                STATS_MED: "%.3f" % median(stats[attr])
            }
            output[attr] = data

    return output


def update_sentiments(text):
    if not text:
        return

    result = analyzer.polarity_scores(text)
    stats[SENTIMENT_POS].append(result[VADER_POS])
    stats[SENTIMENT_NEG].append(result[VADER_NEG])
    stats[SENTIMENT_NEU].append(result[VADER_NEU])
    stats[SENTIMENT_MIX].append(result[VADER_MIX])

def get_url_from_id(id):
    return HACKER_NEWS_PREFIX + HACKER_NEWS_ITEM_PATH + str(id) + JSON_SUFFIX


def get_comments(comment_ids):
    if not comment_ids:
        return

    comment_urls = [get_url_from_id(comment_id) for comment_id in comment_ids]
    result = loop.run_until_complete(fetch_all(comment_urls))

    for comment in result:
        update_sentiments(comment.get(HACKER_NEWS_TEXT))
        get_comments(comment.get(HACKER_NEWS_KIDS, []))
