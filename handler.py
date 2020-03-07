import requests
import json
from serverless_sdk import tag_event
from statistics import mean, median
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

stats = {"positive":[],"negative":[],"neutral":[],"mixed":[]}

querystring = {}

headers = {
     'x-rapidapi-host': "community-hacker-news-v1.p.rapidapi.com",
     'x-rapidapi-key': "70a9a1e646mshfbe352366d4e248p1026d2jsn434e37469a13"
    }

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
    body = {"error", str(exc)}

  if body is None:
    body = "Internal error!"

  response = {
      "statusCode": 200,
       "headers": headers,
       "body": json.dumps(body)
  }
  return response


def run(phrase):
  url = "https://community-hacker-news-v1.p.rapidapi.com/topstories.json"
  response = requests.request("GET", url, headers=headers, params=querystring)

  #error check
  if response.status_code >= 300 or response.status_code < 200:
    print('Connection to Hacker News failed - error code', response.status_code)

  storyIdList = response.json()

  for storyId in storyIdList:
    url = "https://community-hacker-news-v1.p.rapidapi.com/item/" + str(storyId) + ".json"
    response = requests.request("GET", url, headers=headers, params=querystring)
    story = response.json()
    print(story.get("title"))
    if story.get("title").find(phrase) != -1:
      for commentId in story["kids"]:
        commentTraverse(commentId)

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


def commentTraverse(commentId):
  url = "https://community-hacker-news-v1.p.rapidapi.com/item/" + str(commentId) + ".json"
  response = requests.request("GET", url, headers=headers, params=querystring)
  comment = response.json()
  kids = comment.get('kids')
  if kids is None:
    updateSentiments(str(comment.get('text')))
    return
  for kidId in comment["kids"]:
    commentTraverse(kidId)
