import unittest
import os
import io
from flask.helpers import send_from_directory

from monolith import app as tested_app

class TestProfile(unittest.TestCase):
    
    # TODO  commentateli man mano che li fate :)

    def test_profile_picture(self):
        
        app = tested_app.test_client()

        # get an user picture without login
        response = app.get('/users/4/picture', content_type='html/text', follow_redirects=True)
        assert b'<label for="email">E-mail</label>' in response.data
        
        # get form for modifying profile picture without login
        response = app.get('/profile/picture/edit', content_type='html/text', follow_redirects=True)
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

        # get an user picture with wrong format
        response = app.get('/users/WRONG_ID/picture', content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

        # get an user picture with rights
        response = app.get('/users/3/picture', content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # get an user picture without rights
        response = app.get('/users/5/picture', content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code, 403)

        # get form for modifying profile picture without login
        response = app.get('/profile/picture/edit', content_type='html/text', follow_redirects=True)
        assert b'Select a new profile image' in response.data

        # upload new profile image with wrong format
        pictureData = {
            'image': '',
        }

        response = app.post("/profile/picture/edit", data=pictureData, content_type='multipart/form-data', follow_redirects=True)
        assert b'Select a new profile image' in response.data

        # upload new profile image with wrong format
        pictureData = {
            'image': (io.BytesIO(b"contenuto del file"), 'test.pdf'),
        }

        response = app.post("/profile/picture/edit", data=pictureData,
                            content_type='multipart/form-data', follow_redirects=True)
        assert b'This file format is not supported' in response.data
