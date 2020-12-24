import csv
import json
import praw
import re
import requests
import numpy as np

from datetime import datetime, timedelta


def get_subreddit(name):
    if name == "":
        sub = "wallstreetbets"

    with open("config.json") as json_data_file:
        data = json.load(json_data_file)

    # create reddit instance
    reddit = praw.Reddit(client_id=data["login"]["client_id"], client_secret=data["login"]["client_secret"],
                         username=data["login"]["username"], password=data["login"]["password"],
                         user_agent=data["login"]["user_agent"])

    # create a subreddit instance
    subreddit = reddit.subreddit(name)
    return subreddit


def get_tickers():
    with open('tickers.txt', 'r') as w:
        tickers = w.readlines()
        tickers_list = []

        for ticker in tickers:
            ticker = ticker.replace('\n', '')
            tickers_list.append(ticker)

        return tickers_list


def get_all_submissions_id(subreddit):
    # scrape submissions created from 9pm two days ago to 9pm one day ago at 12 midnight
    # this is to avoid scraping newly created submissions
    current_time = datetime.now() + timedelta(hours=10)

    submissions_id = []

    for submission in subreddit.new(limit=1000):
        submission_date = datetime.utcfromtimestamp(submission.created)
        submission_delta = current_time - submission_date

        link = 'www.reddit.com' + submission.permalink
        submission_delta = str(submission_delta)

        if 'day' not in submission_delta:
            submissions_id.append(link.split('/')[-3])

    return submissions_id


def get_all_comments_id(submissions_id):
    comments_id = []

    for submission_id in submissions_id:
        html = requests.get(f'https://api.pushshift.io/reddit/submission/comment_ids/{submission_id}')
        curr_comments_id = html.json()["data"]

        comments_id += curr_comments_id

    return comments_id


def get_all_comments(comments_id):
    comments_id = np.array(comments_id)
    comments = []

    # split the comments id to a group of 1000
    # to fit the pushshift API requirement
    i = 0
    while i < len(comments_id):
        next_comments_list = ",".join(comments_id[0:1000])
        next_comments = _get_comments(next_comments_list)
        comments += next_comments

        remove_me = slice(0, 1000)
        comments_id = np.delete(comments_id, remove_me)

    return comments


def _get_comments(comments_id):
    html = requests.get(f'https://api.pushshift.io/reddit/comment/search?ids={comments_id}&fields=body&size=1000')
    if html.json() is not None:
        next_comments = html.json()['data']

    return next_comments


def clean_comments(comments, tickers):
    cleansed = []

    for comment in comments:
        for ticker in tickers:
            if _check_comment(ticker, comment['body']):
                cleansed.append(re.sub(r"\s", " ", comment['body']))
                break

    return cleansed


def _check_comment(word, body):
    return re.compile(r'\b({0})\b'.format(word), flags=re.IGNORECASE).search(body) is not None


def output_comments(comments):
    data_list = [["index", "comment"]]
    for i, comment in enumerate(comments):
        data_list.append([i, comment])

    with open('../sentiment/comments.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data_list)


def run(name):
    # create subreddit instance
    subreddit = get_subreddit(name)

    # get tickers list
    tickers = get_tickers()

    #get all submissions id within the last 24 hours
    submissions_id = get_all_submissions_id(subreddit)

    # get all comments id from all the submissions
    comments_id = get_all_comments_id(submissions_id)

    # get all comments from the comments id
    comments = get_all_comments(comments_id)

    # remove comments that did not mention any tickers
    comments = clean_comments(comments, tickers)

    # output comments to csv file
    output_comments(comments)


if __name__ == "__main__":
    name = "wallstreetbets"

    run(name)
