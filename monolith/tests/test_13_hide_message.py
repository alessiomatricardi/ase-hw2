import datetime
import os
import unittest

from flask import Blueprint, config, redirect, render_template, request, json, current_app, abort
from flask.helpers import flash, send_from_directory, url_for
from flask.signals import message_flashed, request_finished
from sqlalchemy.orm import query
from sqlalchemy.sql.elements import Null
from werkzeug.utils import secure_filename
from monolith.message_logic import MessageLogic
from monolith.database import Message, Message_Recipient, User, db
from monolith.forms import MessageForm
from monolith.auth import current_user
from monolith import app as tested_app

class TestHide(unittest.TestCase):

    def test_hide_message(self):
        app = tested_app.test_client()

        # trying to hide without being logged in
        response = app.post(
            "/hide", 
            follow_redirects=True
            )
        assert b'<label for="email">E-mail</label>' in response.data 

        #login with Barbara# correct password
        data_login = { 'email' : 'prova4@mail.com' , 'password' : 'prova123' } 
        response = app.post(
            "/login", 
            data = data_login, 
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )
        assert b'Hi Barbara' in response.data 

        # retrieving received bottlebox
        response = app.get('/bottlebox/received',content_type='html/text',follow_redirects=True)
        assert b'Received Bottlebox' in response.data
        assert b'Messaggio per Barbara da utente 5' in response.data
        assert b'Messaggio per Barbara da utente 3' in response.data

        # submitting hide request for message received from user 5 (msg_id == 6)
        data_hide = { 'message_id' : '6' }
        response = app.post(
            "/hide", 
            data = data_hide, 
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )
        assert b'Received Bottlebox' in response.data
        assert b'Messaggio per Barbara da utente 5' not in response.data
        assert b'Messaggio per Barbara da utente 3' in response.data

        # hide request with a missing value for message_id
        data_hide = {'message_id': ''}
        response = app.post(
            "/hide",
            data=data_hide,
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 400)

        # hide request with a wrong format for message_id
        data_hide = {'message_id': 'not_an_integer'}
        response = app.post(
            "/hide",
            data=data_hide,
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 400)
