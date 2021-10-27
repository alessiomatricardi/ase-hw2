import unittest
from monolith.message_logic import MessageLogic
from monolith import app

#APP = app.test_client()

class TestAdd(unittest.TestCase):
    def test_name(self):
        with app.app_context():
        # il db è vuoto
            m = MessageLogic()
            result = m.get_list_of_recipients_email(1) # retrieve all the users that user 1 (admin) can write to
            expected_result = ("example2@example.com", "example2@example.com")
            self.assertEqual(result[0], expected_result)