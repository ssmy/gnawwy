from twitterparser import TwitterParser
import pynotify, time


pynotify.init("gnawwy")
twitparse = TwitterParser('username', 'password')

while True:
        time.sleep(60)
        new_items = twitparse.check()
        if new_items:
            for item in new_items:
                pynotify.Notification(item["title"], item["text"], "file://" + item["icon"].name).show()
