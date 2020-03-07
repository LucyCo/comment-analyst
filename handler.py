from urllib import request
import json
from serverless_sdk import tag_event

def mean(values):
  return sum(values) / len(values)

def median(values):
  if len(values) == 0:
    return None

  return sorted(values)[int(len(values) / 2)]

def make_request(url):
  req =  request.Request('https://hacker-news.firebaseio.com/v0/item/8863.json')
  response = request.urlopen(req)
  return json.loads(response.read())

def get_sentiment(text):
  return {'pos': 0.3, 'neg': '0.4', 'neu': 0.5, 'compound': 0.6} # todo

stats = {"positive":[],"negative":[],"neutral":[],"mixed":[]}

headers = {
  'x-rapidapi-host': "community-hacker-news-v1.p.rapidapi.com",
  'x-rapidapi-key': "70a9a1e646mshfbe352366d4e248p1026d2jsn434e37469a13"
}

def hello(event, context):
  tag_event('comment-analyst', 'sentiment')

  headers = {
       "Access-Control-Allow-Origin": "*",
       "Access-Control-Allow-Credentials": True
  }

  try:
      body = run()
  except Exception as exc:
      body = 'todo error: ' + str(exc)

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
  storyIdList = make_request(url)

  for storyId in storyIdList:
    url = "https://community-hacker-news-v1.p.rapidapi.com/item/" + str(storyId) + ".json"
    story = make_request(url)
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
  result = get_sentiment(text)
  stats["positive"].append(result["pos"])
  stats["negative"].append(result["neg"])
  stats["neutral"].append(result["neu"])
  stats["mixed"].append(result["compound"])


def commentTraverse(commentId):
  url = "https://community-hacker-news-v1.p.rapidapi.com/item/" + str(commentId) + ".json"
  comment = make_request(url)
  kids = comment.get('kids')
  if kids is None:
    updateSentiments(str(comment.get('text')))
    return
  for kidId in comment["kids"]:
    commentTraverse(kidId)
