import re
import unittest
import datetime
from unittest import result
from warnings import resetwarnings

#from flask import app
from flask.signals import message_flashed
from flask_wtf.recaptcha.widgets import RECAPTCHA_SCRIPT
from monolith.database import Message_Recipient, db, Message
from monolith.message_logic import MessageLogic
from monolith.app import create_app

m = MessageLogic()

class TestNewMessage(unittest.TestCase):

    def __init__(self, *args, **kw):
        super(TestNewMessage, self).__init__(*args, **kw)
        self.app = create_app() # create an instance of the app in test mode

    def test_get_list_of_recipients_email(self):
        with self.app.app_context():
            result = m.get_list_of_recipients_email(1) # retrieve all the users that user 1 can write to
            expected_result = ("prova@mail.com", "prova@mail.com")
            self.assertEqual(result[0], expected_result) # test that only the 1st recipient is correct

    def test_validate_message_fields(self):
        with self.app.app_context():
            message = Message()
            message.sender_id = 1
            message.content = "Ciao! sono l'utente 1"
            message.deliver_time = datetime.datetime.strptime("2021-11-01T15:45", '%Y-%m-%dT%H:%M')
            result = m.validate_message_fields(message)
            expected_result = True
            self.assertEqual(result, expected_result) # this test should pass

            #
            # TODO add test when the blacklist is implemented
            #

    def test_create_new_message(self):
        with self.app.app_context():
            message = Message()
            message.sender_id = 1
            message.content = "Ciao! sono l'utente 1"
            message.deliver_time = datetime.datetime.strptime("2021-11-01T15:45", '%Y-%m-%dT%H:%M')
            result = m.create_new_message(message)
            expected_result = db.session.query(Message).filter(Message.id == 4).first() # 4 because there should be 3 default messages in the db
            self.assertEqual(result['sender_id'], message.sender_id)
            self.assertEqual(result['content'],  message.content)
            self.assertEqual(result['deliver_time'],  message.deliver_time)

    def test_email_to_id(self):
        with self.app.app_context():
            result = m.email_to_id("prova@mail.com")
            self.assertEqual(2, result)

    def test_create_new_message_recipient(self):
        with self.app.app_context():
            message_recipient = Message_Recipient()
            message_recipient.id = 4 # create recipients for the previously insterted message
            # message_recipient.read_time = datetime.datetime(2020, 10, 6) # TODO it should be better to set a null vallue, but if done an error occurr
            message_recipient.recipient_id = 2
            result = m.create_new_message_recipient(message_recipient)
            expected_result = db.session.query(Message_Recipient).filter(Message_Recipient.id == 4).first()
            self.assertEqual(expected_result.id, result['id'])
            # self.assertEqual(expected_result.read_time, result['read_time'])
            self.assertEqual(expected_result.recipient_id, result['recipient_id'])
            self.assertEqual(expected_result.is_read, False)

    
    def test_send_bottle(self):
        with self.app.app_context():
            message = db.session.query(Message).filter(Message.id == 4).first()
            result = m.send_bottle(message)
            expected_result = db.session.query(Message).filter(Message.id == 4).first().is_sent
            self.assertEqual(expected_result, result)


    #
    # 
    # TODO test the update of is_delivered attribute
    # TODO test the sending of emails
    #
    #

    def test_rendering(self):
        tested_app = self.app.test_client()

        # check that if the user is not logged, the rendered page is the login page
        response = tested_app.get("/new_message", content_type='html/text', follow_redirects=True)
        assert b'<h1 class="h3 mb-3 fw-normal">Please sign in</h1>' in response.data
        

        # do the login otherwise the sending of a new message can't take place
        data = { 'email' : 'prova4@mail.com' , 'password' : 'prova123' } 
        response = tested_app.post(
            "/login", 
            data = data , 
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )

        # test that the new_message.html page is correctly rendered when "New message in a bottle" is clicked on the homepage
        response = tested_app.get("/new_message", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # test that the new_message.html page is correctly rendered when "Write to" is clicked on the recipient list page
        # in particular, the check verifies that the recipient passed in the URI is checked when the page is rendered
        response = tested_app.get("/new_message?single_recipient=prova@mail.com", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        assert b'<input type="checkbox" name="recipients" value=prova@mail.com checked>' in response.data

        # test that if no recipients are selected the page is re-rendered with a warning
        data = { 
            'content' : 'ININFLUENT FOR THE TEST' ,
            'deliver_time' : "2021-11-01T15:45",
            'submit': 'ININFLUENT FOR THE TEST',
            'attach_image': ''
        }
        response = tested_app.post("/new_message", data = data, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        assert b'<p>Please select at least 1 recipient</p>' in response.data

        # test that the message is saved as a draft, so the rendered page is the index.html
        data = { 
            'content' : 'ININFLUENT FOR THE TEST' ,
            'deliver_time' : "2021-11-01T15:45",
            'recipients': 'prova@mail.com',
            'submit': 'Save draft'
        }
        response = tested_app.post("/new_message", data = data, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        assert b'Hi Barbara!' in response.data 

        # test that the message is sent correctly, so the rendered page is the index.html
        data = { 
            'content' : 'ININFLUENT FOR THE TEST' ,
            'deliver_time' : "2021-11-01T15:45",
            'recipients': 'prova@mail.com',
            'submit': 'Send bottle'
        }
        response = tested_app.post("/new_message", data = data, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        assert b'Hi Barbara!' in response.data 

        #
        # TODO line 83 in messages.py
        #

        # test that neither a get or post request are done
        try:
            response = tested_app.put("/new_message")
        except RuntimeError as e:
            self.assertEqual('This should not happen!', e)
        self.assertEqual(response.status_code, 405)
