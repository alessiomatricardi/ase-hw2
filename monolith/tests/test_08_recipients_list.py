import unittest
from monolith.list_logic import ListLogic
from monolith import app

class TestRecipientsList(unittest.TestCase):
    def test_list_logic_blacklist(self):
        
        with app.app_context():
            l = ListLogic()

            # 2 is blocking 6 and is blocked by 3
            blacklist = l.retrieving_users_in_blacklist(2)
            result = [(b.blocking_user_id, b.blocked_user_id) for b in blacklist]
            expected_result = [(2,5), (3,2)]
            self.assertEqual(result, expected_result)

            # 3 is blocking 2 and is blocked by 4
            blacklist = l.retrieving_users_in_blacklist(3)
            result = [(b.blocking_user_id, b.blocked_user_id) for b in blacklist]
            expected_result = [(3,2), (4,3)]
            self.assertEqual(result, expected_result)

            # 4 is blocking 3 and is blocked by 5
            blacklist = l.retrieving_users_in_blacklist(4)
            result = [(b.blocking_user_id, b.blocked_user_id) for b in blacklist]
            expected_result = [(5,4), (4,3)]
            self.assertEqual(result, expected_result)
            
            # 5 is blocking 4 and is blocked by 2
            blacklist = l.retrieving_users_in_blacklist(5)
            result = [(b.blocking_user_id, b.blocked_user_id) for b in blacklist]
            expected_result = [(2,5), (5,4)]
            self.assertEqual(result, expected_result)

    def test_list_logic_recipients_list(self):
        
        with app.app_context():
            l = ListLogic()

            # 2 should be able to see only 4
            recipients_list = l.retrieving_recipients(2)
            result = [b.id for b in recipients_list]
            expected_result = [4]
            self.assertEqual(result, expected_result)

            # 3 should be able to see only 5
            recipients_list = l.retrieving_recipients(3)
            result = [b.id for b in recipients_list]
            expected_result = [5]
            self.assertEqual(result, expected_result)

            # 4 should be able to see only 2
            recipients_list = l.retrieving_recipients(4)
            result = [b.id for b in recipients_list]
            expected_result = [2]
            self.assertEqual(result, expected_result)

            # 5 should be able to see only 3
            recipients_list = l.retrieving_recipients(5)
            result = [b.id for b in recipients_list]
            expected_result = [3]
            self.assertEqual(result, expected_result)

    def test_recipients_list_rendering(self):
        tested_app = app.test_client()
        
        # checking that accessing the recipients list redirects to the login page if not already logged in
        response = tested_app.get("/users", content_type='html/text', follow_redirects=True)
        assert b'<label for="email">E-mail</label>' in response.data 

        # logging in
        data1 = { 'email' : 'prova2@mail.com' , 'password' : 'prova123' }
        response = tested_app.post("/login", data = data1 , content_type='application/x-www-form-urlencoded', follow_redirects=True)
        assert b'Hi Damiano' in response.data 
          
        # checking the presence of the correct button to write to specific recipient
        response = tested_app.get("/users", data = data1 , content_type='html/text', follow_redirects=True)
        assert b'Write to' in response.data 

        # checking the presence of the correct user in recipients list
        assert b'Carlo Neri' in response.data

