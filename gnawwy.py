import pynotify
import time, ConfigParser, os, sys
import twitterparser, emailparser
import pygtk
pygtk.require("2.0")
import gtk, gobject


class GnawwyGTK(object):
    def __init__(self):
        # Load configuration
        pynotify.init("gnawwy")
        self.loadConfigFile(os.path.expanduser('~/.gnawwyrc'))
        
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
            new_items += parsers[section].check()
        if new_items:
            for item in new_items:
                pynotify.Notification(item["title"], item["text"], "file://" + item["icon"].name).show()
        return True
    
    # Load settings from the specified config file.
    def loadConfigFile(self, filepath):
        # These will eventually be removed; for backwards compat purposes only. All config files should have these set!
        defaults = {"check_interval" : "60", "ssl" : "false"}
        self.check_interval = 60 # In case the _Global section isn't present
        configparse = ConfigParser.SafeConfigParser(defaults)
        try:
            configparse.readfp(open(filepath))
        except IOError:
            print "Error: configuration file not found. Create a .gnawwyrc in your home directory; see the README for the format."
            sys.exit()
            
        self.parsers = {}

        for section in configparse.sections():
            if section == "_Global": # Special section for global settings
                self.check_interval = configparse.getint(section, "check_interval")
                continue
            try:
                parsertype = configparse.get(section, "type")
                username = configparse.get(section, "username")
                password = configparse.get(section, "password")
                if parsertype == "twitter":
                    parser = twitterparser.TwitterParser(username, password)
                elif parsertype == "email": # Email-unique settings
                    server = configparse.get(section, "server")
                    ssl = configparse.getboolean(section, "ssl")
                    parser = emailparser.EmailParser(server, username, password, use_ssl=ssl)
                else:
                    print "Unknown parser type %s found; skipping section %s." % (parsertype, section)
                    continue
                parsers[section] = parser
            except (ConfigParser.NoOptionError, ValueError) as error:
                print "Parsing section %s failed: %s." % (section, error)
    
    def main(self):
        gtk.main()

if __name__ == "__main__":
    gnawwy = GnawwyGTK()
    gnawwy.main()
