import unittest
from monolith.bottlebox_logic import BottleBoxLogic
from monolith import app
import datetime

app.config['WTF_CSRF_ENABLED'] = False

class TestBottlebox(unittest.TestCase):
    
    def test_bottlebox_users(self):
        with app.app_context():
    
            #testing the retrieving of non admin users
            b = BottleBoxLogic()
            result = b.retrieving_all_users() # retrieve all the non admin users 
            result_id = [ob.get_id() for ob in result]
            result_email = [ob.email for ob in result]
            result_firstname = [ob.firstname for ob in result]
            result_lastname = [ob.lastname for ob in result]
            result_administrator = [ob.is_admin for ob in result]
            expected_id = [2,3,5,6]
            expected_email = ["prova@mail.com", "prova2@mail.com", "prova4@mail.com", "prova5@mail.com"]
            expected_firstname = ['Alessio','Damiano','Barbara', 'Carlo']
            expected_lastname = ['Bianchi','Rossi', 'Verdi', 'Neri']
            expected_administrator = [False,False, False, False]
            self.assertEqual(result_email,expected_email)
            self.assertEqual(result_firstname,expected_firstname)
            self.assertEqual(result_lastname,expected_lastname)
            self.assertEqual(result_administrator,expected_administrator)
    
    def test_bottleboxes(self):

        with app.app_context():

            # testing the retrieving of specific-user bottleboxes
            b = BottleBoxLogic()

            # pending messages for user 2
            result = b.retrieving_messages(2,1)
            result_id = [ob.get_id() for ob in result]
            result_sender = [ob.sender_id for ob in result]
            result_deliver_time = [ob.deliver_time for ob in result]
            result_delivered = [ob.is_delivered for ob in result]
            result_msg_content = [ob.content for ob in result]
            expected_id = [1]
            expected_sender = [2]
            expected_deliver_time = [datetime.datetime(2031,10,29,18,32)]
            expected_delivered = [False]
            expected_msg_content = ['ciao']
            self.assertEqual(result_id,expected_id)
            self.assertEqual(result_msg_content,expected_msg_content)
            self.assertEqual(result_sender,expected_sender)
            self.assertEqual(result_deliver_time,expected_deliver_time)
            self.assertEqual(result_delivered,expected_delivered)

            #received messages for user 2
            result = b.retrieving_messages(2,2)
            result_id = [ob.get_id() for ob in result]
            result_sender = [ob.sender_id for ob in result]
            result_deliver_time = [ob.deliver_time for ob in result]
            result_delivered = [ob.is_delivered for ob in result]
            result_msg_content = [ob.content for ob in result]
            expected_id = [2]
            expected_sender = [3]
            expected_deliver_time = [datetime.datetime(2021,9,29,18,32)]
            expected_delivered = [True]
            expected_msg_content = ['ciao']
            self.assertEqual(result_id,expected_id)
            self.assertEqual(result_msg_content,expected_msg_content)
            self.assertEqual(result_sender,expected_sender)
            self.assertEqual(result_deliver_time,expected_deliver_time)
            self.assertEqual(result_delivered,expected_delivered)

            #delivered messages for user 2
            result = b.retrieving_messages(2,3)
            result_id = [ob.get_id() for ob in result]
            result_sender = [ob.sender_id for ob in result]
            result_deliver_time = [ob.deliver_time for ob in result]
            result_delivered = [ob.is_delivered for ob in result]
            result_msg_content = [ob.content for ob in result]
            expected_id = [3 for ob in result]
            expected_sender = [2]
            expected_deliver_time = [datetime.datetime(2021,9,29,18,32)]
            expected_delivered = [True]
            expected_msg_content = ['ciao']
            self.assertEqual(result_id,expected_id)
            self.assertEqual(result_msg_content,expected_msg_content)
            self.assertEqual(result_sender,expected_sender)
            self.assertEqual(result_deliver_time,expected_deliver_time)
            self.assertEqual(result_delivered,expected_delivered)
    
    def test_rendering(self):
        tested_app = app.test_client()

        # checking that accessing the bottlebox home redirects to the login page if not already logged in
        response = tested_app.get("/bottlebox", content_type='html/text', follow_redirects=True)
        assert b'<label for="email">email</label>' in response.data 

        # logging in
        data1 = { 'email' : 'prova2@mail.com' , 'password' : 'prova123' }
        response = tested_app.post("/login", data = data1 , content_type='application/x-www-form-urlencoded', follow_redirects=True)
        assert b'Hi Damiano' in response.data 

        # checking the presence of the correct buttons to retrieve pending, received or delivered messages
        response = tested_app.get("/bottlebox", data = data1 , content_type='html/text', follow_redirects=True)
        assert b'id="bottlebox_button"' in response.data 

        # checking the rendering of pending messages bottlebox
        response = tested_app.get("/bottlebox/pending", data = data1 , content_type='html/text', follow_redirects=True)
        assert b'<h1>Pending Bottlebox</h1>' in response.data 

        # checking the rendering of received messages bottlebox
        response = tested_app.get("/bottlebox/received", data = data1 , content_type='html/text', follow_redirects=True)
        assert b'<h1>Received Bottlebox</h1>' in response.data 

        # checking the rendering of delivered messages bottlebox
        response = tested_app.get("/bottlebox/delivered", data = data1 , content_type='html/text', follow_redirects=True)
        assert b'<h1>Delivered Bottlebox</h1>' in response.data 




