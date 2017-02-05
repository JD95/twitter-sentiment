from json import *
import re
import os
from functools import reduce

states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

class Sentiment:
    def __init__(self, score, frequency = 0):
        self.score = score
        self.frequency = frequency

    def get_score(self):
        self.frequency += 1
        return self.score

    def __str__(self):
        return str(self.score) + ' ' + str(self.frequency)


class Tweet:
    def __init__(self, text, state):
        state_reg = re.compile("^.+, (\w+)\\s*")
        hash_reg = re.compile("\B#\w\w+")
        self.text = text
        self.state = state_reg.findall(state) if not(state is None) else ["_"]
        self.hashtags = hash_reg.findall(text)
        self.score = 0

    def __str__(self):
        return str(self.text) + ", " + str(self.score) + ", " + str(self.hashtags) + ", " + str(self.state)


def generate_sentiment_scores(sentiment_file):
    scores = {}                         # initialize an empty dictionary
    for line in sentiment_file:
        term, score = line.split("\t")  # The file is tab-delimited. "\t" means "tab character"
        scores[term] = Sentiment(int(score))       # Convert the score to an integer.
    return scores


def valid_tweet(tweet): return tweet['text'] != ""


#   score_word :: Map String Sentiment -> String -> Int
def score_word(sentiment_scores): return lambda word: sentiment_scores.get(word.lower(), Sentiment(0))


def score_words(sentiment_scores, tweet): return map(score_word(sentiment_scores), tweet.split())


#   score_tweet :: Map String Sentiment -> Tweet -> Int
def score_tweet_text(sentiment_scores):
    return lambda text: reduce(lambda x, y: x + y.get_score(),  # Checks the frequency of the words as well
                               score_words(sentiment_scores, text), 0)


def get_raw_tweets(file):
    json_tweets = filter(lambda line: line != u"\n", open(file, encoding="utf16"))
    return filter(valid_tweet, map(lambda line: loads(line), json_tweets))


def get_tweets(raw_tweets):
    return map(lambda tweet: Tweet(tweet['text'], tweet['user']['location']), raw_tweets)


def tweet_text(tweets): return map(lambda tweet: tweet.text, tweets)


#   fan_out :: ((a -> b),(a -> c)) -> a -> (a, c)
def fan_out(f, g): return lambda x: (f(x), g(x))


#   unknown_words :: Map String Sentiment -> String -> [String]
def unknown_words(scores): return lambda text: filter(lambda word: not(word in scores), text.split())


#   score_unknown_words :: (Int, [String]) -> (Int, Map Sentiment Int)
def score_unknown_words(args):
    tweet_score, words = (args[0], args[1])
    unknowns = {}
    for word in words:
        unknowns[word] = Sentiment(tweet_score, 1)
    return tweet_score, unknowns


#   merge_term_scores :: (Map a b, Map a b, (b -> b -> b)) -> Map a b
def merge_dicts(xs, ys, f):
    keys = list(xs.keys()) + list(ys.keys())
    return {key: f(xs.get(key, None), ys.get(key, None)) for key in keys}


def avg(x, y):
    if not(x is None or y is None):
        x.score = (x.score + y.score) / 2
        x.frequency += y.frequency
        return x
    else:
        return y if x is None else x


def join_tweet_results(x, y):
    x[0].append(y[0])
    return x[0], merge_dicts(x[1], y[1], avg)


def main():

    # Read in files from command line
    afinnfile = open("AFINN-111.txt")
    scores = generate_sentiment_scores(afinnfile)

    # Filter non-tweet data
    tweets = list(filter(lambda t: t.state != [] and not(states.get(t.state[0],None) is None), get_tweets(get_raw_tweets("output.json"))))

    scores_and_unknowns = map(fan_out(score_tweet_text(scores), unknown_words(scores)), tweet_text(tweets))

    scores_and_new_words = map(score_unknown_words, scores_and_unknowns)

    tweet_scores, new_words = reduce(join_tweet_results, scores_and_new_words, ([], {}))

    for i in range(0, len(tweets)):
        tweets[i].score = tweet_scores[i]

    for tweet in tweets:
        print(str(tweet))

main()