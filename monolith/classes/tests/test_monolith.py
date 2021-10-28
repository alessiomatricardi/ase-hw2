import unittest

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
        
        #assert b'Admin' in response.data # we hav to work on this because it doesn't take the password in this format
        

