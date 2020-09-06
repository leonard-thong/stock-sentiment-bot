import pandas as pd
import nltk

from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')


def get_comments():
    array = []
    file = "comments.csv"
    df = pd.read_csv(file)

    for row in df["comment"]:
        array.append(row)

    return array

def get_tickers():
    a = set()
    file = "comments.csv"
    df = pd.read_csv(file)

    for row in df["ticker"]:
        a.add(row)

    return list(a)


def sentiment_analysis(comments):
    index = 0
    for comment in comments:
        score = SentimentIntensityAnalyzer().polarity_scores(comment)

        if score['neg'] > score['pos'] and score['neg'] + .68 > score['neu']:
            print("Negative Sentiment")
            index += 1
        elif score['neg'] < score['pos'] and score['neu'] < score['pos'] + .68:
            print("Positive Sentiment")
            index += 1
        else:
            print("Neutral Sentiment")
            index += 1




if __name__ == "__main__":
    comments = get_comments()
    tickers = get_tickers()

    sentiment_analysis(comments)

