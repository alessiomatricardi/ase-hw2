import unittest
from monolith.list_logic import ListLogic
from monolith import app
import datetime

app.config['WTF_CSRF_ENABLED'] = False

class TestRecipientsList(unittest.TestCase):
    def test_list_logic_blacklist(self):
        
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

    def test_list_logic_recipients_list(self):
        
        with app.app_context():
            l = ListLogic()

            # 2 should be able to see only 5
            recipients_list = l.retrieving_recipients(2)
            result = [b.id for b in recipients_list]
            expected_result = [5]
            self.assertEqual(result, expected_result)

            # 3 should be able to see only 6
            recipients_list = l.retrieving_recipients(3)
            result = [b.id for b in recipients_list]
            expected_result = [6]
            self.assertEqual(result, expected_result)

            # 5 should be able to see only 2
            recipients_list = l.retrieving_recipients(5)
            result = [b.id for b in recipients_list]
            expected_result = [2]
            self.assertEqual(result, expected_result)

            # 6 should be able to see only 3
            recipients_list = l.retrieving_recipients(6)
            result = [b.id for b in recipients_list]
            expected_result = [3]
            self.assertEqual(result, expected_result)

          


