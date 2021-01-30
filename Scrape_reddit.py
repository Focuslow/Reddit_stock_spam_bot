import praw
from prawcore.exceptions import OAuthException
from praw.exceptions import RedditAPIException
import os
import time
from datetime import datetime


def get_link_url(stock=''):
    if os.path.exists('url_info.txt'):
        with open('url_info.txt', 'r') as file:
            url = file.read()
            url = url.strip('\n')
            url = url.strip(' ')

            if stock:
                url = url + 'stock/' + stock

    else:
        with open('url_info.txt', 'w') as file:
            file.write('https://investsuggest.com/ \n')
            url = 'https://investsuggest.com/'

    return url


def get_subs():  # gets wanted subreddits
    if os.path.exists('subreddits.txt'):
        with open('subreddits.txt', 'r') as file:
            subs = file.read()
            subs.replace('r/', '')
            subs.strip(' ')
            subs = subs.split('\n')

            subs = list(filter(None, subs))

    else:
        with open('subreddits.txt', 'w') as file:
            file.write('Wallstreetbets \n')
            subs = ['Wallstreetbets']

    return subs


def get_user():  # get reddit user and api key
    user = []
    if os.path.exists('reddit_user.txt'):
        # open and get reddit user and api key
        with open('reddit_user.txt', 'r') as file:
            txt = file.read()
            txt.strip(' ')
            txt = txt.split('\n')

            txt = list(filter(None, txt))

            for i in txt:
                str_break = i.index("=")
                user.append(i[str_break + 1:])

    else:
        # testing or if you delete you have correct form just change stuff
        with open('reddit_user.txt', 'w') as file:
            file.write('client_id=pHWeh5UStX5Ffw\n')
            file.write('client_secret=oLlBmvXueQXgfHSYrOVNaTvkSxZjJQ\n')
            file.write('user_agent=Stock_bot_test\n')
            file.write('username=TSLA_bot_test11\n')
            file.write('password=TSLA_bot_test111\n')
            user = ['pHWeh5UStX5Ffw', 'oLlBmvXueQXgfHSYrOVNaTvkSxZjJQ', 'Stock_bot_test', 'TSLA_bot_test11',
                    'TSLA_bot_test111']

    return user


def get_stocks():  # get list of stocks
    if os.path.exists('stocks.txt'):
        with open('stocks.txt', 'r') as file:
            stocks = file.read()
            stocks = stocks.replace(" ","")
            stocks = stocks.split('\n')
            stocks = list(filter(None, stocks))


    else:
        with open('stocks.txt', 'w') as file:
            file.write('TSLA \n')
            stocks = ['TSLA']

    return stocks


def commented_posts(new_entry=''):  # what posts did I reply to, if new_entry then update file
    if not new_entry:
        if os.path.exists('posted.txt'):
            with open("posted.txt", "r") as f:
                commented_posts = f.read()
                commented_posts = commented_posts.split("\n")
                commented_posts = list(filter(None, commented_posts))

        else:
            commented_posts = []

    else:
        with open("posted.txt", "w") as f:
            commented_posts = f.write(new_entry + '\n')

    return commented_posts


def commented_comments(new_entry=''):  # what comments did I reply to, new_entry to update
    if os.path.exists('commented.txt'):
        with open("commented.txt", "r") as f:
            commented_comments = f.read()
            commented_comments = commented_comments.split("\n")
            commented_comments = list(filter(None, commented_comments))

    else:
        commented_comments = []

    return commented_comments


def reddit_API_conn(user):  # connect to reddit API using provided info
    reddit_user = praw.Reddit(client_id=user[0], \
                              client_secret=user[1], \
                              user_agent=user[2], \
                              username=user[3], \
                              password=user[4])

    try:
        print('Connected as: ' + str(reddit_user.user.me()))

    except OAuthException:
        print('Wrong user data could not connect')

    return reddit_user


def post_comments(reddit, submissions, stock=None, old_posts=[], top=False): # post comment on each submission with correct stock.
    for submission in submissions: #each post on subreddit
        if submission.id not in old_posts: #not visited yet
            time.sleep(10)
            while reddit.auth.limits['remaining'] < 20:  # limit rate of requests
                print('Waiting out limit')
                time.sleep(30)

            try:
                if top and stock not in submission.title:
                    submission.reply("Stocks go up bois!! Find more info and analysis on my page -> " + get_link_url())
                    print('Comment -- Stocks go up bois!! Find more info and analysis on my page -> ' + get_link_url())
                else:
                    submission.reply(
                        "Stocks go up bois!! Find more info and analysis on my page -> " + get_link_url(stock))
                    print('Comment -- Stocks go up bois!! Find more info and analysis on my page -> ' + get_link_url(
                        stock))
                old_posts.append(submission.id)
                commented_posts(submission.id)
                print('Commented on: ' + str(submission.title) + " --with ID: " + str(submission.id))


            except RedditAPIException as error:
                print(error)
                time_reset = datetime.fromtimestamp(reddit.auth.limits['reset_timestamp'])
                time_reset = (time_reset-datetime.now())
                print('Waiting for: '+ str(int(time_reset.total_seconds()/60))+" minutes.")
                time.sleep(time_reset.total_seconds())


def post_reply_on_comments(reddit, submissions, stock=None, old_post=None, old_comments=None): #post reply to comments on comment with stocks mention
    for post in submissions: #all posts in subreddit
        post.comments.replace_more(limit=0) # get all comments
        for comment in post.comments.list():
            if comment not in old_comments: #haven't replied to this one yet
                if stock in comment.body: #contains stock
                    time.sleep(10)
                    while reddit.auth.limits['remaining'] < 20:  # limit rate of requests
                        print('Waiting out limit')
                        time.sleep(30)
                    try:
                        comment.reply("Stocks go up bois!! Find more info and analysis on my page -> " + get_link_url())
                        print('Reply -- Commented on comment: ' + str(comment.body) + "--On a post: "+ str(post.title))
                        old_comments.append(comment.id)
                        commented_comments(comment.id)
                        print('Commented on comment: ' + str(comment.body) + "--On a post: "+ str(post.title))

                    except OAuthException as error:
                        print(error)
                        time_reset = datetime.fromtimestamp(reddit.auth.limits['reset_timestamp'])
                        time_reset = (time_reset - datetime.now())
                        print('Waiting for: ' + str(int(time_reset.total_seconds() / 60))+" minutes.")
                        time.sleep(time_reset.total_seconds())


def spam(subs_list, reddit, stocks_list):
    old_posts = commented_posts()
    old_comments = commented_comments()
    for sub in subs_list:
        sub = reddit.subreddit(sub)
        # reply to top 5 posts of each day on each listed subreddit
        top_posts = sub.top('day', limit=5)
        # for each stock find posts in all subreddits and reply to the posts
        for stock in stocks_list:
            submissions = sub.search(stock, limit=5)
            post_comments(reddit, top_posts, stock, old_posts, top=True)
            post_comments(reddit, submissions, stock, old_posts)
            post_reply_on_comments(reddit, submissions, stock, old_posts, old_comments)
            post_reply_on_comments(reddit, top_posts, stock, old_posts, old_comments)


if __name__ == "__main__":
    subreddits = get_subs()
    user = get_user()
    user = reddit_API_conn(user)
    stocks = get_stocks()
    spam(subreddits, user, stocks)
