from datetime import datetime
import unittest
import datetime
from monolith.database import db, User

from monolith import app as tested_app


class TestAuthAndReg(unittest.TestCase):

    # TODO REMEMBER TO DEFINE SINGLE TESTS METHODS PER EACH FUNCTIONALITY

    def test_homepage(self):  
        app = tested_app.test_client()
        
        # testing the Welcome Page of an unlogged user
        response = app.get("/", content_type='html/text')
        self.assertEqual(response.status_code, 200)
        assert b'Hi Anonymous' in response.data
        

    def test_login_logout(self):  
        app = tested_app.test_client()

        # testing that the login fails
        data1 = { 'email' : 'example@example.com' , 'password' : 'admina' } # wrong password
        response = app.post("/login", data = data1 , content_type='html/text')
        assert b'<label for="email">E-mail</label>' in response.data # returns to the login page
        
        # checking that the login succeeds
        app = tested_app.test_client()
        data2 = { 'email' : 'example@example.com' , 'password' : 'admin' } # correct password
        response = app.post(
            "/login", 
            data = data2 , 
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )
        assert b'Hi Admin' in response.data 

        # checking that the login redirects to the Home when the user is already logged in
        response = app.get("/login", content_type='html/text', follow_redirects=True)
        assert b'Hi Admin' in response.data

        # checking that the logout succeeds 
        response = app.get("/logout", content_type='html/text', follow_redirects=True)
        assert b'Hi Anonymous' in response.data


    def test_register(self):
        app = tested_app.test_client()

        # new user to register data
        data1 = { 'email' : 'prova3@mail.com' , 'firstname': 'Mario', 'lastname': 'Rossi', 
        'password' : 'prova123', 'date_of_birth': '1990-05-25'} 
        response = app.post("/register", data = data1 , content_type='application/x-www-form-urlencoded',follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        assert b'Hi Anonymous' in response.data
        
        # try to register again the same user  
        response = app.post("/register", data = data1 , content_type='application/x-www-form-urlencoded',follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        assert b"please register with another email." in response.data


    def test_unregister(self):
        app = tested_app.test_client()
        
        # login in previously created account
        data_login = { 'email' : 'prova3@mail.com' , 'password' : 'prova123' } 
        response = app.post(
            "/login", 
            data = data_login , 
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)

        # unregister with wrong password
        data_unregister = { 'password' : 'xxx' }
        response = app.post("/unregister", data = data_unregister , content_type='application/x-www-form-urlencoded',follow_redirects=True)
        assert b"Mario, are you sure you really want to unregister yourself?" in response.data

        # unregister with correct password
        data_unregister = { 'password' : 'prova123' }
        response = app.post("/unregister", data = data_unregister , content_type='application/x-www-form-urlencoded',follow_redirects=True)
        assert b"Anonymous" in response.data

        # further checks on database
        with tested_app.app_context():
            row = db.session.query(User).where(User.id==6)
            row = [ob for ob in row]
            user = row[0]
            self.assertEqual(user.is_active,False)

            # deleting the test account
            db.session.query(User).where(User.id==6).delete()
            db.session.commit()

