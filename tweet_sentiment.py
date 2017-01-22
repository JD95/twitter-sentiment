from json import *
import re
import os
from functools import reduce


def generate_sentiment_scores(sentiment_file):
    scores = {}                         # initialize an empty dictionary
    for line in sentiment_file:
        term, score = line.split("\t")  # The file is tab-delimited. "\t" means "tab character"
        scores[term] = int(score)       # Convert the score to an integer.
    return scores


def valid_tweet(tweet):
    return tweet['text'] != ""


def score_word(sentiment_scores):
    return lambda word: sentiment_scores.get(word.lower(), 0)

def score_words(sentiment_scores, tweet):
    return map(score_word(sentiment_scores), tweet.split())


def score_tweet(sentiment_scores):
    return lambda tweet: reduce(lambda x, y: x + y, score_words(sentiment_scores, tweet), 0)


def main():

    # Read in files from command line
    afinnfile = open("AFINN-111.txt")
    scores = generate_sentiment_scores(afinnfile)

    # Filter non-tweet data
    json_tweets = filter(lambda line: line != u"\n", open("output.json", encoding="utf16"))

    tweets = filter(valid_tweet, map(lambda line: loads(line), json_tweets))

    # Score filtered tweets
    tweet_scores = map(score_tweet(scores), map(lambda tweet: tweet['text'], tweets))

    # Print scores
    for score in tweet_scores:
        print(str(score))

main()