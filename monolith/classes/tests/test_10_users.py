import unittest
from monolith.database import db, User
from monolith.user_logic import UserLogic
from monolith import app as tested_app
from datetime import datetime

ul = UserLogic()

class TestUsers(unittest.TestCase):
    
    def test_modify_personal_data(self):
        with tested_app.app_context():
            # update personal data of user 5
            form = {
                'firstname': 'Francesco',
                'lastname': 'Viola',
                'date_of_birth': '1995-06-12'
            }
            result = ul.modify_personal_data(5, form)
            self.assertEqual(True, result)
            
            # test that the data are correctly modified for user 5
            result = db.session.query(User).filter(User.id == 5).first()
            self.assertEqual('Francesco', result.firstname)
            self.assertEqual('Viola', result.lastname)
            self.assertEqual(datetime.strptime('1995-06-12', '%Y-%m-%d').date(), result.date_of_birth)

            # test that the data are NOT correctly modified for user 5
            # to do this, an invalid form is created
            form = {
                'firstname': 'Francesco',
                'lastname': 'Viola',
                'date_of_birth': 'INVALID_DATE'
            }
            result = ul.modify_personal_data(5, form)
            self.assertEqual(False, result)
    
    def test_check_form_password(self):
        with tested_app.app_context():
            # try to change the password of user 5 but with an incorrect inserted old password
            result = ul.check_form_password(5, '123456789', 'ININFLUENT FOR TEST', 'ININFLUENT FOR TEST')
            self.assertEqual(1, result)

            # try to change the password of user 5 but with new_password == old_password
            result = ul.check_form_password(5, 'prova123', 'prova123', 'ININFLUENT FOR TEST')
            self.assertEqual(2, result)

            # try to change the password of user 5 but with new_password != repeat_new_password
            result = ul.check_form_password(5, 'prova123', 'prova456', 'prova789')
            self.assertEqual(3, result)

            # try to correctly change the password of user 5
            result = ul.check_form_password(5, 'prova123', 'prova456', 'prova456')
            self.assertEqual(0, result)

    def test_modify_password(self):
        with tested_app.app_context():
            # test that the password of user 5 is updated in the db
            ul.modify_password(5, 'prova456')
            expected_result = db.session.query(User).filter(User.id == 5).first().authenticate('prova456')
            self.assertEqual(expected_result, True)

    def test_rendering(self):
        app = tested_app.test_client()

        # check that if the user is not logged, the rendered page is the login page
        response = app.get("/profile", content_type='html/text', follow_redirects=True)
        assert b'<h1 class="h3 mb-3 fw-normal">Please sign in</h1>' in response.data

        response = app.get("/profile/data", content_type='html/text', follow_redirects=True)
        assert b'<h1 class="h3 mb-3 fw-normal">Please sign in</h1>' in response.data
        
        response = app.get("/profile/password", content_type='html/text', follow_redirects=True)
        assert b'<h1 class="h3 mb-3 fw-normal">Please sign in</h1>' in response.data

        # do the login otherwise the sending of a new message can't take place
        data = { 'email' : 'prova5@mail.com' , 'password' : 'prova456' } 
        response = app.post(
            "/login", 
            data = data , 
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )
        assert b'Hi Francesco' in response.data
        
        # test that the rendered page is a form containing the personal data of the user 5
        response = app.get("/profile/data", content_type='html/text', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        assert b'Francesco' in response.data
        assert b'Viola' in response.data
        assert b'1995-06-12' in response.data

        # test that the data of the profile are correctly modified (and so, they are rendered in the /profile page)
        form = {
            'firstname': 'Ferdinando',
            'lastname': 'Viola',
            'date_of_birth': '1976-09-20'
        }
        response = app.post('/profile/data', data=form, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        assert b'Ferdinando' in response.data
        assert b'Viola' in response.data
        assert b'20/09/1976' in response.data

        # test that incorrect data has been inserted and an error message is displayed
        form = {
            'firstname': 'Ferdinando',
            'lastname': 'Viola',
            'date_of_birth': 'INVALID_DATE'
        }
        response = app.post('/profile/data', data=form, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        assert b'Please insert correct data' in response.data


        # test that the rendered page is the form for the modificaton of the password
        response = app.get("/profile/data", content_type='html/text', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        
        # test that, if the old password is the same of the one stored in the database, an error message is displayed
        form = {
            'old_password': 'not_correct_password',
            'new_password': 'ININFLUENT FOR TEST',
            'repeat_new_password': 'ININFLUENT FOR TEST'
        }
        # note that the old_password prova123 is not correct because it has been changed in the test_modify_password()
        response = app.post("/profile/password", data=form,content_type='application/x-www-form-urlencoded', follow_redirects=True)
        assert b'<p>The old password you inserted is incorrect. Please insert the correct one.</p>' in response.data

        # test that, if the old and new password are the same, an error message is displayed
        form = {
            'old_password': 'prova456',
            'new_password': 'prova456',
            'repeat_new_password': 'ININFLUENT FOR TEST'
        }
        # note that the old_password prova123 is not correct because it has been changed in the test_modify_password()
        response = app.post("/profile/password", data=form,content_type='application/x-www-form-urlencoded', follow_redirects=True)
        assert b'Please insert a password different from the old one.' in response.data

        # test that, if the new password and the repeated new password are not equal, an error message is displayed
        form = {
            'old_password': 'prova456',
            'new_password': 'prova123',
            'repeat_new_password': 'prova789'
        }
        # note that the old_password prova123 is not correct because it has been changed in the test_modify_password()
        response = app.post("/profile/password", data = form ,content_type='application/x-www-form-urlencoded', follow_redirects=True)
        assert b'The new password and its repetition must be equal.' in response.data

        # test that the password is correctly modified, so the rendered page is user_details.html
        form = {
            'old_password': 'prova456',
            'new_password': 'prova123',
            'repeat_new_password': 'prova123'
        }
        # note that the old_password prova123 is not correct because it has been changed in the test_modify_password()
        response = app.post("/profile/password", data = form, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        assert b'Ferdinando' in response.data
        assert b'prova5@mail.com' in response.data
        assert b'Update' in response.data
        assert b'The new password and its repetition must be equal.' not in response.data
        assert b'Please insert a password different from the old one.' not in response.data
        assert b'The old password you inserted is incorrect. Please insert the correct one.' not in response.data

    # test rendering register html page 
    def test_reg_rendering(self):
        app = tested_app.test_client()

        # opening register page
        response = app.get('/register',content_type='html/text',follow_redirects=True)
        assert b'firstname' in response.data
        assert b'lastname' in response.data
        assert b'password' in response.data
        assert b'email' in response.data
        assert b'date_of_birth' in response.data
        assert b'Register' in response.data
        self.assertEqual(response.status_code,200)

        # giving wrong input
        data_wrong_register = { 'email' : 'not_an_email' , 'firstname': 'mars', 'lastname': 'alien', 
        'password' : 'short', 'date_of_birth': 'yesterday_not_a_date'} 
        response = app.post('/register', data = data_wrong_register, content_type = 'html/text',follow_redirects=True)
        assert b'firstname' in response.data
        assert b'lastname' in response.data
        assert b'password' in response.data
        assert b'email' in response.data
        assert b'date_of_birth' in response.data
        assert b'Register' in response.data
        self.assertEqual(response.status_code,200)

    def test_profiles_rendering(self):
        app = tested_app.test_client()

        # accessing a user page redirects to login if not already logged
        response = app.get('/users/4',content_type='html/text',follow_redirects=True)
        assert b'<label for="email">E-mail</label>' in response.data

        # accessing profile page redirects to login if not already logged
        response = app.get('/profile',content_type='html/text',follow_redirects=True)
        assert b'<label for="email">E-mail</label>' in response.data

        # trying to activate content_filter redirects to login if not already logged
        response = app.post('/profile/content_filter',content_type='html/text',follow_redirects=True)
        self.assertEqual(response.status_code,403)

        # trying to get profile image redirects to login if not already logged
        response = app.get('/profile/picture',content_type='html/text',follow_redirects=True)
        assert b'<label for="email">E-mail</label>' in response.data

        #login
        data_login = { 'email' : 'prova4@mail.com' , 'password' : 'prova123' } # correct password
        response = app.post(
            "/login", 
            data = data_login, 
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )
        assert b'Hi Barbara' in response.data 

        # wrong user id field
        response = app.get('/users/not_a_valid_id',content_type='html/text',follow_redirects=True)
        self.assertEqual(response.status_code,404)

        # user accesses to her/his profile trough users router
        response = app.get('/users/4',content_type='html/text',follow_redirects=True)
        assert b'Unregister' in response.data

        # accessing to a blocked/blocking user page returns an error
        response = app.get('/users/5',content_type='html/text',follow_redirects=True)
        self.assertEqual(response.status_code,404)

        # accessing to a non-blocked/blocking user page 
        response = app.get('/users/3',content_type='html/text',follow_redirects=True)
        assert b'prova2@mail.com' in response.data
        assert b'Damiano Rossi' in response.data
        assert b'Block this user' in response.data
        assert b'Write a message' in response.data

        # activating the content filter once logged in redirects to the user profile 
        response = app.post('/profile/content_filter', data = { 'filter_enabled' : 'True' ,'submit' : 'Update' }, content_type='application/x-www-form-urlencoded',follow_redirects=True)
        assert b'<input checked class="form-check-input" id="filter_enabled" name="filter_enabled" type="checkbox" value="y">' in response.data

        # disabling the content filter once logged in redirects to the user profile
        response = app.post('/profile/content_filter', data = { 'filter_enabled' : '' ,'submit' : 'Update' }, content_type='application/x-www-form-urlencoded',follow_redirects=True)
        # print(response.data)
        assert b'<input class="form-check-input" id="filter_enabled" name="filter_enabled" type="checkbox" value="y">' in response.data