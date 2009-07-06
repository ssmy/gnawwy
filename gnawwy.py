#!/usr/bin/env python
import pynotify, time, twitterparser, ConfigParser, os, sys, emailparser, subprocess, shutil
from xdg.BaseDirectory import *

pynotify.init("gnawwy")
config_dir = xdg_config_home
configparse = ConfigParser.SafeConfigParser({'ssl' : 'False'})
try:
    configparse.readfp(open(os.path.join(config_dir, "gnawwy")))
except IOError:
    print "Error: configuration file not found. Going to configuration file editor."
    shutil.copyfile(os.path.join(sys.path[0], 'defaultrc'), os.path.join(config_dir, 'gnawwy'))
    retcode = subprocess.call(['nano', os.path.join(config_dir,'gnawwy')])
    print "Configuration file modified. Continuing..."

parsers = {}
usernames = []
for section in configparse.sections():
    usernames.append(configparse.get(section, "username"))
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
            try:
                new_items += parsers[section].check()
            except urllib2.UrlError:
                print "Error fetching new items."
        if new_items:
            for item in new_items:
                print item["user"]
                if item["user"] in usernames:
                    print "Not displaying tweet from self"
                else:
                    pynotify.Notification(item["title"], item["text"], "file://" + item["icon"].name).show()
        time.sleep(30)
