import csv
import datetime

import numpy as np
import pandas as pd
import requests

from collections import Counter, OrderedDict
from dateutil.parser import parse
from operator import itemgetter
from selenium import webdriver


def grab_html():
    url = 'https://www.reddit.com/r/wallstreetbets/search/?q=flair%3A%22Discussion%22&restrict_sr=1'
    driver = webdriver.Chrome()
    driver.get(url)
    return driver


def grab_stock_link(driver):
    links = driver.find_elements_by_xpath('//*[@class="_eYtD2XCVieq6emjKBH3m"]')
    link = ""

    for a in links:
        if a.text.startswith('Daily Discussion Thread'):
            date = "".join(a.text.split(' ')[-3:])
            parsed = parse(date)
            yesterday = datetime.date.today() - datetime.timedelta(days=1)

            if parse(str(yesterday)) == parsed:
                link = a.find_element_by_xpath('../..').get_attribute('href')

        if a.text.startswith('Weekend'):
            date = "".join(a.text.split(' ')[-3:])
            parsed = parse(date)
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
            twodaysago = datetime.date.today() - datetime.timedelta(days=2)
            threedaysago = datetime.date.today() - datetime.timedelta(days=3)

            if (parse(str(yesterday)) == parsed or
                    parse(str(twodaysago)) == parsed or
                    parse(str(threedaysago)) == parsed):
                link = a.find_element_by_xpath('../..').get_attribute('href')

    stock_link = link.split('/')[-3]
    driver.close()

    return stock_link


def grab_stocks():
    with open('tickers.txt', 'r') as w:
        stocks = w.readlines()
        stocks_list = []
        for a in stocks:
            a = a.replace('\n', '')
            stocks_list.append(a)
        return stocks_list


def grab_comment_id_list(stock_link):
    html = requests.get(f'https://api.pushshift.io/reddit/submission/comment_ids/{stock_link}')
    raw_comment_id_list = html.json()
    return raw_comment_id_list


def get_comments(comment_id_list):
    html = requests.get(f'https://api.pushshift.io/reddit/comment/search?ids={comment_id_list}&fields=body&size=1000')
    new_comments = html.json()
    return new_comments


def get_all_comments():
    list = np.array(raw_comment_id_list['data'])
    comments = {'data': []}

    i = 0
    while i < len(list):
        print(len(list))
        new_comments_list = ",".join(list[0:1000])
        new_comments = get_comments(new_comments_list)

        comments['data'] += new_comments['data']

        remove_me = slice(0, 1000)
        list = np.delete(list, remove_me)

    return comments


def data_cleansing(comments, stocks_list):
    cleansed = []
    for a in comments['data']:
        for ticker in stocks_list:
            word = " " + ticker + " "
            if word in a['body']:
                cleansed.append(a)

    return cleansed


def get_stock_count(comments, stocks_list):
    stock_dict = Counter()

    for a in comments:
        for ticker in stocks_list:
            word = " " + ticker + " "
            if word in a['body']:
                stock_dict[ticker] += 1
    stock_dict = dict(stock_dict)
    return stock_dict


def get_ticker(comment):
    for ticker in stocks_list:
        word = " " + ticker + " "
        if word in comment["body"]:
            return ticker


def output_comments(comments):
    data_list = [["index", "comment", "ticker"]]
    for i, comment in enumerate(comments):
        data_list.append([i, comment["body"], get_ticker(comment)])

    with open('../sentiment/comments.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data_list)


if __name__ == "__main__":
    # grab html
    driver = grab_html()

    # grab comments link
    stock_link = grab_stock_link(driver)

    # grab raw comments from comments link
    raw_comment_id_list = grab_comment_id_list(stock_link)

    # grab all comments
    comments = get_all_comments()

    # grab ticker list
    stocks_list = grab_stocks()

    # cleaning the data
    cleansed_comments = data_cleansing(comments, stocks_list)

    # output the comments
    output_comments(cleansed_comments)

    # print top ten stocks
    stock_count = get_stock_count(cleansed_comments, stocks_list)

    sorted_stock_count = OrderedDict(sorted(stock_count.items(), key=itemgetter(1), reverse=True))
    top_ten_stock = {k: sorted_stock_count[k] for k in list(sorted_stock_count)[:10]}

    df = pd.DataFrame(top_ten_stock.items(), columns=["ticker", "count"])
    print(df)
