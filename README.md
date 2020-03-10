# comment-analyst

# About
For a given phrase - a query is sent to HackerNews via https://github.com/HackerNews/API to be looked for in the last 100 story titles, 
from which, all the sub comments are estimated by their sentiment.
If one or more titles matches and have comments a json with sentiment statistics (positive, negative, neutal, mixed) is returned.

# In this project
handler.py event function resposible for running the logic behind

# Usage
Example: https://nnccmexb6l.execute-api.us-east-1.amazonaws.com/dev/sentiment?phrase=down
where sentiment is the called function
phrase is the text to be searched in titles

# Requirements
requests

vaderSentiment.vaderSentiment

statistics

# About the assignment
According to the assignment requirements the main language that was used is python3(.7) - due to straightforward serverside implementation
For initial development an online dev environment was used (repl.it) to develop and test each function, it can run server requests
Requirements and serverless-python-rquirements were installed on a personal virtual environment for contiuous development and testing and for creating requirements.txt and package.json
For the sentiment stats a 3rd party library named 'vaderSentiment' was used
For parallel get requests the python library asyncio was used
For timeout handling the datetime.timestamp was used - the process returns results returned until timeout deadline
