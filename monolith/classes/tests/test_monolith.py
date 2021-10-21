import json
import unittest

from flask.templating import render_template

from monolith import app as tested_app

#tested_app.testing = True

class TestApp(unittest.TestCase):

    # TODO REMEMBER TO DEFINE SINGLE TESTS METHODS PER EACH FUNCTIONALITY

    def test_homepage(self):  
        app = tested_app.test_client()
        reply = app.get("/")
        result = str(reply.data, 'utf-8')
        self.assertEqual(result, '< h1 > My Message in a Bottle - - Primer < /h1 > \
\
\
                         Hi Anonymous, < a href="/login" > Log in < / a >')
