#!/usr/bin/env python
# coding=utf-8

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import RockPaperScissorsApi

from models import User

class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        for user in users:
            subject = 'This is a reminder!'
            body = 'Hello {}, try out rock, paper, scissors!'.format(user.name)
            # This will send test emails, the arguments to send_mail are:
            # from, to, subject, body
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)


class UpdateUserStats(webapp2.RequestHandler):
    def post(self):
        """Update game listing announcement in memcache."""
        RockPaperScissorsApi._cache_user_stats()
        self.response.set_status(204)

app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_user_stats', UpdateUserStats),
], debug=True)
