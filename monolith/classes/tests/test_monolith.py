import unittest

from monolith import app as tested_app

#tested_app.testing = True

class TestApp(unittest.TestCase):

    # TODO REMEMBER TO DEFINE SINGLE TESTS METHODS PER EACH FUNCTIONALITY

    def test_homepage(self):  
        app = tested_app.test_client()
        response = app.get("/", content_type='html/text')
        self.assertEqual(response.status_code, 200)
