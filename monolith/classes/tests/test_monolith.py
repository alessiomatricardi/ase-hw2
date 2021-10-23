#from flask.templating import render_template
from flask.testing import TestCase

from monolith import app as tested_app

#tested_app.testing = True

class TestApp(TestCase):

    # TODO REMEMBER TO DEFINE SINGLE TESTS METHODS PER EACH FUNCTIONALITY

    def test_homepage(self):  
        self.app = tested_app.test_client()
        reply = self.app.get("/")
        self.assert_template_used('index.html')
        #self.assert_context("greeting", "hello")
