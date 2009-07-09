#!/usr/bin/env python
import twitter, time, calendar, tempfile, urllib

class TwitterParser(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.api = twitter.Api(username=username, password=password)
        self.api.SetCacheTimeout(None)
        tweets = self.api.GetFriendsTimeline()
        self.last_check = tweets[0].id
    def check(self):
        tweets = self.api.GetFriendsTimeline()
        new_tweets = []
        for tweet in tweets:
            if tweet.id <= self.last_check: continue
            new_tweet = {"title" : tweet.user.name, "text" : tweet.text}
            temp = tempfile.NamedTemporaryFile()
            temp.write(urllib.urlopen(tweet.user.profile_image_url).read())
            new_tweet["icon"] = temp
            new_tweet["user"] = tweet.user.screen_name
            temp.flush()
            new_tweets.append(new_tweet)
        if new_tweets:
            self.last_check = tweets[0].id
        return new_tweets
