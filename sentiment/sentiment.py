import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def get_comments():
    array = []
    file = "comments.csv"
    df = pd.read_csv(file)

    for row in df["comment"]:
        array.append(row)

    return array


def sentiment_analyse(sentiment_text):
    score = SentimentIntensityAnalyzer().polarity_scores(sentiment_text)
    if score['neg'] > score['pos']:
        print("Negative Sentiment")
    elif score['neg'] < score['pos']:
        print("Positive Sentiment")
    else:
        print("Neutral Sentiment")


if __name__ == "__main__":
    comments = get_comments()

