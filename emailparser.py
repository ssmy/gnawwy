#!/usr/bin/python
import imaplib, time, email.utils, email.parser, calendar


class EmailParser:
    def __init__(self, server, username, password, port=None, 
use_ssl=False, last_check=time.time()):
        self.server = server
        if not port:
            if use_ssl: self.port = 993
            else: self.port = 110
        else:
            self.port = port
        if use_ssl: self.imap = imaplib.IMAP4_SSL(self.server, 
self.port)
        else: self.imap = imaplib.IMAP4_SSL(self.server, self.port)
        self.imap.login(username, password)
        self.last_check = last_check
    def check(self):
        """
        Check for messages received since the last check.
        Return the number of unread messages.
        """
        self.imap.select()
        response, unseen = self.imap.search(None, 'UNSEEN')
        indices = unseen[0].split()
        nmessages = len(indices)
        i = nmessages - 1
        notifications = []
        while i > 0:
            # Fetch the received date and remove the preceding 'Date: '
            rfc2822 = self.imap.fetch(indices[i], '(BODY[HEADER.FIELDS (DATE)])')[1][0][1][6:]
            time_received = time.mktime(email.utils.parsedate(rfc2822))
            if time_received < self.last_check:
                break
            sender = self.imap.fetch(indices[i], '(BODY[HEADER.FIELDS (FROM)])')[1][0][1][6:-4]
            subject = self.imap.fetch(indices[i], '(BODY[HEADER.FIELDS (SUBJECT)])')[1][0][1][9:-4]
            notifications.append({"title" : sender, "text" : subject, "icon" : open("/dev/null")})
            i -= 1
        self.last_check = time.time()
        return notifications
