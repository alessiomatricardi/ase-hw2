import unittest
from monolith import app

class TestReport(unittest.TestCase):
    def test_reports(self):
        tested_app = app.test_client()

        # without being logged in
        response = tested_app.post('/report', content_type = 'application/x-www-form-urlencoded', follow_redirects = True)
        self.assertEqual(response.status_code,401)

        # log in
        data = { 'email' : 'prova4@mail.com' , 'password' : 'prova123' } 
        response = tested_app.post(
            "/login", 
            data = data , 
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )
        assert b'Hi Barbara' in response.data

        # reporting a non-received message
        data_report1 = { 'message_id': '2'}
        response = tested_app.post('/report', data=data_report1, follow_redirects = True) 
        self.assertEqual(response.status_code,403)

        # reporting a received message
        data_report1 = { 'message_id': '6'}
        response = tested_app.post('/report', data=data_report1, follow_redirects = True) 
        self.assertEqual(response.status_code,200)

        # reportign again a received message
        data_report1 = { 'message_id': '6'}
        response = tested_app.post('/report', data=data_report1, follow_redirects = True) 
        self.assertEqual(response.status_code,409)

        # report request with a missing value for message_id
        data_report = {'message_id': ''}
        response = tested_app.post(
            "/report",
            data=data_report,
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 400)

        # hide request with a wrong format for message_id
        data_report = {'message_id': 'not_an_integer'}
        response = tested_app.post(
            "/report",
            data=data_report,
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 400)
