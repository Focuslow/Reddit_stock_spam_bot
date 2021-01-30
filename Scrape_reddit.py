import praw
from prawcore.exceptions import OAuthException
from praw.exceptions import RedditAPIException
import os
import time
from datetime import datetime
import requests


def get_message():  # get message to post
    if os.path.exists('msg_txt.txt'):
        with open('msg_txt.txt', 'r') as file:
            msg = file.read()
            msg = msg.strip('\n')
            msg = msg.strip(' ')

    else:  # baseline text for testing
        with open('msg_txt.txt', 'w') as file:
            file.write('Stocks go up bois!! Find more info and analysis on my page -> ')
            msg = 'Stocks go up bois!! Find more info and analysis on my page -> '

    return msg


def get_subs():  # gets wanted subreddits, can be empty and will just search reddit
    if os.path.exists('subreddits.txt'):
        with open('subreddits.txt', 'r') as file:
            subs = file.read()
            subs.replace('r/', '')
            subs.strip(' ')
            subs = subs.split('\n')

            subs = list(filter(None, subs))

            if not subs:
                subs = ['all']

    else:
        with open('subreddits.txt', 'w') as file:
            file.write('Wallstreetbets \n')
            subs = ['Wallstreetbets']

    return subs


def get_users():  # get reddit user and api key
    users = []
    user = []
    if os.path.exists('reddit_user.txt'):
        # open and get reddit user and api key
        with open('reddit_user.txt', 'r') as file:
            txt = file.read()
            txt.strip(' ')
            txt = txt.split('\n')

            txt = list(filter(None, txt))

            for line in txt:
                str_break = line.index("=")
                user.append(line[str_break + 1:])
                if line[:str_break] == 'password' and txt.index(line) != 0:
                    users.append(user)
                    user = []




    else:
        # testing or if you delete you have correct form just change stuff
        with open('reddit_user.txt', 'w') as file:
            # user1
            file.write('client_id=pHWeh5UStX5Ffw\n')
            file.write('client_secret=oLlBmvXueQXgfHSYrOVNaTvkSxZjJQ\n')
            file.write('user_agent=Stock_bot_test\n')
            file.write('username=TSLA_bot_test11\n')
            file.write('password=TSLA_bot_test111\n')

            # user2
            file.write('client_id=pt8_ymZy3QdH8Q\n')
            file.write('client_secret=joFigcc09WB3Ytwrdkxk9Vdd_7odQQ\n')
            file.write('user_agent=Stock_bot_test\n')
            file.write('username=get_money_bois1\n')
            file.write('password=get_money_bois12\n')

            users = get_users()

    return users


def get_search_phrases():  # get list of stocks
    if os.path.exists('search_phrases.txt'):
        with open('search_phrases.txt', 'r') as file:
            search_phrases = file.read()
            search_phrases = search_phrases.strip(" ")
            search_phrases = search_phrases.split('\n')
            search_phrases = list(filter(None, search_phrases))


    else:  # start test with stocks
        with open('search_phrases.txt', 'w') as file:
            file.write('stocks')
            search_phrases = ['stocks']

    return search_phrases


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

    except OAuthException as error:
        print('Wrong user data could not connect')
        raise error

    return reddit_user


def post_comments(reddit, submissions, old_posts=[]):  # post comment on each submission.
    for submission in submissions:  # each post on subreddit
        if submission.id not in old_posts:  # not visited yet
            time.sleep(10)
            if reddit.auth.limits['remaining'] < 20:  # limit rate of requests
                raise Exception('Limit reached \n')

            try:
                submission.reply(get_message())
                print('Comment --' + get_message())
                old_posts.append(submission.id)
                commented_posts(submission.id)
                print('Commented on: ' + str(submission.title) + " --with ID: " + str(submission.id))


            except RedditAPIException as error:
                print(error)
                raise error


def post_reply_on_comments(reddit, submissions, phrase=None,
                           old_comments=None):  # post reply to comments on comment with phrase mention
    for post in submissions:  # all posts in subreddit
        post.comments.replace_more(limit=0)  # get all comments
        for comment in post.comments.list():
            if comment not in old_comments:  # haven't replied to this one yet
                if phrase in comment.body:  # contains search phrase
                    time.sleep(10)
                    if reddit.auth.limits['remaining'] < 20:  # limit rate of requests
                        raise Exception('Limit reached \n')

                    try:
                        comment.reply(get_message())
                        print('Reply -- Commented on comment: ' + str(comment.body) + "--On a post: " + str(post.title))
                        print('Comment --' + get_message())
                        old_comments.append(comment.id)
                        commented_comments(comment.id)



                    except RedditAPIException as error:
                        print(error)
                        raise error


def spam(subs_list, reddit, search_phrases):
    old_posts = commented_posts()
    old_comments = commented_comments()

    for sub in subs_list:
        sub = reddit.subreddit(sub)
        # reply to top 5 posts of each day on each listed subreddit if none listed then skip
        if sub != 'all':
            top_posts = sub.top('day', limit=5)
            post_comments(reddit, top_posts, old_posts)
        # for each phrase find posts in all subreddits and reply to the posts
        for phrase in search_phrases:
            submissions = sub.search(phrase, limit=5)
            try:
                post_comments(reddit, submissions, old_posts)
                post_reply_on_comments(reddit, submissions, phrase, old_comments)
                post_reply_on_comments(reddit, top_posts, phrase, old_comments)

            except RedditAPIException as error:
                raise error


if __name__ == "__main__":
    subreddits = get_subs()
    users = get_users()
    tried = 0
    search_phrases = get_search_phrases()

    if not search_phrases:
        print('Error: no search phrases!')
        print('Quitting!')
        quit()

    while 1:
        for user in users:
            if tried==len(users):
                print('Tried all accounts waiting for 1 min')
                print('')
                time.sleep(60)
                tried=0

            try:
                user = reddit_API_conn(user)
            except OAuthException:
                print('Error: Incorrect user info for ' + str(user[-2]) + '. Trying out next user.')
                print('')
                users.remove(user)
                continue

            try:
                spam(subreddits, user, search_phrases)

            except RedditAPIException:
                print('Info: ' + str(user.user.me()) + ' is timed out, trying out next user.')
                print('')
                tried+=1
                continue

            except:
                print('Info: '+ str(user.user.me())+ ' has reached limit, trying out next user.')
                print('')
                tried+=1
                continue
