from urllib import request
import json
from serverless_sdk import tag_event

# 3b22b8fc5b8ace713086f2bf8796c65b9a4a287c~17

def make_request(url):
    req =  request.Request('https://hacker-news.firebaseio.com/v0/item/8863.json')
    response = request.urlopen(req)
    return json.loads(response.read())


def hello(event, context):
    tag_event('custom-tag', 'hello-world', {'custom': {'tag': 'data '}})

    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": True
    }

    try:
        body = make_request('https://hacker-news.firebaseio.com/v0/topstories.json')
    except Exception as exc:
        body = 'todo-error: ' + str(exc)

    response = {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
