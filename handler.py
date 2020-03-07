from urllib import request
import json
from serverless_sdk import tag_event

POSITIVE_WORDS = ['good', 'great', 'happy']
NEGATIVE_WORDS = ['bad', 'terrible', 'sad']


def hello(event, context):
  tag_event('comment-analyst', 'sentiment')

  headers = {
       "Access-Control-Allow-Origin": "*",
       "Access-Control-Allow-Credentials": True
  }

  phrase = event.get('queryStringParameters', {}).get('phrase')
  try:
      body = run(phrase)
  except Exception as exc:
      body = 'error: ' + str(exc)

  response = {
      "statusCode": 200,
       "headers": headers,
       "body": json.dumps(body)
  }
  return response

def mean(values):
  return sum(values) / len(values)

def median(values):
  if len(values) == 0:
    return None

  return sorted(values)[int(len(values) / 2)]

def make_request(url):
  req =  request.Request('https://hacker-news.firebaseio.com/v0/item/8863.json')
  req.add_header('x-rapidapi-host', "community-hacker-news-v1.p.rapidapi.com")
  req.add_header('x-rapidapi-key', "70a9a1e646mshfbe352366d4e248p1026d2jsn434e37469a13")

  response = request.urlopen(req)
  return json.loads(response.read())

def get_sentiment(text):
  words = text.split(' ')
  total = float(len(words))
  positive = len([word for word in words if word in POSITIVE_WORDS])
  negative = len([word for word in words if word in NEGATIVE_WORDS])
  neutral = len(words) - (positive + negative)
  compound = min(positive, negative)
  return {
    'pos': positive / total,
    'neg': negative / total,
    'neu': neutral / total,
    'compound': compound / total
  }

stats = {"positive":[],"negative":[],"neutral":[],"mixed":[]}




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
