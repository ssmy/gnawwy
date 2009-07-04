#!/usr/bin/env python
import pynotify, time, twitterparser, ConfigParser, os, sys, emailparser
from xdg.BaseDirectory import *

pynotify.init("gnawwy")
config_dir = xdg_config_home
configparse = ConfigParser.SafeConfigParser({'ssl' : 'False'})
try:
    configparse.readfp(open(os.path.join(config_dir, "gnawwy")))
except IOError:
    print "Error: configuration file not found. Going to configuration file editor."
    sys.exit()

parsers = {}
for section in configparse.sections():
    try:
        parsertype = configparse.get(section, "type")
        username = configparse.get(section, "username")
        password = configparse.get(section, "password")
        if parsertype == "twitter":
            parser = twitterparser.TwitterParser(username, password)
        elif parsertype == "email":
            server = configparse.get(section, "server")
            ssl = configparse.getboolean(section, "ssl")
            parser = emailparser.EmailParser(server, username, password, use_ssl=ssl)
        else:
            print "Unknown parser type %s found; skipping section %s." % (parsertype, section)
            continue
        parsers[section] = parser
    except (ConfigParser.NoOptionError, ValueError) as error:
        print "Parsing section %s failed: %s." % (section, error)

while True:
        new_items = []
        for section in parsers:
            print "Checking section %s." % section
            new_items += parsers[section].check()
        if new_items:
            for item in new_items:
                pynotify.Notification(item["title"], item["text"], "file://" + item["icon"].name).show()
        time.sleep(60)
