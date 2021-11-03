import unittest
from unittest import result
from warnings import resetwarnings

#from flask import app
from flask.signals import message_flashed
from flask_wtf.recaptcha.widgets import RECAPTCHA_SCRIPT

from monolith import app
from monolith.emails import send_email

class TestNewMessage(unittest.TestCase):
    
    def test_send_email(self):

        with app.app_context():
            
            # email correctly sent 
            msg = f'Subject: SUBJECT\n\nTEXT.'
            result = send_email("prova@mail.com", msg)
            self.assertEqual(True, result)

            
            # email not correctly sent
            msg = f'Subject: SUBJECT\n\nTEXT.'
            result = send_email('not_an_email', msg)
            self.assertEqual(False, result)

            '''
            # email not correctly sent
            msg = None
            result = send_email('', msg)
            self.assertEqual(False, result)
            '''