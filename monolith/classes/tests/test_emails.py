import unittest
from unittest import result
from warnings import resetwarnings

#from flask import app
from flask.signals import message_flashed
from flask_wtf.recaptcha.widgets import RECAPTCHA_SCRIPT

from monolith.app import create_app
from monolith.emails import send_email

class TestNewMessage(unittest.TestCase):

    def __init__(self, *args, **kw):
        super(TestNewMessage, self).__init__(*args, **kw)
        self.app = create_app(True) # create an instance of the app in test mode
    
    def test_send_email(self):
        with self.app.app_context():
            
            # email correctly sent 
            msg = f'Subject: SUBJECT\n\nTEXT.'
            result = send_email("user1@example.com", msg)
            self.assertEqual(True, result)

            # email not correctly sent
            msg = None
            result = send_email("user1@example.com", msg)
            self.assertEqual(False, result)

            # email not correctly sent
            msg = f'Subject: SUBJECT\n\nTEXT.'
            result = send_email(None, msg)
            self.assertEqual(False, result)

            # email not correctly sent
            msg = None
            result = send_email(None, msg)
            self.assertEqual(False, result)
