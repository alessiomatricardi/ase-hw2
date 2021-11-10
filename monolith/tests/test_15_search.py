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

class TestSearch(unittest.TestCase):

    def test_search_user(self):
        app = tested_app.test_client()

        # trying to search without being logged in
        response = app.get(
            "/users/search", 
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

        # retrieving the search functionality
        response = app.get(
            "/users/search", 
            follow_redirects=True
            )
        assert b'Search' in response.data 
        assert b'Search a user' in response.data 
        assert b'firstname' in response.data
        assert b'lastname' in response.data
        assert b'email' in response.data

        # not filling any search field
        form = {
            'firstname': '',
            'lastname': '',
            'email': ''
        }
        response = app.post('/users/search', data=form, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        assert b'Insert at least one field' in response.data


        # searching a non-existing user
        form = {
            'firstname': 'Pippo',
            'lastname': 'Franco',
            'email': 'pippofranco@mail.com'
        }
        response = app.post('/users/search', data=form, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        assert b'No user found' in response.data

        # searching by firstname and lastname an existing user 
        form = {
            'firstname': 'Alessio',
            'lastname': 'Bianchi',
            'email': ''
        }
        response = app.post('/users/search', data=form, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        assert b'Alessio' in response.data 
        assert b'Bianchi' in response.data 

        # searching by email an existing user 
        form = {
            'firstname': '',
            'lastname': '',
            'email': 'prova@mail.com'
        }
        response = app.post('/users/search', data=form, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        assert b'Alessio' in response.data 
        assert b'Bianchi' in response.data 

        # searching an existing user with slightly wrong parameters
        form = {
            'firstname': 'Alesssio',
            'lastname': 'Binchi',
            'email': 'prova@mail.com'
        }
        response = app.post('/users/search', data=form, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        assert b'Alessio' in response.data 
        assert b'Bianchi' in response.data 

        # searching an existing user with wrong parameters
        form = {
            'firstname': 'Alesssio',
            'lastname': 'Binchi',
            'email': 'provaaaa@mail.com'
        }
        response = app.post('/users/search', data=form, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        assert b'Alessio' not in response.data 
        assert b'Bianchi' not in response.data 