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
