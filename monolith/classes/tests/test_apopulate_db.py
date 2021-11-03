from monolith.database import db, Message_Recipient, Message, User, Blacklist, Report
import datetime
import random

import re
import unittest
import datetime
from unittest import result
from warnings import resetwarnings

#from flask import app
from flask.signals import message_flashed
from flask_wtf.recaptcha.widgets import RECAPTCHA_SCRIPT
from monolith import app as tested_app


class TestPopulateDB(unittest.TestCase):

    def test_populate_db(self):
        with tested_app.app_context():
            # add 4 users
            example = User()
            example.email = 'prova@mail.com'
            example.firstname = 'Alessio'
            example.lastname = 'Bianchi'
            example.date_of_birth = datetime.datetime(random.randint(1960, 2000), random.randint(1,12), random.randint(1,29))
            example.is_admin = False
            example.set_password('prova123')
            db.session.add(example)
            db.session.commit()

            example = User()
            example.email = 'prova2@mail.com'
            example.firstname = 'Damiano'
            example.lastname = 'Rossi'
            example.date_of_birth = datetime.datetime(random.randint(1960, 2000), random.randint(1,12), random.randint(1,29))
            example.is_admin = False
            example.set_password('prova123')
            db.session.add(example)
            db.session.commit()

            example = User()
            example.email = 'prova4@mail.com'
            example.firstname = 'Barbara'
            example.lastname = 'Verdi'
            example.date_of_birth = datetime.datetime(random.randint(1960, 2000), random.randint(1,12), random.randint(1,29))
            example.is_admin = False
            example.set_password('prova123')
            db.session.add(example)
            db.session.commit()

            example = User()
            example.email = 'prova5@mail.com'
            example.firstname = 'Carlo'
            example.lastname = 'Neri'
            example.date_of_birth = datetime.datetime(random.randint(1960, 2000), random.randint(1,12), random.randint(1,29))
            example.is_admin = False
            example.set_password('prova123')
            db.session.add(example)
            db.session.commit()

            # add 4 blacklist istances
            blacklist = Blacklist()
            blacklist.blocking_user_id = 2
            blacklist.blocked_user_id = 5
            db.session.add(blacklist)
            db.session.commit()

            blacklist = Blacklist()
            blacklist.blocking_user_id = 3
            blacklist.blocked_user_id = 2
            db.session.add(blacklist)
            db.session.commit()

            blacklist = Blacklist()
            blacklist.blocking_user_id = 5
            blacklist.blocked_user_id = 4
            db.session.add(blacklist)
            db.session.commit()

            blacklist = Blacklist()
            blacklist.blocking_user_id = 4
            blacklist.blocked_user_id = 3
            db.session.add(blacklist)
            db.session.commit()
            
            # add 3 messages
            message = Message()
            message.content = 'ciao'
            message_recipient = Message_Recipient()
            message.sender_id = 2
            message_recipient.id = 1
            message_recipient.recipient_id = 3
            message.is_sent = True
            message.is_delivered  = False
            message_recipient.is_read = False
            message_recipient.read_time = None
            message.deliver_time = datetime.datetime(2031,10,29,18,32)
            db.session.add(message)
            db.session.add(message_recipient)
            db.session.commit()

            message = Message()
            message.content = 'ciao'
            message_recipient = Message_Recipient()
            message.sender_id = 3
            message_recipient.id = 2
            message_recipient.recipient_id = 5
            message.is_sent = True
            message.is_delivered  = True
            message_recipient.is_read = False
            message_recipient.read_time = None
            message.deliver_time = datetime.datetime(2021,9,29,18,32)
            db.session.add(message)
            db.session.add(message_recipient)
            db.session.commit()

            message = Message()
            message.content = 'ciao'
            message_recipient = Message_Recipient()
            message.sender_id = 2
            message_recipient.id = 3
            message_recipient.recipient_id = 3
            message.is_sent = True
            message.is_delivered  = True
            message_recipient.is_read = False
            message_recipient.read_time = None
            message.deliver_time = datetime.datetime(2021,9,29,18,32)
            db.session.add(message)
            db.session.add(message_recipient)
            db.session.commit()

            # TODO create default reports
            # TODO create default blacklists

            #assert b'Ciao' in 'Ciao'

