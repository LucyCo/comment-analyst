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
json
serverless_sdk
statistics
vaderSentiment.vaderSentiment

# About the assignment
I decided to use python since it's usage as serverside and with json is straightforward
I used an online dev environment repl.it to develop and test each function, it can run server requests
I decided not to implement the sentiment calculator by myself and used vaderSentiment library
I used the mean and median functions in statistics library to calculate avg and median values
