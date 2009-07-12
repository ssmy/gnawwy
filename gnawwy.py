#!/usr/bin/env python
import pynotify
import time, ConfigParser, os, sys, shutil, subprocess, urllib2, getopt
import twitterparser, emailparser
import pygtk
pygtk.require("2.0")
import gtk, gobject
import xdg.BaseDirectory


class GnawwyGTK(object):
    def __init__(self):
        # Load configuration
        pynotify.init("gnawwy")
        self.loadConfigFile(os.path.join(xdg.BaseDirectory.xdg_config_home, "gnawwy/gnawwy"))

        # Construct the tray icon
        self.tray_icon = gtk.StatusIcon()
        self.tray_icon.set_from_stock(gtk.STOCK_ABOUT)
        self.tray_icon.set_visible(True)

        # Construct tray icon menu and attach it to the tray icon
        menu = gtk.Menu()
        item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        item.connect('activate', lambda w: gtk.main_quit())
        menu.append(item)
        self.tray_icon.connect('popup-menu', self.popup_menu_cb, menu)

        # Finally, set up a notify timeout after running it once
        self.notify()
        gobject.timeout_add(self.check_interval * 1000, self.notify)

    # Tray icon menu callback
    def popup_menu_cb(self, widget, button, time, data=None):
        data.show_all()
        data.popup(None, None, gtk.status_icon_position_menu, button, time, self.tray_icon)

    # Check the parsers and emit notifications
    def notify(self):
        new_items = []
        for section in self.parsers:
            print "Checking section %s." % section
            try:
                new_items += self.parsers[section].check()
            except urllib2.URLError:
                print "Error fetching new items."
        if new_items:
            for item in new_items:
                if "user" in item and item["user"] in self.usernames:
                    print "Not displaying tweet from self"
                else:
                    pynotify.Notification(item["title"], item["text"], "file://" + item["icon"].name).show()
        return True

    # Load settings from the specified config file.
    def loadConfigFile(self, filepath):
        # These will eventually be removed; for backwards compat purposes only. All config files should have these set!
        defaults = {"check_interval" : "60", "ssl" : "false"}
        self.check_interval = 30 # In case the _Global section isn't present
        configparse = ConfigParser.SafeConfigParser(defaults)
        try:
            configparse.readfp(open(filepath))
        except IOError:
            print "Error: configuration file not found. Going to configuration file editor."
            os.makedirs(os.path.dirname(filepath))
            shutil.copyfile(os.path.join(sys.path[0], 'defaultrc'), filepath)
            retcode = subprocess.call(['nano', filepath])
            print "Configuration file modified. Continuing..."

        self.parsers = {}
        self.usernames = []

        for section in configparse.sections():
            try:
                parsertype = configparse.get(section, "type")
                username = configparse.get(section, "username")
                password = configparse.get(section, "password")
                if parsertype == "twitter":
                    parser = twitterparser.TwitterParser(username, password)
                    self.usernames.append(username)
                elif parsertype == "email": # Email-unique settings
                    server = configparse.get(section, "server")
                    ssl = configparse.getboolean(section, "ssl")
                    parser = emailparser.EmailParser(server, username, password, use_ssl=ssl)
                elif parsertype == "settings": #global settings section
                    self.check_interval = configparse.getint(section, "check_interval")
                    self.trayicon = configparse.getboolean(section, "use_trayicon")
                else:
                    print "Unknown parser type %s found; skipping section %s." % (parsertype, section)
                    continue
                self.parsers[section] = parser
            except (ConfigParser.NoOptionError, ValueError) as error:
                print "Parsing section %s failed: %s." % (section, error)
    def usage():
        print "gnawwy.py [-t]"
        print "-t no tray icon"
    def main(self):
        gtk.main()

if __name__ == "__main__":
    gnawwy = GnawwyGTK()
    gnawwy.main()
