import unittest
from monolith import app as tested_app
from monolith.calendar_logic import CalendatLogic
import json

class TestCalendar(unittest.TestCase):

    def test_get_list_of_sent_messages(self):
        with tested_app.app_context():
            cl = CalendatLogic()

            result = cl.get_list_of_sent_messages(4) # messages sent from user 4 (Barbara Verdi)
            result = json.loads(result)

            expected_result = ["Message sent to Admin Admin (example@example.com)", "2021-11-02T18:30", True]
            self.assertEqual(expected_result, result[0])


    def test_get_list_of_received_messages(self):
        with tested_app.app_context():
            cl = CalendatLogic()

            result = cl.get_list_of_received_messages(4) # messages received by user 4 (Barbara Verdi)
            result = json.loads(result)

            expected_result = ["Message received from Carlo Neri (prova5@mail.com)", "2021-11-04T17:25", True]
            self.assertEqual(expected_result, result[0])


    def test_rendering(self):
        app = tested_app.test_client()

        # check that if the user is not logged, the rendered page is the login page
        response = app.get("/calendar", content_type='html/text', follow_redirects=True)
        assert b'<h1 class="h3 mb-3 fw-normal">Please sign in</h1>' in response.data

        response = app.get("/calendar/sent", content_type='html/text', follow_redirects=True)
        assert b'<h1 class="h3 mb-3 fw-normal">Please sign in</h1>' in response.data
        
        response = app.get("/calendar/received", content_type='html/text', follow_redirects=True)
        assert b'<h1 class="h3 mb-3 fw-normal">Please sign in</h1>' in response.data

        # do the login otherwise the calendar cannot be rendered
        data = { 'email' : 'prova4@mail.com' , 'password' : 'prova123' } 
        response = app.post(
            "/login", 
            data = data , 
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
        )

        # test that the which_calendat.html page is correctly rendered when "Calendar" button is clicked on the homepage
        response = app.get("/calendar", content_type='html/text', follow_redirects=True)
        assert b'Sent messages' in response.data
        assert b'Received messages' in response.data
        self.assertEqual(response.status_code, 200)

        # test that the calendar.html page is correctly rendered when either "Calendar of sent messages"
        # or "Calendar of received messages" button is clicked on the which_calendar.html page
        response = app.get("/calendar/sent", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = app.get("/calendar/received", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code, 200)