import unittest
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
