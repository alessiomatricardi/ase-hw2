from datetime import datetime
import unittest
import datetime
from monolith.database import db, User

from monolith import app as tested_app

# this allows us to test forms without WTForm token
tested_app.config['WTF_CSRF_ENABLED'] = False

#tested_app.testing = True

class TestApp(unittest.TestCase):

    # TODO REMEMBER TO DEFINE SINGLE TESTS METHODS PER EACH FUNCTIONALITY

    def test_homepage(self):  
        app = tested_app.test_client()
        response = app.get("/", content_type='html/text')
        
        self.assertEqual(response.status_code, 200)
        
        #self.assertEqual(response.data, b'Hi') #fails because the parameters have to be exactly the same

        # response.data is the string of the HTML page
        # assert b'Hi' in response.data
        # assert b'Admin' in response.data

    def test_login(self):  
        app = tested_app.test_client()
        data1 = { 'email' : 'example@example.com' , 'password' : 'admina' } # wrong password
        response = app.post("/login", data = data1 , content_type='html/text')
        
        #self.assertEqual(response.status_code, 200)
        
        assert b'email' in response.data # returns to the login page, without the password inserted
        app = tested_app.test_client()
        data2 = { 'email' : 'example@example.com' , 'password' : 'admin' } # correct password
        response = app.post(
            "/login", 
            data = data2 , 
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )
        #response = app.get("/", content_type='html/text')

        #self.assertEqual(response.status_code, 200)
        
        assert b'Admin' in response.data # we hav to work on this because it doesn't take the password in this format
        
    def test_register(self):
        app = tested_app.test_client()

        # new user to register data
        data1 = { 'email' : 'prova3@mail.com' , 'firstname': 'Mario', 'lastname': 'Rossi', 
        'password' : 'prova123', 'date_of_birth': '25/05/1990'} 
        response = app.post("/register", data = data1 , content_type='application/x-www-form-urlencoded',follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)


        assert b"<li>\n      Mario Rossi\n      </li>" in response.data
        
        # register again the same user  
        response = app.post("/register", data = data1 , content_type='application/x-www-form-urlencoded',follow_redirects=True)
        
        print(response.data)
        self.assertEqual(response.status_code, 400)
        
        assert b"This email has already been used in a previous registration, please register with another email." in response.data

    def test_unregister(self):
        app = tested_app.test_client()
        
        # login in previously created password
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
        
        assert b"<h2> Mario, are you sure you really want to unregister yourself? If so insert your password and confirm</h2>" in response.data

        # unregister with correct password
        data_unregister = { 'password' : 'prova123' }

        response = app.post("/unregister", data = data_unregister , content_type='application/x-www-form-urlencoded',follow_redirects=True)
        
        assert b"Anonymous" in response.data

        with tested_app.app_context():
            row = db.session.query(User).where(User.id==4)
            row = [ob for ob in row]
            user = row[0]
            print(row)
            self.assertEqual(user.is_active,False)

            db.session.query(User).where(User.id==4).delete()
            db.session.commit()

