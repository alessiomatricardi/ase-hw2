import unittest
from monolith.list_logic import ListLogic
from monolith import app
import datetime

app.config['WTF_CSRF_ENABLED'] = False

class TestRecipientsList(unittest.TestCase):
    def test_list_logic(self):
        pass
