import unittest
from monolith.message_logic import MessageLogic
from monolith import app
import os

#
# TODO empty the db
# TODO eventually, insert some default data in the db
#


def empty_database():
    if os.path.exists("../mmiab.db"):
        os.remove("mmiab.db")
        print("File removed")
        open("../myfile.txt", "x")
    else:
        print("The file does not exist")

def fill_database_with_default_values():
    # TODO fill the database
    return True

class TestAdd(unittest.TestCase):
    def test_correct_get_list_of_recipients_email(self):
        return True

class TestNewMessage(unittest.TestCase):
    def test_name(self):
        with app.app_context():
            m = MessageLogic()
            result = m.get_list_of_recipients_email(1) # retrieve all the users that user 1 (admin) can write to
            expected_result = ("prova@mail.com", "prova@mail.com")
            self.assertEqual(result[0], expected_result) # test that only the 1st recipient is correct