from monolith.database import db, Message_Recipient, Message, User, Blacklist, Report
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

            example = User()
            example.email = 'prova2@mail.com'
            example.firstname = 'Damiano'
            example.lastname = 'Rossi'
            example.date_of_birth = datetime.datetime(random.randint(1960, 2000), random.randint(1,12), random.randint(1,29))
            example.is_admin = False
            example.set_password('prova123')
            db.session.add(example)

            example = User()
            example.email = 'prova4@mail.com'
            example.firstname = 'Barbara'
            example.lastname = 'Verdi'
            example.date_of_birth = datetime.datetime(random.randint(1960, 2000), random.randint(1,12), random.randint(1,29))
            example.is_admin = False
            example.set_password('prova123')
            db.session.add(example)

            example = User()
            example.email = 'prova5@mail.com'
            example.firstname = 'Carlo'
            example.lastname = 'Neri'
            example.date_of_birth = datetime.datetime(random.randint(1960, 2000), random.randint(1,12), random.randint(1,29))
            example.is_admin = False
            example.set_password('prova123')
            db.session.add(example)

            # add 4 blacklist istances
            blacklist = Blacklist()
            blacklist.blocking_user_id = 2
            blacklist.blocked_user_id = 5
            db.session.add(blacklist)

            blacklist = Blacklist()
            blacklist.blocking_user_id = 3
            blacklist.blocked_user_id = 2
            db.session.add(blacklist)

            blacklist = Blacklist()
            blacklist.blocking_user_id = 5
            blacklist.blocked_user_id = 4
            db.session.add(blacklist)

            blacklist = Blacklist()
            blacklist.blocking_user_id = 4
            blacklist.blocked_user_id = 3
            db.session.add(blacklist)
            
            # add messages
            message = Message()
            message.content = 'ciao'
            message_recipient = Message_Recipient()
            message.sender_id = 2
            message_recipient.id = 1
            message_recipient.recipient_id = 3
            message.is_sent = True
            message.is_delivered  = False
            message_recipient.is_read = False
            message.deliver_time = datetime.datetime(2031,10,29,18,32)
            db.session.add(message)
            db.session.add(message_recipient)

            message = Message()
            message.content = 'ciao'
            message_recipient = Message_Recipient()
            message.sender_id = 3
            message_recipient.id = 2
            message_recipient.recipient_id = 5
            message.is_sent = True
            message.is_delivered  = True
            message_recipient.is_read = False
            message.deliver_time = datetime.datetime(2021,9,29,18,32)
            db.session.add(message)
            db.session.add(message_recipient)

            message = Message()
            message.content = 'ciao'
            message_recipient = Message_Recipient()
            message.sender_id = 2
            message_recipient.id = 3
            message_recipient.recipient_id = 3
            message.is_sent = True
            message.is_delivered  = True
            message_recipient.is_read = False
            message.deliver_time = datetime.datetime(2021,9,29,18,32)
            db.session.add(message)
            db.session.add(message_recipient)

            message = Message()
            message.content = 'Testo a caso'
            message_recipient = Message_Recipient()
            message.sender_id = 4
            message_recipient.id = 4
            message_recipient.recipient_id = 3
            message.is_sent = True
            message.is_delivered  = True
            message_recipient.is_read = False
            message.deliver_time = datetime.datetime(2021,11,2,18,30)
            db.session.add(message)
            db.session.add(message_recipient)
            message_recipient = Message_Recipient()
            message_recipient.id = 4
            message_recipient.recipient_id = 1
            message_recipient.is_read = False
            db.session.add(message_recipient)

            message = Message()
            message.content = 'Messaggio da Barbara'
            message_recipient = Message_Recipient()
            message.sender_id = 4
            message_recipient.id = 5
            message_recipient.recipient_id = 1
            message.is_sent = True
            message.is_delivered  = False
            message_recipient.is_read = False
            message.deliver_time = datetime.datetime(2021,11,29,10,15)
            db.session.add(message)
            db.session.add(message_recipient)

            message = Message()
            message.content = 'Messaggio per Barbara da utente 5'
            message_recipient = Message_Recipient()
            message.sender_id = 5
            message_recipient.id = 6
            message_recipient.recipient_id = 4
            message.is_sent = True
            message.is_delivered  = True
            message_recipient.is_read = False
            message.deliver_time = datetime.datetime(2021,11,4,17,25)
            db.session.add(message)
            db.session.add(message_recipient)

            message = Message()
            message.content = 'Messaggio per Barbara da utente 3'
            message_recipient = Message_Recipient()
            message.sender_id = 1
            message_recipient.id = 7
            message_recipient.recipient_id = 4
            message.is_sent = True
            message.is_delivered  = True
            message_recipient.is_read = True
            message.deliver_time = datetime.datetime(2021,11,4,9,10)
            db.session.add(message)
            db.session.add(message_recipient)
       
            db.session.commit()

            # TODO create default reports
            # TODO create default blacklists

            #assert b'Ciao' in 'Ciao'

