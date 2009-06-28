import pynotify, time, twitterparser, ConfigParser, os, sys


pynotify.init("gnawwy")
configparse = ConfigParser.SafeConfigParser()
try:
    configparse.readfp(open(os.path.expanduser('~/.gnawwyrc')))
except IOError:
    print "Error: configuration file not found. Create a .gnawwyrc in your home directory; see the README for the format."
    sys.exit()

parsers = {}
for section in configparse.sections():
    try:
        parsertype = configparse.get(section, "type")
        username = configparse.get(section, "username")
        password = configparse.get(section, "password")
        if parsertype == "twitter":
            parser = twitterparser.TwitterParser(username, password)
            parsers[section] = parser
        else:
            print "Unknown parser type %s found; skipping section %s." % (parsertype, section)
            continue
    except ConfigParser.NoOptionError as error:
        print "Parsing section %s failed: %s." % (section, error)

while True:
        time.sleep(60)
        new_items = []
        for section in parsers:
            new_items += parsers[section].check()
        if new_items:
            for item in new_items:
                pynotify.Notification(item["title"], item["text"], "file://" + item["icon"].name).show()
                
