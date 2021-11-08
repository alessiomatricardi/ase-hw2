import unittest
from unittest import result

from werkzeug import test
from monolith.database import db, User
from monolith.user_logic import UserLogic
from monolith import app as tested_app
from monolith.forms import ModifyPersonalDataForm
from datetime import date, datetime

tested_app.config['WTF_CSRF_ENABLED'] = False

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
            self.assertEqual(4, result)


    def test_modify_password(self):
        with tested_app.app_context():
            # test that the password of user 5 is updated in the db
            ul.modify_password(5, 'prova456')
            expected_result = db.session.query(User).filter(User.id == 5).first().authenticate('prova456')
            self.assertEqual(expected_result, True)


    def rendering(self):
        app = tested_app.test_client()

        # check that if the user is not logged, the rendered page is the login page
        response = app.get("/profile", content_type='html/text', follow_redirects=True)
        assert b'<h1 class="h3 mb-3 fw-normal">Please sign in</h1>' in response.data

        response = app.get("/profile/data", content_type='html/text', follow_redirects=True)
        assert b'<h1 class="h3 mb-3 fw-normal">Please sign in</h1>' in response.data
        

        # do the login otherwise the sending of a new message can't take place
        data = { 'email' : 'prova5@mail.com' , 'password' : 'prova123' } 
        response = app.post(
            "/login", 
            data = data , 
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )
        
        # test that the rendered page is a form containing the personal data of the user 5
        response = app.get("/profile/data", content_type='html/text', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        assert b'Carlo' in response.data
        assert b'Neri' in response.data
        assert b'1995-06-12' in response.data

        form = {
            'firstname': 'Ferdinando',
            'lastname': 'Viola',
            'date_of_birth': '1976-09-20'
        }
        response = app.post('/profile/data', data=form, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        assert 'First name : Ferdinando' in response.data
        assert 'Last name : Viola' in response.data
        assert 'Birth date : 20/09/1976' in response.data

        form = {
            'firstname': 'Ferdinando',
            'lastname': 'Viola',
            'date_of_birth': 'INVALID_DATE'
        }
        response = app.post('/profile/data', data=form, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        assert b'Please insert correct data' in response.data
