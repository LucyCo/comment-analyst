import json
from serverless_sdk import tag_event


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
    except:
        body = 'todo-error'

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
