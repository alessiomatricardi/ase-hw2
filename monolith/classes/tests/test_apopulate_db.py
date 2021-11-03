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
            example.email = 'prova4@example.com'
            example.firstname = 'Barbara'
            example.lastname = 'Verdi'
            example.date_of_birth = datetime.datetime(random.randint(1960, 2000), random.randint(1,12), random.randint(1,29))
            example.is_admin = False
            example.set_password('prova123')
            db.session.add(example)
            db.session.commit()

            example = User()
            example.email = 'prova5@example.com'
            example.firstname = 'Carlo'
            example.lastname = 'Neri'
            example.date_of_birth = datetime.datetime(random.randint(1960, 2000), random.randint(1,12), random.randint(1,29))
            example.is_admin = False
            example.set_password('prova123')
            db.session.add(example)
            db.session.commit()
            
            # add 3 messages
            for i in range(1,11):
                message = Message()
                message.sender_id = i % 3 + 1
                message.content = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."
                message.is_sent = random.randint(0,1)
                message.is_delivered = 0 if not message.is_sent else random.randint(0,1)
                message.deliver_time = datetime.datetime(2021, 10, 30, 23, 59) if message.is_delivered else datetime.datetime(2021, 11, random.randint(1,30), random.randint(0,23), random.randint(0,59)) 
                db.session.add(message)
            
            # create for each message at least 1 recipient
            for i in range(1,11):
                sender_id = db.session.query(Message).filter(Message.id == i).first().sender_id
                list_of_users_id = [sender_id]
                for j in range(1,random.randint(2,3)): # suppose that every message may have at least 4 recipients
                    message_recipient = Message_Recipient()
                    message_recipient.id = i
                    recipient_id = random.randint(1,3)
                    while recipient_id in list_of_users_id:
                        recipient_id = random.randint(1,3)
                    list_of_users_id.append(recipient_id)
                    message_recipient.recipient_id = recipient_id
                    message_recipient.read_time = datetime.datetime(2000, 1, 1)
                    #
                    # TODO find a way to set a datetime to null
                    #
                    db.session.add(message_recipient)

            db.session.commit()

            # TODO create default reports
            # TODO create default blacklists

            #assert b'Ciao' in 'Ciao'

