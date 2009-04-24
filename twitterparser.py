import twitter, time, calendar


class TwitterParser(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.api = twitter.Api(username=username, password=password)
        self.last_check = time.time()
    def check(self):
        now = time.time()
        tweets = self.api.GetFriendsTimeline()
        new_tweets = [tweet for tweet in tweets if time.localtime(tweet.GetCreatedAtInSeconds()) > time.gmtime(self.last_check)]
        return len(new_tweets)
