import unittest
from monolith.list_logic import ListLogic
from monolith import app
import datetime

app.config['WTF_CSRF_ENABLED'] = False

class TestRecipientsList(unittest.TestCase):
    def test_list_logic(self):
        
        with app.app_context():
            l = ListLogic()

            # 2 is blocking 6 and is blocked by 3
            blacklist = l.retrieving_users_in_blacklist(2)
            result = [(b.blocking_user_id, b.blocked_user_id) for b in blacklist]
            expected_result = [(2,6), (3,2)]
            self.assertEqual(result, expected_result)

            # 3 is blocking 2 and is blocked by 5
            blacklist = l.retrieving_users_in_blacklist(3)
            result = [(b.blocking_user_id, b.blocked_user_id) for b in blacklist]
            expected_result = [(3,2), (5,3)]
            self.assertEqual(result, expected_result)

            # 5 is blocking 3 and is blocked by 6
            blacklist = l.retrieving_users_in_blacklist(5)
            result = [(b.blocking_user_id, b.blocked_user_id) for b in blacklist]
            expected_result = [(6,5), (5,3)]
            self.assertEqual(result, expected_result)
            
            # 6 is blocking 5 and is blocked by 2
            blacklist = l.retrieving_users_in_blacklist(6)
            result = [(b.blocking_user_id, b.blocked_user_id) for b in blacklist]
            expected_result = [(2,6), (6,5)]
            self.assertEqual(result, expected_result)

            




