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


def valid_tweet(tweet): return tweet['text'] != ""


def score_word(sentiment_scores): return lambda word: sentiment_scores.get(word.lower(), 0)


def score_words(sentiment_scores, tweet): return map(score_word(sentiment_scores), tweet.split())


#   score_tweet :: Map String Int -> String -> Int
def score_tweet(sentiment_scores):
    return lambda tweet: reduce(lambda x, y: x + y, score_words(sentiment_scores, tweet), 0)


def get_tweets(file):
    json_tweets = filter(lambda line: line != u"\n", open(file, encoding="utf16"))
    return filter(valid_tweet, map(lambda line: loads(line), json_tweets))


def tweet_text (tweets): return map(lambda tweet: tweet['text'], tweets)


#   fan_out :: ((a -> b),(a -> c)) -> a -> (a, c)
def fan_out(f, g): return lambda x: (f(x), g(x))


#   unknown_words :: Map String Int -> String -> [String]
def unknown_words(scores): return lambda text: filter(lambda word: not(word in scores), text.split())


#   score_unknown_words :: (Int, [String]) -> (Int, Map String Int)
def score_unknown_words(args):
    tweet_score, words = (args[0], args[1])
    unknowns = {}
    for word in words:
        unknowns[word] = tweet_score
    return tweet_score, unknowns


#   merge_term_scores :: (Map a b, Map a b, (b -> b -> b)) -> Map a b
def merge_dicts(xs, ys, f):
    keys = list(xs.keys()) + list(ys.keys())
    return {key: f(xs.get(key, 0), ys.get(key, 0)) for key in keys}


def avg(x, y): return (x + y) / 2


def join_tweet_results(x, y):
    x[0].append(y[0])
    return x[0], merge_dicts(x[1], y[1], avg)


def main():

    # Read in files from command line
    afinnfile = open("AFINN-111.txt")
    scores = generate_sentiment_scores(afinnfile)

    # Filter non-tweet data
    tweets = get_tweets("output.json")

    scores_and_unknowns = map(fan_out(score_tweet(scores), unknown_words(scores)), tweet_text(tweets))

    scores_and_new_words = map(score_unknown_words, scores_and_unknowns)

    tweet_scores, new_words = reduce(join_tweet_results, scores_and_new_words, ([], {}))

    print(new_words)

main()